from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import F
from django.utils import timezone


class UsuarioManager(UserManager):
    # Sem username: o login é por e-mail.
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('E-mail é obrigatório')
        user = self.model(email=self.normalize_email(email).lower(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email__iexact=email)


class Usuario(AbstractUser):
    username = None
    email = models.EmailField('e-mail', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    def __str__(self):
        return self.get_full_name() or self.email

    def clean(self):
        super().clean()
        self.email = self.email.lower()


class Projeto(models.Model):
    nome = models.CharField(max_length=120)
    descricao = models.TextField('descrição', blank=True)
    membros = models.ManyToManyField(Usuario, through='Participacao', related_name='projetos')

    def __str__(self):
        return self.nome


class Participacao(models.Model):
    class Papel(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        COORD = 'COORD', 'Coordenador'
        COLAB = 'COLAB', 'Colaborador'

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='participacoes')
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='participacoes')
    papel = models.CharField(max_length=5, choices=Papel.choices, default=Papel.COLAB)

    class Meta:
        verbose_name = 'participação'
        verbose_name_plural = 'participações'
        constraints = [models.UniqueConstraint(fields=['usuario', 'projeto'], name='participacao_unica')]

    def __str__(self):
        return f'{self.usuario} em {self.projeto} ({self.get_papel_display()})'

    def _travar_e_validar(self, novo_papel):
        # Trava o Projeto para que duas mudanças simultâneas não deixem o Projeto sem Administrador.
        Projeto.objects.select_for_update().get(pk=self.projeto_id)
        self.refresh_from_db()
        outros_admins = self.projeto.participacoes.filter(papel=self.Papel.ADMIN).exclude(pk=self.pk)
        if self.papel == self.Papel.ADMIN and novo_papel != self.Papel.ADMIN and not outros_admins.exists():
            raise ValidationError('O projeto precisa ter ao menos um Administrador.')

    def alterar_papel(self, novo_papel):
        self._travar_e_validar(novo_papel)
        self.papel = novo_papel
        self.save(update_fields=['papel'])

    def remover(self):
        """Tira o Usuário do Projeto; suas Tarefas ficam sem Responsável e seus Comentários permanecem."""
        self._travar_e_validar(None)
        Tarefa.objects.filter(projeto_id=self.projeto_id, responsavel_id=self.usuario_id).update(responsavel=None)
        self.delete()


class Etiqueta(models.Model):
    PADRAO = ['Epic', 'História', 'Bug', 'Issue']

    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='etiquetas')
    nome = models.CharField(max_length=40)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['projeto', 'nome'], name='etiqueta_unica_no_projeto')]

    def __str__(self):
        return self.nome


class Tarefa(models.Model):
    class Prioridade(models.IntegerChoices):
        BAIXA = 1, 'Baixa'
        MEDIA = 2, 'Média'
        ALTA = 3, 'Alta'
        URGENTE = 4, 'Urgente'

    class Estado(models.TextChoices):
        A_FAZER = 'A_FAZER', 'A fazer'
        FAZENDO = 'FAZENDO', 'Fazendo'
        FEITO = 'FEITO', 'Feito'

    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='tarefas')
    titulo = models.CharField('título', max_length=200)
    descricao = models.TextField('descrição', blank=True)
    prioridade = models.PositiveSmallIntegerField(choices=Prioridade.choices, default=Prioridade.MEDIA)
    estado = models.CharField(max_length=7, choices=Estado.choices, default=Estado.A_FAZER)
    responsavel = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tarefas', verbose_name='responsável',
    )
    data_limite = models.DateField(null=True, blank=True)
    etiquetas = models.ManyToManyField(Etiqueta, blank=True, related_name='tarefas')
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-prioridade', F('data_limite').asc(nulls_last=True), 'id']

    def __str__(self):
        return self.titulo

    @property
    def atrasada(self):
        return (
            self.data_limite is not None
            and self.data_limite < timezone.localdate()
            and self.estado != self.Estado.FEITO
        )

    def clean(self):
        # RN02: só membros do Projeto podem ser Responsáveis.
        if self.responsavel_id and not Participacao.objects.filter(
            usuario_id=self.responsavel_id, projeto_id=self.projeto_id
        ).exists():
            raise ValidationError({'responsavel': 'O responsável precisa ser membro do projeto.'})


class Comentario(models.Model):
    tarefa = models.ForeignKey(Tarefa, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='comentarios')
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'comentário'
        ordering = ['criado_em']

    def __str__(self):
        return f'{self.autor} em {self.tarefa}'
