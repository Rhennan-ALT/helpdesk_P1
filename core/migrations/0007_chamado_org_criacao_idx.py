from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_organizacao_obrigatoria"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="chamado",
            index=models.Index(fields=["organizacao", "data_criacao"], name="chamado_org_criacao_idx"),
        ),
    ]
