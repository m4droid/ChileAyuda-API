# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Region(models.Model):
    name = models.CharField(max_length=64)
    iso_3166_2 = models.CharField(max_length=5)

    def __unicode__(self):
        return '{0:d} - {1:s}'.format(self.pk, self.name)

    class Meta:
        ordering = ['pk']


class Province(models.Model):
    name = models.CharField(max_length=64)
    region = models.ForeignKey(Region)

    def __unicode__(self):
        return '{0:s} - {1:s}'.format(self.region.name, self.name)


class Commune(models.Model):
    name = models.CharField(max_length=64)
    province = models.ForeignKey(Province)

    def __unicode__(self):
        return '{0:s} - {1:s} - {2:s}'.format(
            self.province.region.name,
            self.province.name,
            self.name
        )


class Coordinates(models.Model):
    latitude = models.DecimalField(max_digits=9, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)

    def __unicode__(self):
        return '{0:f}, {1:f}'.format(self.latitude, self.longitude)


class Disaster(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()

    user = models.ForeignKey(User)
    date = models.DateTimeField()

    commune = models.ForeignKey(Commune)
    coordinates = models.ForeignKey(Coordinates)

    def __unicode__(self):
        return self.name


class Style(models.Model):
    name = models.CharField(max_length=64)
    color = models.CharField(max_length=7)

    def __unicode__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=64)
    parent = models.ForeignKey(
        'self',
        related_name='children',
        blank=True,
        null=True
    )

    style = models.ForeignKey(Style)

    def __unicode__(self):
        return self.name


class MediaSource(models.Model):
    name = models.CharField(max_length=32)

    def __unicode__(self):
        return '{0:s}'.format(self.name)


class Incident(models.Model):
    disaster = models.ForeignKey(Disaster)
    category = models.ManyToManyField(Category)

    name = models.CharField(max_length=64)
    description = models.TextField()
    date = models.DateTimeField()

    user = models.ForeignKey(User)

    commune = models.ForeignKey(Commune)
    coordinates = models.ForeignKey(Coordinates)

    def __unicode__(self):
        return '{0:s} - {1:s}'.format(self.disaster.name, self.name)

    def validate(self, user, text):
        if user is None:
            return False
        validation = IncidentValidation(
            incident=self,
            user=user,
            text=text,
            date=timezone.now()
        )
        validation.save()
        return True

    def set_details(self, user, details):
        if user is None or details is None or len(details.keys()) == 0:
            return
        details = IncidentDetail(**details)
        details.incident = self
        details.save()

    def rate(self, user, value):
        if user is None \
                or not isinstance(value, (int, long)) or value not in [1, -1]:
            return
        rating = IncidentRating(
            incident=self,
            user=user,
            date=timezone.now(),
            value=value
        )
        rating.save()

    def add_comment(self, user, text):
        if user is None or text is None or text.strip() == '':
            return
        media = IncidentComment(
            incident=self,
            user=user,
            text=text,
            date=timezone.now()
        )
        media.save()

    def add_media(self, user, source, url):
        if user is None or source is None or url is None or url.strip() == '':
            return
        media = IncidentMedia(
            incident=self,
            user=user,
            source=source,
            url=url,
            date=timezone.now()
        )
        media.save()


class IncidentValidation(models.Model):
    incident = models.OneToOneField(Incident)

    user = models.ForeignKey(User)
    date = models.DateTimeField()
    text = models.TextField(blank=True, null=True)


class IncidentDetail(models.Model):
    incident = models.OneToOneField(Incident)

    missing_people = models.IntegerField(blank=True, null=True)
    injured_people = models.IntegerField(blank=True, null=True)
    deceased_people = models.IntegerField(blank=True, null=True)

    damaged_buildings = models.IntegerField(blank=True, null=True)
    damaged_vehicles = models.IntegerField(blank=True, null=True)


class IncidentRating(models.Model):
    incident = models.ForeignKey(Incident)

    user = models.ForeignKey(User)
    date = models.DateTimeField()

    value = models.IntegerField()


class IncidentComment(models.Model):
    incident = models.ForeignKey(Incident)

    user = models.ForeignKey(User)
    date = models.DateTimeField()

    text = models.TextField()


class IncidentMedia(models.Model):
    incident = models.ForeignKey(Incident)

    user = models.ForeignKey(User)

    source = models.ForeignKey(MediaSource)
    url = models.CharField(max_length=2000)
    date = models.DateTimeField()
