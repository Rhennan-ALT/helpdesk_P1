from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_chamado_org_criacao_idx"),
    ]

    operations = [
        migrations.AddField(
            model_name="perfil",
            name="papel",
            field=models.CharField(
                choices=[("admin", "Administrador"), ("operador", "Operador")],
                default="operador",
                max_length=20,
                verbose_name="Papel",
            ),
        ),
    ]
