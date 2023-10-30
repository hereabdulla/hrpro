# -*- coding: utf-8 -*-
# Copyright (c) 2020, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import random
from datetime import datetime
from frappe.utils.data import today, add_days
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import json

class StatutoryDetail(Document):
	pass

@frappe.whitelist()
def statutory_item(employee):
	# frappe.errprint("hi")
	ss_dict = {}
	salary_slip = frappe.get_all('Salary Slip',{'employee':employee},['name','start_date','end_date','total_working_hours','hour_rate'])
	basic = 0
	da = 0
	pf = 0
	esi = 0
	pt = 0
	bonus = 0
	sd_list = []
	for ss in salary_slip:
		date = (ss.start_date)
		month = date.strftime('%B')
		year = date.strftime('%Y')
		salary_detail = frappe.get_all('Salary Detail',{'parent':ss.name},['*'])		
		for sd in salary_detail:
			if sd.salary_component == "Basic":
				basic = sd.amount
			if sd.salary_component == "Dearness Allowance":
				da = sd.amount
			if sd.salary_component == "Provident Fund":
				pf = sd.amount
			if sd.salary_component == "Employee State Insurance":
				esi = sd.amount
			if sd.salary_component == "Professional Tax":
				pt = sd.amount
			if sd.salary_component == "Retention Bonus":
				bonus = sd.amount
			ss_dict =  {
				"basic" : basic,
				"da" : da,
				"pf" : pf,
				"esi" : esi,
				"pt" : pt,
				"bonus" : bonus,
				"month" : month,
				"year": year,
				"salary_slip" : ss.name
			}
		sd_list.append(ss_dict)
	return sd_list

@frappe.whitelist()
def get_gratuity(employee,age,join):
	basic = 0
	da = 0
	# age = 5
	salary_slip = frappe.db.sql("""select name,start_date,end_date,total_working_hours,hour_rate from `tabSalary Slip` where employee = %s ORDER By start_date""",employee,as_dict=True)
	graduity = salary_slip[-1]
	j = datetime.strptime(join,'%Y-%m-%d')
	now_day = (datetime.today()).date()
	num_months = (now_day.year - j.year) * 12 + (now_day.month - j.month)
	salary_detail = frappe.get_all('Salary Detail',{'parent':graduity.name},['*'])
	for sd in salary_detail:
		if sd.salary_component == "Basic":
			basic = sd.amount
		if sd.salary_component == "Dearness Allowance":
			da = sd.amount
	graduity_amount = (basic+da)*15/26*age
	return graduity_amount