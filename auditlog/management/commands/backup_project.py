import shutil
from pathlib import Path

from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone


class Command(BaseCommand):
    help = 'Back up database data and uploaded media files.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            default='backups',
            help='Directory where timestamped backups will be created.',
        )
        parser.add_argument(
            '--include-media',
            action='store_true',
            help='Copy MEDIA_ROOT into the backup directory.',
        )

    def handle(self, *args, **options):
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path(options['output_dir']).resolve() / timestamp
        backup_dir.mkdir(parents=True, exist_ok=False)

        data_path = backup_dir / 'data.json'
        with data_path.open('w', encoding='utf-8') as data_file:
            management.call_command(
                'dumpdata',
                '--natural-foreign',
                '--natural-primary',
                '--indent',
                '2',
                stdout=data_file,
            )

        if connection.vendor == 'sqlite':
            database_path = Path(connection.settings_dict['NAME'])
            if database_path.exists():
                shutil.copy2(database_path, backup_dir / database_path.name)

        if options['include_media'] and Path(settings.MEDIA_ROOT).exists():
            shutil.copytree(settings.MEDIA_ROOT, backup_dir / 'media')

        self.stdout.write(self.style.SUCCESS(f'Backup created at {backup_dir}'))
