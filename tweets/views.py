from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.static import serve as static_serve
from django.db.models import Count
from .models import Tweet, TweetMedia, TweetUser, TweetHashTag
from .forms import TaggerForm


def cors_serve(request, path, document_root=None, show_indexes=False):
    """
    An override to `django.views.static.serve` that will allow us to add our
    own headers for development.

    Like `django.views.static.serve`, this should only ever be used in
    development, and never in production.

    Notes:
        * Taken from: https://stackoverflow.com/questions/28724951/django-dev-server-adding-headers-to-static-files
    """
    response = static_serve(request, path, document_root=document_root, show_indexes=show_indexes)

    response['Access-Control-Allow-Origin'] = '*'

    return response


def index(request):
    template = loader.get_template('index.html')
    context = {'welcome_msg': 'Sitio en desarrollo...'}
    return HttpResponse(template.render(context, request))


def statistics(request):
    template = loader.get_template('statistics.html')

    from datetime import datetime
    from_date = datetime.strptime('2019-05-10 20:57:50', '%Y-%m-%d %H:%M:%S')
    days_count = (datetime.now() - from_date).days

    most_used_hashtags = list(Tweet.objects.values('hashtags').annotate(count=Count('id_str')).order_by('-count')[:13])
    most_active_users = list(
        Tweet.objects.values('user__screen_name').annotate(count=Count('id_str')).order_by('-count')[:12])
    used_languages = Tweet.objects.values('lang').annotate(count=Count('id_str'))
    used_locations = Tweet.objects.values('location').annotate(count=Count('id_str'))
    # most_used_media_types = list(TweetMedia.objects.values('type').annotate(count=Count('id_str')).order_by('-count'))

    context = {
        'statistics': {
            'days_count': days_count,
            'tweets_count': len(Tweet.objects.all()),
            'medias_count': len(TweetMedia.objects.all()),
            # 'memes_count': len(TweetMedia.objects.filter(is_meme=True).all()),
            # 'noise_count': len(TweetMedia.objects.filter(is_meme=False).all()),
            # 'not_classified_count': len(TweetMedia.objects.filter(is_meme=None).all()),
            'users_count': len(TweetUser.objects.all()),
            'hashtags_count': len(TweetHashTag.objects.all()),
            # 'most_used_media_types': most_used_media_types,
            'most_used_hashtags': most_used_hashtags[1:],
            'most_active_users': most_active_users,
            'languages_count': len(used_languages),
            'most_used_languages': list(used_languages.order_by('-count')[:12]),
            'locations_count': len(used_locations),
            'most_used_locations': list(used_locations.order_by('-count')[:12])
        }
    }
    return HttpResponse(template.render(context, request))


def tagger(request):
    template = loader.get_template('tagger.html')

    # apply the following filters to images
    # - first month
    # - less than 10 annotations
    # - current user has never annotated

    tweet_media = TweetMedia.objects.get(pk=1)
    form = TaggerForm(instance=tweet_media)

    contex = {'form': None}
    return HttpResponse(template.render(contex, request))
