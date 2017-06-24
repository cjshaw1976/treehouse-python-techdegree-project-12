from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string

import json

from . import forms
from . import models
from profile.models import Skill, UserSkill


def project(request, pk):
    user = request.user
    project = get_object_or_404(models.Project, pk=pk)
    positions = models.ProjectPosition.objects.filter(project=pk)
    applications = (models.ProjectPositionApplication.objects
                    .filter(position__in=positions))

    return render(request, 'project/project.html', {
                  'project': project,
                  'current_user': user,
                  'positions': positions,
                  'applications': applications })

@login_required
def project_recommended(request):
    """Reccomendations for users based on skill set"""
    user = request.user

    # Any get requests
    show_project = None
    limit_projects = models.Project.objects.exclude(user=user)
    if request.GET.get('project'):
        show_project = request.GET.get('project')
        limit_projects = (models.Project.objects
                          .filter(title__iexact=show_project))

    show_skill = None
    user_skills = UserSkill.objects.filter(user=user).values('skill_id')
    if request.GET.get('skill'):
        show_skill = request.GET.get('skill')
        user_skills = Skill.objects.filter(title__iexact=show_skill)

    # Get the project postions that match the user skills but exculd any that
    # are already selected or have been applied by the user
    positions = (models.ProjectPosition.objects.filter(
                 project__id__in=limit_projects,
                 projectpositionskill__skill__id__in=user_skills)
                 .exclude(projectpositionapplication__status='S')
                 .exclude(projectpositionapplication__user=user).distinct())
    print(positions)
    # Get a listof the projects
    projects = (models.Project.objects
                .filter(projectposition__id__in=positions)
                .annotate(Count('title')))

    # Get a list of skills
    skills = (models.ProjectPositionSkill.objects
              .filter(position__id__in=positions, skill__id__in=user_skills)
              .values('skill__title').annotate(Count('skill_id')))

    return render(request, 'project/recommended.html',
                  { 'projects': projects, 'positions':positions,
                    'current_user': user, 'skills':skills,
                    'show_project': show_project, 'show_skill':show_skill })

@login_required
def project_applications(request):
    """Applications"""
    user = request.user

    show_projects = None
    my_projects = models.Project.objects.filter(user=user)
    if request.GET.get('project'):
        show_projects = request.GET.get('project')
        projects = models.Project.objects.filter(user=user,
                                                 title__iexact=show_projects)
    else:
        projects = my_projects

    show_position = None
    if request.GET.get('position'):
        show_position = request.GET.get('position')
        positions = (models.ProjectPosition.objects
                     .filter(project__in=my_projects,
                             title__iexact=show_position))
    else:
        positions = (models.ProjectPosition.objects
                     .filter(project__in=my_projects))

    show_applications = None
    if request.GET.get('application'):
        show_applications = request.GET.get('application')
        applications = (models.ProjectPositionApplication.objects
                        .filter(position__in=positions,
                                status=show_applications[0].upper()))
    else:
        applications = (models.ProjectPositionApplication.objects
                        .filter(position__in=positions))

    my_positions = (models.ProjectPosition.objects
                    .filter(project__in=my_projects).values('title')
                    .order_by().annotate(Count('title')))

    return render(request, 'project/applications.html', {
                  'current_user': user,
                  'projects': my_projects,
                  'show_projects': show_projects,
                  'positions': my_positions,
                  'show_position': show_position,
                  'applications': applications,
                  'show_applications': show_applications})

@login_required
def project_apply(request):
    """ajax appy for position"""
    user = request.user

    # Check position belongs to project
    project = get_object_or_404(models.Project,
                                pk=request.POST.get('project', None))
    position = (models.ProjectPosition.objects
                .get(project=project, pk=request.POST.get('position', None)))

    if position != None:
        obj, created = (models.ProjectPositionApplication.objects
                        .get_or_create(position=position,
                                       user=user, status='A'))
        if created:
            # Send email to owner to inform of application
            current_site = get_current_site(request)
            subject = "[STB Notification] Application recieved for your project position: {}.".format(position)
            message = render_to_string('position_apply_email.html', {
                'owner':project.user, 'user':user,
                'profile': reverse('profile:profile', args=(user.id,)),
                'domain':current_site.domain,
                'page': reverse('project:project', args=(project.id,)),
                'position': position,
            })
            toemail = project.user.email
            send_mail(subject, message, 'stb@shawcando.com',
                      [toemail], html_message=message, fail_silently=True)

        return JsonResponse(data = { "result": "success" })
    return JsonResponse(data = { "result": "failed" })

@login_required
def position_select(request):
    """ajax select user for position"""
    user = request.user

    # check user is project owner and position belongs to project
    position = (models.ProjectPositionApplication.objects.filter(
                position__project__user=user.id,
                position__project_id=request.POST.get('project', None),
                pk=request.POST.get('position', None), status='A')
                .update(status = 'S'))

    if position > 0:
        # Send email
        selected = (models.ProjectPositionApplication.objects.get(
                    position__project__user=user.id,
                    position__project_id=request.POST.get('project', None),
                    pk=request.POST.get('position', None), status='S'))
        subject = "[STB Notification] Application selected for project position: {}.".format(selected.position)
        message = render_to_string('position_select_email.html', {
            'user':selected.user, 'position': selected.position,
        })
        toemail = selected.user.email
        send_mail(subject, message, 'stb@shawcando.com',
                  [toemail], html_message=message, fail_silently=True)

        # mark rest as rejected
        rejected = (models.ProjectPositionApplication.objects
                    .filter(position=selected.position, status='A'))

        for application in rejected:
            application.status='R'
            application.save()

            # Send email to user to inform of rejection
            subject = "[STB Notification] Application not selected for project position: {}.".format(application.position)
            message = render_to_string('position_reject_email.html', {
                'user':application.user, 'position': application.position,
            })
            toemail = application.user.email
            send_mail(subject, message, 'stb@shawcando.com',
                      [toemail], html_message=message, fail_silently=True)

        return JsonResponse(data = { "result": "success" })
    return JsonResponse(data = { "result": "failed" })

@login_required
def position_reject(request):
    """ajax reject user for position"""
    user = request.user

    # check user is project owner and position belongs to project
    position = (models.ProjectPositionApplication.objects.filter(
                position__project__user=user.id,
                position__project_id=request.POST.get('project', None),
                pk=request.POST.get('position', None), status='A')
                .update(status = 'R'))

    if position > 0:
        # Send email to user to inform of rejection
        application = (models.ProjectPositionApplication.objects
                       .get(pk=request.POST.get('position')))
        subject = "[STB Notification] Application not selected for project position: {}.".format(application.position)
        message = render_to_string('position_reject_email.html', {
            'user':application.user, 'position': application.position,
        })
        toemail = application.user.email
        send_mail(subject, message, 'stb@shawcando.com',
                  [toemail], html_message=message, fail_silently=True)

        return JsonResponse(data = { "result": "success" })
    return JsonResponse(data = { "result": "failed" })

@login_required
def project_delete(request):
    """ajax delete project"""
    user = request.user

    # Check project belongs to user
    project = get_object_or_404(models.Project,
                                pk=request.POST.get('project', None),
                                user=user)
    messages.success(request, "Delete project {}".format(project.title))
    project.delete()
    return JsonResponse(data = { "result": "success" })

@login_required
def project_editor(request, pk=None):
    user = request.user
    project  = models.Project.objects.filter(pk=pk).first()
    if project and project.user != user:
        messages.error(request, "You cannot edit '{}' as this project does not belong to you.".format(project.title))
        return redirect(reverse('profile:home'))

    form = forms.ProjectForm(instance=project)
    position_forms = forms.PositionInlineFormSet(
        queryset=models.ProjectPosition.objects.filter(project=pk)
    )

    if request.method == 'POST':
        form = forms.ProjectForm(data=request.POST, instance=project)
        position_forms = forms.PositionInlineFormSet(
            request.POST,
            queryset=models.ProjectPosition.objects.filter(project=pk)
        )

        if form.is_valid() and position_forms.is_valid():
            # Save form
            project = form.save(commit=False)
            project.user = user
            project.save()

            # Remember marked for delete
            position_forms.save(commit=False)
            marked_for_delete = position_forms.deleted_objects

            # Save position
            count = 0
            for position in position_forms:

                obj = position.save(commit=False)
                obj.project = project
                obj.save()

                models.ProjectPositionSkill.objects.filter(position=obj).delete()

                skills = request.POST.getlist('form-'+str(count)+'-skill[]')
                for title in skills:
                    skill, created = Skill.objects.get_or_create(title=title)
                    models.ProjectPositionSkill.objects.create(position=obj,
                                                               skill=skill)

                count = count + 1

            # Delete removed positions
            for position in marked_for_delete:
                position.delete()

            # Message & Redirect
            messages.success(request, "Saved project {}".format(project.title))
            return HttpResponseRedirect(reverse('project:project',
                                                args=(project.id,)))

    return render(request, 'project/project_new.html',
                  {'form': form, 'formset': position_forms})
