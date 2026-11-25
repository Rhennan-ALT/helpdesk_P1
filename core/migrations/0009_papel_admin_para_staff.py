from django.db import migrations
from django.db.models import Q


def staff_vira_admin(apps, schema_editor):
    Perfil = apps.get_model("core", "Perfil")
    Perfil.objects.filter(
        Q(usuario__is_staff=True) | Q(usuario__is_superuser=True)
    ).update(papel="admin")


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_perfil_papel"),
    ]

    operations = [
        migrations.RunPython(staff_vira_admin, migrations.RunPython.noop),
    ]
