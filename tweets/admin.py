import codecs

from django.contrib import admin

from .models import Tweet
from .models import TweetMedia
from .models import TweetHashTag
from .models import TweetUser
from .models import ReportedUser
from .models import PrioritizedUser
from .models import Annotation
from .models import Target


class PhaseFilter(admin.SimpleListFilter):
    title = 'Fase'
    parameter_name = 'media'

    def lookups(self, request, model_admin):
        return [('Fase de 50000', 'Fase de 50000')]

    def queryset(self, request, queryset):
        if self.value() == 'Fase de 50000':
            phase_range = (52100,104100)
            return queryset.filter(media__id__gt=phase_range[0]).filter(media__id__lte=phase_range[1])


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
    list_display = ('id_str', 'created_at', 'user', 'text', 'favorite_count', 'retweet_count', 'location', 'lang', 'images_tags')
    #list_filter = ('user', 'hashtags',)
    search_fields = ('id_str', )

    list_per_page = 30

    inlines = (TweetMediaInline,)


class TweetMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_str', 'url', 'get_tweets', 'get_users', 'image_tag',)
    #list_filter = ('target',)

    #list_editable = ('target',)

    list_per_page = 20

    search_fields = ('id', 'id_str', )

    readonly_fields = ('id', 'image_tag',)

    inlines = (AnnotationInline,)

    def get_users(self, obj):
        return [', '.join([t.user.screen_name for t in obj.tweets.all()])]
    get_users.short_description = 'Users'

    def get_tweets(self, obj):
        return [', '.join([t.id_str for t in obj.tweets.all()])]
    get_tweets.short_description = 'Tweets'


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


class TargetAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)

    ordering = ('name',)


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('created_by', 'target', 'media', 'get_text_in_media', 'get_description_of_media',
                    'get_interpretation', 'get_image_tag',)
    list_filter = ('created_by', 'target', PhaseFilter,)

    search_fields = ('media__id_str', )

    ordering = ('-media__id', 'created_by',)

    list_per_page = 50

    def get_text_in_media(self, obj):
        return codecs.escape_decode(obj.text_in_media)[0].decode()[2:-1]
    get_text_in_media.short_description = 'Textos'

    def get_description_of_media(self, obj):
        return codecs.escape_decode(obj.description_of_media)[0].decode()[2:-1]
    get_description_of_media.short_description = 'Descripciones'

    def get_interpretation(self, obj):
        return codecs.escape_decode(obj.interpretation)[0].decode()[2:-1]
    get_interpretation.short_description = 'Interpretaciones'

    def get_image_tag(self, obj):
        return obj.media.image_tag()
    get_image_tag.short_description = 'Image'


admin.site.register(Tweet, TweetAdmin)
admin.site.register(TweetMedia, TweetMediaAdmin)
admin.site.register(TweetHashTag)
admin.site.register(TweetUser, TweetUserAdmin)
admin.site.register(ReportedUser, ReportedUserAdmin)
admin.site.register(PrioritizedUser, PrioritizedUserAdmin)
admin.site.register(Target, TargetAdmin)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.site_header = 'Visual-Framing Administration'
