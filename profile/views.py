from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Count, F, Q
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from PIL import Image

import json

from . import forms
from . import models
from . import tokens

from project.models import Project, ProjectPosition, ProjectPositionApplication


def home(request):
    """Home page, also search"""

    search = ''
    if request.GET.get('search'):
        search = request.GET.get('search')

    show_position = None
    if request.GET.get('position'):
        show_position = request.GET.get('position')
        positions = (ProjectPosition.objects
                     .filter(title__iexact=show_position).values('project'))
        projects = (Project.objects.filter(id__in=positions, )
                    .filter(Q(title__icontains=search) |
                            Q(description__icontains=search)))
    else:
        # All projects
        projects = Project.objects.filter(Q(title__icontains=search) |
                                          Q(description__icontains=search))

    # Get all available positions
    taken = (ProjectPositionApplication.objects
             .filter(status='S').values('position'))
    positions = (ProjectPosition.objects.filter(project__in=projects)
                 .exclude(id__in=taken).values('title')
                 .order_by().annotate(Count('title')))

    return render(request, 'profile/index.html', {
                  'projects': projects,
                  'positions': positions,
                  'show_position': show_position,
                  'search': search})


def sign_in(request):
    redirect = None
    if request.GET.get('next'):
        redirect = request.GET.get('next')
    if request.POST.get('next'):
        redirect = request.POST.get('next')

    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            if form.user_cache is not None:
                user = form.user_cache
                if user.is_active:
                    login(request, user)
                    if redirect:
                        return HttpResponseRedirect(redirect)
                    else:
                        profile = models.Profile.objects.get(user=user)
                        if not profile.bio or not profile.avatar:
                            messages.success(request,("Please make sure your "
                            "profile is complete by entering a bio and "
                            "uploading a profile image."))
                            return HttpResponseRedirect(reverse(
                                                'profile:my_profile'))
                        return HttpResponseRedirect(reverse('profile:home'))

    return render(request, 'profile/signin.html', {'form': form,
                                                   'redirect': redirect})


def sign_up(request):
    form = forms.SubscriberForm()
    if request.method == 'POST':
        form = forms.SubscriberForm(data=request.POST)
        if form.is_valid():
            # Unpack form values
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            # Create the User record
            user = User(username=username, email=email)
            user.set_password(password)
            user.is_active = False
            user.save()

            # Send confirmation email
            current_site = get_current_site(request)
            subject = 'Activate your STB account.'
            message = render_to_string('acc_active_email.html', {
                'user': user, 'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': tokens.account_activation_token.make_token(user),
            })
            toemail = form.cleaned_data.get('email')
            send_mail(subject, message, 'stb@shawcando.com',
                      [toemail], html_message=message, fail_silently=True)

            messages.success(request,
                             ("You're now a user! Please click on the "
                              "confirmation link emailed to you to activate "
                              "your account."))

            return HttpResponseRedirect(reverse('profile:home'))
    return render(request, 'profile/signup.html', {'form': form})


def sign_out(request):
    logout(request)
    messages.success(request, "You've been signed out. Come back soon!")
    return HttpResponseRedirect(reverse('profile:home'))


def profile(request, pk=None):
    current_user = request.user
    if pk is None:
        user = request.user
    else:
        user = User.objects.get(id=pk)

    profile = models.Profile.objects.get(user=user)
    skills = models.UserSkill.objects.filter(user=user)
    projects = Project.objects.filter(user=user)
    positions = ProjectPositionApplication.objects.filter(user=user,
                                                          status='S')
    return render(request, 'profile/profile.html',
                  {'current_user': current_user,
                   'user': user,
                   'profile': profile,
                   'skills': skills,
                   'projects': projects,
                   'positions': positions})


@login_required
def profile_edit(request):
    user = request.user
    current_name = request.user.username
    current_email = request.user.email
    skills = models.UserSkill.objects.filter(user=user)
    form = forms.ProfileForm(instance=request.user.profile)
    if request.method == 'POST':
        form = forms.ProfileForm(request.POST, request.FILES or None,
                                 instance=request.user.profile)
        if form.is_valid():
            form.save()
            display_message = 'Your profile was successfully updated!'

            # Handle username change
            new_username = request.POST.get('username')
            if current_name != new_username:
                user.username = new_username

            # Handle email change - Send confirmation email
            new_email = request.POST.get('email')
            if current_email != new_email:

                user.is_active = False
                user.email = form.cleaned_data.get('email')

                current_site = get_current_site(request)
                subject = 'Confirm changed email for your STB account.'
                message = render_to_string('acc_update_email.html', {
                    'user': user, 'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': tokens.account_activation_token.make_token(user),
                })
                send_mail(subject, message, 'stb@shawcando.com', [user.email],
                          html_message=message, fail_silently=True)

                display_message = ('Please click on the confirmation link '
                                   'emailed to confirm your changed email address.')

            # Save user changes, if any.
            user.save()
            messages.success(request, display_message)

            # Handle file upload
            if len(request.FILES) != 0:
                # preprocess uploaded image
                new_image = str(request.user.profile.avatar.file)
                im = Image.open(new_image)
                width, height = im.size
                print("{}, {}".format(width, height))
                # Resize to manageable
                if width > height:
                        im.thumbnail((600, 400), Image.ANTIALIAS)
                else:
                        im.thumbnail((400, 600), Image.ANTIALIAS)

                im.save(new_image)

                # Redirect to cropping
                return HttpResponseRedirect(reverse('profile:profile_crop'))
            return HttpResponseRedirect(reverse('profile:my_profile'))
    return render(request, 'profile/profile_edit.html',
                  {'form': form,
                   'current_user': user,
                   'skills': skills, })


@login_required
def profile_crop(request):
    form = forms.CropForm()
    user = request.user
    profile = request.user.profile
    if request.method == 'POST':
        form = forms.CropForm(data=request.POST)
        if form.is_valid():
            original_image = str(profile.avatar.file)
            crop_coords = {
                'scale': float(form.cleaned_data['scale']),
                'angle': 0 - float(form.cleaned_data['angle']),
                'x': float(form.cleaned_data['x']),
                'y': float(form.cleaned_data['y']),
                'w': float(form.cleaned_data['w']),
                'h': float(form.cleaned_data['h'])
            }
            cropper(original_image, crop_coords)
            return HttpResponseRedirect(reverse('profile:profile'))

    return render(request, 'profile/profile_crop.html',
                  {'user': user, 'profile': profile, 'form': form})


def cropper(original_image_path, crop_coords):
    """ Open original, create and save a new cropped image"""
    editable = Image.open(original_image_path)

    # rotate first
    if crop_coords['angle'] != 0:
        editable = editable.rotate(crop_coords['angle'], expand=True)

    # cropping area
    box = (int(crop_coords['x']/crop_coords['scale']),
           int(crop_coords['y']/crop_coords['scale']),
           int((crop_coords['x'] + crop_coords['w'])/crop_coords['scale']),
           int((crop_coords['y'] + crop_coords['h'])/crop_coords['scale']))
    editable = editable.crop(box)

    # Resize
    width, height = editable.size
    height = int((240 / width) * height)
    editable = editable.resize((240, height), Image.ANTIALIAS)

    # save over original_image_path
    editable.save(original_image_path)


@login_required
def list_skills(request):
    """Filter the skills by user input"""
    no_user = request.GET.get('no_user', False)
    current_user = request.user
    if no_user is False:
        used = models.UserSkill.objects.filter(user=current_user).values('skill')
    else:
        used = ""
    matches = (models.Skill.objects.filter(
        title__icontains=request.GET.get('query', None))
        .exclude(id__in=used)
        .annotate(value=F('title'), data=F('id'))
        .values('value', 'data'))

    data = {
        "suggestions": list(matches)
    }
    return JsonResponse(data)


@login_required
def list_skills_add(request):
    """Add skill for user, create if does not exist"""
    current_user = request.user
    title = request.POST.get('title', None)

    if title is not None:
        obj, created = models.Skill.objects.get_or_create(title=title)

        try:
            models.UserSkill.objects.create(user=current_user, skill=obj)
        except IntegrityError:
            return JsonResponse(data={"result": "already created"})

        return JsonResponse(data={"result": "success"})
    return JsonResponse(data={"result": "failed"})


@login_required
def list_skills_remove(request):
    """Remove skill from user"""
    current_user = request.user
    title = request.POST.get('title', None)

    try:
        models.UserSkill.objects.get(user=current_user, skill__title=title).delete()
    except models.UserSkill.DoesNotExist:
        return JsonResponse(data={"result": "does not exist"})

    return JsonResponse(data={"result": "success"})


def activate(request, uidb64, token):
    """Email confirmation activate"""
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and tokens.account_activation_token.check_token(user,
                                                                        token):
        user.is_active = True
        user.save()
        login(request, user)

        messages.success(request,
                         ("Thank you for your email confirmation. Now you can "
                          "login your account and complete your profile."))
        return HttpResponseRedirect(reverse('profile:signin'))
    else:
        messages.error('Activation link is invalid!')
        return HttpResponseRedirect(reverse('profile:home'))
