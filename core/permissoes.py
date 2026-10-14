"""Único lugar que decide quem pode o quê. Todo poder vem do Papel na Participação (ver ADR 0001)."""
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404

from .models import Participacao, Projeto

Papel = Participacao.Papel


def papel(usuario, projeto):
    """Papel do usuário no projeto, ou None se não participa."""
    return (
        Participacao.objects.filter(usuario=usuario, projeto=projeto)
        .values_list('papel', flat=True)
        .first()
    )


def exigir(usuario, projeto_pk, regra=None):
    """Projeto e Papel do usuário. Não-membro recebe 404 (nem sabe que existe); membro sem permissão, 403."""
    projeto = get_object_or_404(Projeto, pk=projeto_pk)
    p = papel(usuario, projeto)
    if p is None:
        raise Http404
    if regra and not regra(p):
        raise PermissionDenied
    return projeto, p


def pode_gerenciar_tarefas(p):
    """RN04 e RF08: criar, editar, excluir e atribuir Tarefas; criar e editar Etiquetas."""
    return p in (Papel.ADMIN, Papel.COORD)
