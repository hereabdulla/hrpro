# -*- coding: utf-8 -*-
# Copyright (c) 2020, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import today, add_days
from datetime import datetime

class Contractor(Document):
	pass


def rc_wc_expiry_alert():
	contractors = frappe.get_all("Contractor")
	check_date = add_days((datetime.today()).date(),-15)
	for contractor in contractors:
		con = frappe.get_doc("Contractor",contractor)
		for c in con.rc_child:
			if  check_date > c.completion_of_work:
				content = """Dear Sir,<br><br>RC - <b>%s</b> for TPL Plant <b>%s</b> is going to get expired in 15 days.<br><br>Regards,<br>TPL HR Department"""%(c.rc_number,c.plant)
				frappe.sendmail(
				recipients=['subash.p@groupteampro.com'],
				subject='RC Expiry Alert',
				message="""%s"""%(content)
			)
		for c in con.wc_child:
			if  check_date > c.to:
				content = """Dear Sir,<br><br>Workmen's Compensation  <b>(%s)</b> for TPL is going to get expired in 15 days.<br><br>Regards,<br>TPL HR Department"""%(c.insurance_no)
				frappe.sendmail(
				recipients=['subash.p@groupteampro.com'],
				subject='RC Expiry Alert',
				message="""%s"""%(content)
			)
		for c in con.rc_child:
			if  (datetime.today()).date() > c.completion_of_work:
				content = """Dear Sir,<br><br>RC - <b>%s</b> for TPL Plant <b>%s</b> is expired.<br><br>Regards,<br>TPL HR Department"""%(c.rc_number,c.plant)
				frappe.sendmail(
				recipients=['subash.p@groupteampro.com'],
				subject='RC Expiry Alert',
				message="""%s"""%(content)
			)
		for c in con.wc_child:
			if  (datetime.today()).date() > c.to:
				content = """Dear Sir,<br><br>Workmen's Compensation  <b>(%s)</b> for TPL is expired.<br><br>Regards,<br>TPL HR Department"""%(c.insurance_no)
				frappe.sendmail(
				recipients=['subash.p@groupteampro.com'],
				subject='RC Expiry Alert',
				message="""%s"""%(content)
			)


def emp_series():
	ca = []
	# contractor_series = frappe.db.get_value("Contractor",{'status':'Active'},['employee_series']) or ''
	contractor_series = frappe.db.get_list('Contractor',filters={'status': 'Active'},fields =['employee_series'])
	for c in contractor_series:
		ca.append(c.employee_series)
	# contractor_series = frappe.db.sql("""select employee_series from `tabContractor` where status ='Active' """)
	
	unwanted_list=['50','60','70','80','90']
	new_list = list(set(ca).difference(unwanted_list))
	new_list1 = int(max(new_list)) + 1

	print((new_list1))
	