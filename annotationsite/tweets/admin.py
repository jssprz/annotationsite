from django.contrib import admin

from .models import Tweet
from .models import TweetMedia
from .models import TweetHashTag
from .models import TweetUser


class TweetMediaAdmin(admin.ModelAdmin):
    fields = ('image_tag', )
    readonly_fields = ('image_tag', )


admin.site.register(Tweet)
admin.site.register(TweetMedia, TweetMediaAdmin)
admin.site.register(TweetHashTag)
admin.site.register(TweetUser)
