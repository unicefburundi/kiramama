# -*- coding: utf-8 -*-
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
import pytz
from django.conf import settings
import requests
import json
from kiramama_app.models import *
#import datetime
from datetime import datetime, timedelta, time

logger = get_task_logger(__name__)


def send_sms_through_rapidpro(args):
    ''' 
    This function sends messages through rapidpro. Contact(s) and the
    message to send to them must be in args['data']
    '''
    print("Begin send_sms_through_rapidpro")
    token = getattr(settings, 'TOKEN', '')
    data = args['data']
    response = requests.post(settings.RAPIDPRO_BROADCAST_URL, headers={'Content-type': 'application/json', 'Authorization': 'Token %s' % token}, data=json.dumps(data))
    print("response :")
    print(response)

@periodic_task(run_every=(crontab(minute='*/15')), name="tasks.send_scheduled_messages", ignore_result=True) # Name better be in the format of http://bit.ly/gLye1c
def send_scheduled_messages():
    today = datetime.today().date()
    today_7 = datetime.today().date() - timedelta(7)
    # Let's filter all mother notifications which are ready to be sent and which are not already sent
    # ready_to_send_mother_messages = NotificationsMother.objects.filter(date_time_for_sending__lte = datetime.now(), is_sent = False)
    #ready_to_send_mother_messages = NotificationsMother.objects.filter(
        #date_time_for_sending__lte=datetime.now(pytz.utc), is_sent=False)
    
    #The below line should be uncommented later
    #ready_to_send_mother_messages = NotificationsMother.objects.filter(date_time_for_sending__gte = today_7, date_time_for_sending__lte = today, is_sent=False)
    ready_to_send_mother_messages = NotificationsMother.objects.filter(date_time_for_sending__gte = today_7, date_time_for_sending__lte = today)
    args = {}
    if len(ready_to_send_mother_messages) > 0:
        # There is one or more messages to be sent to one or more mothers
        for mother_message in ready_to_send_mother_messages:
            if(mother_message.mother.phone_number):
                the_contact_phone_number = "tel:"+mother_message.mother.phone_number
                data = {
                    "urns": [the_contact_phone_number],
                    "text": mother_message.message_to_send
                    }
                args['data'] = data
                # Changing the message status before calling "send_sms_through_rapidpro" is helpful when the task is running quickly
                # and run the next time before all messages are sent
                print("[Part 1]==>Before sending the message :")
                print(mother_message.message_to_send)
                print("To :")
                print(mother_message.mother.phone_number)
                send_sms_through_rapidpro(args)
                mother_message.is_sent = True
                mother_message.save()
                print("[Part 1]After sending the message :")
                print(mother_message.message_to_send)
                print("To :")
                print(mother_message.mother.phone_number)

    #ready_to_send_chw_messages = NotificationsCHW.objects.filter(
        #date_time_for_sending__lte=datetime.now(pytz.utc),
        #is_sent=False
        #)
    #The below line should be uncommented later
    #ready_to_send_chw_messages = NotificationsCHW.objects.filter(date_time_for_sending__gte = today_7, date_time_for_sending__lte = today, is_sent=False)
    ready_to_send_chw_messages = NotificationsCHW.objects.filter(date_time_for_sending__gte = today_7, date_time_for_sending__lte = today)
    if len(ready_to_send_chw_messages) > 0:
        # There is one or more messages to be sent to one or more mothers
        for chw_message in ready_to_send_chw_messages:
            if(chw_message.chw.phone_number):
                the_contact_phone_number = "tel:"+chw_message.chw.phone_number
                data = {
                    "urns": [the_contact_phone_number],
                    "text": chw_message.message_to_send
                    }
                args['data'] = data
                print("[Part 2]==> Before sending the message to :")
                print(chw_message.message_to_send)
                print("To :")
                print(chw_message.chw.phone_number)
                send_sms_through_rapidpro(args)
                chw_message.is_sent = True
                chw_message.save()
                print("[Part 2] After sending the message :")
                print(chw_message.message_to_send)
                print("To :")
                print(chw_message.chw.phone_number)







def change_chw_status():
    ''' 
        This function switch a CHW to the following status : active/inactive
        A CHW is switched to inactive status if he spend long time without sending any message.
    '''
    key_word_for_chwai_setting = getattr(settings,'KEY_WORD_FOR_CHW_ACTIVE_SETTING','')

    if len(key_word_for_chwai_setting) < 1:
        info = "Exception. Le parametre 'KEY_WORD_FOR_CHW_ACTIVE_SETTING' n est pas configure dans le fichiers settings"
        return

    settings_to_use = Settings.objects.filter(setting_code = key_word_for_chwai_setting)

    if len(settings_to_use) < 1:
        info = "Exception. Un parametre qui montre les criteres d inactivation d un agent de sante communautaire n est pas cree dans le model Settings"
        return

    one_setting_to_use = settings_to_use[0]

    value_for_time = one_setting_to_use.setting_value

    #Let's convert value_for_time to a number
    try:
        value_for_time = int(value_for_time)
    except:
        info = "Exception. The setting value in Settings model is not a number"
        return

    time_unit = one_setting_to_use.time_measuring_unit.code

    limit_time = ""


    if(time_unit.startswith("m") or time_unit.startswith("M")):
        #The time measuring unit used is minutes
        #limit_time = datetime.datetime.now() - datetime.timedelta(minutes = value_for_time)
        limit_time = datetime.now() - timedelta(minutes = value_for_time)
    if(time_unit.startswith("h") or time_unit.startswith("H")):
        #The time measuring unit used is hours
        #limit_time = datetime.datetime.now() - datetime.timedelta(hours = value_for_time)
        limit_time = datetime.now() - timedelta(hours = value_for_time)

    #if not isinstance(limit_time, datetime.datetime):
    if not isinstance(limit_time, datetime):
        info = "Something went wrong for limit time"
        return

    #Let's look for all CHW who didn't send any report for the time specified in settings
    all_chws = CHW.objects.all()

    if len(all_chws) < 1:
        info = "No community health worker recorded in the system"
        return

    for chw in all_chws:
        reports_given_by_the_current_chw = Report.objects.filter(chw = chw)
        
        if len(reports_given_by_the_current_chw) < 1:
            #This community health work doesn't give any report
            #We change his status if there is many days (based on limit_time variable) after his/her registration
            #We will put here the code for changing his status if it is not already changed 
            pass
        else:
            #Let's check if this CHW doesn't spend many days (based on limit_time variable) without sending any report
            his_last_report = reports_given_by_the_current_chw.order_by('-id')[0]


            #if(his_last_report.reporting_date < limit_time):
            #if(datetime.datetime.combine(his_last_report.reporting_date, datetime.datetime.now().time()) < limit_time):
            if(datetime.combine(his_last_report.reporting_date, datetime.now().time()) < limit_time):
                #This CHW spend many days without giving any report. We change his status from active to inactive
                chw.is_active = False
                chw.save()




@periodic_task(run_every=(crontab(minute=0, hour='6')), name="tasks.change_chw_status", ignore_result=True) 
def inform_supersors_on_inactive_chw():
    '''
    This task inform the concerned supervisor if there is a community health work who is not active
    '''

    #Let's update CHW status
    change_chw_status()

    all_none_active_chws = CHW.objects.filter(is_active = False)

    if len(all_none_active_chws) < 1:
        return
    args = {}
    for inactive_chw in all_none_active_chws:
        his_supervisor_phone_number = inactive_chw.supervisor_phone_number
        supervisor_phone_number = "tel:"+his_supervisor_phone_number
        message_to_send = "Umuremesha kiyago akoresha numero '"+inactive_chw.phone_number+"' ntaherutse gutanga ubutumwa"
        data = {
        "urns": [supervisor_phone_number],
        "text": message_to_send
        }
        args['data'] = data
        send_sms_through_rapidpro(args)