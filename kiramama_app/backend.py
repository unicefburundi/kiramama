from jsonview.decorators import json_view
from django.views.decorators.csrf import csrf_exempt
import re
from django.conf import settings
from kiramama_app.models import  Temporary, NotificationType
from recorders import *
import urllib


def identify_message(args):
	''' This function identifies which kind of message this message is. '''
	incoming_prefix = args['text'].split(' ')[0].upper()
	if args['text'].split(' ')[0].upper() in getattr(settings,'KNOWN_PREFIXES',''):
		#Prefixes and related meanings are stored in the dictionary "KNOWN_PREFIXES"
		args['message_type'] = getattr(settings,'KNOWN_PREFIXES','')[incoming_prefix]
	else:
		args['message_type'] = "UNKNOWN_MESSAGE"

def check_session(args):
	'''This function checks if there is an already created session'''
	reporter_phone_number = args['phone']
	concerned_reporter = Temporary.objects.filter(phone_number = reporter_phone_number)
	if len(concerned_reporter) < 1:
		args['has_session'] = False
	else:
		args['has_session'] = True

def eliminate_unnecessary_spaces(args):
    '''This function eliminate unnecessary spaces in an the incoming message'''
    the_incoming_message = args['text']
    print("The text before sub             "+the_incoming_message)
    #the_new_message = re.sub(' +',' ',the_incoming_message)

    #Messages from RapidPro comes with spaces replaced by '+'
    #Let's replace those '+' (one or more) by one space
    the_new_message = re.sub('[+]+',' ',the_incoming_message)

	# Find any comma
    the_new_message = urllib.unquote_plus(the_new_message)	

    #Let's eliminate spaces at the begining and the end of the message
    the_new_message = the_new_message.strip()
    print("The text after sub              "+the_new_message)
    args['text'] = the_new_message
    print("The text after sub args['text'] "+args['text'])


def check_necessary_configurations_are_done(args):
	''' This function checks if the necessary configurations are done '''

	#Let's check if all CPN are created in the database. No need to create CPN1
	cpn2 = NotificationType.objects.filter(code__iexact = "cpn2")
	if len(cpn2) < 1:
		args['valide'] = False
		args['info'] = "Exception. L administrateur du systeme n a pas cree la notification 'CPN2' dans la base de donnees."
	cpn3 = NotificationType.objects.filter(code__iexact = "cpn3")
	if len(cpn3) < 1:
		args['valide'] = False
		args['info'] = "Exception. L administrateur du systeme n a pas cree la notification 'CPN3' dans la base de donnees."
	cpn4 = NotificationType.objects.filter(code__iexact = "cpn4")
	if len(cpn4) < 1:
		args['valide'] = False
		args['info'] = "Exception. L administrateur du systeme n a pas cree la notification 'CPN4' dans la base de donnees."
	acc = NotificationType.objects.filter(code__iexact = "acc")
	if len(acc) < 1:
		args['valide'] = False
		args['info'] = "Exception. L administrateur du systeme n a pas cree la notification 'acc' (accouchement) dans la base de donnees."
	#ris = NotificationType.objects.filter(code__iexact = "ris")
	#if len(acc) < 1:
		#args['valide'] = False
		#args['info'] = "Exception. L administrateur du systeme n a pas cree la notification 'ris' (risque) dans la base de donnees."
	


@csrf_exempt
@json_view
def handel_rapidpro_request(request):
	'''This function receives requests sent by RapidPro.
	This function send json data to RapidPro as a response.'''
	#We will put all data sent by RapidPro in this variable
	incoming_data = {}

	#Two couples of variable/value are separated by &
	#Let's put couples of variable/value in a list called 'list_of_data'
	list_of_data = request.body.split("&")

	#Let's put all the incoming data in the dictionary 'incoming_data'
	for couple in list_of_data:
		incoming_data[couple.split("=")[0]] = couple.split("=")[1]

	#Let's assume that the incoming data is valid
	incoming_data['valide'] = True
	incoming_data['info'] = "The default information."

	#Because RapidPro sends the contact phone number by replacing "+" by "%2B"
	#let's rewrite the phone number in a right way.
	incoming_data['phone'] = incoming_data['phone'].replace("%2B","+")

	#Let's instantiate the variable this function will return
	response = {}

	#Let's eliminate unnecessary spaces in the incoming message
	eliminate_unnecessary_spaces(incoming_data)
	

	#The system can be used if some configurations are done
	check_necessary_configurations_are_done(incoming_data)
	if not incoming_data['valide']:
		print("T2T2T2")
		response['ok'] = False
		response['info_to_contact'] = incoming_data['info']
		return response

	#Let's check which kind of message this message is.
	identify_message(incoming_data)

	if(incoming_data['message_type']=='UNKNOWN_MESSAGE'):
		#Let's check if this contact is confirming his phone number
		#It means that he has an already created session
		check_session(incoming_data)
		if not(incoming_data['has_session']):
			#This contact doesn't have an already created session
			response['ok'] = False
			response['info_to_contact'] = "Le mot qui commence votre message n est pas reconnu par le systeme. Reenvoyez votre message en commencant par un mot cle valide."
			return response
		else:
			#This contact is confirming the phone number of his supervisor
			complete_registration(incoming_data)
			#response['ok'] = False
			response['ok'] = incoming_data['valide']
			response['info_to_contact'] = incoming_data['info_to_contact']
			return response



	if(incoming_data['message_type']=='SELF_REGISTRATION' or incoming_data['message_type']=='SELF_REGISTRATION_M'):
		#The contact who sent the current message is doing self registration  in the group of reporters
		temporary_record_reporter(incoming_data)
	if(incoming_data['message_type']=='PREGNANT_CASE_REGISTRATION'):
		#This contact is registering a pregnant case
		record_pregnant_case(incoming_data)
	if(incoming_data['message_type']=='PRENATAL_CONSULTATION_REGISTRATION'):
		#This contact is registering a pregnant case
		record_prenatal_consultation_report(incoming_data)
	if(incoming_data['message_type']=='BIRTH_REGISTRATION'):
		#This contact is registering a birth case
		record_birth_case_report(incoming_data)
	if(incoming_data['message_type']=='POSTNATAL_CARE_REPORT'):
		#This contact is registering a postnatal care report
		record_postnatal_care_report(incoming_data)
	if(incoming_data['message_type']=='CHILD_FOLLOW_UP_REPORT'):
		#This contact is registering a child follow up report
		record_child_follow_up_report(incoming_data)
	if(incoming_data['message_type']=='RISK_REPORT'):
		#This contact is reporting a risk
		record_risk_report(incoming_data)
	if(incoming_data['message_type']=='RESPONSE_TO_RISK_REPORT'):
		#This contact is reporting a response to a risk report
		record_response_to_risk_report(incoming_data)
	if(incoming_data['message_type']=='DEATH_REPORT'):
		#This contact is reporting a death report
		record_death_report(incoming_data)
	if(incoming_data['message_type']=='LEAVE_REPORT'):
		#This contact is reporting a pregnant mother who change where she live.
		record_leave_report(incoming_data)



	if(incoming_data['message_type']=='PREGNANT_CASE_REGISTRATION_M'):
		#This contact is modifying a pregnant case report
		modify_record_pregnant_case(incoming_data)
	if(incoming_data['message_type']=='PRENATAL_CONSULTATION_REGISTRATION_M'):
		#This contact is modifying a pregnant case report
		modify_record_prenatal_consultation_report(incoming_data)
	if(incoming_data['message_type']=='BIRTH_REGISTRATION_M'):
		#This contact is modifying a birth case report
		modify_record_birth_case_report(incoming_data)
	if(incoming_data['message_type']=='POSTNATAL_CARE_REPORT_M'):
		#This contact is modifying a postnatal care report
		modify_record_postnatal_care_report(incoming_data)
	if(incoming_data['message_type']=='CHILD_FOLLOW_UP_REPORT_M'):
		#This contact is modifying a child follow up report
		modify_record_child_follow_up_report(incoming_data)
	if(incoming_data['message_type']=='RISK_REPORT_M'):
		#This contact is modifying a risk report
		modify_record_risk_report(incoming_data)
	if(incoming_data['message_type']=='RESPONSE_TO_RISK_REPORT_M'):
		#This contact is modifying a response to a risk report
		modify_record_response_to_risk_report(incoming_data)
	if(incoming_data['message_type']=='DEATH_REPORT_M'):
		#This contact is modifying a death report
		modify_record_death_report(incoming_data)
	if(incoming_data['message_type']=='LEAVE_REPORT_M'):
		#This contact is modifying a pregnant mother departure report.
		modify_record_leave_report(incoming_data)


	if incoming_data['valide'] :
		#The message have been recorded
		response['ok'] = True
	else:
		#The message haven't been recorded
		response['ok'] = False

	if incoming_data['info_to_supervisors']:
		response['info_to_supervisors'] = incoming_data['info_to_supervisors']

	response['info_to_contact'] = incoming_data['info_to_contact']

	return response
