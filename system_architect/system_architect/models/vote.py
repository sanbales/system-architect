#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from logging import getLogger
from .core import CoreModel
from .core import WeightLevel
from .relationship import Relationship


__all__ = ('Vote',)


logger = getLogger(__name__)


class Organization(CoreModel):
    # TODO: Complete this model
    pass


class ExpertProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        max_length=128,
        blank=True,
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='personnel',
    )
    phone = models.CharField(
        max_length=32,
    )

    def __str__(self):
        return str(self.user)


@receiver(models.signals.post_save, sender=User)
def create_expert_profile(sender, instance, created, **kwargs):
    if created:
        ExpertProfile.objects.create(user=instance)


@receiver(models.signals.post_save, sender=User)
def save_expert_profile(sender, instance, **kwargs):
    instance.expertprofile.save()


class Vote(models.Model):
    CONFIDENCE_LEVELS = (
        (0, 'High'),
        (1, 'Moderate'),
        (2, 'Low'),
    )
    relationship = models.ForeignKey(
        Relationship,
        on_delete=models.CASCADE,
    )
    expert = models.ForeignKey(
        ExpertProfile,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="The subject matter expert that provided this input.",
    )
    comments = models.TextField(
        blank=True,
        help_text="Notes the user can use to explain their vote.",
    )
    value = models.ForeignKey(
        WeightLevel,
        on_delete=models.CASCADE,
        help_text="The value of the vote.",
    )
    cast_on = models.DateTimeField(
        auto_now=True,
        help_text="When this vote was cast",
    )
    confidence = models.PositiveSmallIntegerField(
        choices=CONFIDENCE_LEVELS,
        default=0,
        help_text="The confidence the SME has on their vote.",
    )

    class Meta:
        if hasattr(models, 'Index'):
            indexes = [
                models.Index(fields=['relationship',
                                     'expert',
                                     '-cast_on']),
            ]
