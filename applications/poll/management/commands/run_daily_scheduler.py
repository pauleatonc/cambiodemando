import time
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Scheduler interno: ejecuta generacion+publicacion diaria a las 12:00 local.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--run-once',
            action='store_true',
            help='Ejecuta una vez (util para pruebas) y termina.',
        )

    def _next_run(self):
        now = timezone.localtime()
        target = now.replace(
            hour=settings.DAILY_POST_HOUR,
            minute=settings.DAILY_POST_MINUTE,
            second=0,
            microsecond=0,
        )
        if now >= target:
            target = target + timedelta(days=1)
        return target

    def _should_run_today_now(self):
        """True si ya pasó la hora de publicación de hoy (para no perder el run si el scheduler arrancó tarde)."""
        now = timezone.localtime()
        target_today = now.replace(
            hour=settings.DAILY_POST_HOUR,
            minute=settings.DAILY_POST_MINUTE,
            second=0,
            microsecond=0,
        )
        return now >= target_today

    def _execute_daily_flow(self):
        current_date = timezone.localdate().isoformat()
        self.stdout.write(f'[{datetime.now().isoformat()}] Ejecutando flujo diario para {current_date}')
        call_command('refresh_instagram_token')
        call_command('generate_daily_image', date=current_date)
        call_command('publish_daily_instagram', date=current_date)
        call_command('publish_daily_x', date=current_date)
        self.stdout.write(f'[{datetime.now().isoformat()}] Flujo diario finalizado')

    def handle(self, *args, **options):
        if options['run_once']:
            self._execute_daily_flow()
            return

        self.stdout.write('Scheduler activo. Esperando proxima ventana diaria...')
        last_run_date = None
        while True:
            now = timezone.localtime()
            next_run = self._next_run()
            # Si ya pasó la hora de hoy y aún no hemos ejecutado hoy, ejecutar ahora (evita perder el run si el contenedor arrancó después de las 12:00).
            if self._should_run_today_now() and (last_run_date is None or last_run_date < now.date()):
                self.stdout.write(
                    f'[{datetime.now().isoformat()}] Ejecutando flujo de hoy (hora de publicación ya pasada).'
                )
                self._execute_daily_flow()
                last_run_date = now.date()
                next_run = self._next_run()
            wait_seconds = max(1, int((next_run - timezone.localtime()).total_seconds()))
            self.stdout.write(
                f'[{datetime.now().isoformat()}] Proxima ejecucion a las {next_run.isoformat()} '
                f'(en {wait_seconds}s)'
            )
            time.sleep(wait_seconds)
            self._execute_daily_flow()
            last_run_date = timezone.localdate()
