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

class EquipeForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Equipe
        fields = ["nome"]

class CategoriaForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome"]

class PrioridadeForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Prioridade
        fields = ["nome"]

class SLAForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SLA
        fields = ["categoria", "prioridade", "horas"]
    
    def clean_horas(self):
        horas = self.cleaned_data.get('horas')
        if horas is not None and horas < 1:
            raise forms.ValidationError(
                'O SLA precisa ter pelo menos 1 hora. Com 0 hora, o prazo '
                'seria igual à data de abertura do chamado.'
            )
        return horas

class ChamadoForm(_BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Chamado
        fields = [
            'titulo', 'descricao', 'equipe', 'categoria', 'prioridade',
            'responsavel', 'status', 'tipo',
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
        }

class CadastroUsuarioForm(_BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(required=False, label="Email")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class LoginForm(_BootstrapFormMixin, AuthenticationForm):
    pass