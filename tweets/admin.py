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
    list_display = ('id_str', 'tweet', 'url', 'image_tag', 'is_meme',)
    list_filter = ('tweet',)

    list_editable = ('is_meme', )

    list_per_page = 10

    readonly_fields = ('image_tag', )


admin.site.register(Tweet, TweetAdmin)
admin.site.register(TweetMedia, TweetMediaAdmin)
admin.site.register(TweetHashTag)
admin.site.register(TweetUser)
