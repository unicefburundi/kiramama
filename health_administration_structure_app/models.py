from __future__ import unicode_literals
from django.db import models


class BPS(models.Model):
    '''In this model, we will store Burundi BPSs(Bureau provincial de la sante)'''
    name = models.CharField(('name'), unique=True, max_length=20)
    code = models.IntegerField(unique=True, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        # return reverse('province_detail', kwargs={'pk': self.id})
        return self.id

    class Meta:
        ordering = ('name',)


class District(models.Model):
    '''In this model, we will store districts'''
    bps = models.ForeignKey(BPS, verbose_name='BPS')
    name = models.CharField(('nom'), unique=True, max_length=40)
    code = models.IntegerField(unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class CDS(models.Model):
    STATUS_CHOICES = (
        ('Pub', 'Public'),
        ('Con', 'Conf'),
        ('Priv', 'Prive'),
        ('Ass', 'Ass'),
        ('HPub', 'HPublic'),
        ('HCon', 'HConf'),
        ('HPrv', 'HPrive'),
    )
    district = models.ForeignKey(District)
    name = models.CharField(max_length=40)
    code = models.CharField(unique=True, max_length=6)
    status = models.CharField(max_length=4, choices=STATUS_CHOICES, blank=True, null=True, help_text=('Either Public, Conf, Ass, Prive  or Hospital status.'))

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
