from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'

    def items(self):
        return ['countdown:index', 'pages:about', 'pages:contact', 'pages:privacy']

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        if item == 'countdown:index':
            return 1.0
        return 0.5
