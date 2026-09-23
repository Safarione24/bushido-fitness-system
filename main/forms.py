from django import forms
from .models import Booking, Comment, Session


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['session']
        widgets = {
            'session': forms.Select(attrs={'class': 'form-select'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Оставьте комментарий...',
            }),
        }
        labels = {'text': ''}


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['title', 'trainer', 'zone', 'date', 'max_participants', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'trainer': forms.Select(attrs={'class': 'form-select'}),
            'zone': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }