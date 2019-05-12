from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.static import serve as static_serve
from django.db.models import Count
from .models import Tweet, TweetMedia, TweetUser, TweetHashTag


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

    most_used_hashtags = list(Tweet.objects.values('hashtags').annotate(count=Count('id_str')).order_by('-count')[:10])
    most_active_users = list(Tweet.objects.values('user__screen_name').annotate(count=Count('id_str')).order_by('-count')[:10])
    most_used_media_types = list(TweetMedia.objects.values('type').annotate(count=Count('id_str')).order_by('-count'))

    context = {
        'statistics': {
            'tweets_count': len(Tweet.objects.all()),
            'medias_count': len(TweetMedia.objects.all()),
            'memes_count': len(TweetMedia.objects.filter(is_meme=True).all()),
            'noise_count': len(TweetMedia.objects.filter(is_meme=False).all()),
            'not_classified_count': len(TweetMedia.objects.filter(is_meme=None).all()),
            'users_count': len(TweetUser.objects.all()),
            'hashtags_count': len(TweetHashTag.objects.all()),
            'most_used_media_types': most_used_media_types,
            'most_used_hashtags': most_used_hashtags[1:],
            'most_active_users': most_active_users,
        }
    }
    return HttpResponse(template.render(context, request))
