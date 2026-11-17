from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('entrar/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('sair/', auth_views.LogoutView.as_view(), name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('senha/', views.TrocarSenha.as_view(), name='trocar_senha'),
    path('projetos/novo/', views.projeto_novo, name='projeto_novo'),
    path('projetos/<int:pk>/', views.projeto_detalhe, name='projeto'),
    path('projetos/<int:pk>/editar/', views.projeto_editar, name='projeto_editar'),
    path('projetos/<int:pk>/excluir/', views.projeto_excluir, name='projeto_excluir'),
    path('projetos/<int:pk>/membros/', views.membro_adicionar, name='membro_adicionar'),
    path('projetos/<int:pk>/membros/<int:participacao_pk>/papel/', views.membro_papel, name='membro_papel'),
    path('projetos/<int:pk>/membros/<int:participacao_pk>/remover/', views.membro_remover, name='membro_remover'),
    path('projetos/<int:pk>/etiquetas/', views.etiquetas, name='etiquetas'),
    path('projetos/<int:pk>/tarefas/nova/', views.tarefa_form, name='tarefa_nova'),
    path('projetos/<int:pk>/tarefas/<int:tarefa_pk>/', views.tarefa_detalhe, name='tarefa'),
    path('projetos/<int:pk>/tarefas/<int:tarefa_pk>/editar/', views.tarefa_form, name='tarefa_editar'),
    path('projetos/<int:pk>/tarefas/<int:tarefa_pk>/excluir/', views.tarefa_excluir, name='tarefa_excluir'),
]
