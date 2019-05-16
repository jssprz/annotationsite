from django.contrib import admin
from django.contrib.admin.options import TabularInline

from .models import Tweet
from .models import TweetMedia
from .models import TweetHashTag
from .models import TweetUser


class TweetMediaInlines(TabularInline):
    model = TweetMedia

    readonly_fields = ('image_tag',)

    # disable deletion of inspections
    can_delete = True

    # show modification/edit link
    show_change_link = True

    # zero extra blank inlines
    extra = 0


class TweetAdmin(admin.ModelAdmin):
    list_display = ('id_str', 'user', 'text', )
    list_filter = ('hashtags',)

    list_per_page = 30

    inlines = (TweetMediaInlines,)


class TweetMediaAdmin(admin.ModelAdmin):
    list_display = ('id_str', 'tweet', 'get_user', 'url', 'image_tag', 'is_meme',)
    list_filter = ('is_meme', 'tweet__user')

    list_editable = ('is_meme', )

    list_per_page = 20

    readonly_fields = ('image_tag', )

    def get_user(self, obj):
        return obj.tweet.user
    get_user.short_description = 'User'
    get_user.admin_order_field = 'tweet__user'


class TweetUserAdmin(admin.ModelAdmin):
    list_display = ('screen_name', 'name', 'location', 'url')
    list_filter = ('location',)

    list_per_page = 30

    ordering = ('screen_name',)


admin.site.register(Tweet, TweetAdmin)
admin.site.register(TweetMedia, TweetMediaAdmin)
admin.site.register(TweetHashTag)
admin.site.register(TweetUser, TweetUserAdmin)
