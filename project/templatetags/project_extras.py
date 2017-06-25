from django import template

from project.models import ProjectPositionSkill

register = template.Library()


@register.filter
def skills_tags(position):
    """Return the skills for a position"""
    if not position:
        return ''
    skills = ProjectPositionSkill.objects.filter(position=position)
    skill_list = ""
    for skill in skills:
        skill_list += "<span>"+skill.skill.title+"</span>"
    return skill_list


@register.filter
def position_applied(set, user):
    """Test if a user has applied for a position"""
    if set.filter(user=user).count() > 0:
        return True
    return False


@register.filter
def position_taken(set):
    """ Test if a position has been selected"""
    for item in set:
        if item.status == 'S':
            return True
    return False


@register.assignment_tag
def get_successful(set):
    for item in set:
        if item.status == 'S':
            return item
    return False


@register.filter
def Applied(status):
    """Test if a status is Applied"""
    if status == 'A':
        return True
    return False


@register.filter
def Rejected(status):
    """Test if a status is Rejected"""
    if status == 'R':
        return True
    return False


@register.filter
def readable_status(status):
    """Human Readable status"""
    if status.upper() == 'R':
        return "Rejected"
    elif status.upper() == 'S':
        return "Selected"
    elif status.upper() == 'A':
        return "Applied"
    else:
        return "Unknown"


@register.filter
def status_buttons(status):
    """Human Readable status"""
    if status.upper() == 'R':
        return '<a class="button button-warning">Rejected</a>'
    elif status.upper() == 'S':
        return '<a class="button button-primary">Selected</a>'
    elif status.upper() == 'A':
        return '<a class="button button-success position_select">Select</a><a class="button button-warning position_reject">Reject</a>'
    else:
        return '<a class="button button-inactive">Unknown</a>'
