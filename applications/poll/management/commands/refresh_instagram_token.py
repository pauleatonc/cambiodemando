from django.core.management.base import BaseCommand, CommandError

from applications.poll.publication import InstagramTokenManager


class Command(BaseCommand):
    help = 'Inspecciona y refresca el token de Instagram/Meta cuando corresponde.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza refresh inmediato, sin evaluar umbral de expiracion.',
        )
        parser.add_argument(
            '--mode',
            choices=['facebook_exchange', 'instagram_refresh', 'disabled'],
            help='Modo de refresh explicito.',
        )
        parser.add_argument(
            '--inspect-only',
            action='store_true',
            help='Solo inspecciona expiracion del token, sin refrescar.',
        )

    def handle(self, *args, **options):
        manager = InstagramTokenManager()
        mode = options.get('mode')
        force = options.get('force')
        inspect_only = options.get('inspect_only')

        try:
            data = manager.inspect_token()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Token inspeccionado: is_valid={data.get('is_valid')} expires_at={data.get('expires_at')}"
                )
            )
        except Exception as exc:  # noqa: BLE001
            if inspect_only:
                raise CommandError(f'No se pudo inspeccionar token: {exc}') from exc
            self.stdout.write(self.style.WARNING(f'No se pudo inspeccionar token: {exc}'))

        if inspect_only:
            return

        try:
            if force:
                result = manager.refresh_token(mode=mode)
                if not result:
                    self.stdout.write(self.style.SUCCESS('Refresh deshabilitado por modo=disabled.'))
                    return
                token, expires_at = result
            else:
                result = manager.refresh_if_needed()
                if not result:
                    self.stdout.write(self.style.SUCCESS('Token vigente. No requiere refresh.'))
                    return
                token, expires_at = result
        except Exception as exc:  # noqa: BLE001
            raise CommandError(f'Error refrescando token: {exc}') from exc

        preview = token[:16] + '...' if token else 'vacío'
        self.stdout.write(
            self.style.SUCCESS(
                f'Token refrescado exitosamente ({preview}) expires_at={expires_at.isoformat() if expires_at else "n/a"}'
            )
        )
