from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

class Petition(models.Model):
    title = models.CharField(max_length=200, help_text="Title of the movie being petitioned")
    description = models.TextField(help_text="Why should this movie be added?")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='petitions')
    created_at = models.DateTimeField(auto_now_add=True)
    votes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='voted_petitions', blank=True)
    vote_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} (by {self.user.username})"

    def save(self, *args, **kwargs):
        # Update vote_count to match the actual number of votes
        if self.pk:
            self.vote_count = self.votes.count()
        super().save(*args, **kwargs)

    def total_votes(self):
        return self.vote_count

    def has_voted(self, user):
        return self.votes.filter(id=user.id).exists()
