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
