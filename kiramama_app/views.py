from django.shortcuts import render
from kiramama_app.models import *

# Create your views here.
def landing(request):
    return render(request, 'landing_page.html')


def change_chw_status(request):
	''' This function switch a CHW to the following status : active/inactive '''

	key_word_for_chwai_setting = getattr(settings,'KEY_WORD_FOR_CHW_ACTIVE_SETTING','')

	setting_to_use = Settings.objects.filter(setting_code = key_word_for_chwai_setting)
