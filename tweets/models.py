from django.db import models
from django.utils.safestring import mark_safe


class TweetUser(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    screen_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    url = models.URLField(default=None, blank=True, null=True)

    def __str__(self):
        return self.screen_name


class TweetHashTag(models.Model):
    text = models.CharField(max_length=100)

    def __str__(self):
        return self.text


class Tweet(models.Model):
    str_id = models.CharField(max_length=100, primary_key=True)
    text = models.TextField()
    user = models.ForeignKey(TweetUser, on_delete=models.CASCADE)
    hashtags = models.ManyToManyField(TweetHashTag)
    created_at = models.DateTimeField()
    favorite_count = models.IntegerField()
    retweet_count = models.IntegerField()

    def __str__(self):
        return self.str_id


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

    image_tag.short_description = 'Image'
    image_tag.allow_tags = True

    def __str__(self):
        return self.id_str

    class Meta:
        verbose_name = 'Imagen de tweet'
        verbose_name_plural = 'Imágenes de tweet'
        ordering = ['tweet']
