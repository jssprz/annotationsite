import json
import csv
import codecs

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.template import loader
from django.views.static import serve as static_serve
from django.db.models import Count, Q
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from .models import Tweet, TweetMedia, TweetUser, TweetHashTag, Annotation, Target
from django.utils.safestring import mark_safe

phase_ranges = {'pre-train': (50000, 50100), 'train': (51100, 52100), '52mil': (52100,104100),
                'classify': {'valentina': (52100, 65100),
                             'frespinoza': (65100, 78100),
                             'mnjarami': (78100, 91100),
                             'japoblete': (91100, 104100),
                             'unknown': (104100, 154100)},
                'train2': (400000, 401000),
                'classify2': {'valentina': (424147, 437147),
                              'frespinoza': (437147, 450147),
                              'mnjarami': (450147, 463147),
                              'japoblete': (463147, 476147),
                              'aarosenb': (476147, 489147),
                              'unknown': (489147, 500000)}}
current_phase = 'train2'


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
    phase_range = phase_ranges[current_phase]
    if request.user.is_authenticated:
        if type(phase_range) is not tuple:
            phase_range = phase_range[request.user.username] if request.user.username in phase_range else phase_range['unknown']
        # apply the following filters to images
        # - first month (first 50000)
        # - less than 10 annotations
        # - current user has never annotated
        user_annotated_medias_ids = Annotation.objects.filter(created_by=request.user).values_list('media_id', flat=True)
        full_annotated_medias_ids = Annotation.objects.annotate(num_per_media=Count('media')).filter(num_per_media__gte=5).values_list('media_id', flat=True)
        excluded_medias_ids = list(user_annotated_medias_ids) + list(full_annotated_medias_ids)
        print(excluded_medias_ids)
        medias = TweetMedia.objects.filter(
            id__gt=phase_range[0]).filter(
            id__lte=phase_range[1]).exclude(
            id__in=excluded_medias_ids).order_by('id').all()
        print(len(medias))
        if len(medias) > 0:
            print(medias[0].id, medias[len(medias)//2].id, medias[len(medias)-1].id)
            s = FileSystemStorage()
            print(s.get_created_time(medias[0].local_image.name).date())
            print(medias[0].local_image.__dict__)
    else:
        base_url = reverse('index')
        login_url = '{}accounts/login/'.format(base_url)
        print('redirectig to {}'.format(login_url))
        response = redirect(login_url)
        return response

    medias = medias[:25]
    s = FileSystemStorage()
    dates = [s.get_created_time(m.local_image.name).date() for m in medias]

    template = loader.get_template('tagger.html')
    contex = {'medias': list(zip(medias, dates)), 'options': Target.objects.all()}
    return HttpResponse(template.render(contex, request))


def tagger_statistics(request):
    phase_range = phase_ranges[current_phase]

    if request.user.is_authenticated:
        if type(phase_range) is not tuple:
            phase_range = phase_range[request.user.username] if request.user.username in phase_range else phase_range[
                'unknown']

        annotations = Annotation.objects.filter(
            media_id__gt=phase_range[0]).filter(
            media_id__lte=phase_range[1]).exclude(
            created_by__username='magdalena').order_by()

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
            annotations_per_target = annotations.filter(media__id_str__in=grouped_medias[4]).values('media', 'target').annotate(Count('created_by'))

            unanimous_count = 0
            for r in annotations_per_target.all():
                if r['created_by__count'] == 4:
                    unanimous_count += 1

            icr_value = unanimous_count / len(grouped_medias[4])

        # count_medias_per_count_of_annotations = count_medias_per_count_of_annotations.order_by('-num_annotations')
        annotations_per_user = annotations.values('created_by__username').annotate(
            count=Count('media')).order_by('-count')

        template = loader.get_template('tagger_statistics.html')
        context = {
            'statistics': {
                'count_of_annotations': annotations.count(),
                'count_medias_per_count_of_annotations': medias_count,
                'annotations_per_user': annotations_per_user.all(),
                'icr': icr_value * 100.0
            }
        }
        return HttpResponse(template.render(context, request))
    else:
        base_url = reverse('index')
        login_url = '{}accounts/login/'.format(base_url)
        print('redirectig to {}'.format(login_url))
        response = redirect(login_url)
        return response


def generate_tagger_summary(phase_range):
    annotations = Annotation.objects.filter(
        media_id__gt=phase_range[0]).filter(
        media_id__lte=phase_range[1]).exclude(
        created_by__username='magdalena').order_by()

    users = annotations.values('created_by__username').distinct().all()
    all_medias = annotations.values('media__id').distinct().all()

    medias = {}
    for m in all_medias:
        medias[TweetMedia.objects.get(pk=m['media__id'])] = [('', '', '', '') for _ in users]

    for i, user in enumerate(users):
        user_annotations = annotations.filter(created_by__username=user['created_by__username']).all()
        print(user_annotations)
        for a in user_annotations:
            medias[a.media][i] = (a.target.name,
                                  codecs.escape_decode(a.text_in_media)[0].decode()[2:-1],
                                  codecs.escape_decode(a.description_of_media)[0].decode()[2:-1],
                                  codecs.escape_decode(a.interpretation)[0].decode()[2:-1])

    return users, medias


def tagger_summary(request):
    phase_range = phase_ranges[current_phase]
    if request.user.is_authenticated:
        if request.user.username in ['jeperez', 'magdalena']:
            username = 'valentina' #valentina frespinoza mnjarami japoblete
            phase_range = phase_range[username]
        elif type(phase_range) is not tuple:
            phase_range = phase_range[request.user.username] if request.user.username in phase_range else phase_range[
                'unknown']
        users, medias = generate_tagger_summary(phase_range)
    else:
        base_url = reverse('index')
        login_url = '{}accounts/login/'.format(base_url)
        print('redirectig to {}'.format(login_url))
        response = redirect(login_url)
        return response

    template = loader.get_template('tagger_summary.html')
    context = {
        'users': users,
        'medias': medias
    }
    return HttpResponse(template.render(context, request))


def tagger_summary_csv(request):
    phase_range = phase_ranges[current_phase]

    if request.user.is_authenticated:
        if type(phase_range) is not tuple:
            phase_range = phase_range[request.user.username] if request.user.username in phase_range else phase_range[
                'unknown']

        users, medias = generate_tagger_summary(phase_range)
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tagger_summary_{}_phase.csv"'.format(current_phase)

        writer = csv.writer(response)
        first_row = ['CASO'] + ['Codificador{}'.format(i) for i, _ in enumerate(users, start=1)]
        writer.writerow(first_row)

        def get_id(t):
            return 0 if t == 'No-meme' else 1 if t == 'Meme' else 2 if t == 'Dudoso' else 3

        for i, (m, targets) in enumerate(medias.items(), start=1):
            writer.writerow([i] + [get_id(t[0]) for t in targets])

        return response
    else:
        base_url = reverse('index')
        login_url = '{}accounts/login/'.format(base_url)
        print('redirectig to {}'.format(login_url))
        response = redirect(login_url)
        return response


def tweets_summary_csv(request):
    phase_range = phase_ranges['52mil']

    if request.user.is_authenticated:
        if type(phase_range) is not tuple:
            phase_range = phase_range[request.user.username] if request.user.username in phase_range else phase_range[
                'unknown']

        annotations = Annotation.objects.filter(
        media_id__gt=phase_range[0]).filter(
        media_id__lte=phase_range[1]).exclude(
        created_by__username='magdalena').order_by()

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tweets_summary_{}_phase.csv"'.format(current_phase)

        writer = csv.writer(response)
        first_row = ['MEDIA', 'Tweets', 'text', 'hashtags', 'created_at', 'favorite_count', 'retweet_count', 'lang', 'name', 'screen_name', 'location', 'url']
        writer.writerow(first_row)

        rows_count = 0
        for a in annotations.all():
            if a.target.name in ['Meme', 'Sticker']:
                tweets = TweetMedia.objects.get(pk=a.media.id).tweets.all()
                for t in tweets:
                    hashtags = ['#' + str(h.text) for h in t.hashtags.all()]
                    ' '.join(hashtags)
                    writer.writerow(['"{}"'.format(a.media.id_str), '"{}"'.format(t.id_str), str(t.text), hashtags, str(t.created_at), t.favorite_count, t.retweet_count, str(t.lang), str(t.user.name), str(t.user.screen_name), str(t.user.location), str(t.user.url)])
                    rows_count += 1
        print('count of tweets in the summary: {}'.format(rows_count))

        return response
    else:
        base_url = reverse('index')
        login_url = '{}accounts/login/'.format(base_url)
        print('redirectig to {}'.format(login_url))
        response = redirect(login_url)
        return response


def annotate(request, media_id_str):
    media = get_object_or_404(TweetMedia, id_str=media_id_str)
    if request.user.is_authenticated:
        try:
            selected_target = Target.objects.get(pk=request.POST['target'])
            text = request.POST['text'].encode('utf-8')
            description = request.POST['description'].encode('utf-8')
            interpretation = request.POST['interpretation'].encode('utf-8')
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
                                        text_in_media=text, description_of_media=description, interpretation=interpretation)
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
