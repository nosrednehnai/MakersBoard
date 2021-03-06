from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save
from phonenumber_field.modelfields import PhoneNumberField


def upload_location(instance, filename):
    return '%s/%s' % (instance.username, filename)


class UserProfile(AbstractUser):
    USERNAME_FIELD = 'username'
    phone_number = PhoneNumberField()
    slug = models.SlugField(unique=True)
    profile_picture = models.ImageField(
        upload_to=upload_location,
        null=True,
        blank=True,
        width_field=None,   # 'height_field',
        height_field=None,  # 'width_field'
    )
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    full_name = models.CharField(max_length=150)
    location = models.CharField(max_length=150)
    bio = models.TextField()

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'slug': self.slug})

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)


def create_slug(instance, new_slug=None):
    slug = instance.username
    if new_slug is not None:
        slug = new_slug
    qs = UserProfile.objects.filter(slug=slug).order_by('username')
    exists = qs.exists()
    if exists:
        new_slug = '%s-%s' % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(pre_save_post_receiver, sender=UserProfile)
