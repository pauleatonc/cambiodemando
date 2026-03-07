"""
Comando para verificar que las credenciales X (OAuth 1.0a) funcionan.
GET account/verify_credentials: si devuelve 200, la app/token/IP están OK.
Si devuelve 403 desde el VPS pero 200 desde tu PC, el problema es la IP del VPS.
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import requests
from requests_oauthlib import OAuth1

VERIFY_URL = 'https://api.twitter.com/1.1/account/verify_credentials.json'


class Command(BaseCommand):
    help = 'Verifica credenciales X (GET account/verify_credentials). Útil para diagnosticar 403 en media upload.'

    def handle(self, *args, **options):
        consumer_key = getattr(settings, 'X_CONSUMER_KEY', '') or ''
        consumer_secret = getattr(settings, 'X_CONSUMER_SECRET', '') or ''
        access_token = getattr(settings, 'X_ACCESS_TOKEN', '') or ''
        access_token_secret = getattr(settings, 'X_ACCESS_TOKEN_SECRET', '') or ''
        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            raise CommandError('Faltan variables X_* en settings/.env')

        auth = OAuth1(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )
        headers = {'User-Agent': 'cambiodemando/1.0 (+https://cambiodemando.com)'}
        resp = requests.get(VERIFY_URL, auth=auth, headers=headers, timeout=15)
        self.stdout.write(f'Status: {resp.status_code}')
        self.stdout.write(f'Headers: {dict(list(resp.headers.items())[:8])}')
        if resp.text:
            self.stdout.write(f'Body: {resp.text[:500]}')
        else:
            self.stdout.write('Body: (empty)')
        if resp.status_code == 200:
            self.stdout.write(self.style.SUCCESS('Credenciales OK. Si media upload sigue en 403, el problema es ese endpoint (p. ej. firma OAuth con multipart).'))
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Si esto es 403 desde el VPS, prueba el mismo comando desde tu PC con el mismo .env. '
                    'Si desde el PC va 200 y desde el VPS 403, el datacenter del VPS está bloqueado.'
                )
            )
