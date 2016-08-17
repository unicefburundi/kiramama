from __future__ import unicode_literals

from django.db import models

from health_administration_structure_app.models import CDS
from public_administration_structure_app.models import SousColline


class CHW(models.Model):
	'''In this model, we will store community health workers'''
	sub_colline = models.ForeignKey(SousColline)
	cds = models.ForeignKey(CDS)
	phone_number = models.CharField(max_length=20)
	supervisor_phone_number = models.CharField(max_length=20)
	
	def __unicode__(self):
		return self.phone_number

	class Meta:
		ordering = ('phone_number',)

class Mother(models.Model):
	''' In this model, we will store mothers properties '''
	id_mother = models.CharField(unique=True, max_length=10)
	phone_number = models.CharField(max_length=20, blank=True)

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
		return "{0} - {1}".format(self.location_category_designation, self.location_category_description)

class CPN(models.Model):
	''' `In this model will be stored CPN categories '''
	cpn_designation = models.CharField(max_length=10)
	cpn_description = models.CharField(max_length=50)

	def __unicode__(self):
		return "{0} - {1}".format(self.cpn_designation, self.cpn_description)

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

	def __unicode__(self):
		return "{0} - {1}".format(self.child_code_designation, self.child_code_meaning)

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

	def __unicode__(self):
		return "{0} - {1}".format(self.symtom_designation, self.symtom_code_meaning)

class DeathCode(models.Model):
	''' In this model we will put "Les codes de deces" '''
	Death_code = models.CharField(max_length=10)
	Death_code_meaning = models.CharField(max_length=50)

	def __unicode__(self):
		return "{0} - {1}".format(self.Death_code, self.Death_code_meaning)

class HealthState(models.Model):
	'''In this model will be stored health state designations'''
	health_state_desigantion = models.CharField(max_length=10)
	health_state_code_meaning = models.CharField(max_length=50)

	def __unicode__(self):
		return "{0} - {1}".format(self.health_state_desigantion, self.health_state_code_meaning)

class Rescue(models.Model):
	'''In ths model will be stored rescue designations'''
	rescue_designation = models.CharField(max_length=50)

	def __unicode__(self):
		return self.location_category_designation

class ReportGRO(models.Model):
	''' In this model will be stored pregnancy confirmation reports '''
	report = models.ForeignKey(Report)
	expected_delivery_date = models.DateField()
	next_appointment_date = models.DateField()
	risk_level = models.ForeignKey(RiskLevel)
	consultation_location = models.ForeignKey(Lieu)

	def __unicode__(self):
		return self.location_category_designation

class ReportCPN(models.Model):
	''' In this model will be stored CPN (consultation prenatale) reports '''
	report = models.ForeignKey(Report)
	concerned_cpn = models.ForeignKey(CPN)
	consultation_date = models.DateField()
	consultation_location = models.ForeignKey(Lieu)
	mother_weight = models.FloatField()
	next_appointment_date = models.DateField()

	def __unicode__(self):
		return self.report

class ReportNSC(models.Model):
	''' In this model will be stored NSC (rapport de naissance) reports '''
	report = models.ForeignKey(Report)
	child_number = models.CharField(max_length=10)
	birth_date = models.DateField()
	birth_location = models.ForeignKey(Lieu)
	gender = models.CharField(max_length=10)
	weight = models.FloatField()
	next_appointment_date = models.DateField()
	breast_feading = models.CharField(max_length=10)

	def __unicode__(self):
		return self.report

class ReportCON(models.Model):
	''' In this model will be stored CON (rapport de soins postnatals) reports '''
	report = models.ForeignKey(Report)
	child = models.ForeignKey(ReportNSC)
	con = models.ForeignKey(CON)
	child_health_state = models.ForeignKey(HealthState, related_name='child_state')
	mother_health_state = models.ForeignKey(HealthState, related_name='mother_state')
	next_appointment_date = models.DateField()

	def __unicode__(self):
		return self.report

class ReportVAC(models.Model):
	''' In this model will be stored VAC (rapport de suivi de l enfant) reports '''
	report = models.ForeignKey(Report)
	child = models.ForeignKey(ReportNSC)
	vac = models.ForeignKey(VAC)
	location = models.ForeignKey(Lieu)

	def __unicode__(self):
		return self.report

class ReportRIS(models.Model):
	''' In this model will be stored RIS (Rapport de risque) reports '''
	report = models.ForeignKey(Report)

	def __unicode__(self):
		return self.report

class ReportRISBebe(models.Model):
	''' In this model will be stored informations specific to child in the case of a child RIS report '''
	ris_report = models.ForeignKey(ReportRIS)
	concerned_child = models.ForeignKey(ReportNSC)

	def __unicode__(self):
		return self.concerned_child

class ReportRER(models.Model):
	''' In this model will be stored RER (Reponse du rapport de risque) reports '''
	report = models.ForeignKey(Report)
	ris = models.ForeignKey(ReportRIS)
	rescue = models.ForeignKey(Rescue)
	current_state = models.ForeignKey(HealthState)
	
	def __unicode__(self):
		return self.report

class ReportDEC(models.Model):
	''' In this model will be stored DEC (Rapport de deces) reports '''
	report = models.ForeignKey(Report)
	location = models.ForeignKey(Lieu)
	death_code = models.ForeignKey(DeathCode)

	def __unicode__(self):
		return self.report

class ReportDECBebe(models.Model):
	''' In this model will be stored informations specific to child in the case of a child death report '''
	death_report = models.ForeignKey(ReportDEC)
	concerned_child = models.ForeignKey(ReportNSC)

	def __unicode__(self):
		return self.death_report

class ReportDEP(models.Model):
	''' In this model will be stored mother departure cases from one "Sous colline" to an other '''
	report = models.ForeignKey(Report)

	def __unicode__(self):
		return self.report

class CONSymptom(models.Model):
	''' In this model will be stored all options of CON symptoms '''
	con_symptom_code = models.CharField(max_length=10)
	con_symptom_code_meaning = models.CharField(max_length=50)

	def __unicode__(self):
		return "{0} - {1}".format(self.con_symptom_code, self.con_symptom_code_meaning)

class RISSymptom(models.Model):
	''' In this model will be stored all options of RIS symptoms '''
	ris_symptom_code = models.CharField(max_length=10)
	ris_symptom_code_meaning = models.CharField(max_length=50)

	def __unicode__(self):
		return "{0} - {1}".format(self.ris_symptom_code, self.ris_symptom_code_meaning)

class CON_Report_Symptom(models.Model):
	''' This model is for CON reports and Symptoms association '''
	con_report = models.ForeignKey(ReportCON)
	symptom = models.ForeignKey(CONSymptom)

	def __unicode__(self):
		return "{0} - {1}".format(self.con_report, self.symptom)

class RIS_Report_Symptom(models.Model):
	''' This model is for RIS reports and Symptoms association '''
	ris_report = models.ForeignKey(ReportRIS)
	symptom = models.ForeignKey(RISSymptom)

	def __unicode__(self):
		return "{0} - {1}".format(self.ris_report, self.symptom)
