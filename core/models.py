from django.db import models
from django.conf import settings
from django.utils import timezone


# equpe
class Equipe(models.Model):
    nome = models.CharField('Nome', max_length = 100, unique = True)

    class Meta:
        verbose_name = 'Equipe'
        verbose_name_plural = 'Equipes'
        ordering = ['nome']

    def __str__(self):
        return self.nome

# categoria
class Categoria(models.Model):
    nome = models.CharField('Nome', max_length = 100, unique = True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome

# prioridade
class Prioridade(models.Model):
    nome = models.CharField('Nome', max_length = 50, unique = True)

    ordem = models.PositiveSmallIntegerField(
        'Ordem',
        default=0,
        help_text='Usada para organizar a orden de prioridade.',
    )

    class Meta:
        verbose_name = 'Prioridade'
        verbose_name_plural = 'Prioridades'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome

# sla
class SLA(models.Model):
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, related_name='slas', verbose_name='Categoria',
    )
    prioridade = models.ForeignKey(
        Prioridade, on_delete=models.CASCADE, related_name='slas', verbose_name='Prioridade',
    )
    horas = models.PositiveIntegerField(
        'Horas para atendimento', help_text='Prazo limite de resolução.',
    )

    class Meta:
        verbose_name = 'SLA'
        verbose_name_plural = 'SLAs'
        unique_together = ('categoria', 'prioridade')
        ordering = ['categoria', 'prioridade']

    def __str__(self):
        return f'{self.categoria} / {self.prioridade} — {self.horas}h'

# chamado
class Chamado(models.Model):
    STATUS_ABERTO = 'ABERTO'
    STATUS_ANDAMENTO = 'ANDAMENTO'
    STATUS_FECHADO = 'FECHADO'
    STATUS_CHOICES = [
        (STATUS_ABERTO, 'Aberto'),
        (STATUS_ANDAMENTO, 'Em Atendimento'),
        (STATUS_FECHADO, 'Concluído'),
    ]

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

    class Meta:
        verbose_name = 'Chamado'
        verbose_name_plural = 'Chamados'
        ordering = ['-data_criacao']

    def __str__(self):
        return f'#{self.pk} - {self.titulo}'

    #metodos
    def calcular_data_limite(self):

        base = self.data_criacao or timezone.now()
        sla = SLA.objects.filter(categoria=self.categoria, prioridade=self.prioridade).first()

        if not sla:
            return None
        return base + timezone.timedelta(hours=sla.horas)

    def save(self, *args, **kwargs):
        eh_novo = self._state.adding

        super().save(*args, **kwargs)

        atualizar_campos = []

        if eh_novo or self.data_limite is None:
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

        if user.is_staff:
            return True
        return user in (self.solicitante, self.responsavel)