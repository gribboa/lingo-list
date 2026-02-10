from django.db import migrations, models


def backfill_source_language(apps, schema_editor):
    """Copy source_language from the related ListItem to each cache row."""
    TranslationCache = apps.get_model("lists", "TranslationCache")
    for cache in TranslationCache.objects.select_related("item").all():
        cache.source_language = cache.item.source_language
        cache.save(update_fields=["source_language"])


class Migration(migrations.Migration):

    dependencies = [
        ("lists", "0005_add_list_archived"),
    ]

    operations = [
        # 1. Add the field as nullable so existing rows aren't rejected.
        migrations.AddField(
            model_name="translationcache",
            name="source_language",
            field=models.CharField(default="", max_length=10),
            preserve_default=False,
        ),
        # 2. Back-fill from the related item.
        migrations.RunPython(
            backfill_source_language,
            reverse_code=migrations.RunPython.noop,
        ),
        # 3. Replace the old unique constraint with one that includes source_language.
        migrations.AlterUniqueTogether(
            name="translationcache",
            unique_together={("item", "source_language", "target_language")},
        ),
    ]
