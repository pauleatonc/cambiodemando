from django.contrib import admin

from .models import DailyPublication, InstagramTokenState, Vote


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


@admin.register(InstagramTokenState)
class InstagramTokenStateAdmin(admin.ModelAdmin):
    list_display = ('provider', 'expires_at', 'data_access_expires_at', 'refreshed_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
