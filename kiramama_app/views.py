from django.shortcuts import render
from kiramama_app.models import *
import datetime

# Create your views here.

def landing(request):
    return render(request, 'landing_page.html')


def change_chw_status(request):
	''' 
		This function switch a CHW to the following status : active/inactive
		A CHW is switched to inactive status if he spend long time without sending any message.
	'''

	key_word_for_chwai_setting = getattr(settings,'KEY_WORD_FOR_CHW_ACTIVE_SETTING','')

	settings_to_use = Settings.objects.filter(setting_code = key_word_for_chwai_setting)

	if len(settings_to_use) < 1:
		info = "Exception. Un parametre qui montre les criteres d inactivation d un agent de sante communautaire n est pas cree dans le model Settings"
		return

	one_setting_to_use = settings_to_use[0]

	value_for_time = one_setting_to_use.setting_value

	time_unit = one_setting_to_use.time_measuring_unit.code

	limit_time = ""

	if(time_unit.startswith("m") or time_unit.startswith("M")):
		limit_time = datetime.datetime.now().time() - datetime.timedelta(minutes = number_for_time)
	if(time_unit.startswith("h") or time_unit.startswith("H")):
		limit_time = datetime.datetime.now().time() - datetime.timedelta(hours = number_for_time)

	if not isinstance(limit_time, datetime.datetime):
		info = "Something went wrong for limit time"
		return

	#Let's look for all CHW who didn't send any report since
	all_chws = CHW.objects.all()

	if len(all_chws) < 1:
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

			if(his_last_report.reporting_date < limit_time):
				#This CHW spend many days without giving any report. We change his status from active to inactive
				chw.is_active = False
				chw.save()
