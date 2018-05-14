# -*- coding: utf-8 -*-
from kiramama_app.models import *
from health_administration_structure_app.models import *
from public_administration_structure_app.models import *

from django.db.models import Q
import re
import datetime
import requests
import json
from django.conf import settings
import unicodedata


def send_sms_through_rapidpro(args):
    ''' This function sends messages through rapidpro. Contact(s) and the message to send to them must be in args['data'] '''
    url = 'https://api.rapidpro.io/api/v2/broadcasts.json'
    token = getattr(settings, 'TOKEN', '')

    data = args['data']
    print "==="
    print data
    response = requests.post(url, headers={'Content-type': 'application/json', 'Authorization': 'Token %s' % token}, data = json.dumps(data))
    print response
    print "---"

def check_supervisor_phone_number_not_for_this_contact(args):
    '''This function checks if the contact didn't send his/her phone number in the place of the supervisor phone number'''

    if args['text'].split(' ')[4] in args['phone']:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Vous avez envoye votre numero de telephone a la place de celui de votre superviseur. Pour corriger, veuillez reenvoyer le message commencant par '"+args['mot_cle']+"' et contenant le vrai numero de ton superviseur"
        args['info_to_contact'] = "Ikosa. Wanditse inomero ya telefone yawe mu kibanza c inomero ya telefone yuwugukurikirana. Kosora mu kurungika kandi ubutumwa butangurwa na '"+args['mot_cle']+"' ushiremwo n inomero ya telefone yukuri yuwugukurikirana"
    else:
        args['valide'] = True
        args['info_to_contact'] = "Le numero de telephone du superviseur est bien note."


def check_if_is_reporter(args):
    ''' This function checks if the contact who sent the current message is a reporter. Reporter is CHW '''
    concerned_reporter = CHW.objects.filter(phone_number = args['phone'])
    if len(concerned_reporter) < 1:
        # This person is not in the list of reporters
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Vous ne vous etes pas enregistre pour pouvoir donner des rapports. Veuillez vous enregistrer en envoyant le message d enregistrement commencant par REG"
        args['info_to_contact'] = "Ikosa. Ntiwiyandikishije kugira ushobore gutanga raporo. Kugira ushobore gutanga ama raporo, banza wiyandikishe mu kurungika mesaje yo kwiyandikisha itangurwa nakajambo REG"
        return

    one_concerned_reporter = concerned_reporter[0]

    if not one_concerned_reporter.cds:
        # The CDS of this reporter is not known
        args['valide'] = False
        args['info_to_contact'] = "Exception. Votre site n est pas enregistre dans le systeme. Veuillez contacter l administrateur du systeme"
        return

    args['the_sender'] = one_concerned_reporter
    args['facility'] = one_concerned_reporter.cds
    args['supervisor_phone_number'] = one_concerned_reporter.supervisor_phone_number
    args['valide'] = True
    args['info_to_contact'] = " Le bureau d affectation de ce rapporteur est connu "


def check_number_of_values(args):
    ''' This function checks if the message sent is composed by an expected number of values '''
    expected_number_of_values_string = args["expected_number_of_values"]
    expected_number_of_values_int = int(expected_number_of_values_string)

    if len(args['text'].split(' ')) < expected_number_of_values_int:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Vous avez envoye peu de valeurs. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Warungitse mesage idakwiye. Mu gukosora, subira urungike iyo mesage itangurwa na '"+args['mot_cle']+"' yanditse neza"
    if len(args['text'].split(' ')) > expected_number_of_values_int:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Vous avez envoye beaucoup de valeurs. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Warungitse mesage ndende. Mu gukosora, subira urungike iyo mesage itangurwa na '"+args['mot_cle']+"' yanditse neza"
    if len(args['text'].split(' ')) == expected_number_of_values_int:
        args['valide'] = True
        args['info_to_contact'] = "Le nombre de valeurs envoye est correct."


def check_number_of_values_ris(args):
    ''' This function checks if the RIS report sent is composed by an expected number of values '''

    # I have to change how the two below variables are initiated. Values must be taken from settings.py
    number_of_values_for_a_child = 4
    number_of_values_for_a_woman = 3

    if((len(args['text'].split(' ')) != number_of_values_for_a_child) and (len(args['text'].split(' ')) != number_of_values_for_a_woman) ):
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Le nombre de valeurs envoye n est pas correct. Il doit etre '"+str(number_of_values_for_a_child)+"' (pour un enfant) ou '"+str(number_of_values_for_a_woman)+"' (pour une maman). Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Igitigiri civyo warungitse sico. Gitegerezwa kuba '"+str(number_of_values_for_a_child)+"' (mugihe iyo mesaje yerekeye umwana) canke '"+str(number_of_values_for_a_woman)+"' (mu gihe iyo mesaje yerekeye umuvyeyi). Mu gukosora, subira urungike iyo mesage itangurwa na '"+args['mot_cle']+"' yanditse neza"
    if(len(args['text'].split(' ')) == number_of_values_for_a_child):
        # This contact is sending a RIS report for a child
        args['valide'] = True
        args['ris_type'] = "RIS_CHILD"
        args['info_to_contact'] = "Le rapport envoye concerne un enfant"
    if(len(args['text'].split(' ')) == number_of_values_for_a_woman):
        # This contact is sending a RIS report for a woman
        args['valide'] = True
        args['ris_type'] = "RIS_WOMAN"
        args['info_to_contact'] = "Le rapport envoye concerne une maman"


def check_number_of_values_dec(args):
    ''' This function checks if the DEC report sent is composed by an expected number of values '''

    # I have to change how the two below variables are initiated. Values must be taken from settings.py
    number_of_values_for_a_child = 5
    number_of_values_for_a_woman = 4
    if((len(args['text'].split(' ')) != number_of_values_for_a_child) and (len(args['text'].split(' ')) != number_of_values_for_a_woman) ):
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Le nombre de valeurs envoye n est pas correct. Il doit etre '"+str(number_of_values_for_a_child)+"' (pour un enfant) ou '"+str(number_of_values_for_a_woman)+"' (pour une maman). Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Igitigiri civyo warungitse sico. Gitegerezwa kuba '"+str(number_of_values_for_a_child)+"' (mugihe iyo mesaje yerekeye umwana) canke '"+str(number_of_values_for_a_woman)+"' (mu gihe iyo mesaje yerekeye umuvyeyi). Mu gukosora, subira urungike iyo mesage itangurwa na '"+args['mot_cle']+"' yanditse neza"
    if(len(args['text'].split(' ')) == number_of_values_for_a_child):
        # This contact is sending a DEC report for a child
        args['valide'] = True
        args['dec_type'] = "DEC_CHILD"
        args['info_to_contact'] = "Le rapport envoye concerne un enfant"
    if(len(args['text'].split(' ')) == number_of_values_for_a_woman):
        # This contact is sending a DEC report for a woman
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
        # args['info_to_contact'] = "Erreur. La date indiquee pour '"+args["date_meaning"]+"' n est pas valide. Verifier si vous avez mis chaque valeur dans sa place. Pour corriger, veuillez reenvoyer un message commencant par "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. '"+args["date_meaning"]+"' siyo. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    sent_date = given_date[0:2]+"-"+given_date[2:4]+"-20"+given_date[4:]

    sent_date_without_dash = sent_date.replace("-","")
    try:
        date_sent = datetime.datetime.strptime(sent_date_without_dash, "%d%m%Y").date()
    except:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. La date indiquee pour '"+args["date_meaning"]+"' n est pas valide. Verifier si vous avez mis chaque valeur dans sa place. Pour corriger, veuillez reenvoyer un message commencant par "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. '"+args["date_meaning"]+"' watanze siryo. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    if date_sent <= datetime.datetime.now().date():
        # The reporter can not report for a past date
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Vous n avez pas indiquez une date du futur pour '"+args["date_meaning"]+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. '"+args["date_meaning"]+"' ryararenganye. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
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
        # args['info_to_contact'] = "Erreur. La date indiquee pour '"+args["date_meaning"]+"' n est pas valide. Verifier si vous avez mis chaque valeur dans sa place. Pour corriger, veuillez reenvoyer un message commencant par "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. '"+args["date_meaning"]+"' watanze siryo. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    sent_date = given_date[0:2]+"-"+given_date[2:4]+"-20"+given_date[4:]

    sent_date_without_dash = sent_date.replace("-","")
    try:
        date_sent = datetime.datetime.strptime(sent_date_without_dash, "%d%m%Y").date()
    except:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. La date indiquee pour '"+args["date_meaning"]+"' n est pas valide. Verifier si vous avez mis chaque valeur dans sa place. Pour corriger, veuillez reenvoyer un message commencant par "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. '"+args["date_meaning"]+"' watanze siryo. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    if date_sent > datetime.datetime.now().date():
        # The reporter can not report for a past date
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Vous avez indiquez une date non acceptable pour '"+args["date_meaning"]+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. '"+args["date_meaning"]+"' watanze ntiribaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
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
        # args['info_to_contact'] = "Erreur. La date indiquee pour '"+args["date_meaning"]+"' n est pas valide. Verifier si vous avez mis chaque valeur dans sa place. Pour corriger, veuillez reenvoyer un message commencant par "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. '"+args["date_meaning"]+"' watanze ntiribaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    sent_date = given_date[0:2]+"-"+given_date[2:4]+"-20"+given_date[4:]

    sent_date_without_dash = sent_date.replace("-","")
    try:
        date_sent = datetime.datetime.strptime(sent_date_without_dash, "%d%m%Y").date()
    except:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. La date indiquee pour '"+args["date_meaning"]+"' n est pas valide. Verifier si vous avez mis chaque valeur dans sa place. Pour corriger, veuillez reenvoyer un message commencant par "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. '"+args["date_meaning"]+"' watanze ntiribaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    if date_sent > datetime.datetime.now().date():
        # The reporter can not report for a past date
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Vous avez indiquez une date qui n est pas encore arrivee pour '"+args["date_meaning"]+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. '"+args["date_meaning"]+"' watanze ntirirabaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
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
        # args['info_to_contact'] = "Erreur. Le niveau de risque indique n est pas reconnu par le systeme. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Ico watanze cerekana uko umuvyeyi amerewe ntikizwi. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
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
        # args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["date_meaning"]+"' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Ico wanditse kuvyerekeye '"+args["date_meaning"]+"' sico. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
    else:
        args['location'] = locations[0]
        args['valide'] = True
        args['info_to_contact'] = "Le lieu indique est valide."


def check_death_code(args):
    ''' This function checks if the death code sent is valid '''
    death_code_sent = args["death_code"]
    death_code_set = DeathCode.objects.filter(Death_code__iexact=death_code_sent)
    if(len(death_code_set) < 1):
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["death_code_meaning"]+"' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Ico wanditse kuvyerekeye '"+args["death_code_meaning"]+"' sico. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
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
        # The phone number is not well written
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Le numero de telephone n est pas bien ecrit. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Inomero ya telefone ntiyanditse neza. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
    else:
        args["phone_number"] = phone_number_to_check_no_space
        args['valide'] = True
        args['info_to_contact'] = "Le numero de telephone est bien ecrit."


def check_if_is_reporter(args):
    ''' This function checks if the contact who sent the current message is a CHW '''
    concerned_chw = CHW.objects.filter(phone_number = args['phone'])
    if len(concerned_chw) < 1:
        # This person is not in the list of community health workers
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Vous ne vous etes pas enregistre pour pouvoir donner des rapports. Veuillez vous enregistrer en envoyant le message d enregistrement commencant par REG"
        args['info_to_contact'] = "Ikosa. Ntiwiyandikishije kugira ushobora gutanga ama raporo. Usabwe kubanza kwiyandikisha mu kurungika ya mesaje itangurwa na 'REG'"
        return

    one_concerned_chw = concerned_chw[0]

    if not one_concerned_chw.cds:
        # The CDS of this reporter is not known
        args['valide'] = False
        args['info_to_contact'] = "Exception. Votre site n est pas enregistre dans le systeme. Veuillez contacter l administrateur du systeme"
        return
    
    args['the_sender'] = one_concerned_chw
    args['facility'] = one_concerned_chw.cds
    args['supervisor_phone_number'] = one_concerned_chw.supervisor_phone_number
    args['sub_colline'] = one_concerned_chw.sub_colline
    args['valide'] = True
    args['info_to_contact'] = "Le bureau d affectation de ce rapporteur est connu"



def check_if_contact_is_from_hf(args):
    ''' This function checks if the contact who sent the current message is a supervisor of a CHW '''
    concerned_chw = CHW.objects.filter(supervisor_phone_number = args['phone'])
    if len(concerned_chw) < 1:
        # This person is not a supervisor of any community health worker
        args['valide'] = False
        args['info_to_contact'] = "Ikosa. Inomero ya telefone yawe ntidushoboye kuyimenya. Kugira itange ubwo butumwa iba yaranditswe numuremesha kiyago ariko ariyandikisha."
        return

    one_concerned_chw = concerned_chw[0]

    if not one_concerned_chw.cds:
        # The CDS of this reporter is not known
        args['valide'] = False
        args['info_to_contact'] = "Exception. Votre site n est pas enregistre dans le systeme. Veuillez contacter l administrateur du systeme"
        return
    
    args['facility'] = one_concerned_chw.cds
    args['supervisor_phone_number'] = one_concerned_chw.supervisor_phone_number
    args['sub_colline'] = one_concerned_chw.sub_colline
    args['valide'] = True
    args['info_to_contact'] = "Le numero de telephone qui rapporte est connu"


def check_mother_id_is_valid(args):
    ''' This function checks if the mother id sent is valid '''
    the_sent_mother_id = args["sent_mother_id"]
    filtered_mother = Mother.objects.filter(id_mother = the_sent_mother_id)
    if(len(filtered_mother) < 1):
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Une maman avec cet identifiant n existe pas dans le systeme. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Nta muvyeyi abaho afise iyo numero wanditse. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
    else:
        args['concerned_mother'] = filtered_mother[0]
        args['valide'] = True
        args['info_to_contact'] = "L identifiant de la maman est valide"


def check_mother_is_affected_somewhere(args):
    ''' This function checks if a given mother is affected somewhere '''
    if not args['concerned_mother'].is_affected_somewhere:
        args['valide'] = False
        args['info_to_contact'] = "Ikosa. Umupfasoni '"+args['concerned_mother'].id_mother+"' ntituzi aho ubu aba. Nimba aba aho ukorera, banza ubimenyeshe mu kurungika mesaje itangurwa nakajambo 'REC' yanditse neza"
    else:
        args['valide'] = True
        args['info_to_contact'] = "Aho umupfasoni '"+args['concerned_mother'].id_mother+"' aba harazwi"


def check_mother_has_ris_report(args):
    ''' This function checks if the current mother has a RIS report recorded '''
    mother_set = ReportRIS.objects.filter(report__mother = args['concerned_mother'])

    if len(mother_set) < 1:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Il n y a pas de risque rapportee pour la maman '"+args['concerned_mother'].id_mother+"'"
        args['info_to_contact'] = "Ikosa. Nta mesaje irigire irungikwa ivuga ukutamererwa neza kw umuvyeyi nomero '"+args['concerned_mother'].id_mother+"'"
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
        # args['info_to_contact'] = "Erreur. Le nom du CPN indique n existe pas dans le systeme. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Ibiranga CPN wanditse ntibibaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
    else:
        args['specified_cpn'] =  filtered_cpn[0]
        args['valide'] = True
        args['info_to_contact'] = "Le nom du CPN indique existe dans le systeme"


def check_cpn_order_respected(args):
    '''
    This function checks if the CPN order is respected for the current woman
    The first CPN should be number 2 (cpn_number = 2), the second number 3, etc
    '''
    the_last_cpn_number_for_this_mother = 1
    the_sent_cpn_number = args["concerned_cpn"].cpn_number
    #Let's check if the CPN indicated is the expected one
    the_last_cpns_for_this_mother = ReportCPN.objects.filter(report__mother = args['concerned_woman']).order_by('id').reverse()
    
    if(len(the_last_cpns_for_this_mother) > 0):
        #At least one CPN have been reported for this mother

        the_last_cpn_number_for_this_mother = the_last_cpns_for_this_mother[0].concerned_cpn.cpn_number

    
    the_expected_cpn_number = the_last_cpn_number_for_this_mother + 1
        
    if(the_sent_cpn_number != the_expected_cpn_number):
        args['valide'] = False
        #args['info_to_contact'] = "Erreur. Le CPN envoye n est pas celui attendu pour cette maman."
        args['info_to_contact'] = "Ikosa. Iyo raporo CPN utanze siyo yari yitezwe kuri uwo mupfasoni."
        return

    args['valide'] = True
    args['info_to_contact'] = "Raporo CPN itanzwe niyo yari yitezwe kuri uyo mupfasoni."

    
def check_is_float(args):
    ''' This function checks if a given value is a float '''

    expression = r'^([0-9]+.[0-9]+)$|^([0-9]+)$|^([0-9]+,[0-9]+)$'

    value_to_check = args["float_value"]

    if re.search(expression, value_to_check) is None:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["date_meaning"]+"' n est pas valide. Pour corriger,  veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Ico wanditse kuvyerekeye '"+args["date_meaning"]+"' ntikibaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
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
        # args['info_to_contact'] = "Erreur. Le numero de l enfant envoye n existe pas. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Wanditse inomero yumwana itabaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
    else:
        args['child_number'] = child_numbers[0]
        args['valide'] = True
        args['info_to_contact'] = "Le numero de l enfant envoye est valide."


def check_child_code_order(args):
    ''' This function is used to check if the order of child codes is respected '''
    if args["child_code"] != '01':
        # Let's check if child numbers which comes before this one have been used 
        current_child_number = args['child_number'].child_number
        previous_child_number = current_child_number-1

        previous_child_numbers = ChildNumber.objects.filter(child_number = previous_child_number)
        if len(previous_child_numbers) < 1:
            args['valide'] = False
            args['info_to_contact'] = "Exception. Un 'ChildNumber' qui precede le courant n est pas trouve"
            return
        one_concerned_previous_child_number = previous_child_numbers[0]
        # Let check if this mother has a ReportNSC with this ChildNumber 
        nsc_with_the_previous_child_number = ReportNSC.objects.filter(report__mother=args['concerned_woman'], child_number=one_concerned_previous_child_number)
        if len(nsc_with_the_previous_child_number) < 1:
            # The previous child number not used
            args['valide'] = False
            args['info_to_contact'] = "Ikosa. Inomero z abana zitegerezwa gukoreshwa ku murongo. Inomero '"+one_concerned_previous_child_number.child_code_designation+"' iza imbere ya '"+args["child_code"]+"'"
        else:
            args['valide'] = True
            args['info_to_contact'] = "Inomero yakoreshejwe iranga umwana niyo"


def check_allaitement_maternel(args):
    ''' This function is used to check if the value sent for "Allaitement maternel" is valid '''
    the_sent_value = args["allaitement_maternel"]

    allaitements = BreastFeed.objects.filter(breast_feed_option_name__iexact = the_sent_value)
    if(len(allaitements) < 1):
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. La valeur envoye pour 'Allaitement maternel' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Ico wanditse kuvyerekeye 'Igihe umwana yonkerejweko ubwa mbere' ntikibaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
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
        # args['info_to_contact'] = "Erreur. La valeur envoyee pour le genre du nouveau nee n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Ico wanditse kuvyerekeye 'Igitsina c umwana' sivyo. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
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
        # args['info_to_contact'] = "Erreur. Le numero de l enfant envoye n existe pas dans le systeme. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Inomero y umwana wanditse ntibaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return
    child_number = child_numbers[0]

    birth_reports_with_this_mother_and_childcode = ReportNSC.objects.filter(report__mother=args['concerned_mother'], child_number=child_number)

    if(len(birth_reports_with_this_mother_and_childcode) < 1):
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. La dame '"+args['concerned_mother'].id_mother+"' n a pas de naissance '"+the_sent_child_number+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Umupfasoni nomero '"+args['concerned_mother'].id_mother+"' nta mwana nomero '"+the_sent_child_number+"' afise. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
    else:
        args['concerned_child'] = birth_reports_with_this_mother_and_childcode[0]
        args['child_number'] = child_number
        args['valide'] = True
        args['info_to_contact'] = "L enfant specifie a ete bien identifie"


def check_con_code(args):
    ''' This function checks if the CON code sent is valid '''

    the_sent_con_code = args["con_code"]
    con_codes = CON.objects.filter(con_designation__iexact=the_sent_con_code)

    if(len(con_codes) < 1):
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. La valeur envoyee pour 'CON effectuee' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Ico wanditse ku vyerekeye 'incuro umuvyeyi yagiriye kw ivuriro inyuma yo kwibaruka' sico. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
    else:
        args['concerned_con'] = con_codes[0]
        args['valide'] = True
        args['info_to_contact'] = "La valeur envoyee pour 'CON effectuee' est valide" 


def check_symptoms(args):
    ''' This function checks if symptoms sent are valid '''

    sent_symptoms = args["symptoms"]
    # Symptoms are separated by comma. Let's put them in a list.
    sent_symptoms_list = sent_symptoms.split(",")

    symptoms_kirundi_names = ""
    first_symptom = True

    red_symptoms_kirundi_names = ""
    red_first_symptom = True

    # Let's assume that all symbols are correct
    valid = True

    # Let's check if every element of the list is a valid symptom
    for current_symptom in sent_symptoms_list:
        if(valid is True):
            symptoms = Symptom.objects.filter(symtom_designation__iexact=current_symptom)
            if(len(symptoms) < 1):
                valid = False
                not_valid_symptom = current_symptom
                args['valide'] = False
                # args['info_to_contact'] = "Erreur. Le symptome '"+not_valid_symptom+"' n existe pas dans le systeme. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
                args['info_to_contact'] = "Ikosa. Ikimenyetso '"+not_valid_symptom+"' ntikibaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
            else:
                one_symptom = symptoms[0]
                kir_symptom_name = one_symptom.kirundi_name

                if first_symptom:
                    symptoms_kirundi_names = symptoms_kirundi_names+""+kir_symptom_name
                    first_symptom = False
                else:
                    symptoms_kirundi_names = symptoms_kirundi_names+", "+kir_symptom_name

                if one_symptom.is_red_symptom:
                    if red_first_symptom:
                        red_symptoms_kirundi_names = red_symptoms_kirundi_names+""+kir_symptom_name
                        red_first_symptom = False
                    else:
                        red_symptoms_kirundi_names = red_symptoms_kirundi_names+", "+kir_symptom_name
                    


    if(valid is True):
        # All sent symptoms are known in the system
        args['checked_symptoms_list'] = sent_symptoms_list
        args['kirundi_symptoms_names'] = symptoms_kirundi_names
        args['kirundi_red_symptoms_names'] = red_symptoms_kirundi_names
        args['valide'] = True
        args['info_to_contact'] = "La liste des symboles envoyes est valide"


def check_health_status(args):
    ''' This function checks if the health status values are valid '''

    sent_health_status_value = args["health_status_value"]

    health_status_group = HealthStatus.objects.filter(health_status_desigantion__iexact = sent_health_status_value)

    if(len(health_status_group) < 1):
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["health_status_meaning"]+"' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Ico warungitse kuvyerekeye '"+args["health_status_meaning"]+"' ntikibaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
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
        # args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["rescue_received_meaning"]+"' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Ico warungitse kuvyerekeye '"+args["rescue_received_meaning"]+"' ntikibaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
    else:
        args['concerned_rescue_received'] = rescue_received_set[0]
        args['valide'] = True
        args['info_to_contact'] = "La valeur envoyee pour '"+args["rescue_received_meaning"]+"' est valide" 


def check_vac_code(args):
    ''' This function cheks if the vaccine code sent is valide '''
    sent_vaccine_code = args["vac_code"]

    concerned_vac_code_objects = VAC.objects.filter(vac_designation__iexact=sent_vaccine_code)

    if(len(concerned_vac_code_objects) < 1):
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Le code envoye pour la vaccination effectuee n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Ico warungitse kuvyerekeye 'urucanco rwagizwe' ntikibaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
    else:
        args['concerned_vac'] = concerned_vac_code_objects[0]
        args['valide'] = True
        args['info_to_contact'] = "Le code envoye pour la vaccination effectuee est valide"

# This function will be deleted and we will use 'def check_mother_id_is_valid(args)' wherever it is used


def check_mother_id_is_valide(args):
    ''' This function cheks if the mother id is valide '''
    sent_mother_id = args["sent_mother_id"]

    concerned_mother = Mother.objects.filter(id_mother = sent_mother_id)
    if len(concerned_mother) < 1:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Une maman avec cet identifiant n existe pas dans le systeme. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Umuvyeyi afise iyo numero uhejeje gutanga ntabaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
    else:
        args['concerned_mother'] = concerned_mother[0]
        args['valide'] = True
        args['info_to_contact'] = "L identifiant de la mere envoye est valide."
# ======================reporters self registration==================================


def check_facility(args):
    ''' This function checks if the facility code sent by the reporter exists '''
    the_facility_code = args['text'].split(' ')[1]
    concerned_facility = CDS.objects.filter(code = the_facility_code)
    if (len(concerned_facility) > 0):
        args['valide'] = True
        args['info_to_contact'] = "Le code CDS envoye est reconnu."
    else:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Le code envoye n est pas associe a un CDS. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Wanditse inomero y ivuriro itabaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"


def check_supervisor_phone_number(args):
    ''' This function checks if the phone number of the supervisor is well written '''
    the_supervisor_phone_number = args['text'].split(' ')[4]
    the_supervisor_phone_number_no_space = the_supervisor_phone_number.replace(" ", "")
    # expression = r'^(\+?(257)?)((62)|(79)|(71)|(76))([0-9]{6})$'
    expression = r'^(\+?(257)?)((61)|(62)|(68)|(69)|(71)|(72)|(75)|(76)|(79))([0-9]{6})$'
    if re.search(expression, the_supervisor_phone_number_no_space) is None:
        # The phone number is not well written
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Le numero de telephone du superviseur n est pas bien ecrit. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle REG"
        args['info_to_contact'] = "Ikosa. Wanditse nabi inomero ya telefone yuwugukurikirana. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
    else:
        args['valide'] = True
        args['info_to_contact'] = "Le numero de telephone du superviseur est bien ecrit."


def save_temporary_the_reporter(args):
    same_existing_temp = Temporary.objects.filter(phone_number = args['phone'])
    if len(same_existing_temp) > 0:
        same_existing_temp = same_existing_temp[0]
        same_existing_temp.delete()
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Vous devriez envoyer le numero de telephone de votre superviseur seulement. Pour corriger, veuillez recommencer l enregistrement."
        args['info_to_contact'] = "Ikosa. Wari wasabwe kurungika inomero ya telefone yuwugukurikirana gusa. Mu gukosora subira utangure kwiyandikisha"
    else:
        the_phone_number = args['phone']

        the_facility_code = args['text'].split(' ')[1]

        facility = CDS.objects.filter(code = the_facility_code)
        if len(facility) > 0:
            # Let's determine the concerned facility
            the_concerned_facility = facility[0]

            the_supervisor_phone_number = args['text'].split(' ')[4]
            the_supervisor_phone_number_no_space = the_supervisor_phone_number.replace(" ", "")

            if len(the_supervisor_phone_number_no_space) == 8:
                the_supervisor_phone_number_no_space = "+257"+the_supervisor_phone_number_no_space
            if len(the_supervisor_phone_number_no_space) == 11:
                the_supervisor_phone_number_no_space = "+"+the_supervisor_phone_number_no_space

            # Let's determine the concerned sub hill
            the_hill_name = args['text'].split(' ')[2].title()

            the_sub_hill_name = args['text'].split(' ')[3].title()

            the_hill = Colline.objects.filter(name__iexact=the_hill_name)
            if len(the_hill) < 1:
                args['valide'] = False
                # args['info_to_contact'] = "Erreur. Le nom de la colline envoye n est pas valide. Pour corriger, reenvoyer le message bien ecrit commencant par REG"
                args['info_to_contact'] = "Ikosa. Izina ryumusozi wanditse ntiribaho. Mu gukosora, subira urungike iyo mesaje itangurwa na 'REG' yanditse neza"
                return
            the_concerned_hill = the_hill[0]

            # Let's check first if the sub hill name sent exist in the system
            the_sub_hill0 = SousColline.objects.filter(name__iexact=the_sub_hill_name)
            if len(the_sub_hill0) < 1:
                args['valide'] = False
                # args['info_to_contact'] = "Erreur. Le nom de la sous colline envoye n est pas valide. Pour corriger, reenvoyer le message bien ecrit commencant par REG"
                args['info_to_contact'] = "Ikosa. Izina ryagacimbiri wanditse ntiribaho . Mu gukosora, subira urungike iyo mesaje itangurwa na 'REG' yanditse neza"
                return
            # If the sub hill name sent by the reporter exist in the system, let's check if it's linked to the specified hill
            the_sub_hill1 = SousColline.objects.filter(name__iexact = the_sub_hill_name, colline = the_concerned_hill)
            if len(the_sub_hill1) < 1:
                args['valide'] = False
                # args['info_to_contact'] = "Erreur. Il n y a pas de sous colline '"+args['text'].split(' ')[3].title()+"' dans la colline '"+args['text'].split(' ')[2].title()+"'."
                args['info_to_contact'] = "Ikosa. Nta gacimbiri kabaho kitwa '"+args['text'].split(' ')[3].title()+"' ku mutumba '"+args['text'].split(' ')[2].title()+"'. Mu gukosora, subira urungike iyo mesaje itangurwa na 'REG' yanditse neza"
                return
            the_concerned_sub_hill = the_sub_hill1[0]

            Temporary.objects.create(phone_number=the_phone_number, facility=the_concerned_facility, supervisor_phone_number=the_supervisor_phone_number_no_space,
            	sub_hill=the_concerned_sub_hill)
            args['valide'] = True
            # args['info_to_contact'] = "Veuillez reenvoyer seulement le numero de telephone de votre superviseur s il vous plait."
            args['info_to_contact'] = "Rungika inomero ya terefone y uwugukurikirana yonyene atakindi ugeretseko kugira iyandikwa ryawe riherahezwe."


def check_has_already_session(args):
    '''This function checks if this contact has a session'''
    same_existing_temp = Temporary.objects.filter(phone_number = args['phone'])
    if len(same_existing_temp) > 0:
        same_existing_temp = same_existing_temp[0]
        same_existing_temp.delete()
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Vous devriez envoyer le numero de telephone de votre superviseur seulement. Pour corriger, veuillez recommencer l enregistrement."
        args['info_to_contact'] = "Ikosa. Wari wasabwe kurungika numero ya telefone yuwugukurikirana gusa. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
    else:
        args['valide'] = True
        args['info_to_contact'] = "Ok."

def check_risk_report_exists_for_given_woman(args):
    '''This function checks if there is a risk report registered for 
    a given woman'''
    the_concerned_woman = args['concerned_mother']
    concerned_risk_reports = ReportRIS.objects.filter(report__mother = the_concerned_woman)
    if len(concerned_risk_reports) > 0:
        one_concerned_risk_reports = concerned_risk_reports[0]
        args['valide'] = True
        args['one_concerned_risk_reports'] = one_concerned_risk_reports
        args['info_to_contact'] = "Ok."
    else:
        args['valide'] = False
        args['info_to_contact'] = "Ikosa. Nta muremesha kiyago ararungika mesaje ivuga ko umupfasoni afise iyo numero agwaye."

def get_national_sup_phone_number():
    urns = []
    national_supervisors = AllSupervisor.objects.filter(is_national_supervisor = True)
    if(len(national_supervisors) > 0):
        for n_s in national_supervisors:
            phone_number = n_s.phone_number
            if len(phone_number) == 8:
                phone_number = "+257"+phone_number
            phone_number = "tel:"+phone_number
            #phone_number = unicodedata.normalize('NFKD', phone_number).encode('ascii','ignore')
            urns.append(phone_number)
    return urns

def activate_inactive_chw(args):
    ''' This function activate inactive CHWs '''
    chw_phone_number = args['phone']
    concerned_chw = CHW.objects.filter(phone_number = chw_phone_number)
    if len(concerned_chw) < 1:
        return
    concerned_chw = concerned_chw[0]
    if concerned_chw.is_active == False:
        concerned_chw.is_active = True
        concerned_chw.save()


def temporary_record_reporter(args):
    '''This function is used to record temporary a reporter'''
    if(args['text'].split(' ')[0].upper() == 'REG'):
        args['mot_cle'] = 'REG'
        # Because REG is used to do the self registration and not the update, if the phone user sends a message starting with REG and             # he/she is already a reporter, we don't allow him/her to continue
        check_if_is_reporter(args)
        if(args['valide'] is True):
            # This contact is already a reporter and can't do the registration the second time
            args['valide'] = False
            # args['info_to_contact'] = "Erreur. Vous vous etes deja enregistre. Si vous voulez modifier votre enregistrement, envoyer le message commencant par le mot cle 'REGM'"
            args['info_to_contact'] = "Ikosa. Warahejeje kwiyandikisha. Nimba harico ushaka guhindira kukuntu wiyandikishije, rungika mesaje yo guhubura itangurwa na 'REGM'"
            return
    if(args['text'].split(' ')[0].upper() == 'REGM'):
        args['mot_cle'] = 'REGM'

    # Let's check if this contact has an existing session
    check_has_already_session(args)
    if not args['valide']:
        return

    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the code of CDS is valid
    check_facility(args)
    if not args['valide']:
        return

    # Let's check is the supervisor phone number is valid
    check_supervisor_phone_number(args)
    if not args['valide']:
        return

    # La ligne ci dessous ne peut pas fonctionner sur les instance Anonimise de RapidPro
    # Let's check if the contact didn't send his/her number in the place of the supervisor number
    check_supervisor_phone_number_not_for_this_contact(args)
    if not args['valide']:
        return

    # Let's temporary save the reporter
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

        # if (the_one_existing_temp.supervisor_phone_number == the_sup_phone_number_without_spaces):
        if (the_sup_phone_number_without_spaces in the_one_existing_temp.supervisor_phone_number) and (len(the_sup_phone_number_without_spaces) >= 8):
            # The confirmation of the phone number of the supervisor pass


            # Let's check if this contact is not registered with the same data as he/she is registered
            # If it is the case, this contact is doing an unnecessary registration
            # check_duplication = CHW.objects.filter(phone_number = the_one_existing_temp.phone_number, cds = the_one_existing_temp.facility, sub_colline = the_one_existing_temp.sub_hill, sub_colline.colline = the_one_existing_temp.sub_hill.colline, supervisor_phone_number = the_one_existing_temp.supervisor_phone_number)
            # check_duplication = CHW.objects.filter(phone_number = the_one_existing_temp.phone_number, cds = the_one_existing_temp.facility, sub_colline = the_one_existing_temp.sub_hill, supervisor_phone_number = the_one_existing_temp.supervisor_phone_number)
            check_duplication = CHW.objects.filter(phone_number = the_one_existing_temp.phone_number)
            the_existing_contact = 0
            is_first_registration = True
            if len(check_duplication) > 0:
                # This contact is doing an update. We update the existing registration
                is_first_registration = False
                the_existing_contact = check_duplication[0]
                # the_existing_contact.delete()
                '''# Let's check if the sent colline is the same with the already saved colline
                the_already_saved_colline = check_duplication[0].sub_colline.colline
                the_sent_colline = the_one_existing_temp.sub_hill.colline

                if(the_sent_colline == the_already_saved_colline):
                    # This phone user is trying to register himself/herself twice
                    # Already registered and nothing to update
                    args['valide'] = False
                    args['info_to_contact'] = "Erreur. Vous vous etes deja enregistre sur ce site et avec ce numero de telephone du superviseur. Envoyer un message bien ecrit et commencant par un mot cle valide ou X pour fermer la session"
                    the_one_existing_temp.delete()
                    return'''

            '''check_duplication = ''


            # Let's check if the contact wants to update his facility
            check_duplication = Reporter.objects.filter(~Q(facility = the_one_existing_temp.facility), phone_number = the_one_existing_temp.phone_number, supervisor_phone_number = the_one_existing_temp.supervisor_phone_number)
            if len(check_duplication) > 0:
                # this contact wants to update his facility
                check_duplication = check_duplication[0]
                check_duplication.facility = the_one_existing_temp.facility
                check_duplication.save()
                args['valide'] = True
                args['info_to_contact'] = "Modification reussie. Votre nouveau site d affectation est : "+the_one_existing_temp.facility.name
                the_one_existing_temp.delete()
                return

            check_duplication = ''



            # Let's check if the contact wants to update the phone number of his supervisor
            check_duplication = Reporter.objects.filter(~Q(supervisor_phone_number = the_one_existing_temp.supervisor_phone_number), phone_number = the_one_existing_temp.phone_number, facility = the_one_existing_temp.facility)
            if len(check_duplication) > 0:
                # this contact wants to update the phone number of his supervisor
                check_duplication = check_duplication[0]
                check_duplication.supervisor_phone_number = the_one_existing_temp.supervisor_phone_number
                check_duplication.save()
                args['valide'] = True
                args['info_to_contact'] = "Modification reussie. Le nouveau numero de telephone de votre superviseur est : "+the_one_existing_temp.supervisor_phone_number+""
                the_one_existing_temp.delete()
                return

            check_duplication = ''



            # Let's check if the contact wants to update both the CDS and the phone number of his supervisor
            check_duplication = Reporter.objects.filter(~Q(facility = the_one_existing_temp.facility), ~Q(supervisor_phone_number = the_one_existing_temp.supervisor_phone_number), phone_number = the_one_existing_temp.phone_number)
            if len(check_duplication) > 0:
                # this contact wants to update the phone number of his supervisor
                check_duplication = check_duplication[0]
                check_duplication.facility = the_one_existing_temp.facility
                check_duplication.supervisor_phone_number = the_one_existing_temp.supervisor_phone_number
                check_duplication.save()
                args['valide'] = True
                args['info_to_contact'] = "Modification reussie. Le nouveau numero de telephone de votre superviseur est '"+the_one_existing_temp.supervisor_phone_number+"' et votre nouveau site d affectation est '"+the_one_existing_temp.facility.name+"'"
                the_one_existing_temp.delete()
                return'''


            # This contact is doing a first registration. Let's record him/her
            if is_first_registration:
                CHW.objects.create(phone_number = the_one_existing_temp.phone_number, cds = the_one_existing_temp.facility, supervisor_phone_number = the_one_existing_temp.supervisor_phone_number, sub_colline = the_one_existing_temp.sub_hill)
                # args['info_to_contact'] = "Enregistrement reussi. [CDS : '"+the_one_existing_temp.facility.name+"', Colline :  '"+the_one_existing_temp.sub_hill.colline.name+"', sous colline : '"+the_one_existing_temp.sub_hill.name+"', Numero du superviseur :  '"+the_one_existing_temp.supervisor_phone_number+"']. Si vous voulez modifier votre enregistrent, veuillez utiliser le mot cle REGM"
                args['info_to_contact'] = "Iyandikwa ryawe rigenze neza. [Ivuriro : '"+the_one_existing_temp.facility.name+"', Umutumba :  '"+the_one_existing_temp.sub_hill.colline.name+"', Agacimbiri : '"+the_one_existing_temp.sub_hill.name+"']. Wihenze, kosora urungitse mesaje yanditse neza itangurwa na 'REGM'"
            else:
                # The contact is doing an update
                the_existing_contact.phone_number = the_one_existing_temp.phone_number
                the_existing_contact.cds = the_one_existing_temp.facility
                the_existing_contact.supervisor_phone_number = the_one_existing_temp.supervisor_phone_number
                the_existing_contact.sub_colline = the_one_existing_temp.sub_hill
                the_existing_contact.save()
                # args['info_to_contact'] = "Modification reussie. [CDS : '"+the_one_existing_temp.facility.name+"', Colline :  '"+the_one_existing_temp.sub_hill.colline.name+"', sous colline : '"+the_one_existing_temp.sub_hill.name+"', Numero du superviseur :  '"+the_one_existing_temp.supervisor_phone_number+"']. Si vous voulez modifier votre enregistrent, veuillez utiliser le mot cle REGM"
                args['info_to_contact'] = "Gukosora vyakunze. [Ivuriro : '"+the_one_existing_temp.facility.name+"', Umutumba :  '"+the_one_existing_temp.sub_hill.colline.name+"', Agacimbiri : '"+the_one_existing_temp.sub_hill.name+"']. Wihenze, kosora urungitse mesaje yanditse neza itangurwa na 'REGM'"

            the_one_existing_temp.delete()
            args['valide'] = True
            # args['info_to_contact'] = "Enregistrement reussi. [CDS : '"+the_one_existing_temp.facility.name+"', Colline :  '"+the_one_existing_temp.sub_hill.colline.name+"', sous colline : '"+the_one_existing_temp.sub_hill.name+"', Numero du superviseur :  '"+the_one_existing_temp.supervisor_phone_number+"']. Si vous voulez modifier votre enregistrent, veuillez utiliser le mot cle REGM"
        else:
            the_one_existing_temp.delete()
            args['valide'] = False
            # args['info_to_contact'] = "Erreur. Vous avez envoye le numero de telephone de votre superviseur de differentes manieres. Pour corriger, veuillez reenvoyer le message commencant par le mot cle REG"
            args['info_to_contact'] = "Ikosa. Warungitse inomero ya telefone yuwugukurikirana ukuntu kubiri gutandukanye. Mu gukosora subira urungike mesaje itangurwa na 'REG' yanditse neza"


# -----------------------------------------------------------------








# ------------------------------PREGNANT CONFIRMATION REPORT-----------------------------------

# RECORD
def record_pregnant_case(args):

    args['mot_cle'] = "GRO"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return

    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the expected giving birth date is a future date
    args["future_date"] = args['text'].split(' ')[1]
    # args["date_meaning"] = "date probable d accouchement"
    args["date_meaning"] = "Igenekerezo umuvyeyi ashobora kuzibarukirako"
    check_is_future_date(args)
    if not args['valide']:
        return
    args["expected_birth_date"] = args['date_well_written']

    # Let's check if the next appointment date is a future date
    args["future_date"] = args['text'].split(' ')[2]
    # args["date_meaning"] = "date du prochain rendez-vous"
    args["date_meaning"] = "Igenekerezo umuvyeyi azosubirira kwivuriro"
    check_is_future_date(args)
    if not args['valide']:
        return
    args["next_appointment_date"] = args['date_well_written']

    # Let's check if the risk level is correct
    args["risk_level"] = args['text'].split(' ')[3]
    check_risk_level(args)
    if not args['valide']:
        return

    # Let's check if the location sent is valid
    args["location"] = args['text'].split(' ')[4]
    # args["date_meaning"] = "lieu de consultation"
    args["date_meaning"] = "Aho umuvyeyi yapimishirije imbanyi"
    check_location(args)
    if not args['valide']:
        return

    # Let's check if the phone number of the concerned mother is valid
    args["phone_number"] = args['text'].split(' ')[5]
    check_phone_number(args)
    if not args['valide']:
        return

    # The mother id is made by two parts.
    # The first part primary key of the cds on which works the CHW who registered her
    # The second part is number of mother registered on that cds

    mother_id = ""

    # The first part of the mother id must have at minimum 3 caracters
    mother_id_1 = str(args['facility'].id)
    if len(mother_id_1) == 1:
        mother_id_1 = "00"+mother_id_1
    if len(mother_id_1) == 2:
        mother_id_1 = "0"+mother_id_1

    # Let's build the second part of the mother id. It's made at minimum by 3 caracters

    gro_reports_from_this_cds = Report.objects.filter(cds = args['facility'], category = args['mot_cle'])

    # the_last_mother_registered_from_this_cds = the_last_gro_report_from_this_cds.mother

    mother_id_2 = '0'
    if(len(gro_reports_from_this_cds) > 0):
        the_last_mother_from_this_cds = Report.objects.filter(cds = args['facility'], category = args['mot_cle']).order_by("-id")[0].mother
        # Let's identify the id used by the system users for this patient
        the_last_mother_id = the_last_mother_from_this_cds.id_mother

        # Let's remove the first part (mother_id_1) and increment the second one
        the_length_of_the_first_part = len(mother_id_1)
        the_second_part = the_last_mother_id[the_length_of_the_first_part:]

        # Let's increment the second part.
        the_second_part_int = int(the_second_part)
        the_second_part_int = the_second_part_int+1

        # mother_id_2 is the second part of the new mother
        mother_id_2 = str(the_second_part_int)
    else:
        mother_id_2 = '0'

    if len(mother_id_2) == 1:
        mother_id_2 = "00"+mother_id_2
    if len(mother_id_2) == 2:
        mother_id_2 = "0"+mother_id_2

    mother_id = mother_id_1+""+mother_id_2


    # Let's check if there is no mother with that id
    '''check_mother_exists = Mother.objects.filter(id_mother = mother_id)
    if len(check_mother_exists) > 0:
        args['valide'] = False
        # Something need to be changed. When we delete a CHW who have already reported one or more pregnant cases, we will have the message below because a woman created by that reporter is not deleted and we have problem of woman id conflict when an other pregnant woman is being reported from that cds.
        args['info_to_contact'] = "Exception. Consulter l equipe de maintenance du systeme."
        return'''

    # All cheks passes. Let's record the pregnant women
    # the_created_mother_record, created = Mother.objects.get_or_create(phone_number = args["phone_number"])
    # the_created_mother_record = Mother.objects.create(id_mother = mother_id, phone_number = args["phone_number"])
    the_created_mother_record, created = Mother.objects.get_or_create(id_mother = mother_id, phone_number = args["phone_number"])
    the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = the_created_mother_record, reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])
    created_gro_report = ReportGRO.objects.create(report = the_created_report, expected_delivery_date = args["expected_birth_date"], next_appointment_date = args["next_appointment_date"], risk_level = args["risklevel"], consultation_location = args['location'])

    #salut
    # Let's record reminders which will be sent out for the next appointment
    cpn2_notification_type = NotificationType.objects.filter(code__iexact = "cpn2")
    if len(cpn2_notification_type) < 1:
        # This case can not occur because we do this check before(In the backend.py file)
        args['valide'] = False
        args['info_to_contact'] = "Exception. L administrateur du systeme n a pas cree la notification 'CPN2' dans la base de donnees."
        return

    # -----------------  
    next_appointment_date_time = datetime.datetime.combine(args["next_appointment_date"], datetime.datetime.now().time())

    # -----------------
    the_cpn2_notification_type = cpn2_notification_type[0]

    notifications_for_mother = NotificationsForMother.objects.filter(notification_type = the_cpn2_notification_type)
    if len(notifications_for_mother) > 0:
        notification_for_mother = notifications_for_mother[0]

        time_measure_unit = notification_for_mother.time_measuring_unit
        number_for_time = notification_for_mother.time_number
        
        if(time_measure_unit.code.startswith("m") or time_measure_unit.code.startswith("M")):
            time_for_reminder = next_appointment_date_time - datetime.timedelta(minutes = number_for_time)
        if(time_measure_unit.code.startswith("h") or time_measure_unit.code.startswith("H")):
            time_for_reminder = next_appointment_date_time - datetime.timedelta(hours = number_for_time)


        remind_message_to_send_to_mother = notification_for_mother.message_to_send

        if notification_for_mother.word_to_replace_by_the_date_in_the_message_to_send:
            remind_message_to_send_to_mother = remind_message_to_send_to_mother.replace(notification_for_mother.word_to_replace_by_the_date_in_the_message_to_send, next_appointment_date_time.date().isoformat())
          
        created_reminder = NotificationsMother.objects.create(mother = the_created_mother_record, notification = notification_for_mother, date_time_for_sending = time_for_reminder, message_to_send = remind_message_to_send_to_mother)

    notifications_for_chw = NotificationsForCHW.objects.filter(notification_type = the_cpn2_notification_type)
    if len(notifications_for_chw) > 0:
        notification_for_chw = notifications_for_chw[0]

        time_measure_unit = notification_for_chw.time_measuring_unit
        number_for_time = notification_for_chw.time_number
        if(time_measure_unit.code.startswith("m") or time_measure_unit.code.startswith("M")):
            time_for_reminder = next_appointment_date_time - datetime.timedelta(minutes = number_for_time)
        if(time_measure_unit.code.startswith("h") or time_measure_unit.code.startswith("H")):
            time_for_reminder = next_appointment_date_time - datetime.timedelta(hours = number_for_time)


        remind_message_to_send_to_chw = notification_for_chw.message_to_send

        if notification_for_chw.word_to_replace_by_the_mother_id_in_the_message_to_send:
            remind_message_to_send_to_chw = remind_message_to_send_to_chw.replace(notification_for_chw.word_to_replace_by_the_mother_id_in_the_message_to_send, the_created_mother_record.id_mother)

        if notification_for_chw.word_to_replace_by_the_date_in_the_message_to_send:
            remind_message_to_send_to_chw = remind_message_to_send_to_chw.replace(notification_for_chw.word_to_replace_by_the_date_in_the_message_to_send, next_appointment_date_time.date().isoformat())

        created_reminder = NotificationsCHW.objects.create(chw = args['the_sender'], notification = notification_for_chw, date_time_for_sending = time_for_reminder, message_to_send = remind_message_to_send_to_chw)

    # acc is a reminder for the delivery
    acc_notification_type = NotificationType.objects.filter(code__iexact = "acc")
    if len(acc_notification_type) < 1:
        # This case can not occur because we do this check before(In the backend.py file)
        args['valide'] = False
        args['info_to_contact'] = "Exception. L administrateur du systeme n a pas cree la notification 'acc' dans la base de donnees."
        return

    # -----------------    
    expected_delivery_date_time = datetime.datetime.combine(args["expected_birth_date"], datetime.datetime.now().time())
    # -----------------

    the_acc_notification_type = acc_notification_type[0]

    notifications_for_mother = NotificationsForMother.objects.filter(notification_type = the_acc_notification_type)
    if len(notifications_for_mother) > 0:
        for notification_for_mother in notifications_for_mother:
            #notification_for_mother = notifications_for_mother[0]
            time_measure_unit = notification_for_mother.time_measuring_unit
            number_for_time = notification_for_mother.time_number
            if(time_measure_unit.code.startswith("m") or time_measure_unit.code.startswith("M")):
                time_for_reminder = expected_delivery_date_time - datetime.timedelta(minutes = number_for_time)
            if(time_measure_unit.code.startswith("h") or time_measure_unit.code.startswith("H")):
                time_for_reminder = expected_delivery_date_time - datetime.timedelta(hours = number_for_time)


            remind_message_to_send_to_mother = notification_for_mother.message_to_send

            if notification_for_mother.word_to_replace_by_the_date_in_the_message_to_send:
                remind_message_to_send_to_mother = remind_message_to_send_to_mother.replace(notification_for_mother.word_to_replace_by_the_date_in_the_message_to_send, expected_delivery_date_time.date().isoformat())

            created_reminder = NotificationsMother.objects.create(mother = the_created_mother_record, notification = notification_for_mother, date_time_for_sending = time_for_reminder, message_to_send = remind_message_to_send_to_mother)


    notifications_for_chw = NotificationsForCHW.objects.filter(notification_type = the_acc_notification_type)
    if len(notifications_for_chw) > 0:
        #notification_for_chw = notifications_for_chw[0]
        for notification_for_chw in notifications_for_chw:
            time_measure_unit = notification_for_chw.time_measuring_unit
            number_for_time = notification_for_chw.time_number
            if(time_measure_unit.code.startswith("m") or time_measure_unit.code.startswith("M")):
                time_for_reminder = expected_delivery_date_time - datetime.timedelta(minutes = number_for_time)
            if(time_measure_unit.code.startswith("h") or time_measure_unit.code.startswith("H")):
                time_for_reminder = expected_delivery_date_time - datetime.timedelta(hours = number_for_time)


            remind_message_to_send_to_chw = notification_for_chw.message_to_send

            if notification_for_chw.word_to_replace_by_the_mother_id_in_the_message_to_send:
                remind_message_to_send_to_chw = remind_message_to_send_to_chw.replace(notification_for_chw.word_to_replace_by_the_mother_id_in_the_message_to_send, the_created_mother_record.id_mother)

            if notification_for_chw.word_to_replace_by_the_date_in_the_message_to_send:
                remind_message_to_send_to_chw = remind_message_to_send_to_chw.replace(notification_for_chw.word_to_replace_by_the_date_in_the_message_to_send, expected_delivery_date_time.date().isoformat())        
            created_reminder = NotificationsCHW.objects.create(chw = args['the_sender'], notification = notification_for_chw, date_time_for_sending = time_for_reminder, message_to_send = remind_message_to_send_to_chw)


    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    args['valide'] = True
    # args['info_to_contact'] = "La femme enceinte est bien enregistree. Son numero est "+mother_id
    args['info_to_contact'] = "Mesaje warungitse yashitse. Inomero yuwo mupfasoni yibungenze ni "+mother_id


# MODIFY
def modify_record_pregnant_case(args):

    args['mot_cle'] = "GROM"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return

    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valide(args)
    if not args['valide']:
        return

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return

    # Let's check if the expected giving birth date is a future date
    args["future_date"] = args['text'].split(' ')[2]
    # args["date_meaning"] = "date probable d accouchement"
    args["date_meaning"] = "Igenekerezo umuvyeyi ashobora kuzibarukirako"
    check_is_future_date(args)
    if not args['valide']:
        return
    args["expected_birth_date"] = args['date_well_written']

    # Let's check if the next appointment date is a future date
    args["future_date"] = args['text'].split(' ')[3]
    # args["date_meaning"] = "date du prochain rendez-vous"
    args["date_meaning"] = "Igenekerezo umuvyeyi azosubirira kw ivuriro"
    check_is_future_date(args)
    if not args['valide']:
        return
    args["next_appointment_date"] = args['date_well_written']

    # Let's check if the risk level is correct
    args["risk_level"] = args['text'].split(' ')[4]
    check_risk_level(args)
    if not args['valide']:
        return

    # Let's check if the location sent is valid
    args["location"] = args['text'].split(' ')[5]
    # args["date_meaning"] = "lieu de consultation"
    args["date_meaning"] = "Aho umuvyeyi yapimishirije imbanyi"
    check_location(args)
    if not args['valide']:
        return

    # Let's check if the phone number of the concerned mother is valid
    args["phone_number"] = args['text'].split(' ')[6]
    check_phone_number(args)
    if not args['valide']:
        return

    # Let's identify the corresponding Report
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

    # Let's update all values
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
    
    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    args['valide'] = True
    # args['info_to_contact'] = "Mise a jour du rapport de confirmation de grossesse de la femme '"+args['concerned_mother'].id_mother+"' a reussie."
    args['info_to_contact'] = "Mesaje yo gukosora iyari yatanzwe ivuga ko umupfasoni nomero '"+args['concerned_mother'].id_mother+"' yibungenze yashitse neza."

# -----------------------------------------------------------------


# -----------------------------------------------------------------
def record_prenatal_consultation_report(args):

    args['mot_cle'] = "CPN"    

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return

    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return
    args['concerned_woman'] = args['concerned_mother']

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return
    # Let's check if the CPN name sent exists
    args["sent_cpn_name"] = args['text'].split(' ')[2]
    check_cpn_name_exists(args)
    if not args['valide']:
        return
    args["concerned_cpn"] = args['specified_cpn']

    # Let's check if the CPN order is respected. The first one should be 
    #number 1
    check_cpn_order_respected(args)
    if not args['valide']:
        return

    # Let's check if the consultation date is valid
    # It must be a previous date or today's date
    args["previous_days_or_today_date"] = args['text'].split(' ')[3]
    # args["date_meaning"] = "Date de consultation prenatale"
    args["date_meaning"] = "Igenekerezo umuvyeyi yapimishirijeko imbanyi"
    check_date_is_previous_or_today(args)
    if not args['valide']:
        return
    args["cpn_consultation_date"] = args['date_well_written']

    # Let's check if the next appointment date is valid
    args["future_date"] = args['text'].split(' ')[4]
    # args["date_meaning"] = "date du prochain rendez-vous"
    args["date_meaning"] = "Igenekerezo umuvyeyi azosubirira kw ivuriro"
    check_is_future_date(args)
    if not args['valide']:
        return
    args["next_appointment_date"] = args['date_well_written']

    # Let's check if the consultation location is valid
    args["location"] = args['text'].split(' ')[5]
    # args["date_meaning"] = "lieu de consultation"
    args["date_meaning"] = "Aho umuvyeyi yipimishirije"
    check_location(args)
    if not args['valide']:
        return

    # Let's check if the indicated woman weight is valid
    args["float_value"] = args['text'].split(' ')[6]
    # args["date_meaning"] = "Poids de la mere"
    args["date_meaning"] = "Ibiro vy umuvyeyi"
    check_is_float(args)
    if not args['valide']:
        return
    try:
        checked_value = float(args['checked_float'])
    except:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["date_meaning"]+"' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Ico wanditse kuvyerekeye '"+args["date_meaning"]+"' ntikibaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    '''# Let's check if the symptom(s) is/are valid
    args["symptoms"] = args['text'].split(' ')[7]
    check_symptoms(args)
    if not args['valide']:
        return'''

    # Now, everything is checked. Let's record the report
    the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_woman'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])
    created_cpn_report = ReportCPN.objects.create(report = the_created_report, concerned_cpn = args["concerned_cpn"], consultation_date = args["cpn_consultation_date"], consultation_location = args['location'], mother_weight = checked_value, next_appointment_date = args["next_appointment_date"])


    '''for one_symbol in args['checked_symptoms_list']:
        one_symptom = Symptom.objects.filter(symtom_designation__iexact = one_symbol)[0]
        created_report_symptom_connection = CPN_Report_Symptom.objects.create(cpn_report = created_cpn_report, symptom = one_symptom)'''

    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    args['valide'] = True
    # args['info_to_contact'] = "Le rapport '"+args["concerned_cpn"].cpn_designation+"' de la maman '"+args['concerned_woman'].id_mother+"' est bien enregistre."
    args['info_to_contact'] = "Mesaje '"+args["concerned_cpn"].cpn_designation+"' warungitse yerekeye umupfasoni '"+args['concerned_woman'].id_mother+"' yashitse."


def modify_record_prenatal_consultation_report(args):

    args['mot_cle'] = "CPNM"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return

    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return
    args['concerned_woman'] = args['concerned_mother']

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return
    # Let's check if the CPN name sent exists
    args["sent_cpn_name"] = args['text'].split(' ')[2]
    check_cpn_name_exists(args)
    if not args['valide']:
        return
    args["concerned_cpn"] = args['specified_cpn']

    # Let's check if the consultation date is valid
    # It must be a previous date or today's date
    args["previous_days_or_today_date"] = args['text'].split(' ')[3]
    # args["date_meaning"] = "Date de consultation prenatale"
    args["date_meaning"] = "Igenekerezo umuvyeyi yapimishirijeko imbanyi"
    check_date_is_previous_or_today(args)
    if not args['valide']:
        return
    args["cpn_consultation_date"] = args['date_well_written']

    # Let's check if the next appointment date is valid
    args["future_date"] = args['text'].split(' ')[4]
    # args["date_meaning"] = "date du prochain rendez-vous"
    args["date_meaning"] = "Igenekerezo umuvyeyi azosubirira kw ivuriro"
    check_is_future_date(args)
    if not args['valide']:
        return
    args["next_appointment_date"] = args['date_well_written']

    # Let's check if the consultation location is valid
    args["location"] = args['text'].split(' ')[5]
    # args["date_meaning"] = "lieu de consultation"
    args["date_meaning"] = "Aho umuvyeyi yapimishirije imbanyi"
    check_location(args)
    if not args['valide']:
        return

    # Let's check if the indicated woman weight is valid
    args["float_value"] = args['text'].split(' ')[6]
    # args["date_meaning"] = "Poids de la mere"
    args["date_meaning"] = "Ibiro vy umuvyeyi"
    check_is_float(args)
    if not args['valide']:
        return
    try:
        checked_value = float(args['checked_float'])
    except:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["date_meaning"]+"' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Ico wanditse kuvyerekeye '"+args["date_meaning"]+"' ntikibaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    '''# Let's check if the symptom(s) is/are valid
    args["symptoms"] = args['text'].split(' ')[7]
    check_symptoms(args)
    if not args['valide']:
        return'''

    # Let's check if the mother with this id has an already registered CPN report
    the_existing_cpn_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3])
    if len(the_existing_cpn_report) < 1:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Aucun rapport 'CPN' trouve de la maman '"+args['concerned_mother'].id_mother+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Nta raporo 'CPN' iratangwa yerekeye umupfasoni '"+args['concerned_mother'].id_mother+"'. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    the_only_one_corresponding_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3]).order_by('-id')[0]

    the_corresponding_cpn_report = ReportCPN.objects.filter(report = the_only_one_corresponding_report)
    if len(the_corresponding_cpn_report) < 1:
        args['valide'] = False
        args['info_to_contact'] = "Exception. Un rapport 'CPN' correspondant a la maman indiquee n est pas trouve. Veuillez contacter l administrateur du systeme"
        return
    the_one_corresponding_cpnreport = the_corresponding_cpn_report[0]
    # Now, everything is checked. Let's do the update

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


    # Let's update 'CPN_Report_Symptom' connections
    '''concerned_cpn_report_symptom_connections = CPN_Report_Symptom.objects.filter(cpn_report = the_one_corresponding_cpnreport)
    if len(concerned_cpn_report_symptom_connections) > 0:
        for one_connection in concerned_cpn_report_symptom_connections:
            one_connection.delete()

    for one_symbol in args['checked_symptoms_list']:
        one_symptom = Symptom.objects.filter(symtom_designation__iexact = one_symbol)[0]
        created_report_symptom_connection = CPN_Report_Symptom.objects.create(cpn_report = the_one_corresponding_cpnreport, symptom = one_symptom)'''

    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    args['valide'] = True
    # args['info_to_contact'] = "Mise a jour du rapport de consultation prenatale de la femme '"+args['concerned_mother'].id_mother+"' a reussie."
    args['info_to_contact'] = "Mesaje ikosora iyari yarungitswe yerekeye ukuja gupimisha imbanyi kwumupfasoni '"+args['concerned_mother'].id_mother+"' yashitse."


# -----------------------------------------------------------------


# -----------------------------------------------------------------
def record_birth_case_report(args):

    args['mot_cle'] = "NSC"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return
    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return
    args['concerned_woman'] = args['concerned_mother']

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return

    # Let's check if the child code is valid
    args["child_code"] = args['text'].split(' ')[2]
    check_child_code(args)
    if not args['valide']:
        return

    # Let's check if the chw is respecting the order of child codes
    args["child_code"] = args['text'].split(' ')[2]
    check_child_code_order(args)
    if not args['valide']:
        return

    # Let check if the birth date is not a future date
    # It must be a previous date or today's date
    args["previous_days_or_today_date"] = args['text'].split(' ')[3]
    # args["date_meaning"] = "Date de naissance"
    args["date_meaning"] = "Igenekerezo umuvyeyi yibarukiyeko"
    check_date_is_previous_or_today(args)
    if not args['valide']:
        return
    args["birth_date"] = args['date_well_written']

    # Let's check if the next CPoN date is a future date
    args["future_date"] = args['text'].split(' ')[4]
    # args["date_meaning"] = "Prochaine date pour les soins postnatals"
    args["date_meaning"] = "Igenekerezo umuvyeyi azosubirira kw ivuriro"
    check_is_future_date(args)
    if not args['valide']:
        return
    args["next_cpon_appointment_date"] = args['date_well_written']

    # Let's check if the location of birth is valid
    args["location"] = args['text'].split(' ')[5]
    # args["date_meaning"] = "lieu de naissance"
    args["date_meaning"] = "Aho umupfasoni azibarukira"
    check_location(args)
    if not args['valide']:
        return

    # Let's check the value sent for "Allaitement maternel"
    args["allaitement_maternel"] = args['text'].split(' ')[6]
    check_allaitement_maternel(args)
    if not args['valide']:
        return

    # Let's check if the value sent for gender is valid
    args["gender"] = args['text'].split(' ')[7]
    check_gender(args)
    if not args['valide']:
        return

    # Let's check if the indicated child weight is valid
    args["float_value"] = args['text'].split(' ')[8]
    # args["date_meaning"] = "Poids du nouveau ne"
    args["date_meaning"] = "Ibiro vyumwana"
    check_is_float(args)
    if not args['valide']:
        return
    try:
        checked_value = float(args['checked_float'])
    except:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["date_meaning"]+"' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Ico wanditse kuvyerekeye '"+args["date_meaning"]+"' sico. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    # Now, everything is checked. Let's record the report
    the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_woman'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])
    created_nsc_report = ReportNSC.objects.create(report = the_created_report, child_number = args['child_number'], birth_date = args["birth_date"], birth_location = args['location'], gender = args['gender'], weight = checked_value, next_appointment_date = args["next_cpon_appointment_date"], breast_feading = args['code_allaitement'])
    
    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    #salut
    # Let's record reminders which will be sent out for the next appointment
    con1_notification_type = NotificationType.objects.filter(code__iexact = "con1")
    if len(con1_notification_type) < 1:
        # This case can not occur because we do this check before(In the backend.py file)
        args['valide'] = False
        args['info_to_contact'] = "Exception. L administrateur du systeme n a pas cree la notification 'CON1' dans la base de donnees."
        return

    # -----------------  
    next_appointment_date_time = datetime.datetime.combine(args["next_cpon_appointment_date"], datetime.datetime.now().time())

    # -----------------
    the_con1_notification_type = con1_notification_type[0]


    notifications_for_mother = NotificationsForMother.objects.filter(notification_type = the_con1_notification_type)
    if len(notifications_for_mother) > 0:
        notification_for_mother = notifications_for_mother[0]

        time_measure_unit = notification_for_mother.time_measuring_unit
        number_for_time = notification_for_mother.time_number
        
        if(time_measure_unit.code.startswith("m") or time_measure_unit.code.startswith("M")):
            time_for_reminder = next_appointment_date_time - datetime.timedelta(minutes = number_for_time)
        if(time_measure_unit.code.startswith("h") or time_measure_unit.code.startswith("H")):
            time_for_reminder = next_appointment_date_time - datetime.timedelta(hours = number_for_time)


        remind_message_to_send_to_mother = notification_for_mother.message_to_send

        if notification_for_mother.word_to_replace_by_the_date_in_the_message_to_send:
            remind_message_to_send_to_mother = remind_message_to_send_to_mother.replace(notification_for_mother.word_to_replace_by_the_date_in_the_message_to_send, next_appointment_date_time.date().isoformat())
          
        created_reminder = NotificationsMother.objects.create(mother = args['concerned_woman'], notification = notification_for_mother, date_time_for_sending = time_for_reminder, message_to_send = remind_message_to_send_to_mother)

    notifications_for_chw = NotificationsForCHW.objects.filter(notification_type = the_con1_notification_type)
    if len(notifications_for_chw) > 0:
        notification_for_chw = notifications_for_chw[0]

        time_measure_unit = notification_for_chw.time_measuring_unit
        number_for_time = notification_for_chw.time_number
        if(time_measure_unit.code.startswith("m") or time_measure_unit.code.startswith("M")):
            time_for_reminder = next_appointment_date_time - datetime.timedelta(minutes = number_for_time)
        if(time_measure_unit.code.startswith("h") or time_measure_unit.code.startswith("H")):
            time_for_reminder = next_appointment_date_time - datetime.timedelta(hours = number_for_time)


        remind_message_to_send_to_chw = notification_for_chw.message_to_send

        if notification_for_chw.word_to_replace_by_the_mother_id_in_the_message_to_send:
            remind_message_to_send_to_chw = remind_message_to_send_to_chw.replace(notification_for_chw.word_to_replace_by_the_mother_id_in_the_message_to_send, args['concerned_woman'].id_mother)

        if notification_for_chw.word_to_replace_by_the_date_in_the_message_to_send:
            remind_message_to_send_to_chw = remind_message_to_send_to_chw.replace(notification_for_chw.word_to_replace_by_the_date_in_the_message_to_send, next_appointment_date_time.date().isoformat())

        created_reminder = NotificationsCHW.objects.create(chw = args['the_sender'], notification = notification_for_chw, date_time_for_sending = time_for_reminder, message_to_send = remind_message_to_send_to_chw)




    args['valide'] = True
    # args['info_to_contact'] = "Le rapport de naissance du bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_woman'].id_mother+"' est bien enregistre."
    args['info_to_contact'] = "Mesaje ivuga ivuka ry umwana '" +args['child_number'].child_code_designation+"' w umupfasoni '"+args['concerned_woman'].id_mother+"' yashitse"


# Modify
def modify_record_birth_case_report(args):

    args['mot_cle'] = "NSCM"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return
    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return
    args['concerned_woman'] = args['concerned_mother']

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return

    # Let's check if the child code is valid
    args["child_code"] = args['text'].split(' ')[2]
    check_child_code(args)
    if not args['valide']:
        return

    # Let's check if the chw is respecting the order of child codes
    args["child_code"] = args['text'].split(' ')[2]
    check_child_code_order(args)
    if not args['valide']:
        return

    # Let check if the birth date is not a future date
    # It must be a previous date or today's date
    args["previous_days_or_today_date"] = args['text'].split(' ')[3]
    # args["date_meaning"] = "Date de naissance"
    args["date_meaning"] = "Igenekerezo umwana yavukiyeko"
    check_date_is_previous_or_today(args)
    if not args['valide']:
        return
    args["birth_date"] = args['date_well_written']

    # Let's check if the next CPoN date is a future date
    args["future_date"] = args['text'].split(' ')[4]
    # args["date_meaning"] = "Prochaine date pour les soins postnatals"
    args["date_meaning"] = "Igenekerezo umuvyeyi azosubirirako kw ivuriro"
    check_is_future_date(args)
    if not args['valide']:
        return
    args["next_cpon_appointment_date"] = args['date_well_written']

    # Let's check if the location of birth is valid
    args["location"] = args['text'].split(' ')[5]
    # args["date_meaning"] = "lieu de naissance"
    args["date_meaning"] = "Ikibanza umuvyeyi yavukiyemwo"
    check_location(args)
    if not args['valide']:
        return

    # Let's check the value sent for "Allaitement maternel"
    args["allaitement_maternel"] = args['text'].split(' ')[6]
    check_allaitement_maternel(args)
    if not args['valide']:
        return

    # Let's check if the value sent for gender is valid
    args["gender"] = args['text'].split(' ')[7]
    check_gender(args)
    if not args['valide']:
        return

    # Let's check if the indicated child weight is valid
    args["float_value"] = args['text'].split(' ')[8]
    # args["date_meaning"] = "Poids du nouveau ne"
    args["date_meaning"] = "Ibiro umwana yavukanye"
    check_is_float(args)
    if not args['valide']:
        return
    try:
        checked_value = float(args['checked_float'])
    except:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. La valeur envoyee pour '"+args["date_meaning"]+"' n est pas valide. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Ico wanditse kuvyerekeye '"+args["date_meaning"]+"' sico. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    # Let's check if the mother with this id has an already registered NSC report
    the_existing_nsc_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3])
    if len(the_existing_nsc_report) < 1:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Aucun rapport 'NSC' trouve de la maman '"+args['concerned_mother'].id_mother+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Nta raporo yigeze itangwa ivuga ko umuvyeyi nomero '"+args['concerned_mother'].id_mother+"' yibarutse. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    the_only_one_corresponding_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3]).order_by('-id')[0]

    the_corresponding_nsc_report = ReportNSC.objects.filter(report = the_only_one_corresponding_report)
    if len(the_corresponding_nsc_report) < 1:
        args['valide'] = False
        args['info_to_contact'] = "Exception. Un rapport 'NSC' correspondant a la maman indiquee n est pas trouve. Veuillez contacter l administrateur du systeme"
        return
    the_one_corresponding_nscreport = the_corresponding_nsc_report[0]

    # Now, everything is checked. Let's do the update

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
    
    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    args['valide'] = True
    # args['info_to_contact'] = "Mise a jour du rapport de naissance du bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_woman'].id_mother+"' a reussie."
    args['info_to_contact'] = "Mesaje ikosora iyari yatanzwe yerekeye umwana '" +args['child_number'].child_code_designation+"' w umupfasoni '"+args['concerned_woman'].id_mother+"' yashitse"

# -----------------------------------------------------------------


# -----------------------------------------------------------------
def record_postnatal_care_report(args):

    args['mot_cle'] = "CON"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return
    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return

    # Let's check if this mother has a child with the sent child number
    args["child_id"] = args['text'].split(' ')[2]
    check_child_exists(args)
    if not args['valide']:
        return

    # Let's check if the consultation code sent is valid
    args["con_code"] = args['text'].split(' ')[3]
    check_con_code(args)
    if not args['valide']:
        return

    # Let's check if the next appointment date is a future date
    args["future_date"] = args['text'].split(' ')[4]
    # args["date_meaning"] = "Date du prochain rendez-vous"
    args["date_meaning"] = "Igenekerezo umuvyeyi azosubirirako kw ivuriro"
    check_is_future_date(args)
    if not args['valide']:
        return
    args["next_appointment_date"] = args['date_well_written']
    # Let's check if the symptom(s) is/are valid
    args["symptoms"] = args['text'].split(' ')[5]
    check_symptoms(args)
    if not args['valide']:
        return

    # Let's check mother health status value
    args["health_status_value"] = args['text'].split(' ')[6]
    # args["health_status_meaning"] = "etat de sante de la mere"
    args["health_status_meaning"] = "Ingene amagara y umuvyeyi yifashe"
    check_health_status(args)
    if not args['valide']:
        return
    args['mother_s_health_state'] = args['concerned_health_status']

    # Let's check child health status value
    args["health_status_value"] = args['text'].split(' ')[7]
    # args["health_status_meaning"] = "etat de sante de l enfant"
    args["health_status_meaning"] = "Ingene amagara y umuvyeyi yifashe"
    check_health_status(args)
    if not args['valide']:
        return
    args['child_s_health_state'] = args['concerned_health_status']

    # Now, everything is checked. Let's record the report
    the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_mother'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])
    created_con_report = ReportCON.objects.create(report = the_created_report, child = args['concerned_child'], con = args['concerned_con'], child_health_state = args['child_s_health_state'], mother_health_state = args['mother_s_health_state'], next_appointment_date = args["next_appointment_date"])

    for one_symbol in args['checked_symptoms_list']:
        one_symptom = Symptom.objects.filter(symtom_designation__iexact = one_symbol)[0]
        created_report_symptom_connection = CON_Report_Symptom.objects.create(con_report = created_con_report, symptom = one_symptom)

    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)



    #If the reported CON is CON1, let's record reminders for CON2
    #salut
    if(args['concerned_con'].con_designation.upper() == 'CON1'):
        con2_notification_type = NotificationType.objects.filter(code__iexact = "con2")
        if len(con2_notification_type) < 1:
            args['valide'] = False
            args['info_to_contact'] = "Exception. L administrateur du systeme n a pas cree la notification 'CON2' dans la base de donnees."
            return

        # -----------------  
        next_appointment_date_time = datetime.datetime.combine(args["next_appointment_date"], datetime.datetime.now().time())

        # -----------------
        the_con2_notification_type = con2_notification_type[0]


        notifications_for_mother = NotificationsForMother.objects.filter(notification_type = the_con2_notification_type)
        if len(notifications_for_mother) > 0:
            notification_for_mother = notifications_for_mother[0]

            time_measure_unit = notification_for_mother.time_measuring_unit
            number_for_time = notification_for_mother.time_number
        
            if(time_measure_unit.code.startswith("m") or time_measure_unit.code.startswith("M")):
                time_for_reminder = next_appointment_date_time - datetime.timedelta(minutes = number_for_time)
            if(time_measure_unit.code.startswith("h") or time_measure_unit.code.startswith("H")):
                time_for_reminder = next_appointment_date_time - datetime.timedelta(hours = number_for_time)


            remind_message_to_send_to_mother = notification_for_mother.message_to_send

            if notification_for_mother.word_to_replace_by_the_date_in_the_message_to_send:
                remind_message_to_send_to_mother = remind_message_to_send_to_mother.replace(notification_for_mother.word_to_replace_by_the_date_in_the_message_to_send, next_appointment_date_time.date().isoformat())
          
            created_reminder = NotificationsMother.objects.create(mother = args['concerned_mother'], notification = notification_for_mother, date_time_for_sending = time_for_reminder, message_to_send = remind_message_to_send_to_mother)

        notifications_for_chw = NotificationsForCHW.objects.filter(notification_type = the_con2_notification_type)
        if len(notifications_for_chw) > 0:
            notification_for_chw = notifications_for_chw[0]

            time_measure_unit = notification_for_chw.time_measuring_unit
            number_for_time = notification_for_chw.time_number
            if(time_measure_unit.code.startswith("m") or time_measure_unit.code.startswith("M")):
                time_for_reminder = next_appointment_date_time - datetime.timedelta(minutes = number_for_time)
            if(time_measure_unit.code.startswith("h") or time_measure_unit.code.startswith("H")):
                time_for_reminder = next_appointment_date_time - datetime.timedelta(hours = number_for_time)


            remind_message_to_send_to_chw = notification_for_chw.message_to_send

            if notification_for_chw.word_to_replace_by_the_mother_id_in_the_message_to_send:
                remind_message_to_send_to_chw = remind_message_to_send_to_chw.replace(notification_for_chw.word_to_replace_by_the_mother_id_in_the_message_to_send, args['concerned_mother'].id_mother)

            if notification_for_chw.word_to_replace_by_the_date_in_the_message_to_send:
                remind_message_to_send_to_chw = remind_message_to_send_to_chw.replace(notification_for_chw.word_to_replace_by_the_date_in_the_message_to_send, next_appointment_date_time.date().isoformat())

            created_reminder = NotificationsCHW.objects.create(chw = args['the_sender'], notification = notification_for_chw, date_time_for_sending = time_for_reminder, message_to_send = remind_message_to_send_to_chw)



    args['valide'] = True
    # args['info_to_contact'] = "Le rapport de soins postnatals pour le bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."
    args['info_to_contact'] = "Mesaje warungitse yerekeye ukuja kwivuriro kw umwana '" +args['child_number'].child_code_designation+"' w umupfasoni '"+args['concerned_mother'].id_mother+"' yashitse"


# Modify
def modify_record_postnatal_care_report(args):

    args['mot_cle'] = "CONM"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return

    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return

    # Let's check if this mother has a child with the sent child number
    args["child_id"] = args['text'].split(' ')[2]
    check_child_exists(args)
    if not args['valide']:
        return

    # Let's check if the consultation code sent is valid
    args["con_code"] = args['text'].split(' ')[3]
    check_con_code(args)
    if not args['valide']:
        return

    # Let's check if the next appointment date is a future date
    args["future_date"] = args['text'].split(' ')[4]
    # args["date_meaning"] = "Date du prochain rendez-vous"
    args["date_meaning"] = "Igenekerezo umuvyeyi azosubirirako kw ivuriro"
    check_is_future_date(args)
    if not args['valide']:
        return
    args["next_appointment_date"] = args['date_well_written']

    # Let's check if the symptom(s) is/are valid
    args["symptoms"] = args['text'].split(' ')[5]
    check_symptoms(args)
    if not args['valide']:
        return

    # Let's check mother health status value
    args["health_status_value"] = args['text'].split(' ')[6]
    args["health_status_meaning"] = "etat de sante de la mere"
    check_health_status(args)
    if not args['valide']:
        return
    args['mother_s_health_state'] = args['concerned_health_status']

    # Let's check child health status value
    args["health_status_value"] = args['text'].split(' ')[7]
    args["health_status_meaning"] = "etat de sante de l enfant"
    check_health_status(args)
    if not args['valide']:
        return
    args['child_s_health_state'] = args['concerned_health_status']

    # Let's check if the mother with this id has an already registered CON report
    the_existing_con_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3])
    if len(the_existing_con_report) < 1:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Aucun rapport 'CON' trouve de la maman '"+args['concerned_mother'].id_mother+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Nta raporo 'CON' yumuvyeyi nomero '"+args['concerned_mother'].id_mother+"' irabaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    the_only_one_corresponding_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3]).order_by('-id')[0]

    the_corresponding_con_report = ReportCON.objects.filter(report = the_only_one_corresponding_report)
    if len(the_corresponding_con_report) < 1:
        args['valide'] = False
        args['info_to_contact'] = "Exception. Un rapport 'CON' correspondant a la maman indiquee n est pas trouve. Veuillez contacter l administrateur du systeme"
        return
    the_one_corresponding_conreport = the_corresponding_con_report[0]

    # Now, everything is checked. Let's record the report
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

    # Let's update 'CON_Report_Symptom' connections
    concerned_con_report_symptom_connections = CON_Report_Symptom.objects.filter(con_report = the_one_corresponding_conreport)
    if len(concerned_con_report_symptom_connections) > 0:
        for one_connection in concerned_con_report_symptom_connections:
            one_connection.delete()

    for one_symbol in args['checked_symptoms_list']:
        one_symptom = Symptom.objects.filter(symtom_designation__iexact = one_symbol)[0]
        created_report_symptom_connection = CON_Report_Symptom.objects.create(con_report = the_one_corresponding_conreport, symptom = one_symptom)

    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    args['valide'] = True
    # args['info_to_contact'] = "Mise a jour du rapport de soins postnatals pour le bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_mother'].id_mother+"' a reussie."
    args['info_to_contact'] = "Mesaje ikosora iyari yatanzwe yerekeye ukuja kw ivuriro kw umwana '" +args['child_number'].child_code_designation+"' w umupfasoni '"+args['concerned_mother'].id_mother+"' yashitse"

# -----------------------------------------------------------------


# -----------------------------------------------------------------
def record_child_follow_up_report(args):

    args['mot_cle'] = "VAC"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return

    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return

    # Let's check if this mother has a child with the sent child number
    args["child_id"] = args['text'].split(' ')[2]
    check_child_exists(args)
    if not args['valide']:
        return

    # Let's check if the vaccine code sent is valid
    args["vac_code"] = args['text'].split(' ')[3]
    check_vac_code(args)
    if not args['valide']:
        return

    # Let's check if the location sent is valid
    args["location"] = args['text'].split(' ')[4]
    # args["date_meaning"] = "lieu de vaccination"
    args["date_meaning"] = "Ikibanza icandagwa ryabereyemwo"
    check_location(args)
    if not args['valide']:
        return

    # Let's record the report
    the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_mother'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])

    created_vac_report = ReportVAC.objects.create(report = the_created_report, child = args['concerned_child'], vac = args['concerned_vac'], location = args['location'])

    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    args['valide'] = True
    # args['info_to_contact'] = "Le rapport de suivi du bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."
    args['info_to_contact'] = "Mesaje yerekeye ikurikiranwa ry umwana '" +args['child_number'].child_code_designation+"' w umupfasoni '"+args['concerned_mother'].id_mother+"' yashitse neza"


# Modify
def modify_record_child_follow_up_report(args):

    args['mot_cle'] = "VACM"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return

    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return

    # Let's check if this mother has a child with the sent child number
    args["child_id"] = args['text'].split(' ')[2]
    check_child_exists(args)
    if not args['valide']:
        return

    # Let's check if the vaccine code sent is valid
    args["vac_code"] = args['text'].split(' ')[3]
    check_vac_code(args)
    if not args['valide']:
        return

    # Let's check if the location sent is valid
    args["location"] = args['text'].split(' ')[4]
    # args["date_meaning"] = "lieu de vaccination"
    args["date_meaning"] = "Ikibanza icandagwa ryabereyemwo"
    check_location(args)
    if not args['valide']:
        return

    # Let's check if the mother with this id has an already registered VAC report
    the_existing_vac_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3])
    if len(the_existing_vac_report) < 1:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Aucun rapport 'VAC' trouve de la maman '"+args['concerned_mother'].id_mother+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Nta raporo 'VAC' yumuvyeyi numero '"+args['concerned_mother'].id_mother+"' irabaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    the_only_one_corresponding_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3]).order_by('-id')[0]

    the_corresponding_vac_report = ReportVAC.objects.filter(report = the_only_one_corresponding_report)
    if len(the_corresponding_vac_report) < 1:
        args['valide'] = False
        args['info_to_contact'] = "Exception. Un rapport 'VAC' correspondant a la maman indiquee n est pas trouve. Veuillez contacter l administrateur du systeme"
        return
    the_one_corresponding_vacreport = the_corresponding_vac_report[0]

    # Let's do the update

    the_only_one_corresponding_report.chw = args['the_sender']
    the_only_one_corresponding_report.sub_hill = args['sub_colline']
    the_only_one_corresponding_report.cds = args['facility']
    the_only_one_corresponding_report.mother = args['concerned_mother']
    the_only_one_corresponding_report.reporting_date = datetime.datetime.now().date()
    the_only_one_corresponding_report.text = args['text']
    the_only_one_corresponding_report.save()

    the_one_corresponding_vacreport.report = the_only_one_corresponding_report
    the_one_corresponding_vacreport.child = args['concerned_child']
    the_one_corresponding_vacreport.vac = args['concerned_vac']
    the_one_corresponding_vacreport.location = args['location']
    the_one_corresponding_vacreport.save()
    
    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    args['valide'] = True
    # args['info_to_contact'] = "Mise a jour du rapport de suivi du bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_mother'].id_mother+"' a reussie."
    args['info_to_contact'] = "Mesaje ikosora iyari yatanzwe yerekeye ikurikiranwa ry umwana '" +args['child_number'].child_code_designation+"' w umupfasoni '"+args['concerned_mother'].id_mother+"' yashitse neza"

# -----------------------------------------------------------------


# -----------------------------------------------------------------
def record_risk_report(args):

    args['mot_cle'] = "RIS"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return

    # Let's check if it is report about a child or a mother. We count the number of values sent
    # Let's check if the message sent is composed by an expected number of values
    # args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values_ris(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return

    # Let's check if the symptom(s) is/are valid
    args["symptoms"] = args['text'].split(' ')[2]
    check_symptoms(args)
    if not args['valide']:
        return

    if(args['ris_type'] == "RIS_CHILD"):
        # The report sent is a child report
        # Let's check if this mother has a child with the sent child number
        args["child_id"] = args['text'].split(' ')[3]
        check_child_exists(args)
        if not args['valide']:
            return

    if(args['ris_type'] == "RIS_WOMAN"):
        # We record a woman report
        pass

    # Now, everything is checked. Let's record the report
    the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_mother'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])
    created_ris_report = ReportRIS.objects.create(report = the_created_report)

    '''string_of_symptoms = ""
    first_symptom = True

    string_of_red_symptoms = ""
    first_red_symptom = True

    for one_symbol in args['checked_symptoms_list']:
        one_symptom = Symptom.objects.filter(symtom_designation__iexact = one_symbol)[0]
        created_report_symptom_connection = RIS_Report_Symptom.objects.create(ris_report = created_ris_report, symptom = one_symptom)
        if first_symptom:
            string_of_symptoms = string_of_symptoms+one_symptom.symtom_designation
            first_symptom = False
        else:
            string_of_symptoms = string_of_symptoms+", "+one_symptom.symtom_designation
        
        if one_symptom.is_red_symptom:
            if first_red_symptom:
                string_of_red_symptoms = string_of_red_symptoms+one_symptom.symtom_designation
                first_red_symptom = False
            else:
                string_of_red_symptoms = string_of_red_symptoms+", "+one_symptom.symtom_designation
                '''

    if(args['ris_type'] == "RIS_CHILD"):
        # Let's record informations related to the child
        report_ris_bebe = ReportRISBebe.objects.create(ris_report = created_ris_report, concerned_child = args['concerned_child'])

    # The message in this variable will be sent to supervisors
    args['info_to_supervisors'] = ""

    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    args['valide'] = True

    if(args['ris_type'] == "RIS_CHILD"):
        # args['info_to_contact'] = "Le rapport de risque pour le bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."
        args['info_to_contact'] = "Mesaje warungitse yerekeye ibimenyetse vy indwara kumwana '" +args['child_number'].child_code_designation+"' w umupfasoni '"+args['concerned_mother'].id_mother+"' yashitse neza"
        # args['info_to_supervisors'] = "L enfant '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_mother'].id_mother+"' presente les symptomes suivants : "+string_of_symptoms
        args['info_to_supervisors'] = "Umwana '" +args['child_number'].child_code_designation+"' w umupfasoni nomero '"+args['concerned_mother'].id_mother+"', akurikiranwa n umuremesha kiyago '"+args['the_sender'].phone_number+"', wo mu gacimbiri '"+args['sub_colline'].name+"' afise ikimenyetso mburizi : "+args['kirundi_red_symptoms_names']

    if(args['ris_type'] == "RIS_WOMAN"):
        # args['info_to_contact'] = "Le rapport de risque de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."
        args['info_to_contact'] = "Mesaje warungitse yerekeye ibimenyetso vy indwara ku mupfasoni '"+args['concerned_mother'].id_mother+"' yashitse neza"
        # args['info_to_supervisors'] = "La maman '"+args['concerned_mother'].id_mother+"' presente les symptomes suivants : "+string_of_symptoms
        args['info_to_supervisors'] = "Umupfasoni nomero '"+args['concerned_mother'].id_mother+"', akurikiranwa n umuremesha kiyago '"+args['the_sender'].phone_number+"', wo mu gacimbiri '"+args['sub_colline'].name+"' afise ikimenyetso mburizi : "+args['kirundi_red_symptoms_names']

    if len(args['kirundi_red_symptoms_names']) > 1:
        #We inform red alerts only to supervisors
        the_contact_phone_number = "tel:"+args['supervisor_phone_number']
        data = {"urns": [the_contact_phone_number],"text": args['info_to_supervisors']}
        args['data'] = data
        send_sms_through_rapidpro(args)

        #if len(string_of_red_symptoms) > 1:
        #We need to inform national supervisors
        if(args['ris_type'] == "RIS_CHILD"):
            args['info_to_supervisors'] = "Umwana '" +args['child_number'].child_code_designation+"' w umupfasoni '"+args['concerned_mother'].id_mother+"', wo mu gacimbiri '"+args['sub_colline'].name+"' ko muri '"+args['the_sender'].cds.name+"', '"+args['the_sender'].cds.district.name+"', BPS '"+args['the_sender'].cds.district.bps.name+"' afise ikimenyetso mburizi : "+args['kirundi_red_symptoms_names']

        if(args['ris_type'] == "RIS_WOMAN"):
            args['info_to_supervisors'] = "Umupfasoni '"+args['concerned_mother'].id_mother+"', wo mu gacimbiri '"+args['sub_colline'].name+"' ko muri '"+args['the_sender'].cds.name+"', '"+args['the_sender'].cds.district.name+"', BPS '"+args['the_sender'].cds.district.bps.name+"' afise ikimenyetso mburizi : "+args['kirundi_red_symptoms_names']

        national_sup_phone_numbers = get_national_sup_phone_number()

        print national_sup_phone_numbers

        data = {"urns": national_sup_phone_numbers,"text": args['info_to_supervisors']}
        args['data'] = data
        send_sms_through_rapidpro(args)



# -----------------------------------------------------------------
def record_mother_arrived_at_hf(args):
    ''' This function is used to record that a woman for whom a red alert
    report have been sent arrived at the health facility '''

    args['mot_cle'] = "ARR"

    # Let's check if the person who send this message is a supervisor of a CHW
    #He/she should be from a health facility
    check_if_contact_is_from_hf(args)
    if not args['valide']:
        return

    # Let's check if it is report about a child or a mother. We count the number of values sent
    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return

    # Let's check if there is a registered risk report about this mother
    check_risk_report_exists_for_given_woman(args)
    if not args['valide']:
        return

    args['one_concerned_risk_reports'].mother_arrived_at_health_facility = True
    args['one_concerned_risk_reports'].save()

    args['info_to_contact'] = "Ubutumwa uhejeje kurungika buvuga ko umupfasoni afise inomero "+args["sent_mother_id"]+" yashitse kw ivuriro bwashitse neza."

    args['info_to_supervisors'] = "Umuntu akoresheje nomero ya telephone "+args['phone']+" amenyesheje ko umupfasoni afise inomero "+args["sent_mother_id"]+" yashitse kw ivuriro."

    national_sup_phone_numbers = get_national_sup_phone_number()

    print national_sup_phone_numbers

    data = {"urns": national_sup_phone_numbers,"text": args['info_to_supervisors']}
    args['data'] = data
    print data
    send_sms_through_rapidpro(args)


    national_sup_phone_numbers = get_national_sup_phone_number()

    print national_sup_phone_numbers

    data = {"urns": national_sup_phone_numbers,"text": args['info_to_supervisors']}
    args['data'] = data
    send_sms_through_rapidpro(args)


def modify_record_risk_report(args):

    args['mot_cle'] = "RISM"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return

    # Let's check if it is report about a child or a mother. We count the number of values sent
    # Let's check if the message sent is composed by an expected number of values
    # args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values_ris(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return

    # Let's check if the symptom(s) is/are valid
    args["symptoms"] = args['text'].split(' ')[2]
    check_symptoms(args)
    if not args['valide']:
        return

    if(args['ris_type'] == "RIS_CHILD"):
        # The report sent is a child report
        # Let's check if this mother has a child with the sent child number
        args["child_id"] = args['text'].split(' ')[3]
        check_child_exists(args)
        if not args['valide']:
            return

    if(args['ris_type'] == "RIS_WOMAN"):
        # We record a woman report
        pass

    # Let's check if the mother with this id has an already registered RIS report
    the_existing_ris_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3])
    if len(the_existing_ris_report) < 1:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Aucun rapport 'RIS' trouve de la maman '"+args['concerned_mother'].id_mother+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Nta raporo 'RIS' yumuvyeyi '"+args['concerned_mother'].id_mother+"' irabaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    the_only_one_corresponding_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3]).order_by('-id')[0]

    the_corresponding_ris_report = ReportRIS.objects.filter(report = the_only_one_corresponding_report)
    if len(the_corresponding_ris_report) < 1:
        args['valide'] = False
        args['info_to_contact'] = "Exception. Un rapport 'RIS' correspondant a la maman indiquee n est pas trouve. Veuillez contacter l administrateur du systeme"
        return
    the_one_corresponding_risreport = the_corresponding_ris_report[0]

    # Let's update
    the_only_one_corresponding_report.chw = args['the_sender']
    the_only_one_corresponding_report.sub_hill = args['sub_colline']
    the_only_one_corresponding_report.cds = args['facility']
    the_only_one_corresponding_report.mother = args['concerned_mother']
    the_only_one_corresponding_report.reporting_date = datetime.datetime.now().date()
    the_only_one_corresponding_report.text = args['text']
    the_only_one_corresponding_report.save()

    the_one_corresponding_risreport.report = the_only_one_corresponding_report
    the_one_corresponding_risreport.save()

    all_ris_report_symptom_connections = RIS_Report_Symptom.objects.filter(ris_report = the_one_corresponding_risreport)
    if len(all_ris_report_symptom_connections) > 0:
        for one_ris_report_symptom_connection in all_ris_report_symptom_connections:
            one_ris_report_symptom_connection.delete()

    '''string_of_symptoms = ""
    first_symptom = True

    string_of_red_symptoms = ""
    first_red_symptom = True

    for one_symbol in args['checked_symptoms_list']:
        one_symptom = Symptom.objects.filter(symtom_designation__iexact = one_symbol)[0]
        created_report_symptom_connection = RIS_Report_Symptom.objects.create(ris_report = the_one_corresponding_risreport, symptom = one_symptom)
        if first_symptom:
            string_of_symptoms = string_of_symptoms+one_symptom.symtom_designation
            first_symptom = False
        else:
            string_of_symptoms = string_of_symptoms+", "+one_symptom.symtom_designation


        if one_symptom.is_red_symptom:
            if first_red_symptom:
                string_of_red_symptoms = string_of_red_symptoms+one_symptom.symtom_designation
                first_red_symptom = False
            else:
                string_of_red_symptoms = string_of_red_symptoms+", "+one_symptom.symtom_designation
                '''


    if(args['ris_type'] == "RIS_CHILD"):
        # Let's record informations related to the child
        report_ris_bebe = ReportRISBebe.objects.get_or_create(ris_report = the_one_corresponding_risreport, concerned_child = args['concerned_child'])

    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    args['valide'] = True
    if(args['ris_type'] == "RIS_CHILD"):
        # args['info_to_contact'] = "Mise a jour du rapport de risque pour le bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_mother'].id_mother+"' a reussie."
        args['info_to_contact'] = "Mesaje ikosora iyari yarungitswe yerekeye ibimenyetso vy indwara kumwana '" +args['child_number'].child_code_designation+"' w umupfasoni '"+args['concerned_mother'].id_mother+"' yashitse neza"
        args['info_to_supervisors'] = "Mesaje yo gukosora. Umwana '" +args['child_number'].child_code_designation+"' w umupfasoni nomero '"+args['concerned_mother'].id_mother+"', akurikiranwa n umuremesha kiyago '"+args['the_sender'].phone_number+"', wo mu gacimbiri '"+args['sub_colline'].name+"' afise ikimenyetso mburizi : "+args['kirundi_red_symptoms_names']
    if(args['ris_type'] == "RIS_WOMAN"):
        # args['info_to_contact'] = "Mise a jour du rapport de risque de la maman '"+args['concerned_mother'].id_mother+"' a reussie."
        args['info_to_contact'] = "Mesaje ikosora iyari yarungitswe yerekeye ibimenyetso vy indwara ku mupfasoni '"+args['concerned_mother'].id_mother+"' yashitse neza"
        args['info_to_supervisors'] = "Mesaje yo gukosora. Umupfasoni nomero '"+args['concerned_mother'].id_mother+"', akurikiranwa n umuremesha kiyago '"+args['the_sender'].phone_number+"', wo mu gacimbiri '"+args['sub_colline'].name+"' afise ikimenyetso mburizi : "+args['kirundi_red_symptoms_names']

    if len(args['kirundi_red_symptoms_names']) > 1:
        the_contact_phone_number = "tel:"+args['supervisor_phone_number']
        data = {"urns": [the_contact_phone_number],"text": args['info_to_supervisors']}
        args['data'] = data
        send_sms_through_rapidpro(args)

        #if len(string_of_red_symptoms) > 1:
        #We need to inform national supervisors
        if(args['ris_type'] == "RIS_CHILD"):
            args['info_to_supervisors'] = "Mesaje yo gukosora. Umwana '" +args['child_number'].child_code_designation+"' w umupfasoni '"+args['concerned_mother'].id_mother+"', wo mu gacimbiri '"+args['sub_colline'].name+"' ko muri '"+args['the_sender'].cds.name+"', '"+args['the_sender'].cds.district.name+"', BPS '"+args['the_sender'].cds.district.bps.name+"' afise ikimenyetso mburizi : "+args['kirundi_red_symptoms_names']

        if(args['ris_type'] == "RIS_WOMAN"):
            args['info_to_supervisors'] = "Mesaje yo gukosora. Umupfasoni '"+args['concerned_mother'].id_mother+"', wo mu gacimbiri '"+args['sub_colline'].name+"' ko muri '"+args['the_sender'].cds.name+"', '"+args['the_sender'].cds.district.name+"', BPS '"+args['the_sender'].cds.district.bps.name+"' afise ikimenyetso mburizi : "+args['kirundi_red_symptoms_names']


        national_sup_phone_numbers = get_national_sup_phone_number()

        print national_sup_phone_numbers

        data = {"urns": national_sup_phone_numbers,"text": args['info_to_supervisors']}
        args['data'] = data
        send_sms_through_rapidpro(args)
# -----------------------------------------------------------------


# -----------------------------------------------------------------
def record_response_to_risk_report(args):

    args['mot_cle'] = "RER"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return

    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return

    # Let's check if there is a RIS report already recorded
    check_mother_has_ris_report(args)
    if not args['valide']:
        return

    # Let's check health status value
    args["health_status_value"] = args['text'].split(' ')[2]
    args["health_status_meaning"] = "etat de sante"
    check_health_status(args)
    if not args['valide']:
        return

    # Let's check if the value of rescue received exists
    args["rescue_received"] = args['text'].split(' ')[3]
    args["rescue_received_meaning"] = "Secourt recu"
    check_rescue_received(args)
    if not args['valide']:
        return

    # Let's record the report
    the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_mother'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])

    created_rer_report = ReportRER.objects.create(report = the_created_report, ris = args['the_concerned_ris'], rescue = args['concerned_rescue_received'], current_state = args['concerned_health_status'])
    
    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    args['valide'] = True
    # args['info_to_contact'] = "Le rapport envoye de reponse au risque de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."
    args['info_to_contact'] = "Mesaje ivuga icakozwe ku vyerekeye ibimenyetso vy indwara vyabonetse ku mupfasoni '"+args['concerned_mother'].id_mother+"' yashitse neza"


# Modify
def modify_record_response_to_risk_report(args):

    args['mot_cle'] = "RERM"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return

    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return

    # Let's check if there is a RIS report already recorded
    check_mother_has_ris_report(args)
    if not args['valide']:
        return

    # Let's check health status value
    args["health_status_value"] = args['text'].split(' ')[2]
    args["health_status_meaning"] = "etat de sante"
    check_health_status(args)
    if not args['valide']:
        return

    # Let's check if the value of rescue received exists
    args["rescue_received"] = args['text'].split(' ')[3]
    args["rescue_received_meaning"] = "Secourt recu"
    check_rescue_received(args)
    if not args['valide']:
        return

    # Let's check if the mother with this id has an already registered RER report
    the_existing_rer_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3])
    if len(the_existing_rer_report) < 1:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Aucun rapport 'RER' trouve de la maman '"+args['concerned_mother'].id_mother+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Nta raporo 'RER' yumuvyeyi '"+args['concerned_mother'].id_mother+"' irabaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    the_only_one_corresponding_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3]).order_by('-id')[0]

    the_corresponding_rer_report = ReportRER.objects.filter(report = the_only_one_corresponding_report)
    if len(the_corresponding_rer_report) < 1:
        args['valide'] = False
        args['info_to_contact'] = "Exception. Un rapport 'RER' correspondant a la maman indiquee n est pas trouve. Veuillez contacter l administrateur du systeme"
        return
    the_one_corresponding_rerreport = the_corresponding_rer_report[0]

    # Let's update
    the_only_one_corresponding_report.chw = args['the_sender']
    the_only_one_corresponding_report.sub_hill = args['sub_colline']
    the_only_one_corresponding_report.cds = args['facility']
    the_only_one_corresponding_report.mother = args['concerned_mother']
    the_only_one_corresponding_report.reporting_date = datetime.datetime.now().date()
    the_only_one_corresponding_report.text = args['text']
    the_only_one_corresponding_report.save()

    the_one_corresponding_rerreport.report = the_only_one_corresponding_report
    the_one_corresponding_rerreport.ris = args['the_concerned_ris']
    the_one_corresponding_rerreport.rescue = args['concerned_rescue_received']
    the_one_corresponding_rerreport.current_state = args['concerned_health_status']
    the_one_corresponding_rerreport.save()

    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    args['valide'] = True
    # args['info_to_contact'] = "Mise a jour du rapport envoye en rapport avec la reponse au risque concernant la maman '"+args['concerned_mother'].id_mother+"' a reussie."
    args['info_to_contact'] = "Mesaje ikosora iyari yatanzwe ivuga icakozwe ku vyerekeye ibimenyetso vy indwara vy abonetse ku mupfasoni '"+args['concerned_mother'].id_mother+"' yashitse neza"
# -----------------------------------------------------------------


# -----------------------------------------------------------------
def record_death_report(args):

    args['mot_cle'] = "DEC"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return

    # Let's check if the message sent is composed by an expected number of values
    '''args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return'''

    # Let's check if it is report about a child or a mother. We count the number of values sent
    # Let's check if the message sent is composed by an expected number of values
    check_number_of_values_dec(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return

    # Let's check if the location is valid
    args["location"] = args['text'].split(' ')[2]
    # date_meaning should be change to location_meaning
    # args["date_meaning"] = "lieu de deces"
    args["date_meaning"] = "Ikibanza umuntu yapfiriyemwo"
    check_location(args)
    if not args['valide']:
        return

    # Let's check if the death code is valid
    args["death_code"] = args['text'].split(' ')[3]
    args["death_code_meaning"] = "Code de deces"
    check_death_code(args)
    if not args['valide']:
        return

    if(args['dec_type'] == "DEC_CHILD"):
        # The report sent is a child report
        # Let's check if this mother has a child with the sent child number
        args["child_id"] = args['text'].split(' ')[4]
        check_child_exists(args)
        if not args['valide']:
            return

    if(args['dec_type'] == "DEC_WOMAN"):
        # We record a woman report
        pass

    # Now, everything is checked. Let's record the report
    the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_mother'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])

    created_dec_report = ReportDEC.objects.create(report = the_created_report, location = args['location'], death_code = args['death_code'])

    if(args['dec_type'] == "DEC_CHILD"):
        # Let's record informations related to the child
        report_dec_bebe = ReportDECBebe.objects.create(death_report = created_dec_report, concerned_child = args['concerned_child'])

    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    args['valide'] = True
    if(args['dec_type'] == "DEC_CHILD"):
        # args['info_to_contact'] = "Le rapport de deces du bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."
        args['info_to_contact'] = "Mesaje ivuga urupfu rw umwana '" +args['child_number'].child_code_designation+"' w umupfasoni '"+args['concerned_mother'].id_mother+"' yashitse"
        args['info_to_supervisors'] = "Umuremesha kiyago akoresha '"+args['phone']+"' ahejeje gutanga mesaje ivuga urupfu rw umwana '" +args['child_number'].child_code_designation+"' w umupfasoni '"+args['concerned_mother'].id_mother+"'."
    if(args['dec_type'] == "DEC_WOMAN"):
        # args['info_to_contact'] = "Le rapport de deces de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."
        args['info_to_contact'] = "Mesaje ivuga urupfu rw umupfasoni '"+args['concerned_mother'].id_mother+"' yashitse"
        args['info_to_supervisors'] = "Umuremesha kiyago akoresha '"+args['phone']+"' ahejeje gutanga mesaje ivuga urupfu rw umupfasoni '"+args['concerned_mother'].id_mother+"'"

    
    the_contact_phone_number = "tel:"+args['supervisor_phone_number']
    data = {"urns": [the_contact_phone_number],"text": args['info_to_supervisors']}
    args['data'] = data
    send_sms_through_rapidpro(args)


    #We need to inform national supervisors
    if(args['dec_type'] == "DEC_CHILD"):
        args['info_to_supervisors'] = "Umuremesha kiyago akoresha '"+args['phone']+"', wo mu gacimbiri '"+args['sub_colline'].name+"' ko muri '"+args['the_sender'].cds.name+"', '"+args['the_sender'].cds.district.name+"', BPS '"+args['the_sender'].cds.district.bps.name+"' ahejeje gutanga mesaje ivuga urupfu rw umwana '" +args['child_number'].child_code_designation+"' w umupfasoni '"+args['concerned_mother'].id_mother+"'."
    if(args['dec_type'] == "DEC_WOMAN"):
        args['info_to_supervisors'] = "Umuremesha kiyago akoresha '"+args['phone']+"', wo mu gacimbiri '"+args['sub_colline'].name+"' ko muri '"+args['the_sender'].cds.name+"', '"+args['the_sender'].cds.district.name+"', BPS '"+args['the_sender'].cds.district.bps.name+"' ahejeje gutanga mesaje ivuga urupfu rw umupfasoni '"+args['concerned_mother'].id_mother+"'"

    national_sup_phone_numbers = get_national_sup_phone_number()

    print national_sup_phone_numbers

    data = {"urns": national_sup_phone_numbers,"text": args['info_to_supervisors']}
    args['data'] = data
    send_sms_through_rapidpro(args)



# Modify
def modify_record_death_report(args):

    args['mot_cle'] = "DECM"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return

    # Let's check if the message sent is composed by an expected number of values
    '''args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return'''

    # Let's check if it is report about a child or a mother. We count the number of values sent
    # Let's check if the message sent is composed by an expected number of values
    check_number_of_values_dec(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return

    # Let's check if the location is valid
    args["location"] = args['text'].split(' ')[2]
    # date_meaning should be change to location_meaning
    args["date_meaning"] = "Ikibanza umuntu yapfiriyemwo"
    check_location(args)
    if not args['valide']:
        return

    # Let's check if the death code is valid
    args["death_code"] = args['text'].split(' ')[3]
    args["death_code_meaning"] = "Code de deces"
    check_death_code(args)
    if not args['valide']:
        return

    if(args['dec_type'] == "DEC_CHILD"):
        # The report sent is a child report
        # Let's check if this mother has a child with the sent child number
        args["child_id"] = args['text'].split(' ')[4]
        check_child_exists(args)
        if not args['valide']:
            return

    if(args['dec_type'] == "DEC_WOMAN"):
        # We record a woman report
        pass

    # Let's check if the mother with this id has an already registered DEC report
    the_existing_dec_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3])
    if len(the_existing_dec_report) < 1:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Aucun rapport 'DEC' trouve de la maman '"+args['concerned_mother'].id_mother+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Nta raporo 'DEC' yumuvyeyi numero '"+args['concerned_mother'].id_mother+"' irabaho. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    the_only_one_corresponding_report = Report.objects.filter(mother = args['concerned_mother'], category = args['mot_cle'][0:3]).order_by('-id')[0]

    the_corresponding_dec_report = ReportDEC.objects.filter(report = the_only_one_corresponding_report)
    if len(the_corresponding_dec_report) < 1:
        args['valide'] = False
        args['info_to_contact'] = "Exception. Un rapport 'DEC' correspondant a la maman indiquee n est pas trouve. Veuillez contacter l administrateur du systeme"
        return
    the_one_corresponding_decreport = the_corresponding_dec_report[0]

    # Let's update
    the_only_one_corresponding_report.chw = args['the_sender']
    the_only_one_corresponding_report.sub_hill = args['sub_colline']
    the_only_one_corresponding_report.cds = args['facility']
    the_only_one_corresponding_report.mother = args['concerned_mother']
    the_only_one_corresponding_report.reporting_date = datetime.datetime.now().date()
    the_only_one_corresponding_report.text = args['text']
    the_only_one_corresponding_report.save()

    the_one_corresponding_decreport.report = the_only_one_corresponding_report
    the_one_corresponding_decreport.location = args['location']
    the_one_corresponding_decreport.death_code = args['death_code']
    if(args['dec_type'] == "DEC_CHILD"):
        # Let's update informations related to the child
        reports_dec_bebe = ReportDECBebe.objects.filter(death_report = the_one_corresponding_decreport)
        if len(reports_dec_bebe) < 1:
            report_dec_bebe = ReportDECBebe.objects.create(death_report = the_one_corresponding_decreport, concerned_child = args['concerned_child'])
        else:
            one_corresponding_report_dec_bebe = reports_dec_bebe[0]
            one_corresponding_report_dec_bebe.death_report = the_one_corresponding_decreport
            one_corresponding_report_dec_bebe.concerned_child = args['concerned_child']
            one_corresponding_report_dec_bebe.save()
    the_one_corresponding_decreport.save()

    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    args['valide'] = True
    if(args['dec_type'] == "DEC_CHILD"):
        # args['info_to_contact'] = "Mise a jour du rapport de deces du bebe '" +args['child_number'].child_code_designation+"' de la maman '"+args['concerned_mother'].id_mother+"' a reussie."
        args['info_to_contact'] = "Mesaje ikosora iyari yatanzwe yerekeye urupfu rw umwana '" +args['child_number'].child_code_designation+"' w umupfasoni '"+args['concerned_mother'].id_mother+"' yashitse"
        args['info_to_supervisors'] = "Mesaje ikosora iyari yatanzwe : Umuremesha kiyago akoresha '"+args['phone']+"' ahejeje gutanga mesaje ivuga urupfu rw umwana '" +args['child_number'].child_code_designation+"' w umupfasoni '"+args['concerned_mother'].id_mother+"'."
    if(args['dec_type'] == "DEC_WOMAN"):
        # args['info_to_contact'] = "Mise a jour du rapport de deces de la maman '"+args['concerned_mother'].id_mother+"' a reussie."
        args['info_to_contact'] = "Mesaje ikosora iyari yatanzwe yerekeye urupfu rw umupfasoni '"+args['concerned_mother'].id_mother+"' yashitse"
        args['info_to_supervisors'] = "Mesaje ikosora iyari yatanzwe : Umuremesha kiyago akoresha '"+args['phone']+"' ahejeje gutanga mesaje ivuga urupfu rw umupfasoni '"+args['concerned_mother'].id_mother+"'"


    the_contact_phone_number = "tel:"+args['supervisor_phone_number']
    data = {"urns": [the_contact_phone_number],"text": args['info_to_supervisors']}
    args['data'] = data
    send_sms_through_rapidpro(args)


    #We need to inform national supervisors
    if(args['dec_type'] == "DEC_CHILD"):
        args['info_to_supervisors'] = "Mesaje ikosora iyari yatanzwe. Umuremesha kiyago akoresha '"+args['phone']+"', wo mu gacimbiri '"+args['sub_colline'].name+"' ko muri '"+args['the_sender'].cds.name+"', '"+args['the_sender'].cds.district.name+"', BPS '"+args['the_sender'].cds.district.bps.name+"' ahejeje gutanga mesaje ivuga urupfu rw umwana '" +args['child_number'].child_code_designation+"' w umupfasoni '"+args['concerned_mother'].id_mother+"'."
    if(args['dec_type'] == "DEC_WOMAN"):
        args['info_to_supervisors'] = "Mesaje ikosora iyari yatanzwe. Umuremesha kiyago akoresha '"+args['phone']+"', wo mu gacimbiri '"+args['sub_colline'].name+"' ko muri '"+args['the_sender'].cds.name+"', '"+args['the_sender'].cds.district.name+"', BPS '"+args['the_sender'].cds.district.bps.name+"' ahejeje gutanga mesaje ivuga urupfu rw umupfasoni '"+args['concerned_mother'].id_mother+"'"

    national_sup_phone_numbers = get_national_sup_phone_number()

    print national_sup_phone_numbers

    data = {"urns": national_sup_phone_numbers,"text": args['info_to_supervisors']}
    args['data'] = data
    send_sms_through_rapidpro(args)

# -----------------------------------------------------------------


# -----------------------------------------------------------------
def record_leave_report(args):

    args['mot_cle'] = "DEP"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return
    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return

    # Let's record the report
    the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_mother'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])

    created_dep_report = ReportDEP.objects.create(report = the_created_report)

    # Let's change the status of this mother. Now is not affected anywhere
    args['concerned_mother'].is_affected_somewhere = False
    args['concerned_mother'].save()
    
    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    args['valide'] = True
    # args['info_to_contact'] = "Le rapport du depart de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."
    args['info_to_contact'] = "Mesaje ivuga ko umupfasoni '"+args['concerned_mother'].id_mother+"' yimutse yashitse neza"


def modify_record_leave_report(args):
    # This function needs to be rewritten
    args['mot_cle'] = "DEPM"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return

    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return

    # Let's check if this mother is affected somewhere
    check_mother_is_affected_somewhere(args)
    if not args['valide']:
        return

    # Let's check if the last report of this mother comes from this colline
    the_existing_dep_report = Report.objects.filter(mother = args['concerned_mother'])
    if len(the_existing_dep_report) < 1:
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Aucun rapport trouve concernant la maman '"+args['concerned_mother'].id_mother+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Erreur. Aucun rapport trouve concernant la maman '"+args['concerned_mother'].id_mother+"'. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        return

    the_only_one_corresponding_report = Report.objects.filter(mother = args['concerned_mother']).order_by('-id')[0]

    if(the_only_one_corresponding_report.sub_hill != args['the_sender'].sub_colline):
        args['valide'] = False
        # args['info_to_contact'] = "Erreur. Le dernier rapport de la maman '"+args['concerned_mother'].id_mother+"' n est pas venu de votre sous colline. Pour corriger, veuillez reenvoyer un message corrige et commencant par le mot cle "+args['mot_cle']
        args['info_to_contact'] = "Ikosa. Raporo yanyuma yumuvyeyi nomero '"+args['concerned_mother'].id_mother+"' ntiyavuye aho usanzwe ukorera. Mu gukosora, subira urungike iyo mesaje itangurwa na '"+args['mot_cle']+"' yanditse neza"
        return

    the_corresponding_dep_report = ReportDEP.objects.filter(report = the_only_one_corresponding_report)
    if len(the_corresponding_dep_report) < 1:
        args['valide'] = False
        args['info_to_contact'] = "Exception. Un rapport 'DEP' correspondant a la maman indiquee n est pas trouve. Veuillez contacter l administrateur du systeme"
        return
    the_one_corresponding_depreport =the_corresponding_dep_report[0]

    # Let's update
    the_only_one_corresponding_report.chw = args['the_sender']
    the_only_one_corresponding_report.sub_hill = args['sub_colline']
    the_only_one_corresponding_report.cds = args['facility']
    the_only_one_corresponding_report.mother = args['concerned_mother']
    the_only_one_corresponding_report.reporting_date = datetime.datetime.now().date()
    the_only_one_corresponding_report.text = args['text']
    the_only_one_corresponding_report.save()

    the_one_corresponding_depreport.report = the_only_one_corresponding_report
    the_one_corresponding_depreport.save()

    #If the CHW was inactive, i activate him/her
    activate_inactive_chw(args)

    args['valide'] = True
    # args['info_to_contact'] = "Mise a jour du rapport de depart de la maman '"+args['concerned_mother'].id_mother+"' a reussie."
    args['info_to_contact'] = "Mesaje ikosora iyari yatenzwe ivuga iyimuka ry umupfasoni '"+args['concerned_mother'].id_mother+"' yashitse neza"
# -----------------------------------------------------------------


# -----------------------------------------------------------------

def record_mother_reception_report(args):

    args['mot_cle'] = "REC"

    # Let's check if the person who send this message is a reporter
    check_if_is_reporter(args)
    if not args['valide']:
        return

    # Let's check if the message sent is composed by an expected number of values
    args["expected_number_of_values"] = getattr(settings, 'EXPECTED_NUMBER_OF_VALUES', '')[args['message_type']]
    check_number_of_values(args)
    if not args['valide']:
        return

    # Let's check if the mother id sent is valid
    args["sent_mother_id"] = args['text'].split(' ')[1]
    check_mother_id_is_valid(args)
    if not args['valide']:
        return

    # Let's record the report
    the_created_report = Report.objects.create(chw = args['the_sender'], sub_hill = args['sub_colline'], cds = args['facility'], mother = args['concerned_mother'], reporting_date = datetime.datetime.now().date(), text = args['text'], category = args['mot_cle'])

    created_rec_report = ReportREC.objects.create(report = the_created_report)

    # Let's change the status of this mother. Now is affected somewhere
    args['concerned_mother'].is_affected_somewhere = True
    args['concerned_mother'].save()

    args['valide'] = True
    # args['info_to_contact'] = "Le rapport de reception de la maman '"+args['concerned_mother'].id_mother+"' est bien enregistre."
    args['info_to_contact'] = "Mesaje ivuga ko umupfasoni '"+args['concerned_mother'].id_mother+"' yimukiye aho ukorera yashitse neza"
