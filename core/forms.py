from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Etiqueta, Participacao, Projeto, Tarefa, Usuario


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


class ExcluirProjetoForm(forms.Form):
    confirmacao = forms.CharField(label='Digite o nome do projeto para confirmar')

    def __init__(self, projeto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.projeto = projeto

    def clean_confirmacao(self):
        if self.cleaned_data['confirmacao'] != self.projeto.nome:
            raise forms.ValidationError('O nome não confere.')
        return self.cleaned_data['confirmacao']


class AdicionarMembroForm(forms.Form):
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'placeholder': 'e-mail do usuário'}))
    papel = forms.ChoiceField(choices=Participacao.Papel.choices, initial=Participacao.Papel.COLAB)

    def __init__(self, projeto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.projeto = projeto

    def clean_email(self):
        email = self.cleaned_data['email']
        self.usuario = Usuario.objects.filter(email__iexact=email).first()
        if self.usuario is None:
            raise forms.ValidationError('Nenhum usuário cadastrado com este e-mail.')
        if self.projeto.participacoes.filter(usuario=self.usuario).exists():
            raise forms.ValidationError('Este usuário já é membro do projeto.')
        return email

    def save(self):
        return self.projeto.participacoes.create(usuario=self.usuario, papel=self.cleaned_data['papel'])


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


class EtiquetaForm(forms.ModelForm):
    class Meta:
        model = Etiqueta
        fields = ['nome']

    def __init__(self, projeto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.projeto = projeto

    def clean_nome(self):
        # A constraint do banco não é checada pelo form (projeto não é campo dele), então checamos aqui.
        nome = self.cleaned_data['nome'].strip()
        mesmas = self.instance.projeto.etiquetas.filter(nome__iexact=nome).exclude(pk=self.instance.pk)
        if mesmas.exists():
            raise forms.ValidationError('Já existe uma etiqueta com este nome no projeto.')
        return nome
