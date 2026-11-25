from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import SLA, Categoria, Chamado, Equipe, Prioridade

class _BootstrapFormMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            classe = 'form-select' if isinstance(field.widget, (forms.Select, forms.SelectMultiple)) else 'form-control'
            existente = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existente} {classe}'.strip()

class _OrgFormMixin:
    campos_da_org = ()

    def __init__(self, *args, org=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.org = org
        for nome in self.campos_da_org:
            self.fields[nome].queryset = self.fields[nome].queryset.filter(organizacao=org)

class _NomeUnicoPorOrgMixin:

    def clean_nome(self):
        nome = self.cleaned_data['nome']
        repetidos = self._meta.model.objects.filter(organizacao=self.org, nome=nome)
        if self.instance.pk:
            repetidos = repetidos.exclude(pk=self.instance.pk)
        if repetidos.exists():
            raise forms.ValidationError('Já existe um registro com este nome na sua organização.')
        return nome

class EquipeForm(_OrgFormMixin, _NomeUnicoPorOrgMixin, _BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Equipe
        fields = ["nome"]

class CategoriaForm(_OrgFormMixin, _NomeUnicoPorOrgMixin, _BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome"]

class PrioridadeForm(_OrgFormMixin, _NomeUnicoPorOrgMixin, _BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Prioridade
        fields = ["nome"]

class SLAForm(_OrgFormMixin, _BootstrapFormMixin, forms.ModelForm):
    campos_da_org = ('categoria', 'prioridade')

    class Meta:
        model = SLA
        fields = ["categoria", "prioridade", "horas"]

class ChamadoForm(_OrgFormMixin, _BootstrapFormMixin, forms.ModelForm):
    campos_da_org = ('equipe', 'categoria', 'prioridade')

    class Meta:
        model = Chamado
        fields = [
            'titulo', 'descricao', 'equipe', 'categoria', 'prioridade',
            'responsavel', 'status', 'tipo',
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['responsavel'].queryset = User.objects.filter(perfil__organizacao=self.org)

class CadastroUsuarioForm(_BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(required=False, label="Email")
    organizacao = forms.CharField(
        label="Nome da organização", max_length=120,
        help_text="Uma nova organização será criada para você.",
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class LoginForm(_BootstrapFormMixin, AuthenticationForm):
    pass

class PeriodoForm(_BootstrapFormMixin, forms.Form):
    inicio = forms.DateField(
        label='De', required=False, widget=forms.DateInput(attrs={'type': 'date'}),
    )
    fim = forms.DateField(
        label='Até', required=False, widget=forms.DateInput(attrs={'type': 'date'}),
    )

    def clean(self):
        dados = super().clean()
        inicio, fim = dados.get('inicio'), dados.get('fim')
        if inicio and fim and inicio > fim:
            raise forms.ValidationError('A data inicial não pode ser depois da data final.')
        return dados

