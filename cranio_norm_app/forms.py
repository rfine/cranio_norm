
from django import forms
from django.core.validators import FileExtensionValidator


class HomeForm(forms.Form):
    # By default these values will be required
    phi = forms.FloatField(label='Phi Value')
    theta = forms.FloatField(label='Theta Value')
    phi_sig = forms.IntegerField(label='Phi Significant Figure')
    theta_sig = forms.IntegerField(label='Theta Significant Figure')
    files = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'multiple': True}), validators=[FileExtensionValidator(['ply', 'stl'])])
