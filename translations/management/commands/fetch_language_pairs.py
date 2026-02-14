"""Management command to download language pairs from LibreTranslate."""

import requests
from django.core.management.base import BaseCommand

from translations.models import LanguagePair

LIBRETRANSLATE_LANGUAGES_URL = "https://libretranslate.com/languages"


class Command(BaseCommand):
    help = "Download supported language pairs from LibreTranslate and store them in the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            default=LIBRETRANSLATE_LANGUAGES_URL,
            help="URL of the LibreTranslate /languages endpoint (default: %(default)s)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Remove all existing language pairs before importing.",
        )

    def handle(self, *args, **options):
        url = options["url"]

        self.stdout.write(f"Fetching languages from {url} ...")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            self.stderr.write(self.style.ERROR(f"Failed to fetch languages: {exc}"))
            return

        languages = response.json()

        # Build a lookup of code -> name for resolving target names
        name_by_code = {lang["code"]: lang["name"] for lang in languages}

        if options["clear"]:
            deleted, _ = LanguagePair.objects.all().delete()
            self.stdout.write(f"Cleared {deleted} existing language pair(s).")

        created = 0
        skipped = 0
        for lang in languages:
            source_code = lang["code"]
            source_name = lang["name"]
            for target_code in lang.get("targets", []):
                target_name = name_by_code.get(target_code, target_code)
                _, was_created = LanguagePair.objects.update_or_create(
                    source_code=source_code,
                    target_code=target_code,
                    defaults={
                        "source_name": source_name,
                        "target_name": target_name,
                    },
                )
                if was_created:
                    created += 1
                else:
                    skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created {created} new pair(s), updated {skipped} existing pair(s)."
            )
        )
