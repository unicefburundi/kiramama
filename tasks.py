from celery import Celery
from datetime import timedelta
#from django.core.management import setup_environ
#from kiramama import settings
import os
from django.core.wsgi import get_wsgi_application
import pytz
from django.conf import settings
import requests
import json

os.environ['DJANGO_SETTINGS_MODULE'] = 'kiramama.settings'
application = get_wsgi_application()

from kiramama_app.models import *


celery = Celery(__name__)
celery.config_from_object(__name__)


def send_sms_through_rapidpro(args):
    ''' This function sends messages through rapidpro. Contact(s) and the message to send to them must be in args['data'] '''
    url = 'https://api.rapidpro.io/api/v1/broadcasts.json'
    token = getattr(settings,'TOKEN','')

    data = args['data']

    response = requests.post(url, headers={'Content-type': 'application/json', 'Authorization': 'Token %s' % token}, data = json.dumps(data))


@celery.task
def send_scheduled_messages():
	print('***BIGIN - Here is in the task****')
	#Let's filter all mother notifications which are ready to be sent and which are not already sent
	#ready_to_send_mother_messages = NotificationsMother.objects.filter(date_time_for_sending__lte = datetime.now(), is_sent = False)
	ready_to_send_mother_messages = NotificationsMother.objects.filter(date_time_for_sending__lte = datetime.now(pytz.utc), is_sent = False)
	args = {}
	if len(ready_to_send_mother_messages) > 0:
	#There is one or more messages to be sent to one or more mothers
		for mother_message in ready_to_send_mother_messages:
			if(mother_message.mother.phone_number):
				print(mother_message.mother.phone_number)
				print mother_message.message_to_send
				the_contact_phone_number = "tel:"+mother_message.mother.phone_number
				data = {"urns": [the_contact_phone_number],"text": mother_message.message_to_send}
				args['data'] = data
				#Changing the message status before calling "send_sms_through_rapidpro" is helpful when the task is running quickly
				#and run the next time before all messages are sent
				mother_message.is_sent = True
				mother_message.save()
				send_sms_through_rapidpro(args)
				#mother_message.is_sent = True
				#mother_message.save()

	ready_to_send_chw_messages = NotificationsCHW.objects.filter(date_time_for_sending__lte = datetime.now(pytz.utc), is_sent = False)
	if len(ready_to_send_chw_messages) > 0:
	#There is one or more messages to be sent to one or more mothers
		for chw_message in ready_to_send_chw_messages:
			if(chw_message.chw.phone_number):
				print(chw_message.chw.phone_number)
				print chw_message.message_to_send
				the_contact_phone_number = "tel:"+chw_message.chw.phone_number
				data = {"urns": [the_contact_phone_number],"text": chw_message.message_to_send}
				args['data'] = data
				chw_message.is_sent = True
				chw_message.save()
				send_sms_through_rapidpro(args)
				#chw_message.is_sent = True
				#chw_message.save()
	print('***END - Here is in the task****')

CELERYBEAT_SCHEDULE = {
    'every-second': {
        'task': 'tasks.send_scheduled_messages',
        'schedule': timedelta(seconds=60),
    },
}
