from django.contrib import admin

# Register your models here.

from .models import Song, Voter, SpotifyInfo, Feedback, VotedSong

class FeedbackAdmin(admin.ModelAdmin):
    readonly_fields=('time',)

class VotedSongAdmin(admin.ModelAdmin):
    readonly_fields=('play_time', 'votes')

    def votes(self, obj):
        return obj.voter_set.count()


# Register your models here.
admin.site.register(Song)
admin.site.register(Voter)
admin.site.register(VotedSong, VotedSongAdmin)
admin.site.register(SpotifyInfo)
admin.site.register(Feedback, FeedbackAdmin)
