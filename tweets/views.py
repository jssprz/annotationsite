import json
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.template import loader
from django.views.static import serve as static_serve
from django.db.models import Count, Sum
from django.urls import reverse
from .models import Tweet, TweetMedia, TweetUser, TweetHashTag, Annotation, Target


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
            'most_used_locations': list(used_locations.order_by('-count')[:12]),
        }
    }
    return HttpResponse(template.render(context, request))


def tagger(request):
    template = loader.get_template('tagger.html')

    if request.user.is_authenticated:
        # apply the following filters to images
        # - first month (first 50000)
        # - less than 10 annotations
        # - current user has never annotated
        user_annotated_medias_ids = Annotation.objects.filter(created_by=request.user).values_list('media_id', flat=True)
        full_annotated_medias_ids = Annotation.objects.annotate(num_per_media=Count('media')).filter(num_per_media__gte=5).values_list('media_id', flat=True)
        excluded_medias_ids = list(user_annotated_medias_ids) + list(full_annotated_medias_ids)
        print(excluded_medias_ids)
        medias = TweetMedia.objects.filter(id__gte=3000, id__lte=50000).exclude(id__in=excluded_medias_ids).all()
        print(len(medias))
    else:
        # medias = TweetMedia.objects.filter(id__gt=50000).filter(id__lte=60000).all()
        base_url = reverse('index')
        login_url = '{}accounts/login/'.format(base_url)
        print('redirectig to {}'.format(login_url))
        response = redirect(login_url)
        return response

    contex = {'medias': medias[:25], 'options': Target.objects.all()}
    return HttpResponse(template.render(contex, request))


def tagger_statistics(request):
    template = loader.get_template('tagger_statistics.html')

    annotations = Annotation.objects.exclude(created_by__username='magdalena')

    annotations_per_media = annotations.values('media__id_str').annotate(Count('created_by'))
    print(len(annotations_per_media.all()))
    print(annotations_per_media.all())

    medias_count = {}
    grouped_medias = {}
    for r in annotations_per_media.all():
        if r['created_by__count'] in medias_count:
            medias_count[r['created_by__count']] += 1
            grouped_medias[r['created_by__count']].append(r['media__id_str'])
        else:
            medias_count[r['created_by__count']] = 1
            grouped_medias[r['created_by__count']] = [r['media__id_str']]

    print(medias_count)

    icr_value = 0.0
    if 4 in medias_count:
        annotations_per_target = annotations.filter(media__id_str__in=grouped_medias[4]).values('target').annotate(Count('created_by'))

        unanimous_count = 0
        for r in annotations_per_target.all():
            if r['created_by__count'] == 4:
                unanimous_count += 1

        icr_value = unanimous_count / len(grouped_medias[4])

    # count_medias_per_count_of_annotations = count_medias_per_count_of_annotations.order_by('-num_annotations')
    annotations_per_user = annotations.values('created_by__username').annotate(
        count=Count('media')).order_by('-count')

    context = {
        'statistics': {
            'count_of_annotations': annotations.count(),
            'count_medias_per_count_of_annotations': medias_count,
            'annotations_per_user': annotations_per_user.all(),
            'icr': icr_value * 100.0
        }
    }
    return HttpResponse(template.render(context, request))


def annotate(request, media_id_str):
    media = get_object_or_404(TweetMedia, id_str=media_id_str)
    if request.user.is_authenticated:
        try:
            selected_target = Target.objects.get(pk=request.POST['target'])
            text = request.POST['text'].encode('utf-8')
            description = request.POST['description'].encode('utf-8')
        except (KeyError, Target.DoesNotExist):
            print('target {} unknown'.format(request.POST['target']))
            # Redisplay the question voting form.
            return render(request, 'tweets/error.html', {
                'media': media,
                'error_message': "You didn't select a choice.",
            })
        else:
            response_data = {}
            if not Annotation.objects.filter(media=media, created_by=request.user).exists():
                annotation = Annotation(media=media, created_by=request.user, target=selected_target,
                                        text_in_media=text, description_of_media=description)
                response_data['result_msg'] = 'saved new annotation ({}) of media {} by {}'.format(selected_target.name, media_id_str, request.user.username)
                response_data['result'] = 'saved'
            else:
                annotation = Annotation.objects.get(media=media, created_by=request.user)
                annotation.target = selected_target
                annotation.text_in_media = text
                annotation.description_of_media = description
                response_data['result_msg'] = 'updated annotation ({}) of {} by {}'.format(selected_target.name, media_id_str, request.user.username)
                response_data['result'] = 'change saved'
            annotation.save()
            print(response_data['result_msg'])
            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
    else:
        pass
