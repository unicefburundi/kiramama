from celery import Celery
from datetime import timedelta
#from django.core.management import setup_environ
#from kiramama import settings
import os
from django.core.wsgi import get_wsgi_application
import pytz

os.environ['DJANGO_SETTINGS_MODULE'] = 'kiramama.settings'
application = get_wsgi_application()

from kiramama_app.models import *


celery = Celery(__name__)
celery.config_from_object(__name__)


@celery.task
def send_scheduled_messages():
	print('***BIGIN - Here is in the task****')
	#Let's filter all mother notifications which are ready to be sent and which are not already sent
	#ready_to_send_mother_messages = NotificationsMother.objects.filter(date_time_for_sending__lte = datetime.now(), is_sent = False)
	ready_to_send_mother_messages = NotificationsMother.objects.filter(date_time_for_sending__lte = datetime.now(pytz.utc), is_sent = False)
	if len(ready_to_send_mother_messages) > 0:
	#There is one or more messages to be sent to one or more mothers
		for mother_message in ready_to_send_mother_messages:
			print mother_message

	ready_to_send_chw_messages = NotificationsCHW.objects.filter(date_time_for_sending__lte = datetime.now(pytz.utc), is_sent = False)
	if len(ready_to_send_chw_messages) > 0:
	#There is one or more messages to be sent to one or more mothers
		for chw_message in ready_to_send_chw_messages:
			print chw_message
	print('***END - Here is in the task****')

CELERYBEAT_SCHEDULE = {
    'every-second': {
        'task': 'tasks.send_scheduled_messages',
        'schedule': timedelta(seconds=5),
    },
}
