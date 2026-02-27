from django.contrib import admin

from .models import Vote


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('option', 'created_at')
    list_filter = ('option',)
    date_hierarchy = 'created_at'
