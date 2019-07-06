from django import forms
from tweets.models import Annotation


class TaggerForm(forms.ModelForm):
    class Meta:
        model = Annotation
        fields = ['target']
