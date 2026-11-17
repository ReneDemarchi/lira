from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy

from .forms import (
    AdicionarMembroForm, EtiquetaForm, ExcluirProjetoForm, ProjetoForm, TarefaForm, UsuarioCreationForm,
)
from .models import Etiqueta, Participacao, Tarefa
from .permissoes import exigir, pode_gerenciar_projeto, pode_gerenciar_tarefas


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


def projeto_detalhe(request, pk, form_membro=None):
    projeto, papel = exigir(request.user, pk)
    participacoes = projeto.participacoes.select_related('usuario').order_by('usuario__first_name')
    colunas = {valor: (nome, []) for valor, nome in Tarefa.Estado.choices}  # RN08: uma coluna por Estado
    for t in projeto.tarefas.select_related('responsavel').prefetch_related('etiquetas'):
        colunas[t.estado][1].append(t)
    return render(request, 'core/projeto.html', {
        'projeto': projeto, 'participacoes': participacoes,
        'pode_gerenciar': pode_gerenciar_projeto(papel),
        'pode_gerenciar_tarefas': pode_gerenciar_tarefas(papel),
        'colunas': [(valor, nome, tarefas) for valor, (nome, tarefas) in colunas.items()],
        'papeis': Participacao.Papel.choices,
        'form_membro': form_membro or AdicionarMembroForm(projeto),
    })


def projeto_editar(request, pk):
    projeto, _ = exigir(request.user, pk, pode_gerenciar_projeto)
    form = ProjetoForm(request.POST or None, instance=projeto)
    if form.is_valid():
        form.save()
        messages.success(request, 'Projeto atualizado.')
        return redirect('projeto', pk)
    return render(request, 'core/projeto_form.html', {'form': form, 'projeto': projeto})


def projeto_excluir(request, pk):
    projeto, _ = exigir(request.user, pk, pode_gerenciar_projeto)
    form = ExcluirProjetoForm(projeto, request.POST or None)
    if form.is_valid():
        projeto.delete()
        messages.success(request, f'Projeto "{projeto.nome}" excluído.')
        return redirect('home')
    return render(request, 'core/projeto_excluir.html', {'form': form, 'projeto': projeto})


@require_POST
def membro_adicionar(request, pk):
    projeto, _ = exigir(request.user, pk, pode_gerenciar_projeto)
    form = AdicionarMembroForm(projeto, request.POST)
    if not form.is_valid():
        return projeto_detalhe(request, pk, form_membro=form)
    form.save()
    messages.success(request, f'{form.usuario} adicionado ao projeto.')
    return redirect('projeto', pk)


@require_POST
def membro_papel(request, pk, participacao_pk):
    projeto, _ = exigir(request.user, pk, pode_gerenciar_projeto)
    participacao = get_object_or_404(projeto.participacoes, pk=participacao_pk)
    novo = request.POST.get('papel')
    if novo not in Participacao.Papel.values:
        messages.error(request, 'Papel inválido.')
    else:
        try:
            participacao.alterar_papel(novo)
            messages.success(request, f'{participacao.usuario} agora é {participacao.get_papel_display()}.')
        except ValidationError as e:
            messages.error(request, e.messages[0])
    return redirect('projeto', pk)


@require_POST
def membro_remover(request, pk, participacao_pk):
    projeto, _ = exigir(request.user, pk, pode_gerenciar_projeto)
    participacao = get_object_or_404(projeto.participacoes, pk=participacao_pk)
    try:
        participacao.remover()
    except ValidationError as e:
        messages.error(request, e.messages[0])
        return redirect('projeto', pk)
    messages.success(request, f'{participacao.usuario} removido do projeto.')
    if participacao.usuario == request.user:
        return redirect('home')  # saiu do próprio projeto: perdeu o acesso
    return redirect('projeto', pk)


def tarefa_form(request, pk, tarefa_pk=None):
    projeto, _ = exigir(request.user, pk, pode_gerenciar_tarefas)
    tarefa = get_object_or_404(projeto.tarefas, pk=tarefa_pk) if tarefa_pk else None
    form = TarefaForm(projeto, request.POST or None, instance=tarefa)
    if form.is_valid():
        tarefa = form.save()
        messages.success(request, 'Tarefa salva.')
        return redirect('tarefa', pk, tarefa.pk)
    return render(request, 'core/tarefa_form.html', {'projeto': projeto, 'tarefa': tarefa, 'form': form})


@require_POST
def tarefa_excluir(request, pk, tarefa_pk):
    projeto, _ = exigir(request.user, pk, pode_gerenciar_tarefas)
    get_object_or_404(projeto.tarefas, pk=tarefa_pk).delete()
    messages.success(request, 'Tarefa excluída.')
    return redirect('projeto', pk)


def etiquetas(request, pk):
    projeto, _ = exigir(request.user, pk, pode_gerenciar_tarefas)
    form = EtiquetaForm(projeto)
    if request.method == 'POST':
        id_ = request.POST.get('id', '')
        if id_ and not id_.isdigit():
            return HttpResponseBadRequest('Etiqueta inválida.')
        etiqueta = get_object_or_404(projeto.etiquetas, pk=id_) if id_ else None
        if request.POST.get('acao') == 'excluir' and etiqueta:
            etiqueta.delete()
            messages.success(request, f'Etiqueta "{etiqueta}" excluída.')
            return redirect('etiquetas', pk)
        form = EtiquetaForm(projeto, request.POST, instance=etiqueta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Etiqueta salva.')
            return redirect('etiquetas', pk)
        if etiqueta:  # erro ao renomear: mostra como mensagem, o form de cima é o de criar
            messages.error(request, form.errors['nome'][0])
            return redirect('etiquetas', pk)
    return render(request, 'core/etiquetas.html', {
        'projeto': projeto, 'form': form, 'etiquetas': projeto.etiquetas.order_by('nome'),
    })


def tarefa_detalhe(request, pk, tarefa_pk):
    projeto, papel = exigir(request.user, pk)
    tarefa = get_object_or_404(projeto.tarefas, pk=tarefa_pk)
    return render(request, 'core/tarefa.html', {
        'projeto': projeto, 'tarefa': tarefa, 'pode_gerenciar_tarefas': pode_gerenciar_tarefas(papel),
    })
