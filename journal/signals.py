from django.db.models.signals import post_save
from django.dispatch import receiver

from . models import Post


@receiver(post_save, sender=Post)
def set_file_extension(sender, instance, created, **kwargs):

        try:
            url = instance.mediaImage.url
            extension = url.split('.')[-1]

            if extension in ('mp4', 'avi', 'mpeg', 'webm'):
                instance.file_extension = 'video'
            elif extension in ('png', 'jpeg', 'jpg'):
                instance.file_extension = 'image'
        except Exception as e:
            print(e)

