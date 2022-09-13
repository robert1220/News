from django import forms
from django.forms.widgets import HiddenInput
from news.models import Category


class CommentForm(forms.Form):
    comment = forms.CharField(label='Treść', min_length=3,max_length=5000, widget=forms.Textarea(attrs={'class':'form-control', 'title': 'Napisz coś', 'placeholder':'Napisz tu coś' }))
    article_id = forms.IntegerField(required=True, widget=HiddenInput(attrs={'type': 'hidden'}))


class UpdateCommentForm(forms.Form):
    comment = forms.CharField(label='Treść', min_length=3,max_length=5000, widget=forms.Textarea(attrs={'class':'form-control', 'title': 'Napisz coś', 'placeholder':'Napisz tu coś' }))
    comment_id = forms.IntegerField(required=True, widget=HiddenInput(attrs={'type': 'hidden'}))


class DeleteItemForm(forms.Form):
    item_id = forms.IntegerField(required=True, min_value=1, widget=HiddenInput(attrs={'type': 'hidden'}))


class ArticleDataTextForm(forms.Form):
    name = forms.CharField(label='Tytuł', min_length=3, max_length=120, widget=forms.TextInput(attrs={'class':'form-control','title': 'Imię', 'placeholder':'Imię' }))
    article = forms.CharField(label="Treść", min_length=3, max_length=25000, widget=forms.Textarea(attrs={'class':'form-control', 'title': 'Napisz coś', 'placeholder':'Tutaj napisz treść swojego Artykułu' }))
    choice_category = forms.ModelChoiceField(label='Wybierz kategorię:', queryset=Category.objects.all().order_by('name'))


class ArticleImageForm(forms.Form):
    img = forms.ImageField(label='Twój obrazek', required=True)


class LogInForm(forms.Form):
    user = forms.CharField(label='Login', max_length=60, widget=forms.TextInput(attrs={'class':'form-control','title': 'login', 'placeholder':'login' }))
    password = forms.CharField(label='Hasło', max_length=60, widget=forms.TextInput(attrs={'class': 'form-control','type':'password', 'title': 'password', 'placeholder': 'password'}))


class DataUserForm(forms.Form):
    first_name = forms.CharField(label='Imię',min_length=3, max_length=25, required=False, widget=forms.TextInput(attrs={'class':'form-control','title': 'first_name', 'placeholder':'Imię' }))
    last_name = forms.CharField(label='Nazwisko',min_length=3, max_length=25, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'title': 'last_name', 'placeholder': 'Nazwisko'}))
    email = forms.EmailField(label='e-mail', min_length=3, max_length=40, required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'title': 'e-mail', 'placeholder': 'email'}))