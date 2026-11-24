import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_sla_horas_minimo"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Organizacao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=120, verbose_name="Nome")),
                ("criada_em", models.DateTimeField(auto_now_add=True, verbose_name="Criada em")),
            ],
            options={
                "verbose_name": "Organização",
                "verbose_name_plural": "Organizações",
                "ordering": ["nome"],
            },
        ),
        migrations.CreateModel(
            name="Perfil",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "organizacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="perfis",
                        to="core.organizacao",
                        verbose_name="Organização",
                    ),
                ),
                (
                    "usuario",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuário",
                    ),
                ),
            ],
            options={
                "verbose_name": "Perfil",
                "verbose_name_plural": "Perfis",
            },
        ),
        migrations.AddField(
            model_name="categoria",
            name="organizacao",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core.organizacao",
                verbose_name="Organização",
            ),
        ),
        migrations.AddField(
            model_name="chamado",
            name="organizacao",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core.organizacao",
                verbose_name="Organização",
            ),
        ),
        migrations.AddField(
            model_name="equipe",
            name="organizacao",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core.organizacao",
                verbose_name="Organização",
            ),
        ),
        migrations.AddField(
            model_name="prioridade",
            name="organizacao",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core.organizacao",
                verbose_name="Organização",
            ),
        ),
        migrations.AddField(
            model_name="sla",
            name="organizacao",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core.organizacao",
                verbose_name="Organização",
            ),
        ),
    ]
