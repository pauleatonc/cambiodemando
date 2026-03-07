import time
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from applications.poll.models import DailyPublication
from applications.poll.publication import XPublisher


class Command(BaseCommand):
    help = 'Publica en X (Twitter) la imagen diaria ya generada.'

    def add_arguments(self, parser):
        parser.add_argument('--date', dest='publication_date', help='Fecha objetivo YYYY-MM-DD')
        parser.add_argument('--retries', type=int, default=3, help='Cantidad de intentos ante fallo transitorio')
        parser.add_argument('--retry-delay', type=int, default=5, help='Segundos de espera inicial entre reintentos')
        parser.add_argument('--debug', action='store_true', help='Imprimir respuesta completa de X en caso de error (headers + body)')

    def _parse_date(self, value):
        if not value:
            return timezone.localdate()
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise CommandError('La fecha debe venir en formato YYYY-MM-DD') from exc

    def handle(self, *args, **options):
        publication_date = self._parse_date(options['publication_date'])
        retries = max(1, options['retries'])
        retry_delay = max(1, options['retry_delay'])
        debug = options.get('debug', False)

        publisher = XPublisher(debug=debug)
        if not publisher._has_credentials():
            self.stdout.write('Credenciales X no configuradas; omitiendo publicacion en X.')
            return

        publication = DailyPublication.objects.filter(publication_date=publication_date).first()
        if not publication:
            raise CommandError(f'No existe imagen generada para {publication_date}')
        if publication.x_tweet_id:
            self.stdout.write(self.style.SUCCESS(f'Ya estaba publicada en X: {publication.x_tweet_id}'))
            return

        last_exc = None
        current_delay = retry_delay
        for attempt in range(1, retries + 1):
            try:
                publication = publisher.publish(publication)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Publicacion X OK: date={publication.publication_date} tweet_id={publication.x_tweet_id}'
                    )
                )
                return
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                if attempt < retries:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Intento {attempt}/{retries} fallo: {exc}. Reintentando en {current_delay}s...'
                        )
                    )
                    time.sleep(current_delay)
                    current_delay *= 2

        raise CommandError(f'No se pudo publicar en X: {last_exc}')
