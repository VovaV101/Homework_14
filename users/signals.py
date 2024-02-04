from pathlib import Path
from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.conf import settings

from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        try:
            Profile.objects.create(user=instance)
        except:
            ...

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except:
        ...

@receiver(pre_delete, sender=User)
def delete_avatar(sender, instance, **kwargs):
    try:
        avatar = instance.profile.avatar
        # mroot = settings.MEDIA_ROOT
        field = Profile._meta.get_field('avatar')
        default_value = field.get_default()
        print("**********  delete_avatar", avatar.name, avatar.path, default_value)
        if avatar.name != default_value:
            avatar.delete(save=False)
    except:
        ...

