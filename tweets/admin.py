from django.contrib import admin

from .models import Tweet
from .models import TweetMedia
from .models import TweetHashTag
from .models import TweetUser
from .models import ReportedUser
from .models import PrioritizedUser
from .models import Annotation

class TweetMediaInline(admin.TabularInline):
    model = Tweet.medias.through

    # readonly_fields = ('image_tag',)

    # disable deletion of inspections
    can_delete = True

    # show modification/edit link
    show_change_link = True

    # zero extra blank inlines
    extra = 0


class AnnotationInline(admin.TabularInline):
    model = Annotation
    can_delete = False  # disable deletion of annotations
    show_change_link = False  # modification/edit link
    extra = 0


class TweetAdmin(admin.ModelAdmin):
    list_display = ('id_str', 'user', 'text', 'images_tags')
    list_filter = ('user', 'hashtags',)

    list_per_page = 30

    inlines = (TweetMediaInline,)


class TweetMediaAdmin(admin.ModelAdmin):
    list_display = ('id_str', 'url', 'get_users', 'image_tag',)
    #list_filter = ('target',)

    #list_editable = ('target',)

    list_per_page = 20

    readonly_fields = ('image_tag',)

    inlines = (AnnotationInline,)

    def get_users(self, obj):
        return [', '.join([t.user.screen_name for t in obj.tweets.all()])]
    get_users.short_description = 'Users'


class TweetUserAdmin(admin.ModelAdmin):
    list_display = ('screen_name', 'name', 'location', 'url',)
    list_filter = ('location',)

    list_per_page = 30

    ordering = ('screen_name',)


class ReportedUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'reason',)

    ordering = ('user',)


class PrioritizedUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'reason',)

    ordering = ('user',)


admin.site.register(Tweet, TweetAdmin)
admin.site.register(TweetMedia, TweetMediaAdmin)
admin.site.register(TweetHashTag)
admin.site.register(TweetUser, TweetUserAdmin)
admin.site.register(ReportedUser, ReportedUserAdmin)
admin.site.register(PrioritizedUser, PrioritizedUserAdmin)
admin.site.site_header = 'Visual-Framing Administration'
