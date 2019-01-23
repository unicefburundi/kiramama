#  -*- coding: utf-8 -*-
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
import pytz
from django.conf import settings
import requests
import json
from kiramama_app.models import *
from datetime import datetime, timedelta, time

logger = get_task_logger(__name__)


def send_sms_through_rapidpro(args):
    ''' 
    This function sends messages through rapidpro. Contact(s) and the
    message to send to them must be in args['data']
    '''
    token = getattr(settings, 'TOKEN', '')
    data = args['data']
    print(data)
    response = requests.post(settings.RAPIDPRO_BROADCAST_URL, headers={'Content-type': 'application/json', 'Authorization': 'Token %s' % token}, data=json.dumps(data))
    print("response :")
    print(response)


@periodic_task(run_every=(crontab(minute=20, hour='8')), name="send_scheduled_messages", ignore_result=True)
def send_scheduled_messages():
    today = datetime.today().date()
    today_7 = datetime.today().date() - timedelta(4)

    ready_to_send_mother_messages = NotificationsMother.objects.filter(date_time_for_sending__gte = today_7, date_time_for_sending__lte = today, is_sent=False)
    args = {}
    if len(ready_to_send_mother_messages) > 0:
        #  There is one or more messages to be sent to one or more mothers
        for mother_message in ready_to_send_mother_messages:
            if(mother_message.mother.phone_number):
                the_contact_phone_number = "tel:"+mother_message.mother.phone_number
                data = {
                    "urns": [the_contact_phone_number],
                    "text": mother_message.message_to_send
                    }
                args['data'] = data
                #  Changing the message status before calling "send_sms_through_rapidpro" is helpful when the task is running quickly
                #  and run the next time before all messages are sent
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

    ready_to_send_chw_messages = NotificationsCHW.objects.filter(date_time_for_sending__gte = today_7, date_time_for_sending__lte = today, is_sent=False)
    if len(ready_to_send_chw_messages) > 0:
        #  There is one or more messages to be sent to one or more mothers
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
    print("=== Begin change_chw_status ===")
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

    # Let's convert value_for_time to a number
    try:
        value_for_time = int(value_for_time)
    except:
        info = "Exception. The setting value in Settings model is not a number"
        return

    time_unit = one_setting_to_use.time_measuring_unit.code

    limit_time = ""


    if(time_unit.startswith("m") or time_unit.startswith("M")):
        # The time measuring unit used is minutes
        limit_time = datetime.now() - timedelta(minutes = value_for_time)
    if(time_unit.startswith("h") or time_unit.startswith("H")):
        # The time measuring unit used is hours
        limit_time = datetime.now() - timedelta(hours = value_for_time)

    if not isinstance(limit_time, datetime):
        info = "Something went wrong for limit time"
        return

    # Let's look for all CHW who didn't send any report for the time specified in settings
    all_chws = CHW.objects.filter(is_deleted=False)

    if len(all_chws) < 1:
        info = "No community health worker recorded in the system"
        return

    for chw in all_chws:
        reports_given_by_the_current_chw = Report.objects.filter(chw = chw)
        
        if len(reports_given_by_the_current_chw) < 1:
            # This community health work doesn't give any report
            # We change his status if there is many days (based on limit_time variable) after his/her registration
            # We will put here the code for changing his status if it is not already changed 
            pass
        else:
            # Let's check if this CHW doesn't spend many days (based on limit_time variable) without sending any report
            his_last_report = reports_given_by_the_current_chw.order_by('-id')[0]


            # if(his_last_report.reporting_date < limit_time):
            if(datetime.combine(his_last_report.reporting_date, datetime.now().time()) < limit_time):
                # This CHW spend many days without giving any report. We change his status from active to inactive
                chw.is_active = False
                chw.save()
            else:
                chw.is_active = True
                chw.save()

    print("=== Finish change_chw_status ===")




@periodic_task(run_every=(crontab(minute=30, hour='10')), name="tasks.change_chw_status", ignore_result=True) 
def inform_supersors_on_inactive_chw():
    '''
    This task inform the concerned supervisor if there is a community health work who is not active
    '''
    print("---Begin inform_supersors_on_inactive_chw---")
    # Let's update CHW status
    change_chw_status()

    all_none_active_chws = CHW.objects.filter(is_active = False, is_deleted=False)

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
    print("---Finish inform_supersors_on_inactive_chw---")



@periodic_task(run_every=(crontab(minute=30, hour='7')), name="tasks.cancel_reminders", ignore_result=True) 
def cancel_reminders():
    '''
    This task is used to cancel no longer needed reminders
    '''
    today = datetime.today().date()

    start_date = datetime.today().date() - timedelta(7)
    end_date = datetime.today().date() + timedelta(300)

    concerned_mothers_dec = Mother.objects.filter(report__category = "DEC")

    if len(concerned_mothers_dec) > 0:
        '''There is at least one death report.'''
        for one_woman in concerned_mothers_dec:
            #Let's delete notifications scheduled to be sent to this woman
            notifications_to_woman = NotificationsMother.objects.filter(mother = one_woman, date_time_for_sending__gte = start_date, date_time_for_sending__lte = end_date, is_sent=False)
            if len(notifications_to_woman) > 0:
                #We have to delete all these notifications
                for one_notification in notifications_to_woman:
                    print "==== Before deleting ===="
                    print one_notification.mother
                    print one_notification.date_time_for_sending
                    print one_notification.message_to_send
                    one_notification.delete()
                    print "==== After deleting ===="

            #Let's delete notifications scheduled to be sent to a CHW
            mother_id = one_woman.id_mother
            mother_id = " "+mother_id+" "
            notifications_to_chw = NotificationsCHW.objects.filter(message_to_send__contains = mother_id)
            if len(notifications_to_chw) > 0:
                #We have to delete all these notifications
                for one_notification in notifications_to_chw:
                    print "==== Before deleting ===="
                    print mother_id
                    print one_notification.date_time_for_sending
                    print one_notification.message_to_send
                    one_notification.delete()
                    print "==== After deleting ===="

