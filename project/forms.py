from django import forms


from . import models


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = [
            'title',
            'description',
            'timeline',
            'requirements',
        ]


class ProjectPositionForm(forms.ModelForm):
    class Meta:
        model = models.ProjectPosition
        fields = [
            'title',
            'description',
            'timeline',
        ]


PositionFormSet = forms.modelformset_factory(
    models.ProjectPosition,
    form=ProjectPositionForm,
    extra=1,
)

PositionInlineFormSet = forms.inlineformset_factory(
    models.Project,
    models.ProjectPosition,
    extra=1,
    fields=('title', 'description', 'timeline',),
    formset=PositionFormSet,
    min_num=0,
)
