from django.db import migrations


def seed_default_language_pairs(apps, schema_editor):
    """Seed and enable core translation pairs for EN/RU/FR."""
    LanguagePair = apps.get_model("translations", "LanguagePair")

    defaults = [
        ("en", "English", "ru", "Russian"),
        ("ru", "Russian", "en", "English"),
        ("en", "English", "fr", "French"),
        ("fr", "French", "en", "English"),
        ("ru", "Russian", "fr", "French"),
        ("fr", "French", "ru", "Russian"),
    ]

    for source_code, source_name, target_code, target_name in defaults:
        LanguagePair.objects.update_or_create(
            source_code=source_code,
            target_code=target_code,
            defaults={
                "source_name": source_name,
                "target_name": target_name,
                "enabled": True,
            },
        )

class Migration(migrations.Migration):
    dependencies = [
        ("translations", "0002_languagepair_enabled"),
    ]

    operations = [
        migrations.RunPython(
            seed_default_language_pairs,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
