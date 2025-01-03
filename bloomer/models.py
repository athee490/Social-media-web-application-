
from django.db import models
from django.contrib.auth.models import  Group, Permission

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings

# Custom User Model
class User(AbstractUser):
     # Retain default fields but fix related_name conflicts
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # Change this to a unique related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",  # Change this to a unique related_name
        blank=True
    )
    """
    Custom User model with followers and following relationships.
    """
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='following',
        blank=True
    )

    def __str__(self):
        return self.username

# Post Model
class Post(models.Model):
    """
    Represents a post in the social media feed.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    image = models.ImageField(upload_to='myproject/images/')
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='liked_posts', 
        blank=True
    )

    def like_count(self):
        return self.likes.count()

    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at}"

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    pic = models.ImageField(upload_to='myproject/profiles/')

    def _str_(self):
        return self.user.username


class Steps(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='steps')
    monday = models.PositiveIntegerField(default=0)
    tuesday = models.PositiveIntegerField(default=0)
    wednesday = models.PositiveIntegerField(default=0)
    thursday = models.PositiveIntegerField(default=0)
    friday = models.PositiveIntegerField(default=0)
    saturday = models.PositiveIntegerField(default=0)
    sunday = models.PositiveIntegerField(default=0)

    def total_steps(self):
        """Return total steps for the week."""
        return (
            self.monday + self.tuesday + self.wednesday + 
            self.thursday + self.friday + self.saturday + 
            self.sunday
        )

    def _str_(self):
        return f"{self.user.username} - Total Steps: {self.total_steps()}"

