from datetime import date

from django.core.management.base import BaseCommand, CommandError

from applications.poll.publication import DailyCardGenerator


class Command(BaseCommand):
    help = 'Genera el JPG diario con la composicion de encuesta.'

    def add_arguments(self, parser):
        parser.add_argument('--date', dest='publication_date', help='Fecha objetivo YYYY-MM-DD')
        parser.add_argument('--force', action='store_true', help='Regenera aunque ya exista artefacto')

    def handle(self, *args, **options):
        publication_date = None
        if options['publication_date']:
            try:
                publication_date = date.fromisoformat(options['publication_date'])
            except ValueError as exc:
                raise CommandError('La fecha debe venir en formato YYYY-MM-DD') from exc

        generator = DailyCardGenerator()
        publication, out_path = generator.generate(publication_date=publication_date, force=options['force'])
        self.stdout.write(
            self.style.SUCCESS(
                f'Imagen diaria lista: {out_path} | status={publication.status} | url={publication.public_image_url}'
            )
        )
