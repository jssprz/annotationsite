import os
import urllib
import urllib3

from django.db import models
from django.utils.safestring import mark_safe
from django.core.files import File
from django.conf import settings


class TweetUser(models.Model):
    id_str = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    screen_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(default=None, blank=True, null=True)

    def __str__(self):
        return self.screen_name

    class Meta:
        verbose_name = 'Usuario de Twitter'
        verbose_name_plural = 'Usuarios de tweets'
        ordering = ['name']


class TweetHashTag(models.Model):
    text = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Hash-tag de tweet'
        verbose_name_plural = 'Hash-tags de tweets'
        ordering = ['text']


class Tweet(models.Model):
    id_str = models.CharField(max_length=100, primary_key=True)
    text = models.TextField()
    user = models.ForeignKey(TweetUser, on_delete=models.CASCADE)
    hashtags = models.ManyToManyField(TweetHashTag)
    created_at = models.DateTimeField()
    favorite_count = models.IntegerField()
    retweet_count = models.IntegerField()
    lang = models.CharField(max_length=10)
    location = models.CharField(max_length=100, null=True, blank=True)
    coordinates_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    coordinates_long = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.id_str


class TweetMedia(models.Model):
    id_str = models.CharField(max_length=100)
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    url = models.URLField()
    media_url = models.URLField()
    media_url_https = models.URLField()
    local_image = models.ImageField(upload_to='tweet_medias', verbose_name='local_url', max_length=256)
    type = models.CharField(max_length=50)
    is_meme = models.BooleanField(null=True)

    def image_tag(self):
        return mark_safe('<img src="%s" width="150" height="150" />' % self.local_image.url)

    def cache(self):
        """Store image locally if we have a URL"""

        if self.media_url and not self.local_image:
            self.local_image.name = 'tweet_medias/{}'.format(os.path.basename(self.media_url))
            path_to_save = os.path.join(settings.MEDIA_ROOT, self.local_image.name)

            http = urllib3.PoolManager()
            r = http.request('GET', self.media_url, preload_content=False)

            with open(path_to_save, 'wb') as out:
                while True:
                    data = r.read(100)
                    if not data:
                        break
                    out.write(data)

            # self.local_image.save(
            #     '{}_{}'.format(self.id_str, os.path.basename(self.url)),
            #     File(open(result[0], 'rb'))
            # )

    def download_media(self):
        """

        :return:
        """

        http = urllib3.PoolManager()
        r = http.request('GET', url, preload_content=False)

        path = os.path.abspath(
            os.path.join(self.__save_media_dir, '{}_{}.{}'.format(tweet['id_str'], i, url.split('.')[-1])))

        with open(path, 'wb') as out:
            while True:
                data = r.read()
                if not data:
                    break
                out.write(data)
                saved_paths.append(path)

        r.release_conn()

    image_tag.short_description = 'Image'
    image_tag.allow_tags = True

    def __str__(self):
        return self.id_str

    class Meta:
        verbose_name = 'Imagen de tweet'
        verbose_name_plural = 'Imágenes de los tweets'
        ordering = ['tweet']