from django.contrib import admin

from .models import DailyPublication, Vote


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('option', 'session_key', 'created_at')
    list_filter = ('option',)
    date_hierarchy = 'created_at'


@admin.register(DailyPublication)
class DailyPublicationAdmin(admin.ModelAdmin):
    list_display = (
        'publication_date',
        'status',
        'good_pct_display',
        'bad_pct_display',
        'generated_at',
        'published_at',
    )
    list_filter = ('status',)
    search_fields = ('publication_date', 'result_label', 'instagram_media_id')
