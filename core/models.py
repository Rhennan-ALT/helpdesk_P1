from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Organizacao(models.Model):
    nome = models.CharField('Nome', max_length=120)
    criada_em = models.DateTimeField('Criada em', auto_now_add=True)

    class Meta:
        verbose_name = 'Organização'
        verbose_name_plural = 'Organizações'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Perfil(models.Model):
    PAPEL_ADMIN = 'admin'
    PAPEL_OPERADOR = 'operador'
    PAPEIS = [
        (PAPEL_ADMIN, 'Administrador'),
        (PAPEL_OPERADOR, 'Operador'),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuário',
    )
    organizacao = models.ForeignKey(
        Organizacao, on_delete=models.PROTECT, related_name='perfis', verbose_name='Organização',
    )
    papel = models.CharField('Papel', max_length=20, choices=PAPEIS, default=PAPEL_OPERADOR)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'{self.usuario} ({self.organizacao} - {self.get_papel_display()})'

    @property
    def eh_admin(self):
        return self.papel == self.PAPEL_ADMIN


class DaOrganizacao(models.Model):
    organizacao = models.ForeignKey(
        Organizacao, on_delete=models.PROTECT, verbose_name='Organização',
    )

    class Meta:
        abstract = True


# equpe
class Equipe(DaOrganizacao):
    nome = models.CharField('Nome', max_length=100)

    class Meta:
        verbose_name = 'Equipe'
        verbose_name_plural = 'Equipes'
        constraints = [
            models.UniqueConstraint(fields=['organizacao', 'nome'], name='equipe_nome_unico_por_org'),
        ]
        ordering = ['nome']

    def __str__(self):
        return self.nome

# categoria
class Categoria(DaOrganizacao):
    nome = models.CharField('Nome', max_length=100)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        constraints = [
            models.UniqueConstraint(fields=['organizacao', 'nome'], name='categoria_nome_unico_por_org'),
        ]
        ordering = ['nome']

    def __str__(self):
        return self.nome

# prioridade
class Prioridade(DaOrganizacao):
    nome = models.CharField('Nome', max_length=50)

    ordem = models.PositiveSmallIntegerField(
        'Ordem',
        default=0,
        help_text='Usada para organizar a orden de prioridade.',
    )

    class Meta:
        verbose_name = 'Prioridade'
        verbose_name_plural = 'Prioridades'
        constraints = [
            models.UniqueConstraint(fields=['organizacao', 'nome'], name='prioridade_nome_unico_por_org'),
        ]
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome

# sla
class SLA(DaOrganizacao):
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, related_name='slas', verbose_name='Categoria',
    )
    prioridade = models.ForeignKey(
        Prioridade, on_delete=models.CASCADE, related_name='slas', verbose_name='Prioridade',
    )
    horas = models.PositiveIntegerField(
        'Horas para atendimento', help_text='Prazo limite de resolução.',
        validators=[MinValueValidator(
            1,
            message='O SLA precisa ter pelo menos 1 hora. Com 0 hora, o prazo '
                    'seria igual à data de abertura do chamado.',
        )],
    )

    class Meta:
        verbose_name = 'SLA'
        verbose_name_plural = 'SLAs'
        unique_together = ('categoria', 'prioridade')
        ordering = ['categoria', 'prioridade']

    def __str__(self):
        return f'{self.categoria} / {self.prioridade} — {self.horas}h'

class ChamadoQuerySet(models.QuerySet):

    def em_aberto(self):
        return self.exclude(status=Chamado.STATUS_FECHADO)

    def atrasados(self):
        return self.em_aberto().filter(data_limite__lt=timezone.now())


# chamado
class Chamado(DaOrganizacao):
    STATUS_ABERTO = 'ABERTO'
    STATUS_ANDAMENTO = 'ANDAMENTO'
    STATUS_FECHADO = 'FECHADO'
    STATUS_CHOICES = [
        (STATUS_ABERTO, 'Aberto'),
        (STATUS_ANDAMENTO, 'Em Atendimento'),
        (STATUS_FECHADO, 'Concluído'),
    ]
    
    TIPO_INCIDENTE = 'INCIDENTE'
    TIPO_REQUISICAO = 'REQUISICAO'
    TIPO_DUVIDA = 'DUVIDA'
    TIPO_CHOICES = [
        (TIPO_INCIDENTE, 'Incidente'),
        (TIPO_REQUISICAO, 'Requisição'),
        (TIPO_DUVIDA, 'Dúvida'),
    ]

    tipo = models.CharField(
        'Tipo', max_length=12, choices=TIPO_CHOICES, default=TIPO_INCIDENTE,
    )

    titulo = models.CharField('Título', max_length = 200)
    descricao = models.TextField('Descrição')

    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='chamados_abertos', verbose_name='Solicitante',
    )
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='chamados_responsavel', verbose_name='Responsável',
    )
    equipe = models.ForeignKey(
        Equipe, on_delete=models.PROTECT, related_name='chamados', verbose_name='Equipe',
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name='chamados', verbose_name='Categoria',
    )
    prioridade = models.ForeignKey(
        Prioridade, on_delete=models.PROTECT, related_name='chamados', verbose_name='Prioridade',
    )
    status = models.CharField(
        'Status', max_length=10, choices=STATUS_CHOICES, default=STATUS_ABERTO,
    )

    data_criacao = models.DateTimeField('Criado em', auto_now_add=True)
    data_limite = models.DateTimeField(
        'Prazo limite (SLA)', null=True, blank=True, editable=False,
    )
    data_fechamento = models.DateTimeField('Fechado em', null=True, blank=True, editable=False)

    objects = ChamadoQuerySet.as_manager()

    class Meta:
        verbose_name = 'Chamado'
        verbose_name_plural = 'Chamados'
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['organizacao', 'data_criacao'], name='chamado_org_criacao_idx'),
        ]

    def __str__(self):
        return f'#{self.pk} - {self.titulo}'

    #metodos
    def calcular_data_limite(self):

        base = self.data_criacao or timezone.now()
        sla = SLA.objects.filter(categoria=self.categoria, prioridade=self.prioridade).first()

        if not sla:
            return None
        return base + timezone.timedelta(hours=sla.horas)

    def _sla_mudou(self):
        anterior = (
            Chamado.objects.filter(pk=self.pk)
            .values('categoria_id', 'prioridade_id')
            .first()
        )
        if anterior is None:
            return True
        return (
            anterior['categoria_id'] != self.categoria_id
            or anterior['prioridade_id'] != self.prioridade_id
        )

    def save(self, *args, **kwargs):
        eh_novo = self._state.adding
        sla_mudou = not eh_novo and self._sla_mudou()

        super().save(*args, **kwargs)

        atualizar_campos = []

        if eh_novo or sla_mudou or self.data_limite is None:
            data_limite_calculada = self.calcular_data_limite()
            if data_limite_calculada != self.data_limite:
                self.data_limite = data_limite_calculada
                atualizar_campos.append('data_limite')

        if self.status == self.STATUS_FECHADO and self.data_fechamento is None:
            self.data_fechamento = timezone.now()
            atualizar_campos.append('data_fechamento')

        elif self.status != self.STATUS_FECHADO and self.data_fechamento is not None:
            self.data_fechamento = None
            atualizar_campos.append('data_fechamento')

        if atualizar_campos:
            super().save(update_fields=atualizar_campos)

    @property
    def esta_atrasado(self):

        if self.status == self.STATUS_FECHADO:
            return False
        if not self.data_limite:
            return False
        return timezone.now() > self.data_limite

    def usuario_pode_gerenciar(self, user):
        perfil = getattr(user, 'perfil', None)
        if perfil is not None and perfil.eh_admin:
            return True
        return user in (self.solicitante, self.responsavel)