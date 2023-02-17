
from django import forms
from django.core.validators import FileExtensionValidator


class HomeForm(forms.Form):
    # By default these values will be required 
    phi = forms.FloatField(label='Phi Value')
    theta = forms.FloatField(label='Theta Value')
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), validators=[FileExtensionValidator( ['ply'] ) ] )  




