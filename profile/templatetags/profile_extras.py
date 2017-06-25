from django import template

from project import models

register = template.Library()


@register.filter
def available_positions(project):
    """Return available positions for project"""

    # Get all taken positions
    taken = (models.ProjectPositionApplication.objects
             .filter(status='S').values('position'))

    # Get all available positions
    positions = (models.ProjectPosition.objects.filter(project=project)
                 .exclude(id__in=taken))

    # Create the output
    output = ""
    for position in positions:
        output += position.title + ","

    return output[:-1]


@register.filter
def login_error(error_list):
    """Customise the errors when logging in"""
    for error in error_list:
        if error == ('Please enter a correct username and password. Note that '
                     'both fields may be case-sensitive.'):
            return('Please enter a correct email or username and password '
                   'combination. Note that both fields are be case-sensitive.')
        if error == 'This account is inactive.':
            return('That account is inactive. To activate, please click on '
                   'the link in the email confirmation sent to you.')
        return error
