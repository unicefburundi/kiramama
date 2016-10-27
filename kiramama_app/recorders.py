from kiramama_app.models import *
from health_administration_structure_app.models import *
from public_administration_structure_app.models import *

from django.db.models import Q
import re
import datetime
import requests
import json
from django.conf import settings


def check_supervisor_phone_number_not_for_this_contact(args):
	'''This function checks if the contact didn't send his/her phone number in the place of the supervisor phone number'''

	if args['text'].split(' ')[4] in args['phone']:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Vous avez envoye votre numero de telephone a la place de celui de votre superviseur. Pour corriger, veuillez reenvoyer le message commencant par '"+args['mot_cle']+"' et contenant le vrai numero de ton superviseur"
	else:
		args['valide'] = True
		args['info_to_contact'] = "Le numero de telephone du superviseur est bien note."

def check_if_is_reporter(args):
	''' This function checks if the contact who sent the current message is a reporter. Reporter is CHW '''
	concerned_reporter = CHW.objects.filter(phone_number = args['phone'])
	if len(concerned_reporter) < 1:
		#This person is not in the list of reporters
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Vous ne vous etes pas enregistre pour pouvoir donner des rapports. Veuillez vous enregistrer en envoyant le message d enregistrement commencant par REG"
		return 

	one_concerned_reporter = concerned_reporter[0]

	if not one_concerned_reporter.cds:
		#The CDS of this reporter is not known
		args['valide'] = False
		args['info_to_contact'] = "Exception. Votre site n est pas enregistre dans le systeme. Veuillez contacter l administrateur du systeme"
		return

	args['the_sender'] =  one_concerned_reporter
	args['facility'] = one_concerned_reporter.cds
	args['supervisor_phone_number'] = one_concerned_reporter.supervisor_phone_number
	args['valide'] = True
	args['info_to_contact'] = " Le bureau d affectation de ce rapporteur est connu "



'''
def check_number_of_values(args):
	#This function checks if the message sent is composed by an expected number of values
	print("==len(args['text'].split(' '))==")
	print(len(args['text'].split(' ')))
	print(args['text'].split(' '))


	if(args['message_type']=='SELF_REGISTRATION' or args['message_type']=='SELF_REGISTRATION_M'):
		if len(args['text'].split(' ')) < 5:
			args['valide'] = False
			args['info_to_contact'] = "Erreur. Vous avez envoye peu de valeurs. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
		if len(args['text'].split(' ')) > 5:
			args['valide'] = False
			args['info_to_contact'] = "Erreur. Vous avez envoye beaucoup de valeurs. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
		if len(args['text'].split(' ')) == 5:
			args['valide'] = True
			args['info_to_contact'] = "Le nombre de valeurs envoye est correct."
		return
'''
def check_number_of_values(args):
	''' This function checks if the message sent is composed by an expected number of values '''
	expected_number_of_values_string = args["expected_number_of_values"]
	expected_number_of_values_int = int(expected_number_of_values_string)

	if len(args['text'].split(' ')) < expected_number_of_values_int:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Vous avez envoye peu de valeurs. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	if len(args['text'].split(' ')) > expected_number_of_values_int:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Vous avez envoye beaucoup de valeurs. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	if len(args['text'].split(' ')) == expected_number_of_values_int:
		args['valide'] = True
		args['info_to_contact'] = "Le nombre de valeurs envoye est correct."


def check_number_of_values_ris(args):
	''' This function checks if the RIS report sent is composed by an expected number of values '''

	#I have to change how the two below variables are initiated. Values must be taken from settings.py
	number_of_values_for_a_child = 4
	number_of_values_for_a_woman = 3

	if((len(args['text'].split(' ')) != number_of_values_for_a_child) and (len(args['text'].split(' ')) != number_of_values_for_a_woman) ):
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Le nombre de valeurs envoye n est pas correct. Il doit etre '"+str(number_of_values_for_a_child)+"' (pour un enfant) ou '"+str(number_of_values_for_a_woman)+"' (pour une maman). Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	if(len(args['text'].split(' ')) == number_of_values_for_a_child):
		#This contact is sending a RIS report for a child
		args['valide'] = True
		args['ris_type'] = "RIS_CHILD"
		args['info_to_contact'] = "Le rapport envoye concerne un enfant"
	if(len(args['text'].split(' ')) == number_of_values_for_a_woman):
		#This contact is sending a RIS report for a woman
		args['valide'] = True
		args['ris_type'] = "RIS_WOMAN"
		args['info_to_contact'] = "Le rapport envoye concerne une maman"


def check_number_of_values_dec(args):
	''' This function checks if the DEC report sent is composed by an expected number of values '''

	#I have to change how the two below variables are initiated. Values must be taken from settings.py
	number_of_values_for_a_child = 5
	number_of_values_for_a_woman = 4
	
	if((len(args['text'].split(' ')) != number_of_values_for_a_child) and (len(args['text'].split(' ')) != number_of_values_for_a_woman) ):
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Le nombre de valeurs envoye n est pas correct. Il doit etre '"+str(number_of_values_for_a_child)+"' (pour un enfant) ou '"+str(number_of_values_for_a_woman)+"' (pour une maman). Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	if(len(args['text'].split(' ')) == number_of_values_for_a_child):
		#This contact is sending a DEC report for a child
		args['valide'] = True
		args['dec_type'] = "DEC_CHILD"
		args['info_to_contact'] = "Le rapport envoye concerne un enfant"
	if(len(args['text'].split(' ')) == number_of_values_for_a_woman):
		#This contact is sending a DEC report for a woman
		args['valide'] = True
		args['dec_type'] = "DEC_WOMAN"
		args['info_to_contact'] = "Le rapport envoye concerne une maman"

def check_is_future_date(args):
	''' This function checks if a given date is a future date '''
	given_date = args["future_date"]
	if not given_date:
		args['valide'] = False
		args['info_to_contact'] = "Exception. Pas de date trouvee pour la verification."
		return

	expression = r'^((0[1-9])|([1-2][0-9])|(3[01]))((0[1-9])|(1[0-2]))[0-9]{2}$'
	if re.search(expression, given_date) is None:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La date indiquee pour '"+args["date_meaning"]+"' n est pas valide. Verifier si vous avez mis chaque valeur dans sa place. Pour corriger, veuillez reenvoyer un message commencant par "+args['mot_cle']
		return


	sent_date = given_date[0:2]+"-"+given_date[2:4]+"-20"+given_date[4:]

	sent_date_without_dash = sent_date.replace("-","")
	try:
		date_sent = datetime.datetime.strptime(sent_date_without_dash, "%d%m%Y").date()
	except:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La date indiquee pour '"+args["date_meaning"]+"' n est pas valide. Verifier si vous avez mis chaque valeur dans sa place. Pour corriger, veuillez reenvoyer un message commencant par "+args['mot_cle']
		return


	if date_sent <= datetime.datetime.now().date():
		#The reporter can not report for a past date
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Vous n avez pas indiquez une date du futur pour '"+args["date_meaning"]+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
		return
	args['date_well_written'] = date_sent
	args['valide'] = True
	args['info_to_contact'] = "La date verifiee est dans le futur"


def check_is_past_date(args):
	''' This function checks if a given date is a past date '''
	given_date = args["past_date"]
	if not given_date:
		args['valide'] = False
		args['info_to_contact'] = "Exception. Pas de date trouvee pour la verification."
		return

	expression = r'^((0[1-9])|([1-2][0-9])|(3[01]))((0[1-9])|(1[0-2]))[0-9]{2}$'
	if re.search(expression, given_date) is None:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La date indiquee pour '"+args["date_meaning"]+"' n est pas valide. Verifier si vous avez mis chaque valeur dans sa place. Pour corriger, veuillez reenvoyer un message commencant par "+args['mot_cle']
		return


	sent_date = given_date[0:2]+"-"+given_date[2:4]+"-20"+given_date[4:]

	sent_date_without_dash = sent_date.replace("-","")
	try:
		date_sent = datetime.datetime.strptime(sent_date_without_dash, "%d%m%Y").date()
	except:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La date indiquee pour '"+args["date_meaning"]+"' n est pas valide. Verifier si vous avez mis chaque valeur dans sa place. Pour corriger, veuillez reenvoyer un message commencant par "+args['mot_cle']
		return


	if date_sent > datetime.datetime.now().date():
		#The reporter can not report for a past date
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Vous avez indiquez une date non acceptable pour '"+args["date_meaning"]+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
		return
	args['date_well_written'] = date_sent
	args['valide'] = True
	args['info_to_contact'] = "La date verifiee est dans le passe"



def check_date_is_previous_or_today(args):
	''' This function checks if a given date is for previous days or today '''
	given_date = args["previous_days_or_today_date"]
	if not given_date:
		args['valide'] = False
		args['info_to_contact'] = "Exception. Pas de date trouvee pour la verification."
		return

	expression = r'^((0[1-9])|([1-2][0-9])|(3[01]))((0[1-9])|(1[0-2]))[0-9]{2}$'
	if re.search(expression, given_date) is None:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La date indiquee pour '"+args["date_meaning"]+"' n est pas valide. Verifier si vous avez mis chaque valeur dans sa place. Pour corriger, veuillez reenvoyer un message commencant par "+args['mot_cle']
		return


	sent_date = given_date[0:2]+"-"+given_date[2:4]+"-20"+given_date[4:]

	sent_date_without_dash = sent_date.replace("-","")
	try:
		date_sent = datetime.datetime.strptime(sent_date_without_dash, "%d%m%Y").date()
	except:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La date indiquee pour '"+args["date_meaning"]+"' n est pas valide. Verifier si vous avez mis chaque valeur dans sa place. Pour corriger, veuillez reenvoyer un message commencant par "+args['mot_cle']
		return


	if date_sent > datetime.datetime.now().date():
		#The reporter can not report for a past date
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Vous avez indiquez une date qui n est pas encore arrivee pour '"+args["date_meaning"]+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
		return
	args['date_well_written'] = date_sent
	args['valide'] = True
	args['info_to_contact'] = "La date verifiee est dans le passe"



def check_risk_level(args):
	''' This function checks if a risk level specified is valid '''
	sent_risk_level = args["risk_level"]
	risk_levels = RiskLevel.objects.filter(risk_designation__iexact = sent_risk_level)
	if(len(risk_levels) < 1):
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Le niveau de risque indique n est pas reconnu par le systeme. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	else:
		args["risklevel"] = risk_levels[0]
		args['valide'] = True
		args['info_to_contact'] = "Le niveau de risque indique est valide."



def check_location(args):
	''' This function checks if the location sent is valid '''
	location_to_check = args["location"]
	locations = Lieu.objects.filter(location_category_designation__iexact = location_to_check)
	if(len(locations) < 1):
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["date_meaning"]+"' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	else:
		args['location'] = locations[0]
		args['valide'] = True
		args['info_to_contact'] = "Le lieu indique est valide."

def check_death_code(args):
	''' This function checks if the death code sent is valid '''
	death_code_sent = args["death_code"]
	
	death_code_set = DeathCode.objects.filter(Death_code__iexact = death_code_sent)
	
	if(len(death_code_set) < 1):
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["death_code_meaning"]+"' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	else:
		args['death_code'] = death_code_set[0]
		args['valide'] = True
		args['info_to_contact'] = "Le code de deces indique est valide."

def check_phone_number(args):
	''' This function checks if a phone number sent is valid '''
	phone_number_to_check = args["phone_number"]
	phone_number_to_check_no_space = phone_number_to_check.replace(" ", "")
	expression = r'^(\+?(257)?)((61)|(62)|(68)|(69)|(71)|(72)|(75)|(76)|(79))([0-9]{6})$'
	if re.search(expression, phone_number_to_check_no_space) is None:
		#The phone number is not well written
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Le numero de telephone n est pas bien ecrit. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	else:
		args["phone_number"] = phone_number_to_check_no_space
		args['valide'] = True
		args['info_to_contact'] = "Le numero de telephone est bien ecrit."


def check_if_is_reporter(args):
	''' This function checks if the contact who sent the current message is a CHW '''
	concerned_chw = CHW.objects.filter(phone_number = args['phone'])
	if len(concerned_chw) < 1:
		#This person is not in the list of community health workers
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Vous ne vous etes pas enregistre pour pouvoir donner des rapports. Veuillez vous enregistrer en envoyant le message d enregistrement commencant par REG"
		return 

	one_concerned_chw = concerned_chw[0]

	if not one_concerned_chw.cds:
		#The CDS of this reporter is not known
		args['valide'] = False
		args['info_to_contact'] = "Exception. Votre site n est pas enregistre dans le systeme. Veuillez contacter l administrateur du systeme"
		return

	args['the_sender'] =  one_concerned_chw
	args['facility'] = one_concerned_chw.cds
	args['supervisor_phone_number'] = one_concerned_chw.supervisor_phone_number
	args['sub_colline'] = one_concerned_chw.sub_colline
	args['valide'] = True
	args['info_to_contact'] = "Le bureau d affectation de ce rapporteur est connu"


def check_mother_id_is_valid(args):
	''' This function checks if the mother id sent is valid '''
	the_sent_mother_id = args["sent_mother_id"]
	filtered_mother = Mother.objects.filter(id_mother = the_sent_mother_id)
	if(len(filtered_mother) < 1):
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Une maman avec cet identifiant n existe pas dans le systeme. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	else:
		args['concerned_mother'] = filtered_mother[0]
		args['valide'] = True
		args['info_to_contact'] = "L identifiant de la maman est valide"


def check_mother_has_ris_report(args):
	''' This function checks if the current mother has a RIS report recorded '''
	
	mother_set = ReportRIS.objects.filter(report__mother = args['concerned_mother'])

	if len(mother_set) < 1:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Il n y a pas de risque rapportee pour la maman '"+args['concerned_mother'].id_mother+"'"
	else:
		args['valide'] = True
		the_concerned_ris = ReportRIS.objects.filter(report__mother = args['concerned_mother']).order_by('-id')[0]
		args['the_concerned_ris'] = the_concerned_ris
		args['info_to_contact'] = "Un rapport RIS de cette maman a ete bien trouve"

def check_cpn_name_exists(args):
	''' This function checks if the CPN name sent exists in the system '''
	the_sent_cpn_name = args["sent_cpn_name"]
	filtered_cpn = CPN.objects.filter(cpn_designation__iexact = the_sent_cpn_name)
	if(len(filtered_cpn) < 1):
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Le nom du CPN indique n existe pas dans le systeme. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	else:
		args['specified_cpn'] =  filtered_cpn[0]
		args['valide'] = True
		args['info_to_contact'] = "Le nom du CPN indique existe dans le systeme"


def check_is_float(args):
	''' This function checks if a given value is a float '''

	expression = r'^([0-9]+.[0-9]+)$|^([0-9]+)$|^([0-9]+,[0-9]+)$'

	value_to_check = args["float_value"]

	if re.search(expression, value_to_check) is None:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["date_meaning"]+"' n est pas valide. Pour corriger,  veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	else:
		args['checked_float'] = value_to_check
		args['valide'] = True
		args['info_to_contact'] = "La valeur envoyee pour '"+args["date_meaning"]+"' est valide."



def check_child_code(args):
	''' This function is used to check if the child code is valid '''
	the_sent_child_code = args["child_code"]

	child_numbers = ChildNumber.objects.filter(child_code_designation = the_sent_child_code)

	if(len(child_numbers) < 1):
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Le numero de l enfant envoye n existe pas. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	else:
		args['child_number'] = child_numbers[0]
		args['valide'] = True
		args['info_to_contact'] = "Le numero de l enfant envoye est valide."


def check_allaitement_maternel(args):
	''' This function is used to check if the value sent for "Allaitement maternel" is valid '''
	
	the_sent_value = args["allaitement_maternel"]

	allaitements = BreastFeed.objects.filter(breast_feed_option_name__iexact = the_sent_value)
	if(len(allaitements) < 1):
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La valeur envoye pour 'Allaitement maternel' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	else:
		args['code_allaitement'] = allaitements[0]
		args['valide'] = True
		args['info_to_contact'] = "La valeur envoyee pour allaitement est valide"


def check_gender(args):
	''' This function is used to check if the value sent for gender is valid '''
	
	the_sent_gender = args["gender"]

	genders = Gender.objects.filter(gender_code__iexact = the_sent_gender)

	if(len(genders) < 1):
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La valeur envoyee pour le genre du nouveau nee n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	else:
		args['gender'] = genders[0]
		args['valide'] = True
		args['info_to_contact'] = "La valeur envoyee pour le genre du nouveau nee est valide"



def check_child_exists(args):
	''' This function checks if the child number sent exists and if that mother has a child with that number '''
	the_sent_child_number = args["child_id"]

	child_numbers = ChildNumber.objects.filter(child_code_designation__iexact = the_sent_child_number)
	
	if(len(child_numbers) < 1):
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Le numero de l enfant envoye n existe pas dans le systeme. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
		return
	
	child_number = child_numbers[0]

	birth_reports_with_this_mother_and_childcode = ReportNSC.objects.filter(report__mother = args['concerned_mother'], child_number = child_number)

	if(len(birth_reports_with_this_mother_and_childcode) < 1):
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La dame '"+args['concerned_mother'].id_mother+"' n a pas de naissance '"+the_sent_child_number+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	else:
		args['concerned_child'] = birth_reports_with_this_mother_and_childcode[0]
		args['child_number'] = child_number
		args['valide'] = True
		args['info_to_contact'] = "L enfant specifie a ete bien identifie"
		

def check_con_code(args):
	''' This function checks if the CON code sent is valid '''

	the_sent_con_code = args["con_code"]
	
	con_codes = CON.objects.filter(con_designation__iexact = the_sent_con_code)

	if(len(con_codes) < 1):
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La valeur envoyee pour 'CON effectuee' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	else:
		args['concerned_con'] = con_codes[0]
		args['valide'] = True
		args['info_to_contact'] = "La valeur envoyee pour 'CON effectuee' est valide" 


def check_symptoms(args):
	''' This function checks if symptoms sent are valid '''

	sent_symptoms = args["symptoms"]
	
	#Symptoms are separated by comma. Let's put them in a list.
	print("====>>>")
	print(sent_symptoms)
	sent_symptoms_list = sent_symptoms.split(",")
	print("====>>>")
	print(sent_symptoms_list)

	#Let's assume that all symbols are correct
	valid = True

	#Let's check if every element of the list is a valid symptom
	for current_symptom in sent_symptoms_list:
		if(valid == True):
			symptoms = Symptom.objects.filter(symtom_designation = current_symptom)
			if(len(symptoms) < 1):
				valid = False
				not_valid_symptom = current_symptom
				args['valide'] = False
				args['info_to_contact'] = "Erreur. Le symptome '"+not_valid_symptom+"' n existe pas dans le systeme. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']

	if(valid == True):
		#All sent symptoms are known in the system
		args['checked_symptoms_list'] = sent_symptoms_list
		args['valide'] = True
		args['info_to_contact'] = "La liste des symboles envoyes est valide"


def check_health_status(args):
	''' This function checks if the health status values are valid '''

	sent_health_status_value = args["health_status_value"]

	health_status_group = HealthStatus.objects.filter(health_status_desigantion__iexact = sent_health_status_value)

	if(len(health_status_group) < 1):
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["health_status_meaning"]+"' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	else:
		args['concerned_health_status'] = health_status_group[0]
		args['valide'] = True
		args['info_to_contact'] = "La valeur envoyee pour '"+args["health_status_meaning"]+"' est valide" 

def check_rescue_received(args):
	''' This function checks if the value sent for the rescue received is valid '''

	sent_rescue_received_value = args["rescue_received"]

	rescue_received_set = Rescue.objects.filter(rescue_designation__iexact = sent_rescue_received_value)

	if(len(rescue_received_set) < 1):
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["rescue_received_meaning"]+"' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	else:
		args['concerned_rescue_received'] = rescue_received_set[0]
		args['valide'] = True
		args['info_to_contact'] = "La valeur envoyee pour '"+args["rescue_received_meaning"]+"' est valide" 

def check_vac_code(args):
	''' This function cheks if the vaccine code sent is valide '''
	sent_vaccine_code = args["vac_code"]

	concerned_vac_code_objects = VAC.objects.filter(vac_designation__iexact = sent_vaccine_code)

	if(len(concerned_vac_code_objects) < 1):
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Le code envoye pour la vaccination effectuee n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	else:
		args['concerned_vac'] = concerned_vac_code_objects[0]
		args['valide'] = True
		args['info_to_contact'] = "Le code envoye pour la vaccination effectuee est valide"

#This function will be deleted and we will use 'def check_mother_id_is_valid(args)' wherever it is used
def check_mother_id_is_valide(args):
	''' This function cheks if the mother id is valide '''
	sent_mother_id = args["sent_mother_id"]

	concerned_mother = Mother.objects.filter(id_mother = sent_mother_id)
	if len(concerned_mother) < 1:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Une maman avec cet identifiant n existe pas dans le systeme. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
	else:
		args['concerned_mother'] = concerned_mother[0]
		args['valide'] = True
		args['info_to_contact'] = "L identifiant de la mere envoye est valide."
#======================reporters self registration==================================


def check_facility(args):
	''' This function checks if the facility code sent by the reporter exists '''
	the_facility_code = args['text'].split(' ')[1]
	concerned_facility = CDS.objects.filter(code = the_facility_code)
	if (len(concerned_facility) > 0):
		args['valide'] = True
		args['info_to_contact'] = "Le code CDS envoye est reconnu."
	else:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Le code envoye n est pas associe a un CDS. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']

def check_supervisor_phone_number(args):
	''' This function checks if the phone number of the supervisor is well written '''
	the_supervisor_phone_number = args['text'].split(' ')[4]
	the_supervisor_phone_number_no_space = the_supervisor_phone_number.replace(" ", "")
	#expression = r'^(\+?(257)?)((62)|(79)|(71)|(76))([0-9]{6})$'
	expression = r'^(\+?(257)?)((61)|(62)|(68)|(69)|(71)|(72)|(75)|(76)|(79))([0-9]{6})$'
	print(the_supervisor_phone_number_no_space)
	if re.search(expression, the_supervisor_phone_number_no_space) is None:
		#The phone number is not well written
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Le numero de telephone du superviseur n est pas bien ecrit. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle REG"
	else:
		args['valide'] = True
		args['info_to_contact'] = "Le numero de telephone du superviseur est bien ecrit."



def save_temporary_the_reporter(args):
	same_existing_temp = Temporary.objects.filter(phone_number = args['phone'])
	if len(same_existing_temp) > 0:
		same_existing_temp = same_existing_temp[0]
		same_existing_temp.delete()
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Vous devriez envoyer le numero de telephone de votre superviseur seulement. Pour corriger, veuillez recommencer l enregistrement."
	else:
		the_phone_number = args['phone']

		the_facility_code = args['text'].split(' ')[1]

		facility = CDS.objects.filter(code = the_facility_code)
		if len(facility) > 0:
			#Let's determine the concerned facility
			the_concerned_facility = facility[0]

			the_supervisor_phone_number = args['text'].split(' ')[4]
			the_supervisor_phone_number_no_space = the_supervisor_phone_number.replace(" ", "")

			if len(the_supervisor_phone_number_no_space) == 8:
				the_supervisor_phone_number_no_space = "+257"+the_supervisor_phone_number_no_space
			if len(the_supervisor_phone_number_no_space) == 11:
				the_supervisor_phone_number_no_space = "+"+the_supervisor_phone_number_no_space


			#Let's determine the concerned sub hill
			
			the_hill_name = args['text'].split(' ')[2].title()

			the_sub_hill_name = args['text'].split(' ')[3].title()


			the_hill = Colline.objects.filter(name__iexact = the_hill_name)
			
			if len(the_hill) < 1:
				print("The hill name ==>"+the_hill_name)
				print("The sub hill name ==>"+the_sub_hill_name)
				args['valide'] = False
				args['info_to_contact'] = "Erreur. Le nom de la colline envoye n est pas valide. Pour corriger, reenvoyer le message bien ecrit commencant par REG"
				return
			
			the_concerned_hill = the_hill[0]

			#Let's check first if the sub hill name sent exist in the system
			the_sub_hill0 = SousColline.objects.filter(name__iexact = the_sub_hill_name)
			if len(the_sub_hill0) < 1:
				args['valide'] = False
				args['info_to_contact'] = "Erreur. Le nom de la sous colline envoye n est pas valide. Pour corriger, reenvoyer le message bien ecrit commencant par REG"
				return
			
			
			#If the sub hill name sent by the reporter exist in the system, let's check if it's linked to the specified hill
			the_sub_hill1 = SousColline.objects.filter(name__iexact = the_sub_hill_name, colline = the_concerned_hill)
			if len(the_sub_hill1) < 1:
				args['valide'] = False
				args['info_to_contact'] = "Erreur. Il n y a pas de sous colline '"+args['text'].split(' ')[3].title()+"' dans la colline '"+args['text'].split(' ')[2].title()+"'."
				return


			the_concerned_sub_hill = the_sub_hill1[0]


			Temporary.objects.create(phone_number = the_phone_number, facility = the_concerned_facility, supervisor_phone_number = the_supervisor_phone_number_no_space, sub_hill = the_concerned_sub_hill)
			args['valide'] = True
			args['info_to_contact'] = "Veuillez reenvoyer seulement le numero de telephone de votre superviseur s il vous plait."


def check_has_already_session(args):
	'''This function checks if this contact has a session'''
	same_existing_temp = Temporary.objects.filter(phone_number = args['phone'])
	if len(same_existing_temp) > 0:
		same_existing_temp = same_existing_temp[0]
		same_existing_temp.delete()
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Vous devriez envoyer le numero de telephone de votre superviseur seulement. Pour corriger, veuillez recommencer l enregistrement."
	else:
		args['valide'] = True
		args['info_to_contact'] = "Ok."

def temporary_record_reporter(args):
	'''This function is used to record temporary a reporter'''
	
	if(args['text'].split(' ')[0].upper() == 'REG'):
		args['mot_cle'] = 'REG'
		
		#Because REG is used to do the self registration and not the update, if the phone user sends a message starting with REG and 			#he/she is already a reporter, we don't allow him/her to continue
		check_if_is_reporter(args)
		if(args['valide'] == True):
			#This contact is already a reporter and can't do the registration the second time
			args['valide'] = False
			args['info_to_contact'] = "Erreur. Vous vous etes deja enregistre. Si vous voulez modifier votre enregistrement, envoyer le message commencant par le mot cle 'REGM'"
			return
	
	if(args['text'].split(' ')[0].upper() == 'REGM'):
		args['mot_cle'] = 'REGM'

	#Let's check if this contact has an existing session
	check_has_already_session(args)
	if not args['valide']:
		return



	#Let's check if the message sent is composed by an expected number of values
	args["expected_number_of_values"] = getattr(settings,'EXPECTED_NUMBER_OF_VALUES','')[args['message_type']]
	check_number_of_values(args)
	if not args['valide']:
		return



	#Let's check if the code of CDS is valid
	check_facility(args)
	if not args['valide']:
		return



	#Let's check is the supervisor phone number is valid
	check_supervisor_phone_number(args)
	if not args['valide']:
		return

	#La ligne ci dessous ne peut pas fonctionner sur les instance Anonimise de RapidPro
	#Let's check if the contact didn't send his/her number in the place of the supervisor number
	check_supervisor_phone_number_not_for_this_contact(args)
	if not args['valide']:
		return

	#Let's temporary save the reporter
	save_temporary_the_reporter(args)


def complete_registration(args):
	the_sup_phone_number = args['text']
	the_sup_phone_number_without_spaces = the_sup_phone_number.replace(" ", "")

	the_existing_temp = Temporary.objects.filter(phone_number = args['phone'])

	if len(the_existing_temp) < 1:
		args['valide'] = False
		args['info_to_contact'] = "Votre message n est pas considere."
	else:
		the_one_existing_temp = the_existing_temp[0]


		#if (the_one_existing_temp.supervisor_phone_number == the_sup_phone_number_without_spaces):
		if (the_sup_phone_number_without_spaces in the_one_existing_temp.supervisor_phone_number) and (len(the_sup_phone_number_without_spaces) >= 8):
			#The confirmation of the phone number of the supervisor pass


			#Let's check if this contact is not registered with the same data as he/she is registered
			#If it is the case, this contact is doing an unnecessary registration
			#check_duplication = CHW.objects.filter(phone_number = the_one_existing_temp.phone_number, cds = the_one_existing_temp.facility, sub_colline = the_one_existing_temp.sub_hill, sub_colline.colline = the_one_existing_temp.sub_hill.colline, supervisor_phone_number = the_one_existing_temp.supervisor_phone_number)
			#check_duplication = CHW.objects.filter(phone_number = the_one_existing_temp.phone_number, cds = the_one_existing_temp.facility, sub_colline = the_one_existing_temp.sub_hill, supervisor_phone_number = the_one_existing_temp.supervisor_phone_number)
			check_duplication = CHW.objects.filter(phone_number = the_one_existing_temp.phone_number)
			the_existing_contact = 0
			is_first_registration = True
			if len(check_duplication) > 0:
				#This contact is doing an update. We update the existing registration
				is_first_registration = False
				the_existing_contact = check_duplication[0]
				#the_existing_contact.delete()
				'''#Let's check if the sent colline is the same with the already saved colline
				the_already_saved_colline = check_duplication[0].sub_colline.colline
				the_sent_colline = the_one_existing_temp.sub_hill.colline

				if(the_sent_colline == the_already_saved_colline):
					#This phone user is trying to register himself/herself twice
					#Already registered and nothing to update
					args['valide'] = False
					args['info_to_contact'] = "Erreur. Vous vous etes deja enregistre sur ce site et avec ce numero de telephone du superviseur. Envoyer un message bien ecrit et commencant par un mot cle valide ou X pour fermer la session"
					the_one_existing_temp.delete()
					return'''

			'''check_duplication = ''


			#Let's check if the contact wants to update his facility
			check_duplication = Reporter.objects.filter(~Q(facility = the_one_existing_temp.facility), phone_number = the_one_existing_temp.phone_number, supervisor_phone_number = the_one_existing_temp.supervisor_phone_number)
			if len(check_duplication) > 0:
				#this contact wants to update his facility
				check_duplication = check_duplication[0]
				check_duplication.facility = the_one_existing_temp.facility
				check_duplication.save()
				args['valide'] = True
				args['info_to_contact'] = "Modification reussie. Votre nouveau site d affectation est : "+the_one_existing_temp.facility.name
				the_one_existing_temp.delete()
				return

			check_duplication = ''



			#Let's check if the contact wants to update the phone number of his supervisor
			check_duplication = Reporter.objects.filter(~Q(supervisor_phone_number = the_one_existing_temp.supervisor_phone_number), phone_number = the_one_existing_temp.phone_number, facility = the_one_existing_temp.facility)
			if len(check_duplication) > 0:
				#this contact wants to update the phone number of his supervisor
				check_duplication = check_duplication[0]
				check_duplication.supervisor_phone_number = the_one_existing_temp.supervisor_phone_number
				check_duplication.save()
				args['valide'] = True
				args['info_to_contact'] = "Modification reussie. Le nouveau numero de telephone de votre superviseur est : "+the_one_existing_temp.supervisor_phone_number+""
				the_one_existing_temp.delete()
				return

			check_duplication = ''



			#Let's check if the contact wants to update both the CDS and the phone number of his supervisor
			check_duplication = Reporter.objects.filter(~Q(facility = the_one_existing_temp.facility), ~Q(supervisor_phone_number = the_one_existing_temp.supervisor_phone_number), phone_number = the_one_existing_temp.phone_number)
			if len(check_duplication) > 0:
				#this contact wants to update the phone number of his supervisor
				check_duplication = check_duplication[0]
				check_duplication.facility = the_one_existing_temp.facility
				check_duplication.supervisor_phone_number = the_one_existing_temp.supervisor_phone_number
				check_duplication.save()
				args['valide'] = True
				args['info_to_contact'] = "Modification reussie. Le nouveau numero de telephone de votre superviseur est '"+the_one_existing_temp.supervisor_phone_number+"' et votre nouveau site d affectation est '"+the_one_existing_temp.facility.name+"'"
				the_one_existing_temp.delete()
				return'''


			#This contact is doing a first registration. Let's record him/her
			if is_first_registration:
				CHW.objects.create(phone_number = the_one_existing_temp.phone_number, cds = the_one_existing_temp.facility, supervisor_phone_number = the_one_existing_temp.supervisor_phone_number, sub_colline = the_one_existing_temp.sub_hill)
				args['info_to_contact'] = "Enregistrement reussi. [CDS : '"+the_one_existing_temp.facility.name+"', Colline :  '"+the_one_existing_temp.sub_hill.colline.name+"', sous colline : '"+the_one_existing_temp.sub_hill.name+"', Numero du superviseur :  '"+the_one_existing_temp.supervisor_phone_number+"']. Si vous voulez modifier votre enregistrent, veuillez utiliser le mot cle REGM"
			else:
				#The contact is doing an update
				the_existing_contact.phone_number = the_one_existing_temp.phone_number
				the_existing_contact.cds = the_one_existing_temp.facility
				the_existing_contact.supervisor_phone_number = the_one_existing_temp.supervisor_phone_number
				the_existing_contact.sub_colline = the_one_existing_temp.sub_hill
				the_existing_contact.save()
				args['info_to_contact'] = "Modification reussie. [CDS : '"+the_one_existing_temp.facility.name+"', Colline :  '"+the_one_existing_temp.sub_hill.colline.name+"', sous colline : '"+the_one_existing_temp.sub_hill.name+"', Numero du superviseur :  '"+the_one_existing_temp.supervisor_phone_number+"']. Si vous voulez modifier votre enregistrent, veuillez utiliser le mot cle REGM"

			the_one_existing_temp.delete()
			args['valide'] = True
			#args['info_to_contact'] = "Enregistrement reussi. [CDS : '"+the_one_existing_temp.facility.name+"', Colline :  '"+the_one_existing_temp.sub_hill.colline.name+"', sous colline : '"+the_one_existing_temp.sub_hill.name+"', Numero du superviseur :  '"+the_one_existing_temp.supervisor_phone_number+"']. Si vous voulez modifier votre enregistrent, veuillez utiliser le mot cle REGM"
		else:
			the_one_existing_temp.delete()
			args['valide'] = False
			args['info_to_contact'] = "Erreur. Vous avez envoye le numero de telephone de votre superviseur de differentes manieres. Pour corriger, veuillez reenvoyer le message commencant par le mot cle REG"


#-----------------------------------------------------------------








#------------------------------PREGNANT CONFIRMATION REPORT-----------------------------------

#RECORD
def record_pregnant_case(args):

	args['mot_cle'] = "GRO"

	#Let's check if the person who send this message is a reporter
	check_if_is_reporter(args)
	print(args['valide'])
	if not args['valide']:
		return

	#Let's check if the message sent is composed by an expected number of values
	args["expected_number_of_values"] = getattr(settings,'EXPECTED_NUMBER_OF_VALUES','')[args['message_type']]
	check_number_of_values(args)
	if not args['valide']:
		return

	

	#Let's check if the expected giving birth date is a future date
	args["future_date"] = args['text'].split(' ')[1]
	args["date_meaning"] = "date probable d accouchement"
	check_is_future_date(args)
	if not args['valide']:
		return
	args["expected_birth_date"] = args['date_well_written']

	#Let's check if the next appointment date is a future date
	args["future_date"] = args['text'].split(' ')[2]
	args["date_meaning"] = "date du prochain rendez-vous"
	check_is_future_date(args)
	if not args['valide']:
		return
	args["next_appointment_date"] = args['date_well_written']

	#Let's check if the risk level is correct
	args["risk_level"] = args['text'].split(' ')[3]
	check_risk_level(args)
	if not args['valide']:
		return

	#Let's check if the location sent is valid
	args["location"] = args['text'].split(' ')[4]
	args["date_meaning"] = "lieu de consultation"
	check_location(args)
	if not args['valide']:
		return

	#Let's check if the phone number of the concerned mother is valid
	args["phone_number"] = args['text'].split(' ')[5]
	check_phone_number(args)
	if not args['valide']:
		return



	#The mother id is made by two parts.
	#The first part primary key of the cds on which works the CHW who registered her
	#The second part is number of mother registered on that cds

	mother_id = ""

	#The first part of the mother id must have at minimum 3 caracters
	mother_id_1 = str(args['facility'].id)
	if len(mother_id_1) == 1:
		mother_id_1 = "00"+mother_id_1
	if len(mother_id_1) == 2:
		mother_id_1 = "0"+mother_id_1

	#Let's build the second part of the mother id. It's made at minimum by 3 caracters

	gro_reports_from_this_cds = Report.objects.filter(cds = args['facility'], category = args['mot_cle'])

	#the_last_mother_registered_from_this_cds = the_last_gro_report_from_this_cds.mother

	mother_id_2 = '0'
	print("-1-")	
	if(len(gro_reports_from_this_cds) > 0):
		print("-2-")
		the_last_mother_from_this_cds = Report.objects.filter(cds = args['facility'], category = args['mot_cle']).order_by("-id")[0].mother
		#Let's identify the id used by the system users for this patient
		the_last_mother_id = the_last_mother_from_this_cds.id_mother

		#Let's remove the first part (mother_id_1) and increment the second one
		the_length_of_the_first_part = len(mother_id_1)
		the_second_part = the_last_mother_id[the_length_of_the_first_part:]

		#Let's increment the second part.
		the_second_part_int = int(the_second_part)
		the_second_part_int = the_second_part_int+1

		#mother_id_2 is the second part of the new mother
		mother_id_2 = str(the_second_part_int)
		print("-3-")
	else:
		print("-4-")
		mother_id_2 = '0'

	print("-5-")
	if len(mother_id_2) == 1:
		mother_id_2 = "00"+mother_id_2
	if len(mother_id_2) == 2:
		mother_id_2 = "0"+mother_id_2


	mother_id = mother_id_1+""+mother_id_2

	print("Mother id")
	print("=========")
	print(mother_id)

	#Let's check if there is no mother with that id
	check_mother_exists = Mother.objects.filter(id_mother = mother_id)
	if len(check_mother_exists) > 0:
		args['valide'] = False
		args['info_to_contact'] = "Exception. Consulter l equipe de maintenance du systeme."
		return






	#All cheks passes. Let's record the pregnant women
	#the_created_mother_record, created = Mother.objects.get_or_create(phone_number = args["phone_number"])
	the_created_mother_record = Mother.objects.create(id_mother = mother_id, phone_number = args["phone_number"])
	the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = the_created_mother_record, reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])
	created_gro_report = ReportGRO.objects.create(report = the_created_report, expected_delivery_date = args["expected_birth_date"], next_appointment_date = args["next_appointment_date"], risk_level = args["risklevel"], consultation_location = args['location'])
	
	args['valide'] = True
	args['info_to_contact'] = "La femme enceinte est bien enregistree. Son numero est "+mother_id




#MODIFY
def modify_record_pregnant_case(args):

	args['mot_cle'] = "GROM"

	#Let's check if the person who send this message is a reporter
	check_if_is_reporter(args)
	print(args['valide'])
	if not args['valide']:
		return

	#Let's check if the message sent is composed by an expected number of values
	args["expected_number_of_values"] = getattr(settings,'EXPECTED_NUMBER_OF_VALUES','')[args['message_type']]
	check_number_of_values(args)
	if not args['valide']:
		return

	#Let's check if the mother id sent is valid
	args["sent_mother_id"] = args['text'].split(' ')[1]
	check_mother_id_is_valide(args)
	if not args['valide']:
		return

	#Let's check if the expected giving birth date is a future date
	args["future_date"] = args['text'].split(' ')[2]
	args["date_meaning"] = "date probable d accouchement"
	check_is_future_date(args)
	if not args['valide']:
		return
	args["expected_birth_date"] = args['date_well_written']

	#Let's check if the next appointment date is a future date
	args["future_date"] = args['text'].split(' ')[3]
	args["date_meaning"] = "date du prochain rendez-vous"
	check_is_future_date(args)
	if not args['valide']:
		return
	args["next_appointment_date"] = args['date_well_written']

	#Let's check if the risk level is correct
	args["risk_level"] = args['text'].split(' ')[4]
	check_risk_level(args)
	if not args['valide']:
		return

	#Let's check if the location sent is valid
	args["location"] = args['text'].split(' ')[5]
	args["date_meaning"] = "lieu de consultation"
	check_location(args)
	if not args['valide']:
		return

	#Let's check if the phone number of the concerned mother is valid
	args["phone_number"] = args['text'].split(' ')[6]
	check_phone_number(args)
	if not args['valide']:
		return


	#Let's identify the corresponding Report
	the_corresponding_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3])
	if len(the_corresponding_report) < 1:
		args['valide'] = False
		args['info_to_contact'] = "Exception. Un rapport de categorie 'GRO' correspondant a la maman indiquee n est pas trouve. Veuillez contacter l administrateur du systeme"
		return
	the_one_corresponding_report = the_corresponding_report[0]

	the_corresponding_gro_report = ReportGRO.objects.filter(report = the_one_corresponding_report)
	if len(the_corresponding_gro_report) < 1:
		args['valide'] = False
		args['info_to_contact'] = "Exception. Un rapport 'GRO' correspondant a la maman indiquee n est pas trouve. Veuillez contacter l administrateur du systeme"
		return
	the_one_corresponding_gro_report = the_corresponding_gro_report[0]

	#Let's update all values
	args['concerned_mother'].phone_number = args["phone_number"]
	args['concerned_mother'].save()

	the_one_corresponding_report.mother = args['concerned_mother']
	the_one_corresponding_report.reporting_date = datetime.datetime.now().date()
	the_one_corresponding_report.text = args['text']
	the_one_corresponding_report.save()

	the_one_corresponding_gro_report.expected_delivery_date = args["expected_birth_date"]
	the_one_corresponding_gro_report.next_appointment_date = args["next_appointment_date"]
	the_one_corresponding_gro_report.risk_level = args["risklevel"]
	the_one_corresponding_gro_report.consultation_location = args['location']
	the_one_corresponding_gro_report.save()
	
	args['valide'] = True
	args['info_to_contact'] = "Mise a jour du rapport de confirmation de grossesse de la femme '"+args['concerned_mother'].id_mother+"' a reussie."

#-----------------------------------------------------------------



#-----------------------------------------------------------------
def record_prenatal_consultation_report(args):

	args['mot_cle'] = "CPN"	

	#Let's check if the person who send this message is a reporter
	check_if_is_reporter(args)
	if not args['valide']:
		return

	#Let's check if the message sent is composed by an expected number of values
	args["expected_number_of_values"] = getattr(settings,'EXPECTED_NUMBER_OF_VALUES','')[args['message_type']]
	check_number_of_values(args)
	if not args['valide']:
		return

	#Let's check if the mother id sent is valid
	args["sent_mother_id"] = args['text'].split(' ')[1]
	check_mother_id_is_valid(args)
	if not args['valide']:
		return
	args['concerned_woman'] = args['concerned_mother']
	
	#Let's check if the CPN name sent exists
	args["sent_cpn_name"] =  args['text'].split(' ')[2]
	check_cpn_name_exists(args)
	if not args['valide']:
		return
	args["concerned_cpn"] = args['specified_cpn']

	#Let's check if the consultation date is valid
	#It must be a previous date or today's date
	args["previous_days_or_today_date"] = args['text'].split(' ')[3]
	args["date_meaning"] = "Date de consultation prenatale"
	check_date_is_previous_or_today(args)
	if not args['valide']:
		return
	args["cpn_consultation_date"] = args['date_well_written']

	#Let's check if the next appointment date is valid
	args["future_date"] = args['text'].split(' ')[4]
	args["date_meaning"] = "date du prochain rendez-vous"
	check_is_future_date(args)
	if not args['valide']:
		return
	args["next_appointment_date"] = args['date_well_written']

	#Let's check if the consultation location is valid
	args["location"] = args['text'].split(' ')[5]
	args["date_meaning"] = "lieu de consultation"
	check_location(args)
	if not args['valide']:
		return

	#Let's check if the indicated woman weight is valid
	args["float_value"] = args['text'].split(' ')[6]
	args["date_meaning"] = "Poids de la mere"
	check_is_float(args)
	if not args['valide']:
		return
	try:
		checked_value = float(args['checked_float'])
	except:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["date_meaning"]+"' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
		return


	#Now, everything is checked. Let's record the report
	the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_woman'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])
	created_cpn_report = ReportCPN.objects.create(report = the_created_report, concerned_cpn = args["concerned_cpn"], consultation_date = args["cpn_consultation_date"], consultation_location = args['location'], mother_weight = checked_value, next_appointment_date = args["next_appointment_date"])
	
	args['valide'] = True
	args['info_to_contact'] = "Le rapport '"+args["concerned_cpn"].cpn_designation+"' de la maman '"+args['concerned_woman'].id_mother+"' est bien enregistre."




def modify_record_prenatal_consultation_report(args):

	args['mot_cle'] = "CPNM"	

	#Let's check if the person who send this message is a reporter
	check_if_is_reporter(args)
	if not args['valide']:
		return

	#Let's check if the message sent is composed by an expected number of values
	args["expected_number_of_values"] = getattr(settings,'EXPECTED_NUMBER_OF_VALUES','')[args['message_type']]
	check_number_of_values(args)
	if not args['valide']:
		return

	#Let's check if the mother id sent is valid
	args["sent_mother_id"] = args['text'].split(' ')[1]
	check_mother_id_is_valid(args)
	if not args['valide']:
		return
	args['concerned_woman'] = args['concerned_mother']
	
	#Let's check if the CPN name sent exists
	args["sent_cpn_name"] =  args['text'].split(' ')[2]
	check_cpn_name_exists(args)
	if not args['valide']:
		return
	args["concerned_cpn"] = args['specified_cpn']

	#Let's check if the consultation date is valid
	#It must be a previous date or today's date
	args["previous_days_or_today_date"] = args['text'].split(' ')[3]
	args["date_meaning"] = "Date de consultation prenatale"
	check_date_is_previous_or_today(args)
	if not args['valide']:
		return
	args["cpn_consultation_date"] = args['date_well_written']

	#Let's check if the next appointment date is valid
	args["future_date"] = args['text'].split(' ')[4]
	args["date_meaning"] = "date du prochain rendez-vous"
	check_is_future_date(args)
	if not args['valide']:
		return
	args["next_appointment_date"] = args['date_well_written']

	#Let's check if the consultation location is valid
	args["location"] = args['text'].split(' ')[5]
	args["date_meaning"] = "lieu de consultation"
	check_location(args)
	if not args['valide']:
		return

	#Let's check if the indicated woman weight is valid
	args["float_value"] = args['text'].split(' ')[6]
	args["date_meaning"] = "Poids de la mere"
	check_is_float(args)
	if not args['valide']:
		return
	try:
		checked_value = float(args['checked_float'])
	except:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["date_meaning"]+"' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
		return


	#Let's check if the mother with this id has an already registered CPN report
	the_existing_cpn_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3])
	if len(the_existing_cpn_report) < 1:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Aucun rapport 'CPN' trouve de la maman '"+args['concerned_mother'].id_mother+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
		return

	the_only_one_corresponding_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3]).order_by('-id')[0]

	the_corresponding_cpn_report = ReportCPN.objects.filter(report = the_only_one_corresponding_report)
	if len(the_corresponding_cpn_report) < 1:
		args['valide'] = False
		args['info_to_contact'] = "Exception. Un rapport 'CON' correspondant a la maman indiquee n est pas trouve. Veuillez contacter l administrateur du systeme"
		return
	the_one_corresponding_cpnreport = the_corresponding_cpn_report[0]
		

	#Now, everything is checked. Let's do the update

	the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_woman'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])
	created_cpn_report = ReportCPN.objects.create(report = the_created_report, concerned_cpn = args["concerned_cpn"], consultation_date = args["cpn_consultation_date"], consultation_location = args['location'], mother_weight = checked_value, next_appointment_date = args["next_appointment_date"])

	the_only_one_corresponding_report.chw = args['the_sender']
	the_only_one_corresponding_report.sub_hill = args['sub_colline']
	the_only_one_corresponding_report.cds = args['facility']
	the_only_one_corresponding_report.mother = args['concerned_woman']
	the_only_one_corresponding_report.reporting_date = datetime.datetime.now().date()
	the_only_one_corresponding_report.text = args['text']
	the_only_one_corresponding_report.save()

	the_one_corresponding_cpnreport.report = the_created_report
	the_one_corresponding_cpnreport.concerned_cpn = args["concerned_cpn"]
	the_one_corresponding_cpnreport.consultation_date = args["cpn_consultation_date"]
	the_one_corresponding_cpnreport.consultation_location = args['location']
	the_one_corresponding_cpnreport.mother_weight = checked_value
	the_one_corresponding_cpnreport.next_appointment_date = args["next_appointment_date"]
	the_one_corresponding_cpnreport.save()

	args['valide'] = True
	args['info_to_contact'] = "Mise a jour du rapport de consultation prenatale de la femme '"+args['concerned_mother'].id_mother+"' a reussie."


	
#-----------------------------------------------------------------




#-----------------------------------------------------------------
def record_birth_case_report(args):

	args['mot_cle'] = "NSC"

	#Let's check if the person who send this message is a reporter
	check_if_is_reporter(args)
	print(args['valide'])
	if not args['valide']:
		return
	
	#Let's check if the message sent is composed by an expected number of values
	args["expected_number_of_values"] = getattr(settings,'EXPECTED_NUMBER_OF_VALUES','')[args['message_type']]
	check_number_of_values(args)
	if not args['valide']:
		return

	#Let's check if the mother id sent is valid
	args["sent_mother_id"] = args['text'].split(' ')[1]
	check_mother_id_is_valid(args)
	if not args['valide']:
		return
	args['concerned_woman'] = args['concerned_mother']

	#Let's check if the child code is valid
	args["child_code"] = args['text'].split(' ')[2]
	check_child_code(args)
	if not args['valide']:
		return

	#Let check if the birth date is not a future date
	#It must be a previous date or today's date
	args["previous_days_or_today_date"] = args['text'].split(' ')[3]
	args["date_meaning"] = "Date de naissance"
	check_date_is_previous_or_today(args)
	if not args['valide']:
		return
	args["birth_date"] = args['date_well_written']


	#Let's check if the next CPoN date is a future date
	args["future_date"] = args['text'].split(' ')[4]
	args["date_meaning"] = "Prochaine date pour les soins postnatals"
	check_is_future_date(args)
	if not args['valide']:
		return
	args["next_cpon_appointment_date"] = args['date_well_written']

	
	#Let's check if the location of birth is valid
	args["location"] = args['text'].split(' ')[5]
	args["date_meaning"] = "lieu de naissance"
	check_location(args)
	if not args['valide']:
		return

	#Let's check the value sent for "Allaitement maternel"
	args["allaitement_maternel"] = args['text'].split(' ')[6]
	check_allaitement_maternel(args)
	if not args['valide']:
		return

	#Let's check if the value sent for gender is valid
	args["gender"] = args['text'].split(' ')[7]
	check_gender(args)
	if not args['valide']:
		return

	#Let's check if the indicated child weight is valid
	args["float_value"] = args['text'].split(' ')[8]
	args["date_meaning"] = "Poids du nouveau ne"
	check_is_float(args)
	if not args['valide']:
		return
	try:
		checked_value = float(args['checked_float'])
	except:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["date_meaning"]+"' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
		return
	
	
	#Now, everything is checked. Let's record the report
	the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_woman'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])
	created_nsc_report = ReportNSC.objects.create(report = the_created_report, child_number = args['child_number'], birth_date = args["birth_date"], birth_location = args['location'], gender = args['gender'], weight = checked_value, next_appointment_date = args["next_cpon_appointment_date"], breast_feading = args['code_allaitement'])
	
	args['valide'] = True
	args['info_to_contact'] = "Le rapport de naissance du bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_woman'].id_mother+"' est bien enregistre."



#Modify
def modify_record_birth_case_report(args):

	args['mot_cle'] = "NSCM"

	#Let's check if the person who send this message is a reporter
	check_if_is_reporter(args)
	print(args['valide'])
	if not args['valide']:
		return
	
	#Let's check if the message sent is composed by an expected number of values
	args["expected_number_of_values"] = getattr(settings,'EXPECTED_NUMBER_OF_VALUES','')[args['message_type']]
	check_number_of_values(args)
	if not args['valide']:
		return

	#Let's check if the mother id sent is valid
	args["sent_mother_id"] = args['text'].split(' ')[1]
	check_mother_id_is_valid(args)
	if not args['valide']:
		return
	args['concerned_woman'] = args['concerned_mother']

	#Let's check if the child code is valid
	args["child_code"] = args['text'].split(' ')[2]
	check_child_code(args)
	if not args['valide']:
		return

	#Let check if the birth date is not a future date
	#It must be a previous date or today's date
	args["previous_days_or_today_date"] = args['text'].split(' ')[3]
	args["date_meaning"] = "Date de naissance"
	check_date_is_previous_or_today(args)
	if not args['valide']:
		return
	args["birth_date"] = args['date_well_written']


	#Let's check if the next CPoN date is a future date
	args["future_date"] = args['text'].split(' ')[4]
	args["date_meaning"] = "Prochaine date pour les soins postnatals"
	check_is_future_date(args)
	if not args['valide']:
		return
	args["next_cpon_appointment_date"] = args['date_well_written']

	
	#Let's check if the location of birth is valid
	args["location"] = args['text'].split(' ')[5]
	args["date_meaning"] = "lieu de naissance"
	check_location(args)
	if not args['valide']:
		return

	#Let's check the value sent for "Allaitement maternel"
	args["allaitement_maternel"] = args['text'].split(' ')[6]
	check_allaitement_maternel(args)
	if not args['valide']:
		return

	#Let's check if the value sent for gender is valid
	args["gender"] = args['text'].split(' ')[7]
	check_gender(args)
	if not args['valide']:
		return

	#Let's check if the indicated child weight is valid
	args["float_value"] = args['text'].split(' ')[8]
	args["date_meaning"] = "Poids du nouveau ne"
	check_is_float(args)
	if not args['valide']:
		return
	try:
		checked_value = float(args['checked_float'])
	except:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["date_meaning"]+"' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
		return




	#Let's check if the mother with this id has an already registered NSC report
	the_existing_nsc_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3])
	if len(the_existing_nsc_report) < 1:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Aucun rapport 'NSC' trouve de la maman '"+args['concerned_mother'].id_mother+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
		return

	the_only_one_corresponding_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3]).order_by('-id')[0]

	the_corresponding_nsc_report = ReportNSC.objects.filter(report = the_only_one_corresponding_report)
	if len(the_corresponding_nsc_report) < 1:
		args['valide'] = False
		args['info_to_contact'] = "Exception. Un rapport 'NSC' correspondant a la maman indiquee n est pas trouve. Veuillez contacter l administrateur du systeme"
		return
	the_one_corresponding_nscreport = the_corresponding_nsc_report[0]
	
	

	
	#Now, everything is checked. Let's do the update

	the_only_one_corresponding_report.chw = args['the_sender']
	the_only_one_corresponding_report.sub_hill = args['sub_colline']
	the_only_one_corresponding_report.cds = args['facility']
	the_only_one_corresponding_report.mother = args['concerned_woman']
	the_only_one_corresponding_report.reporting_date = datetime.datetime.now().date()
	the_only_one_corresponding_report.text = args['text']
	the_only_one_corresponding_report.save()

	the_one_corresponding_nscreport.report = the_only_one_corresponding_report
	the_one_corresponding_nscreport.child_number = args['child_number']
	the_one_corresponding_nscreport.birth_date = args["birth_date"]
	the_one_corresponding_nscreport.birth_location = args['location']
	the_one_corresponding_nscreport.gender = args['gender']
	the_one_corresponding_nscreport.weight = checked_value
	the_one_corresponding_nscreport.next_appointment_date = args["next_cpon_appointment_date"]
	the_one_corresponding_nscreport.breast_feading = args['code_allaitement']
	the_one_corresponding_nscreport.save()
	
	args['valide'] = True
	args['info_to_contact'] = "Mise a jour du rapport de naissance du bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_woman'].id_mother+"' a reussie."

#-----------------------------------------------------------------



#-----------------------------------------------------------------
def record_postnatal_care_report(args):

	args['mot_cle'] = "CON"

	#Let's check if the person who send this message is a reporter
	check_if_is_reporter(args)
	print(args['valide'])
	if not args['valide']:
		return
	
	#Let's check if the message sent is composed by an expected number of values
	args["expected_number_of_values"] = getattr(settings,'EXPECTED_NUMBER_OF_VALUES','')[args['message_type']]
	check_number_of_values(args)
	if not args['valide']:
		return

	#Let's check if the mother id sent is valid
	args["sent_mother_id"] = args['text'].split(' ')[1]
	check_mother_id_is_valid(args)
	if not args['valide']:
		return

	#Let's check if this mother has a child with the sent child number
	args["child_id"] = args['text'].split(' ')[2]
	check_child_exists(args)
	if not args['valide']:
		return

	#Let's check if the consultation code sent is valid
	args["con_code"] = args['text'].split(' ')[3]
	check_con_code(args)
	if not args['valide']:
		return

	#Let's check if the next appointment date is a future date
	args["future_date"] = args['text'].split(' ')[4]
	args["date_meaning"] = "Date du prochain rendez-vous"
	check_is_future_date(args)
	if not args['valide']:
		return
	args["next_appointment_date"] = args['date_well_written']
	
	#Let's check if the symptom(s) is/are valid
	args["symptoms"] = args['text'].split(' ')[5]
	check_symptoms(args)
	if not args['valide']:
		return

	#Let's check mother health status value
	args["health_status_value"] = args['text'].split(' ')[6]
	args["health_status_meaning"] = "etat de sante de la mere"
	check_health_status(args)
	if not args['valide']:
		return
	args['mother_s_health_state'] = args['concerned_health_status']

	#Let's check child health status value
	args["health_status_value"] = args['text'].split(' ')[7]
	args["health_status_meaning"] = "etat de sante de l enfant"
	check_health_status(args)
	if not args['valide']:
		return
	args['child_s_health_state'] = args['concerned_health_status']

	
	#Now, everything is checked. Let's record the report
	the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_mother'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])
	created_con_report = ReportCON.objects.create(report = the_created_report, child = args['concerned_child'], con = args['concerned_con'], child_health_state = args['child_s_health_state'], mother_health_state = args['mother_s_health_state'], next_appointment_date = args["next_appointment_date"])


	for one_symbol in args['checked_symptoms_list']:
		one_symptom = Symptom.objects.filter(symtom_designation = one_symbol)[0]
		created_report_symptom_connection = CON_Report_Symptom.objects.create(con_report = created_con_report, symptom = one_symptom)

	args['valide'] = True
	args['info_to_contact'] = "Le rapport de soins postnatals pour le bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."



#Modify
def modify_record_postnatal_care_report(args):

	args['mot_cle'] = "CONM"

	#Let's check if the person who send this message is a reporter
	check_if_is_reporter(args)
	print(args['valide'])
	if not args['valide']:
		return
	
	#Let's check if the message sent is composed by an expected number of values
	args["expected_number_of_values"] = getattr(settings,'EXPECTED_NUMBER_OF_VALUES','')[args['message_type']]
	check_number_of_values(args)
	if not args['valide']:
		return

	#Let's check if the mother id sent is valid
	args["sent_mother_id"] = args['text'].split(' ')[1]
	check_mother_id_is_valid(args)
	if not args['valide']:
		return

	#Let's check if this mother has a child with the sent child number
	args["child_id"] = args['text'].split(' ')[2]
	check_child_exists(args)
	if not args['valide']:
		return

	#Let's check if the consultation code sent is valid
	args["con_code"] = args['text'].split(' ')[3]
	check_con_code(args)
	if not args['valide']:
		return

	#Let's check if the next appointment date is a future date
	args["future_date"] = args['text'].split(' ')[4]
	args["date_meaning"] = "Date du prochain rendez-vous"
	check_is_future_date(args)
	if not args['valide']:
		return
	args["next_appointment_date"] = args['date_well_written']
	
	#Let's check if the symptom(s) is/are valid
	args["symptoms"] = args['text'].split(' ')[5]
	check_symptoms(args)
	if not args['valide']:
		return

	#Let's check mother health status value
	args["health_status_value"] = args['text'].split(' ')[6]
	args["health_status_meaning"] = "etat de sante de la mere"
	check_health_status(args)
	if not args['valide']:
		return
	args['mother_s_health_state'] = args['concerned_health_status']

	#Let's check child health status value
	args["health_status_value"] = args['text'].split(' ')[7]
	args["health_status_meaning"] = "etat de sante de l enfant"
	check_health_status(args)
	if not args['valide']:
		return
	args['child_s_health_state'] = args['concerned_health_status']




	#Let's check if the mother with this id has an already registered CON report
	the_existing_con_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3])
	if len(the_existing_con_report) < 1:
		args['valide'] = False
		args['info_to_contact'] = "Erreur. Aucun rapport 'CON' trouve de la maman '"+args['concerned_mother'].id_mother+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
		return

	the_only_one_corresponding_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3]).order_by('-id')[0]

	the_corresponding_con_report = ReportCON.objects.filter(report = the_only_one_corresponding_report)
	if len(the_corresponding_con_report) < 1:
		args['valide'] = False
		args['info_to_contact'] = "Exception. Un rapport 'CON' correspondant a la maman indiquee n est pas trouve. Veuillez contacter l administrateur du systeme"
		return
	the_one_corresponding_conreport = the_corresponding_con_report[0]



	#Now, everything is checked. Let's record the report
	the_only_one_corresponding_report.chw = args['the_sender']
	the_only_one_corresponding_report.sub_hill = args['sub_colline']
	the_only_one_corresponding_report.cds = args['facility']
	the_only_one_corresponding_report.mother = args['concerned_mother']
	the_only_one_corresponding_report.reporting_date = datetime.datetime.now().date()
	the_only_one_corresponding_report.text = args['text']
	the_only_one_corresponding_report.save()


	the_one_corresponding_conreport.report = the_only_one_corresponding_report
	the_one_corresponding_conreport.child = args['concerned_child']
	the_one_corresponding_conreport.con = args['concerned_con']
	the_one_corresponding_conreport.child_health_state = args['child_s_health_state']
	the_one_corresponding_conreport.mother_health_state = args['mother_s_health_state']
	the_one_corresponding_conreport.next_appointment_date = args["next_appointment_date"]
	the_one_corresponding_conreport.save()

	#Let's update 'CON_Report_Symptom' connections
	concerned_con_report_symptom_connections = CON_Report_Symptom.objects.filter(con_report = the_one_corresponding_conreport)
	if len(concerned_con_report_symptom_connections) > 0:
		for one_connection in concerned_con_report_symptom_connections:
			one_connection.delete()

	for one_symbol in args['checked_symptoms_list']:
		one_symptom = Symptom.objects.filter(symtom_designation = one_symbol)[0]
		created_report_symptom_connection = CON_Report_Symptom.objects.create(con_report = the_one_corresponding_conreport, symptom = one_symptom)

	args['valide'] = True
	args['info_to_contact'] = "Mise a jour du rapport de soins postnatals pour le bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_mother'].id_mother+"' a reussie."

#-----------------------------------------------------------------



#-----------------------------------------------------------------
def record_child_follow_up_report(args):

	args['mot_cle'] = "VAC"

	#Let's check if the person who send this message is a reporter
	check_if_is_reporter(args)
	print(args['valide'])
	if not args['valide']:
		return
	
	#Let's check if the message sent is composed by an expected number of values
	args["expected_number_of_values"] = getattr(settings,'EXPECTED_NUMBER_OF_VALUES','')[args['message_type']]
	check_number_of_values(args)
	if not args['valide']:
		return

	#Let's check if the mother id sent is valid
	args["sent_mother_id"] = args['text'].split(' ')[1]
	check_mother_id_is_valid(args)
	if not args['valide']:
		return

	#Let's check if this mother has a child with the sent child number
	args["child_id"] = args['text'].split(' ')[2]
	check_child_exists(args)
	if not args['valide']:
		return

	#Let's check if the vaccine code sent is valid
	args["vac_code"] = args['text'].split(' ')[3]
	check_vac_code(args)
	if not args['valide']:
		return

	#Let's check if the location sent is valid
	args["location"] = args['text'].split(' ')[4]
	args["date_meaning"] = "lieu de vaccination"
	check_location(args)
	if not args['valide']:
		return

	#Let's record the report
	the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_mother'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])

	created_vac_report = ReportVAC.objects.create(report = the_created_report, child = args['concerned_child'], vac = args['concerned_vac'], location = args['location'])
	
	args['valide'] = True
	args['info_to_contact'] = "Le rapport de suivi du bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."
#-----------------------------------------------------------------






#-----------------------------------------------------------------
def record_risk_report(args):

	args['mot_cle'] = "RIS"

	#Let's check if the person who send this message is a reporter
	check_if_is_reporter(args)
	print(args['valide'])
	if not args['valide']:
		return

	#Let's check if it is report about a child or a mother. We count the number of values sent
	#Let's check if the message sent is composed by an expected number of values
	#args["expected_number_of_values"] = getattr(settings,'EXPECTED_NUMBER_OF_VALUES','')[args['message_type']]
	check_number_of_values_ris(args)
	if not args['valide']:
		return

	#Let's check if the mother id sent is valid
	args["sent_mother_id"] = args['text'].split(' ')[1]
	check_mother_id_is_valid(args)
	if not args['valide']:
		return
	
	#Let's check if the symptom(s) is/are valid
	args["symptoms"] = args['text'].split(' ')[2]
	check_symptoms(args)
	if not args['valide']:
		return


	if(args['ris_type'] == "RIS_CHILD"):
		#The report sent is a child report
		#Let's check if this mother has a child with the sent child number
		args["child_id"] = args['text'].split(' ')[3]
		check_child_exists(args)
		if not args['valide']:
			return

	if(args['ris_type'] == "RIS_WOMAN"):
		#We record a woman report
		pass

	#Now, everything is checked. Let's record the report
	the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_mother'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])
	created_ris_report = ReportRIS.objects.create(report = the_created_report)


	for one_symbol in args['checked_symptoms_list']:
		one_symptom = Symptom.objects.filter(symtom_designation = one_symbol)[0]
		created_report_symptom_connection = RIS_Report_Symptom.objects.create(ris_report = created_ris_report, symptom = one_symptom)

	
	if(args['ris_type'] == "RIS_CHILD"):
		#Let's record informations related to the child
		report_ris_bebe = ReportRISBebe.objects.create(ris_report = created_ris_report, concerned_child = args['concerned_child'])

	args['valide'] = True
	
	if(args['ris_type'] == "RIS_CHILD"):
		args['info_to_contact'] = "Le rapport de risque pour le bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."
	if(args['ris_type'] == "RIS_WOMAN"):
		args['info_to_contact'] = "Le rapport de risque de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."

#-----------------------------------------------------------------




#-----------------------------------------------------------------
def record_response_to_risk_report(args):

	args['mot_cle'] = "RER"

	#Let's check if the person who send this message is a reporter
	check_if_is_reporter(args)
	print(args['valide'])
	if not args['valide']:
		return
	
	#Let's check if the message sent is composed by an expected number of values
	args["expected_number_of_values"] = getattr(settings,'EXPECTED_NUMBER_OF_VALUES','')[args['message_type']]
	check_number_of_values(args)
	if not args['valide']:
		return

	#Let's check if the mother id sent is valid
	args["sent_mother_id"] = args['text'].split(' ')[1]
	check_mother_id_is_valid(args)
	if not args['valide']:
		return

	#Let's check if there is a RIS report already recorded
	check_mother_has_ris_report(args)
	if not args['valide']:
		return

	#Let's check health status value
	args["health_status_value"] = args['text'].split(' ')[2]
	args["health_status_meaning"] = "etat de sante"
	check_health_status(args)
	if not args['valide']:
		return

	#Let's check if the value of rescue received exists
	args["rescue_received"] = args['text'].split(' ')[3]
	args["rescue_received_meaning"] = "Secourt recu"
	check_rescue_received(args)
	if not args['valide']:
		return

	#Let's record the report
	the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_mother'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])

	created_rer_report = ReportRER.objects.create(report = the_created_report, ris = args['the_concerned_ris'], rescue = args['concerned_rescue_received'], current_state = args['concerned_health_status'])
	
	args['valide'] = True
	args['info_to_contact'] = "Le rapport envoye de reponse au risque de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."
#-----------------------------------------------------------------




#-----------------------------------------------------------------
def record_death_report(args):

	args['mot_cle'] = "DEC"

	#Let's check if the person who send this message is a reporter
	check_if_is_reporter(args)
	print(args['valide'])
	if not args['valide']:
		return
	
	#Let's check if the message sent is composed by an expected number of values
	'''args["expected_number_of_values"] = getattr(settings,'EXPECTED_NUMBER_OF_VALUES','')[args['message_type']]
	check_number_of_values(args)
	if not args['valide']:
		return'''

	#Let's check if it is report about a child or a mother. We count the number of values sent
	#Let's check if the message sent is composed by an expected number of values
	check_number_of_values_dec(args)
	if not args['valide']:
		return

	#Let's check if the mother id sent is valid
	args["sent_mother_id"] = args['text'].split(' ')[1]
	check_mother_id_is_valid(args)
	if not args['valide']:
		return

	#Let's check if the location is valid
	args["location"] = args['text'].split(' ')[2]
	#date_meaning should be change to location_meaning
	args["date_meaning"] = "lieu de deces"
	check_location(args)
	if not args['valide']:
		return

	#Let's check if the death code is valid
	args["death_code"] = args['text'].split(' ')[3]
	args["death_code_meaning"] = "Code de deces"
	check_death_code(args)
	if not args['valide']:
		return

	if(args['dec_type'] == "DEC_CHILD"):
		#The report sent is a child report
		#Let's check if this mother has a child with the sent child number
		args["child_id"] = args['text'].split(' ')[4]
		check_child_exists(args)
		if not args['valide']:
			return

	if(args['dec_type'] == "DEC_WOMAN"):
		#We record a woman report
		pass


	#Now, everything is checked. Let's record the report
	the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_mother'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])

	created_dec_report = ReportDEC.objects.create(report = the_created_report, location = args['location'], death_code = args['death_code'])

	
	if(args['dec_type'] == "DEC_CHILD"):
		#Let's record informations related to the child
		report_dec_bebe = ReportDECBebe.objects.create(death_report = created_dec_report, concerned_child = args['concerned_child'])

	args['valide'] = True
	
	if(args['dec_type'] == "DEC_CHILD"):
		args['info_to_contact'] = "Le rapport de deces du bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."
	if(args['dec_type'] == "DEC_WOMAN"):
		args['info_to_contact'] = "Le rapport de deces de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."
#-----------------------------------------------------------------




#-----------------------------------------------------------------
def record_leave_report(args):

	args['mot_cle'] = "DEP"

	#Let's check if the person who send this message is a reporter
	check_if_is_reporter(args)
	print(args['valide'])
	if not args['valide']:
		return
	
	#Let's check if the message sent is composed by an expected number of values
	args["expected_number_of_values"] = getattr(settings,'EXPECTED_NUMBER_OF_VALUES','')[args['message_type']]
	check_number_of_values(args)
	if not args['valide']:
		return

	#Let's check if the mother id sent is valid
	args["sent_mother_id"] = args['text'].split(' ')[1]
	check_mother_id_is_valid(args)
	if not args['valide']:
		return

	#Let's record the report
	the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_mother'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])

	created_dep_report = ReportDEP.objects.create(report = the_created_report)
	
	args['valide'] = True
	args['info_to_contact'] = "Le rapport du depart de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."
#-----------------------------------------------------------------
