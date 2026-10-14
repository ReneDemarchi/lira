from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import UsuarioChangeForm, UsuarioCreationForm
from .models import Comentario, Etiqueta, Participacao, Projeto, Tarefa, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm
    ordering = ['email']
    list_display = ['email', 'first_name', 'last_name', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    fieldsets = [
        (None, {'fields': ['email', 'password']}),
        ('Dados pessoais', {'fields': ['first_name', 'last_name']}),
        ('Acesso', {'fields': ['is_active', 'is_staff', 'is_superuser']}),
    ]
    add_fieldsets = [(None, {'fields': ['first_name', 'email', 'password1', 'password2']})]


class ParticipacaoInline(admin.TabularInline):
    model = Participacao
    extra = 0
    autocomplete_fields = ['usuario']


class EtiquetaInline(admin.TabularInline):
    model = Etiqueta
    extra = 0


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    search_fields = ['nome']
    inlines = [ParticipacaoInline, EtiquetaInline]


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'projeto', 'estado', 'prioridade', 'responsavel', 'data_limite']
    list_filter = ['projeto', 'estado', 'prioridade']
    search_fields = ['titulo']
    autocomplete_fields = ['responsavel']
    filter_horizontal = ['etiquetas']
    inlines = [ComentarioInline]
