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

class AttendanceandOTRegister(Document):
	def validate(self):
		self.get_employee_no()
		self.canteen_salary()
		self.transport_salary()
	
	def get_employee_no(self):
		employee = frappe.db.get_value("Employee",{"client_employee_no":self.client_employee_no},["name"])
		self.employee = employee
	
	def canteen_salary(self):
		additional_salary = frappe.db.get_value("Additional Salary",{"employee":self.employee,"salary_component": "Canteen Charges","payroll_date": self.start_date},["name"])
		if not additional_salary:
			if self.canteen_charges > 0:
				additional_salary = frappe.new_doc('Additional Salary')
				additional_salary.update({
					"employee": self.employee,
					"payroll_date": self.start_date,
					"salary_component": "Canteen Charges",
					"amount": int(self.canteen_charges),
					"overwrite_salary_structure_amount": "1"
				})
				additional_salary.save(ignore_permissions=True)
				additional_salary.submit()
				frappe.db.commit()

	def transport_salary(self):
		additional_salary = frappe.db.get_value("Additional Salary",{"employee":self.employee,"salary_component": "Transport Charges","payroll_date": self.start_date},["name"])
		if not additional_salary:
			if self.transport_charges > 0:
				additional_salary = frappe.new_doc('Additional Salary')
				additional_salary.update({
					"employee": self.employee,
					"payroll_date": self.start_date,
					"salary_component": "Transport Charges",
					"amount": int(self.transport_charges),
					"overwrite_salary_structure_amount": "1"
				})
				additional_salary.save(ignore_permissions=True)
				additional_salary.submit()
				frappe.db.commit()


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
def get_employee(client_id):
	employee = frappe.db.get_value("Employee",{"client_employee_no":client_id},["name"])
	return employee

@frappe.whitelist()
def create_canteen_salary(canteen,payroll_date,employee):
	additional_salary = frappe.db.get_value("Additional Salary",{"employee":employee,"salary_component": "Canteen Charges","payroll_date": payroll_date},["name"])
	if not additional_salary:
		additional_salary = frappe.new_doc('Additional Salary')
		additional_salary.update({
			"employee": employee,
			"payroll_date": payroll_date,
			"salary_component": "Canteen Charges",
			"amount": int(canteen),
			"overwrite_salary_structure_amount": "1"
		})
		additional_salary.save(ignore_permissions=True)
		additional_salary.submit()
		frappe.db.commit()

@frappe.whitelist()
def create_transport_salary(transport,payroll_date,employee):
	additional_salary = frappe.db.get_value("Additional Salary",{"employee":employee,"salary_component": "Transport Charges","payroll_date": payroll_date},["name"])
	if not additional_salary:
		additional_salary = frappe.new_doc('Additional Salary')
		additional_salary.update({
			"employee": employee,
			"payroll_date": payroll_date,
			"salary_component": "Transport Charges",
			"amount": int(transport),
			"overwrite_salary_structure_amount": "1"
		})
		additional_salary.save(ignore_permissions=True)
		additional_salary.submit()
		frappe.db.commit()