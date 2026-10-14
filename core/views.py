from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import ProjetoForm, TarefaForm, UsuarioCreationForm
from .models import Etiqueta, Participacao, Tarefa
from .permissoes import exigir, pode_gerenciar_tarefas


def home(request):
    participacoes = request.user.participacoes.select_related('projeto').order_by('projeto__nome')
    return render(request, 'core/home.html', {'participacoes': participacoes})


@login_not_required
def cadastro(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = UsuarioCreationForm(request.POST or None)
    if form.is_valid():
        login(request, form.save(), backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'Conta criada. Bem-vindo ao LIRA!')
        return redirect('home')
    return render(request, 'registration/cadastro.html', {'form': form})


class TrocarSenha(SuccessMessageMixin, PasswordChangeView):
    success_url = reverse_lazy('home')
    success_message = 'Senha alterada.'


def projeto_novo(request):
    form = ProjetoForm(request.POST or None)
    if form.is_valid():
        projeto = form.save()
        projeto.participacoes.create(usuario=request.user, papel=Participacao.Papel.ADMIN)
        Etiqueta.objects.bulk_create(Etiqueta(projeto=projeto, nome=n) for n in Etiqueta.PADRAO)
        messages.success(request, 'Projeto criado.')
        return redirect('projeto', projeto.pk)
    return render(request, 'core/projeto_form.html', {'form': form})


def projeto_detalhe(request, pk):
    projeto, papel = exigir(request.user, pk)
    participacoes = projeto.participacoes.select_related('usuario').order_by('usuario__first_name')
    colunas = {valor: (nome, []) for valor, nome in Tarefa.Estado.choices}  # RN08: uma coluna por Estado
    for t in projeto.tarefas.select_related('responsavel').prefetch_related('etiquetas'):
        colunas[t.estado][1].append(t)
    return render(request, 'core/projeto.html', {
        'projeto': projeto, 'participacoes': participacoes,
        'pode_gerenciar_tarefas': pode_gerenciar_tarefas(papel),
        'colunas': [(valor, nome, tarefas) for valor, (nome, tarefas) in colunas.items()],
    })


def tarefa_nova(request, pk):
    projeto, _ = exigir(request.user, pk, pode_gerenciar_tarefas)
    form = TarefaForm(projeto, request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Tarefa criada.')
        return redirect('projeto', pk)
    return render(request, 'core/tarefa_form.html', {'projeto': projeto, 'form': form})
