from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Projeto, Tarefa, Usuario


class UsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'email')
        labels = {'first_name': 'Nome'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True


class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = '__all__'


class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ['nome', 'descricao']
        widgets = {'descricao': forms.Textarea(attrs={'rows': 3})}


class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['titulo', 'descricao', 'estado', 'prioridade', 'responsavel', 'data_limite', 'etiquetas']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'data_limite': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'etiquetas': forms.CheckboxSelectMultiple,
        }

    def __init__(self, projeto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.projeto = projeto
        self.fields['responsavel'].queryset = projeto.membros.order_by('first_name')
        self.fields['etiquetas'].queryset = projeto.etiquetas.order_by('nome')
