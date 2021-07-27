from django import forms
from .models import *

# class SelectMajorForm(forms.Form):
#
#     def __init__(self,*args,**kwargs):
#         self.request = kwargs.pop('request', None)
#         super(SelectMajorForm, self).__init__(*args, **kwargs)
#         school_majors = SchoolMajor.objects.filter(userpath__user=self.request.user).distinct()
#         schools = forms.ChoiceField(choices=[(i, sm.name) for i, sm in enumerate(school_majors)])
#
#     # blah = forms.CharField(label='omg', max_length=100)
#     school_majors = ['I', 'have', 'no', 'clue']
#     # school_majors = [major.name for major in school_majors]
#     schools = forms.ChoiceField(choices=[(i, sm) for i, sm in enumerate(school_majors)])

class SelectMajorForm(forms.Form):

    def __init__(self,*args,**kwargs):
        self.request = kwargs.pop('request', None)
        super(SelectMajorForm, self).__init__(*args, **kwargs)

    school_majors = forms.ModelChoiceField(queryset = SchoolMajor.objects.all())

class AddUserPath(forms.ModelForm):
    class Meta:
        model = UserPath
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school_major'].queryset = SchoolMajor.objects.none()

        if 'school' in self.data:
            try:
                school_id = int(self.data.get('school'))
                self.fields['school_major'].queryset = SchoolMajor.objects.filter(school_id=school_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['school_major'].queryset = self.instance.school.school_major_set.order_by('name')
