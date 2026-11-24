import django.core.validators
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_chamado_tipo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sla",
            name="horas",
            field=models.PositiveIntegerField(
                help_text="Prazo limite de resolução.",
                validators=[
                    django.core.validators.MinValueValidator(
                        1,
                        message="O SLA precisa ter pelo menos 1 hora. Com 0 hora, o prazo seria igual à data de abertura do chamado.",
                    )
                ],
                verbose_name="Horas para atendimento",
            ),
        ),
    ]
