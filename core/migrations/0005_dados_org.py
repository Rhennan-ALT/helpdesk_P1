from django.db import migrations

MODELOS = ["Equipe", "Categoria", "Prioridade", "SLA", "Chamado"]


def org_padrao(apps, schema_editor):
    Organizacao = apps.get_model("core", "Organizacao")
    Perfil = apps.get_model("core", "Perfil")
    User = apps.get_model("auth", "User")

    org, _ = Organizacao.objects.get_or_create(nome="Organização padrão")

    for nome in MODELOS:
        Modelo = apps.get_model("core", nome)
        Modelo.objects.filter(organizacao__isnull=True).update(organizacao=org)

    for usuario in User.objects.filter(perfil__isnull=True):
        Perfil.objects.create(usuario=usuario, organizacao=org)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_organizacao_perfil"),
    ]

    operations = [
        migrations.RunPython(org_padrao, migrations.RunPython.noop),
    ]
