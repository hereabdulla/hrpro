# -*- coding: utf-8 -*-
# Copyright (c) 2020, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from dateutil.relativedelta import relativedelta
from frappe.utils import cint, flt, nowdate, add_days, getdate, fmt_money, add_to_date, DATE_FORMAT, date_diff, money_in_words
from frappe import _
import functools
from datetime import datetime, timedelta

class ClientInvoice(Document):
	pass


@frappe.whitelist()
def get_default_company_address(name, sort_key='is_primary_address', existing_address=None):
	if sort_key not in ['is_shipping_address', 'is_primary_address']:
		return None

	out = frappe.db.sql(""" SELECT
			addr.name, addr.%s
		FROM
			`tabAddress` addr, `tabDynamic Link` dl
		WHERE
			dl.parent = addr.name and dl.link_doctype = 'Company' and
			dl.link_name = %s and ifnull(addr.disabled, 0) = 0
		""" %(sort_key, '%s'), (name)) #nosec

	if existing_address:
		if existing_address in [d[0] for d in out]:
			return existing_address

	if out:
		return sorted(out, key = functools.cmp_to_key(lambda x,y: cmp(y[1], x[1])))[0][0]
	else:
		return None

@frappe.whitelist()
def get_end_date(start_date, frequency):
	start_date = getdate(start_date)
	frequency = frequency.lower() if frequency else 'monthly'
	kwargs = get_frequency_kwargs(frequency) if frequency != 'bimonthly' else get_frequency_kwargs('monthly')

	# weekly, fortnightly and daily intervals have fixed days so no problems
	end_date = add_to_date(start_date, **kwargs) - relativedelta(days=1)
	if frequency != 'bimonthly':
		return dict(end_date=end_date.strftime(DATE_FORMAT))

	else:
		return dict(end_date='')

def get_frequency_kwargs(frequency_name):
	frequency_dict = {
		'monthly': {'months': 1},
		'fortnightly': {'days': 14},
		'weekly': {'days': 7},
		'daily': {'days': 1}
	}
	return frequency_dict.get(frequency_name)
	
@frappe.whitelist()
def invoice_item(start_date,end_date,company,client,site):
	salary_Slip = frappe.get_all('Salary Slip',{'company':company,'client_name':client,'site':site,'start_date':start_date,'end_date':end_date},['name','total_working_hours','hour_rate','start_date'])
	ot_hours = 0
	ot_amount = 0
	ctc_amount = 0
	ot_count = 0
	emp_count = len(salary_Slip)
	for ss in salary_Slip:
		date = ss.start_date
		month = date.strftime("%B-%Y")
		salary_detail = frappe.get_all('Salary Detail',{'parent':ss.name},['*'])		
		for sd in salary_detail:
			if sd.salary_component == "Cost to Company":
				ot_hours += ss.total_working_hours
				ctc_amount += sd.amount
			if sd.salary_component == "Over Time":
				ot_amount += sd.amount
				if sd.amount > 0:
					ot_count +=1
	gross = ot_amount + ctc_amount
	tax = gross * 0.09
	net_amount = round(gross + tax + tax)
	ot_hours = round(ot_hours)
	total_in_words = money_in_words(net_amount)
	return ot_hours,ot_amount,ctc_amount,emp_count,ot_count,gross,tax,net_amount,month,total_in_words