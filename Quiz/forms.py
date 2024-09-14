from django import forms
from .models import Question, Choice
from django.forms import inlineformset_factory, modelformset_factory


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['ques_text', 'question_type', 'points', 'topic', 'feedback',]
        widgets = {
            'ques_text': forms.TextInput(attrs={'class': 'input-box', 'placeholder': 'Question name'}),
            'points': forms.NumberInput(attrs={'class': 'input-box'}),
            'question_type': forms.Select(attrs={'class': 'input-box'}),
            'topic': forms.Select(attrs={'class': 'input-box'}),
            'feedback': forms.TextInput(
                attrs={'placeholder': 'Write Feedback'}),
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'is_correct', 'choice_image']
        widgets = {
            'choice_text': forms.TextInput(attrs={'placeholder': 'Option name', 'class': 'choice_text formset-field'}),
            'choice_image': forms.FileInput(attrs={'class': 'formset-field'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'checkbox formset-field'}),
        }
