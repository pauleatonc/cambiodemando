from django.db import models


class Vote(models.Model):
    """Voto de la encuesta ¿Cómo vamos? (Bien / Mal). Un voto por sesión por día."""

    OPTION_GOOD = 'good'
    OPTION_BAD = 'bad'
    OPTIONS = [
        (OPTION_GOOD, 'Bien'),
        (OPTION_BAD, 'Mal'),
    ]

    option = models.CharField(max_length=10, choices=OPTIONS)
    session_key = models.CharField(max_length=40, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'voto (encuesta)'
        verbose_name_plural = 'Votos (encuesta)'

    def __str__(self):
        return f'{self.get_option_display()} ({self.created_at})'


class DailyPublication(models.Model):
    """Bitacora diaria para generacion/publicacion de la imagen de encuesta."""

    STATUS_GENERATED = 'generated'
    STATUS_PUBLISH_PENDING = 'publish_pending'
    STATUS_PUBLISHED = 'published'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_GENERATED, 'Generated'),
        (STATUS_PUBLISH_PENDING, 'Publish pending'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_FAILED, 'Failed'),
    ]

    publication_date = models.DateField(unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_GENERATED)

    image_path = models.CharField(max_length=500, blank=True)
    public_image_url = models.URLField(max_length=500, blank=True)

    result_label = models.CharField(max_length=120, blank=True)
    good_count = models.PositiveIntegerField(default=0)
    bad_count = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    good_pct_display = models.PositiveSmallIntegerField(default=0)
    bad_pct_display = models.PositiveSmallIntegerField(default=0)

    creation_id = models.CharField(max_length=100, blank=True)
    instagram_media_id = models.CharField(max_length=100, blank=True)
    last_error = models.TextField(blank=True)

    generated_at = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-publication_date']
        verbose_name = 'publicacion diaria'
        verbose_name_plural = 'Publicaciones diarias'

    def __str__(self):
        return f'{self.publication_date} - {self.status}'


class InstagramTokenState(models.Model):
    """Estado del access token de Meta usado para publicar en Instagram."""

    provider_facebook = 'facebook_graph'
    provider_instagram = 'instagram_graph'
    PROVIDER_CHOICES = [
        (provider_facebook, 'Facebook Graph'),
        (provider_instagram, 'Instagram Graph'),
    ]

    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default=provider_facebook)
    access_token = models.TextField(blank=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    data_access_expires_at = models.DateTimeField(blank=True, null=True)
    refreshed_at = models.DateTimeField(blank=True, null=True)
    token_type = models.CharField(max_length=40, blank=True)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'estado token instagram'
        verbose_name_plural = 'Estados token instagram'

    def __str__(self):
        return f'{self.provider} - {"set" if self.access_token else "missing"}'
