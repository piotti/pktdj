from django.contrib import admin

# Register your models here.

from .models import Song, Voter, SpotifyInfo, Feedback

class FeedbackAdmin(admin.ModelAdmin):
    readonly_fields=('time',)

# Register your models here.
admin.site.register(Song)
admin.site.register(Voter)
admin.site.register(SpotifyInfo)
admin.site.register(Feedback, FeedbackAdmin)
