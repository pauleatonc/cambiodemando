from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render


def privacy(request):
    return render(request, 'pages/privacy.html', {
        'title': 'Política de Privacidad — Cambio de Mando',
        'meta_description': 'Política de privacidad del sitio Cambio de Mando.',
    })


def about(request):
    return render(request, 'pages/about.html', {
        'title': 'Acerca de — Cambio de Mando',
        'meta_description': 'Conoce el propósito y el equipo detrás de Cambio de Mando.',
    })


def contact(request):
    return render(request, 'pages/contact.html', {
        'title': 'Contacto — Cambio de Mando',
        'meta_description': 'Información de contacto de Cambio de Mando.',
        'contact_email': getattr(settings, 'CONTACT_EMAIL', ''),
    })


def robots_txt(request):
    sitemap_url = request.build_absolute_uri('/sitemap.xml')
    lines = [
        'User-agent: *',
        'Allow: /',
        '',
        'Disallow: /admin/',
        'Disallow: /poll/api/',
        '',
        f'Sitemap: {sitemap_url}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


def ads_txt(request):
    adsense_client = getattr(settings, 'ADSENSE_CLIENT', '')
    if adsense_client:
        pub_id = adsense_client.replace('ca-pub-', '').replace('ca-', '')
        content = f'google.com, pub-{pub_id}, DIRECT, f08c47fec0942fa0\n'
    else:
        content = ''
    return HttpResponse(content, content_type='text/plain')
