import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_dados_org"),
    ]

    operations = [
        migrations.AlterField(
            model_name="categoria",
            name="organizacao",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="core.organizacao",
                verbose_name="Organização",
            ),
        ),
        migrations.AlterField(
            model_name="chamado",
            name="organizacao",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="core.organizacao",
                verbose_name="Organização",
            ),
        ),
        migrations.AlterField(
            model_name="equipe",
            name="organizacao",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="core.organizacao",
                verbose_name="Organização",
            ),
        ),
        migrations.AlterField(
            model_name="prioridade",
            name="organizacao",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="core.organizacao",
                verbose_name="Organização",
            ),
        ),
        migrations.AlterField(
            model_name="sla",
            name="organizacao",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="core.organizacao",
                verbose_name="Organização",
            ),
        ),
        migrations.AlterField(
            model_name="categoria",
            name="nome",
            field=models.CharField(max_length=100, verbose_name="Nome"),
        ),
        migrations.AlterField(
            model_name="equipe",
            name="nome",
            field=models.CharField(max_length=100, verbose_name="Nome"),
        ),
        migrations.AlterField(
            model_name="prioridade",
            name="nome",
            field=models.CharField(max_length=50, verbose_name="Nome"),
        ),
        migrations.AddConstraint(
            model_name="categoria",
            constraint=models.UniqueConstraint(fields=("organizacao", "nome"), name="categoria_nome_unico_por_org"),
        ),
        migrations.AddConstraint(
            model_name="equipe",
            constraint=models.UniqueConstraint(fields=("organizacao", "nome"), name="equipe_nome_unico_por_org"),
        ),
        migrations.AddConstraint(
            model_name="prioridade",
            constraint=models.UniqueConstraint(fields=("organizacao", "nome"), name="prioridade_nome_unico_por_org"),
        ),
    ]
