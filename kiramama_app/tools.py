import datetime
from kiramama_app.models import *



def reajust_scheduled_delivery_messages():
	'''
	This function is used to fix well scheduled messages
	'''
	start_date = datetime.datetime.now().date() + datetime.timedelta(hours = 24)
	end_date = datetime.datetime.strptime('02112017', "%d%m%Y").date()
	
	concerned_report_gro = ReportGRO.objects.filter(expected_delivery_date__gte = start_date, report__reporting_date__lte = end_date)
	
	acc_notification_type = NotificationType.objects.get(code = "acc")
	
	acc_template_mother_notifications = NotificationsForMother.objects.filter(notification_type = acc_notification_type)
	

	acc_template_chw_notifications = NotificationsForCHW.objects.filter(notification_type = acc_notification_type)

	i = 1
	for r in concerned_report_gro:
		print "========================="
		concerned_mother = r.report.mother

		old_mother_notifications = NotificationsMother.objects.filter(mother = concerned_mother, notification__notification_type = acc_notification_type)
		print i
		i = i + 1
		if len(old_mother_notifications) > 0:
			for j in old_mother_notifications:
				print "Old message"
				print j.message_to_send
				j.delete()

		expected_delivery_date = r.expected_delivery_date

		print "expected_delivery_date"
		print expected_delivery_date

		if len(acc_template_mother_notifications) > 0:
			for notification_for_mother in acc_template_mother_notifications:
				#notification_for_mother = notifications_for_mother[0]
				time_measure_unit = notification_for_mother.time_measuring_unit
				number_for_time = notification_for_mother.time_number
				if(time_measure_unit.code.startswith("m") or time_measure_unit.code.startswith("M")):
					time_for_reminder = expected_delivery_date - datetime.timedelta(minutes = number_for_time)
				if(time_measure_unit.code.startswith("h") or time_measure_unit.code.startswith("H")):
					time_for_reminder = expected_delivery_date - datetime.timedelta(hours = number_for_time)

				remind_message_to_send_to_mother = notification_for_mother.message_to_send

				if notification_for_mother.word_to_replace_by_the_date_in_the_message_to_send:
					remind_message_to_send_to_mother = remind_message_to_send_to_mother.replace(notification_for_mother.word_to_replace_by_the_date_in_the_message_to_send, expected_delivery_date.isoformat())
					print "New message to send"
					print remind_message_to_send_to_mother

				created_reminder = NotificationsMother.objects.create(mother = concerned_mother, notification = notification_for_mother, date_time_for_sending = time_for_reminder, message_to_send = remind_message_to_send_to_mother)






