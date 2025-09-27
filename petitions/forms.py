from django import forms
from .models import Petition

class PetitionForm(forms.ModelForm):
    class Meta:
        model = Petition
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter movie title'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Tell us why this movie should be added to our catalog',
                'rows': 4
            }),
        }
        labels = {
            'title': 'Movie Title',
            'description': 'Your Reason',
        }
