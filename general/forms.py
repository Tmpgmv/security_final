from django import forms


class ModelInputForm(forms.Form):
    model_name = forms.CharField(label="Наименование модели", max_length=100)
