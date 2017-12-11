# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from health_administration_structure_app.models import *
from public_administration_structure_app.models import *


class CHW(models.Model):
    '''In this model, we will store community health workers'''
    sub_colline = models.ForeignKey(SousColline)
    cds = models.ForeignKey(CDS)
    phone_number = models.CharField(max_length=20)
    supervisor_phone_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    reg_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.phone_number

    class Meta:
        ordering = ('phone_number',)


class Mother(models.Model):
    ''' In this model, we will store mothers properties '''
    id_mother = models.CharField(unique=True, max_length=10)
    phone_number = models.CharField(max_length=20, blank=True)
    is_affected_somewhere = models.BooleanField(default=True)

    def __unicode__(self):
        return "{0} - {1}".format(self.id_mother, self.phone_number)


class Report(models.Model):
    ''' In this model, we will store all reports '''
    chw = models.ForeignKey(CHW)
    sub_hill = models.ForeignKey(SousColline)
    cds = models.ForeignKey(CDS)
    mother = models.ForeignKey(Mother)
    reporting_date = models.DateField()
    text = models.CharField(max_length=200)
    category = models.CharField(max_length=100)

    def __unicode__(self):
        return self.text

    class Meta:
        ordering = ('reporting_date',)


class RiskLevel(models.Model):
    ''' In this model will be stored risk levels '''
    risk_designation = models.CharField(max_length=10)
    risk_level_meaning = models.CharField(max_length=50)

    def __unicode__(self):
        return "{0} - {1}".format(self.risk_designation, self.risk_level_meaning)


class Lieu(models.Model):
    ''' In this model will be stored categories of locations '''
    location_category_designation = models.CharField(max_length=10)
    location_category_description = models.CharField(max_length=50)

    def __unicode__(self):
        return "{0}".format(self.location_category_description)


class CPN(models.Model):
    ''' `In this model will be stored CPN categories '''
    cpn_number = models.IntegerField(unique=True)
    cpn_designation = models.CharField(max_length=10)
    cpn_description = models.CharField(max_length=50)

    def __unicode__(self):
        return "{0} - {1} - {2}".format(self.cpn_number, self.cpn_designation, self.cpn_description)


class BreastFeed(models.Model):
    ''' In this model will be stored breastfeed options based on the time the child have been breast-feeded after his/her born '''
    breast_feed_option_name = models.CharField(max_length=10)
    breast_feed_option_description = models.CharField(max_length=50)

    def __unicode__(self):
        return "{0} - {1}".format(self.breast_feed_option_name, self.breast_feed_option_description)


class CON(models.Model):
    ''' In this model will be stored CON (soins postnatals) categories '''
    con_designation = models.CharField(max_length=10)
    con_description = models.CharField(max_length=50)

    def __unicode__(self):
        return "{0} - {1}".format(self.con_designation, self.con_description)


class ChildNumber(models.Model):
    ''' In this model will be stored codes which will be used to number children '''
    child_code_designation = models.CharField(max_length=10)
    child_code_meaning = models.CharField(max_length=50)
    child_number = models.IntegerField(default=1)

    def __unicode__(self):
        return "{0}".format(self.child_number)


class Gender(models.Model):
    ''' In  this model will be stored gender codes '''
    gender_code = models.CharField(max_length=10)
    gender_code_meaning = models.CharField(max_length=50)

    def __unicode__(self):
        return "{0} - {1}".format(self.gender_code, self.gender_code_meaning)


class VAC(models.Model):
    ''' In this model will be stored VAC (suivi de l enfant) desigantions '''
    vac_designation = models.CharField(max_length=10)
    vac_code_meaning = models.CharField(max_length=50)

    def __unicode__(self):
        return "{0} - {1}".format(self.vac_designation, self.vac_code_meaning)


class Symptom(models.Model):
    ''' In this model will be stored symptom designations '''
    symtom_designation = models.CharField(max_length=50)
    symtom_code_meaning = models.CharField(max_length=50)
    kirundi_name = models.CharField(max_length=50, default="")
    is_red_symptom = models.BooleanField(default=False)

    def __unicode__(self):
        return "{0} - {1}".format(self.symtom_designation, self.symtom_code_meaning)


class DeathCode(models.Model):
    ''' In this model we will put "Les codes de deces" '''
    Death_code = models.CharField(max_length=10)
    Death_code_meaning = models.CharField(max_length=50)

    def __unicode__(self):
        return "{0} - {1}".format(self.Death_code, self.Death_code_meaning)


class HealthStatus(models.Model):
    '''In this model will be stored health state designations'''
    health_status_desigantion = models.CharField(max_length=10)
    health_status_code_meaning = models.CharField(max_length=50)

    def __unicode__(self):
        return "{0} - {1}".format(self.health_status_desigantion, self.health_status_code_meaning)


class Rescue(models.Model):
    '''In ths model will be stored rescue designations'''
    rescue_designation = models.CharField(max_length=50)

    def __unicode__(self):
        return self.rescue_designation


class ReportGRO(models.Model):
    ''' In this model will be stored pregnancy confirmation reports '''
    report = models.ForeignKey(Report)
    expected_delivery_date = models.DateField()
    next_appointment_date = models.DateField()
    risk_level = models.ForeignKey(RiskLevel)
    consultation_location = models.ForeignKey(Lieu)

    def __unicode__(self):
        return self.report.text


class ReportCPN(models.Model):
    ''' In this model will be stored CPN (consultation prenatale) reports '''
    report = models.ForeignKey(Report)
    concerned_cpn = models.ForeignKey(CPN)
    consultation_date = models.DateField()
    consultation_location = models.ForeignKey(Lieu)
    mother_weight = models.FloatField()
    next_appointment_date = models.DateField()

    def __unicode__(self):
        return self.report.text


class ReportNSC(models.Model):
    ''' In this model will be stored NSC (rapport de naissance) reports '''
    report = models.ForeignKey(Report)
    child_number = models.ForeignKey(ChildNumber)
    birth_date = models.DateField()
    birth_location = models.ForeignKey(Lieu)
    gender = models.ForeignKey(Gender)
    weight = models.FloatField()
    next_appointment_date = models.DateField()
    breast_feading = models.ForeignKey(BreastFeed)

    def __unicode__(self):
        return self.report.text


class ReportCON(models.Model):
    ''' In this model will be stored CON (rapport de soins postnatals) reports '''
    report = models.ForeignKey(Report)
    child = models.ForeignKey(ReportNSC)
    con = models.ForeignKey(CON)
    child_health_state = models.ForeignKey(HealthStatus, related_name='child_state')
    mother_health_state = models.ForeignKey(HealthStatus, related_name='mother_state')
    next_appointment_date = models.DateField()

    def __unicode__(self):
        return self.report.text


class ReportVAC(models.Model):
    ''' In this model will be stored VAC (rapport de suivi de l enfant) reports '''
    report = models.ForeignKey(Report)
    child = models.ForeignKey(ReportNSC)
    vac = models.ForeignKey(VAC)
    location = models.ForeignKey(Lieu)

    def __unicode__(self):
        return self.report.text


class ReportRIS(models.Model):
    ''' In this model will be stored RIS (Rapport de risque) reports '''
    report = models.ForeignKey(Report)

    def __unicode__(self):
        return self.report.text


class ReportRISBebe(models.Model):
    ''' In this model will be stored informations specific to child in the case of a child RIS report '''
    ris_report = models.ForeignKey(ReportRIS)
    concerned_child = models.ForeignKey(ReportNSC)

    def __unicode__(self):
        return self.ris_report.report.text


class ReportRER(models.Model):
    ''' In this model will be stored RER (Reponse du rapport de risque) reports '''
    report = models.ForeignKey(Report)
    ris = models.ForeignKey(ReportRIS)
    rescue = models.ForeignKey(Rescue)
    current_state = models.ForeignKey(HealthStatus)

    def __unicode__(self):
        return self.report.text


class ReportDEC(models.Model):
    ''' In this model will be stored DEC (Rapport de deces) reports '''
    report = models.ForeignKey(Report)
    location = models.ForeignKey(Lieu)
    death_code = models.ForeignKey(DeathCode)

    def __unicode__(self):
        return self.report.text


class ReportDECBebe(models.Model):
    ''' In this model will be stored informations specific to child in the case
     of a child death report '''
    death_report = models.ForeignKey(ReportDEC)
    concerned_child = models.ForeignKey(ReportNSC)

    def __unicode__(self):
        return self.death_report.report.text


class ReportDEP(models.Model):
    ''' In this model will be stored mother departure cases from one 
    "Sous colline" to an other '''
    report = models.ForeignKey(Report)

    def __unicode__(self):
        return self.report.text


class ReportREC(models.Model):
    ''' In this model will be stored reports about mothers (mothers from other areas) receptions. '''
    report = models.ForeignKey(Report)

    def __unicode__(self):
        return self.report.text


class CON_Report_Symptom(models.Model):
    ''' This model is for CON reports and Symptoms association '''
    con_report = models.ForeignKey(ReportCON)
    symptom = models.ForeignKey(Symptom)

    def __unicode__(self):
        return "{0} - {1}".format(self.con_report, self.symptom)


class CPN_Report_Symptom(models.Model):
    ''' This model is for CPN reports and Symptoms association '''
    cpn_report = models.ForeignKey(ReportCPN)
    symptom = models.ForeignKey(Symptom)

    def __unicode__(self):
        return "{0} - {1}".format(self.cpn_report, self.symptom)


class RIS_Report_Symptom(models.Model):
    ''' This model is for RIS reports and Symptoms association '''
    ris_report = models.ForeignKey(ReportRIS)
    symptom = models.ForeignKey(Symptom)

    def __unicode__(self):
        return "{0} - {1}".format(self.ris_report, self.symptom)


class Temporary(models.Model):
    '''
    This model will be used to temporary store a reporter who doesn't finish his self registration
    '''
    facility = models.ForeignKey(CDS)
    sub_hill = models.ForeignKey(SousColline)
    phone_number = models.CharField(max_length=20)
    supervisor_phone_number = models.CharField(max_length=20)

    def __unicode__(self):
        return self.phone_number


class NotificationType(models.Model):
    ''' This model is used to store notification categories
    '''
    code = models.CharField(max_length=20)
    description = models.CharField(max_length=100)

    def __unicode__(self):
        return "{0} - {1}".format(self.code, self.description)


class TimeMeasuringUnit(models.Model):
    '''
    This model is used to store time measuring units
    '''
    code = models.CharField(max_length=4)
    description = models.CharField(max_length=20)

    def __unicode__(self):
        return "{0} - {1}".format(self.code, self.description)


class Settings(models.Model):
    '''
    In this model we will put settings
    '''
    setting_code = models.CharField(max_length=20)
    setting_name = models.CharField(max_length=200)
    setting_value = models.CharField(max_length=100)
    time_measuring_unit = models.ForeignKey(TimeMeasuringUnit, null=True)
    # Change the above line. It should accept null. It doesn't accept null values for the moment

    def __unicode__(self):
        return "{0} - {1}".format(self.setting_name, self.setting_value)


class NotificationsForMother(models.Model):
    ''' This model is used to store notifications which are sent to mothers
    '''
    notification_type = models.ForeignKey(NotificationType)
    word_to_replace_by_the_date_in_the_message_to_send = models.CharField(max_length=50)
    message_to_send = models.CharField(max_length=160)
    time_measuring_unit = models.ForeignKey(TimeMeasuringUnit)
    time_number = models.IntegerField()

    def __unicode__(self):
        return self.message_to_send


class NotificationsForCHW(models.Model):
    ''' This model is used to store notifications which are sent to CHW
    '''
    notification_type = models.ForeignKey(NotificationType)
    word_to_replace_by_the_mother_id_in_the_message_to_send = models.CharField(max_length=50)
    word_to_replace_by_the_date_in_the_message_to_send = models.CharField(max_length=50)
    message_to_send = models.CharField(max_length=160)
    time_measuring_unit = models.ForeignKey(TimeMeasuringUnit)
    time_number = models.IntegerField()

    def __unicode__(self):
        return self.message_to_send


class NotificationsMother(models.Model):
    ''' This model is used to link notifications to mothers
    '''
    mother = models.ForeignKey(Mother)
    notification = models.ForeignKey(NotificationsForMother)
    date_time_for_sending = models.DateTimeField()
    message_to_send = models.CharField(max_length=160)
    is_sent = models.BooleanField(default=False)

    def __unicode__(self):
        return "{0} - {1}".format(self.mother, self.notification)


class NotificationsCHW(models.Model):
    ''' This model is used to link notifications to CHWs
    '''
    chw = models.ForeignKey(CHW)
    notification = models.ForeignKey(NotificationsForCHW)
    date_time_for_sending = models.DateTimeField()
    message_to_send = models.CharField(max_length=160)
    is_sent = models.BooleanField(default=False)

    def __unicode__(self):
        return "{0} - {1}".format(self.chw, self.notification)


class AllSupervisor(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    is_national_supervisor = models.BooleanField(default=False)

    def __unicode__(self):
        return "{0} {1} {2} {3}".format(self.first_name, self.last_name, self.phone_number, self.is_national_supervisor)


class ProvinceSupervisor(models.Model):
    province = models.ForeignKey(Province)
    supervisor = models.ForeignKey(AllSupervisor)

    def __unicode__(self):
        return "{0} {1} Supervise {2}".format(self.supervisor.first_name, self.supervisor.last_name, self.province.name)



class DistrictSupervisor(models.Model):
    district = models.ForeignKey(District)
    supervisor = models.ForeignKey(AllSupervisor)

    def __unicode__(self):
        return "{0} {1} Supervise {2}".format(self.supervisor.first_name, self.supervisor.last_name, self.district.name)
