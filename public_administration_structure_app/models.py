from __future__ import unicode_literals

from django.db import models

class Province(models.Model):
    '''In this model, we will store burundi provinces'''
    name = models.CharField(_('name'),unique=True, max_length=20)
    code = models.IntegerField(unique=True, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        # return reverse('province_detail', kwargs={'pk': self.id})
        return self.id

    class Meta:
        ordering = ('name',)

class Commune(models.Model):
    '''In this model, we will store burundi communes'''
    province = models.ForeignKey(Province)
    name = models.CharField(_('name'),unique=True, max_length=20)
    code = models.IntegerField(unique=True, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        # return reverse('province_detail', kwargs={'pk': self.id})
        return self.id

    class Meta:
        ordering = ('name',)

class Colline(models.Model):
    '''In this model, we will store burundi colline'''
    commune = models.ForeignKey(Commune)
    name = models.CharField(_('name'), max_length=30)
    code = models.IntegerField(unique=True, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        # return reverse('province_detail', kwargs={'pk': self.id})
        return self.id

    class Meta:
        ordering = ('name',)

class SousColline(models.Model):
    '''In this model, we will store burundi sub hills'''
    colline = models.ForeignKey(Colline)
    name = models.CharField(_('name'), max_length=30)
    code = models.IntegerField(unique=True, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        # return reverse('province_detail', kwargs={'pk': self.id})
        return self.id

    class Meta:
        ordering = ('name',)
