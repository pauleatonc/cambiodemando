import time
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from applications.poll.models import DailyPublication
from applications.poll.publication import InstagramPublisher, InstagramTokenManager


class Command(BaseCommand):
    help = 'Publica en Instagram la imagen diaria ya generada.'

    def add_arguments(self, parser):
        parser.add_argument('--date', dest='publication_date', help='Fecha objetivo YYYY-MM-DD')
        parser.add_argument('--retries', type=int, default=3, help='Cantidad de intentos ante fallo transitorio')
        parser.add_argument('--retry-delay', type=int, default=5, help='Segundos de espera inicial entre reintentos')

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

        publication = DailyPublication.objects.filter(publication_date=publication_date).first()
        if not publication:
            raise CommandError(f'No existe imagen generada para {publication_date}')
        if publication.status == DailyPublication.STATUS_PUBLISHED:
            self.stdout.write(self.style.SUCCESS(f'Ya estaba publicada: {publication.instagram_media_id}'))
            return

        publisher = InstagramPublisher()
        token_manager = InstagramTokenManager()
        current_delay = retry_delay
        last_exc = None
        for attempt in range(1, retries + 1):
            try:
                if attempt == 1:
                    token_manager.refresh_if_needed()
                publication = publisher.publish(publication)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Publicacion OK: date={publication.publication_date} media_id={publication.instagram_media_id}'
                    )
                )
                return
            except Exception as exc:  # noqa: BLE001 - comando CLI
                last_exc = exc
                # Si el error de auth aparece en primer intento, forzar refresh y reintentar.
                if attempt == 1 and ('OAuth' in str(exc) or 'access token' in str(exc).lower()):
                    try:
                        token_manager.refresh_token()
                        self.stdout.write(self.style.WARNING('Se detecto fallo de token. Token refrescado, reintentando.'))
                    except Exception as refresh_exc:  # noqa: BLE001
                        self.stdout.write(self.style.WARNING(f'No se pudo refrescar token automaticamente: {refresh_exc}'))
                if attempt < retries:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Intento {attempt}/{retries} fallo: {exc}. Reintentando en {current_delay}s...'
                        )
                    )
                    time.sleep(current_delay)
                    current_delay *= 2

        publication.status = DailyPublication.STATUS_FAILED
        publication.last_error = str(last_exc or 'Error desconocido')
        publication.save(update_fields=['status', 'last_error', 'updated_at'])
        raise CommandError(f'No se pudo publicar: {publication.last_error}')
