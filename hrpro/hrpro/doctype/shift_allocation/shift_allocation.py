# -*- coding: utf-8 -*-
# Copyright (c) 2021, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import formatdate, getdate
from datetime import datetime
import pandas as pd

class OverlapError(frappe.ValidationError): pass

class ShiftAllocation(Document):
	def validate(self):
		self.validate_dates()
		self.validate_shift_request_overlap_dates()
		self.validate_approver()
		self.validate_default_shift()

	def on_submit(self):
		if self.status not in ["Approved", "Rejected"]:
			frappe.throw(_("Only Shift Allocation with status 'Approved' and 'Rejected' can be submitted"))
		if self.status == "Approved":
			datelist = pd.date_range(self.from_date, self.to_date).tolist()
			for date in datelist:
				frappe.errprint(date.date())
				assignment_doc = frappe.new_doc("Shift Assignment")
				assignment_doc.company = self.company
				assignment_doc.shift_type = self.shift_type
				assignment_doc.employee = self.employee
				assignment_doc.start_date = date.date()
				if self.to_date:
					assignment_doc.end_date = date.date()
				assignment_doc.shift_allocation = self.name
				assignment_doc.insert()
				assignment_doc.submit()
				frappe.msgprint(_("Shift Assignment: {0} created for Employee: {1}").format(frappe.bold(assignment_doc.name), frappe.bold(self.employee)))

	def on_cancel(self):
		shift_assignment_list = frappe.get_list("Shift Assignment", {'employee': self.employee, 'shift_allocation': self.name})
		if shift_assignment_list:
			for shift in shift_assignment_list:
				shift_assignment_doc = frappe.get_doc("Shift Assignment", shift['name'])
				shift_assignment_doc.cancel()

	def validate_default_shift(self):
		default_shift = frappe.get_value("Employee", self.employee, "default_shift")
		if self.shift_type == default_shift:
			frappe.throw(_("You can not request for your Default Shift: {0}").format(frappe.bold(self.shift_type)))

	def validate_approver(self):
		if self.approver:
			department = frappe.get_value("Employee", self.employee, "department")
			shift_approver = frappe.get_value("Employee", self.employee, "shift_request_approver")
			approvers = frappe.db.sql("""select approver from `tabDepartment Approver` where parent= %s and parentfield = 'shift_request_approver'""", (department))
			approvers = [approver[0] for approver in approvers]
			approvers.append(shift_approver)
			if self.approver not in approvers:
				frappe.throw(_("Only Approvers can Approve this Request."))

	def validate_dates(self):
		if self.from_date and self.to_date and (getdate(self.to_date) < getdate(self.from_date)):
			frappe.throw(_("To date cannot be before from date"))

	def validate_shift_request_overlap_dates(self):
			if not self.name:
				self.name = "New Shift Allocation"

			d = frappe.db.sql("""
				select
					name, shift_type, from_date, to_date
				from `tabShift Allocation`
				where employee = %(employee)s and docstatus < 2
				and ((%(from_date)s >= from_date
					and %(from_date)s <= to_date) or
					( %(to_date)s >= from_date
					and %(to_date)s <= to_date ))
				and name != %(name)s""", {
					"employee": self.employee,
					"shift_type": self.shift_type,
					"from_date": self.from_date,
					"to_date": self.to_date,
					"name": self.name
				}, as_dict=1)

			for date_overlap in d:
				if date_overlap ['name']:
					self.throw_overlap_error(date_overlap)

	def throw_overlap_error(self, d):
		msg = _("Employee {0} has already applied for {1} between {2} and {3} : ").format(self.employee,
			d['shift_type'], formatdate(d['from_date']), formatdate(d['to_date'])) \
			+ """ <b><a href="#Form/Shift Allocation/{0}">{0}</a></b>""".format(d["name"])
		frappe.throw(msg, OverlapError)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_approvers(doctype, txt, searchfield, start, page_len, filters):

	if not filters.get("employee"):
		frappe.throw(_("Please select Employee first."))

	approvers = []
	department_details = {}
	department_list = []
	employee = frappe.get_value("Employee", filters.get("employee"), ["employee_name","department", "leave_approver", "expense_approver", "shift_request_approver"], as_dict=True)

	employee_department = filters.get("department") or employee.department
	if employee_department:
		department_details = frappe.db.get_value("Department", {"name": employee_department}, ["lft", "rgt"], as_dict=True)
	if department_details:
		department_list = frappe.db.sql("""select name from `tabDepartment` where lft <= %s
			and rgt >= %s
			and disabled=0
			order by lft desc""", (department_details.lft, department_details.rgt), as_list=True)

	if filters.get("doctype") == "Leave Application" and employee.leave_approver:
		approvers.append(frappe.db.get_value("User", employee.leave_approver, ['name', 'first_name', 'last_name']))

	if filters.get("doctype") == "Expense Claim" and employee.expense_approver:
		approvers.append(frappe.db.get_value("User", employee.expense_approver, ['name', 'first_name', 'last_name']))

	if filters.get("doctype") == "Shift Request" and employee.shift_request_approver:
		approvers.append(frappe.db.get_value("User", employee.shift_request_approver, ['name', 'first_name', 'last_name']))
	
	if filters.get("doctype") == "Shift Allocation" and employee.shift_request_approver:
		approvers.append(frappe.db.get_value("User", employee.shift_request_approver, ['name', 'first_name', 'last_name']))

	if filters.get("doctype") == "Leave Application":
		parentfield = "leave_approvers"
		field_name = "Leave Approver"
	elif filters.get("doctype") == "Expense Claim":
		parentfield = "expense_approvers"
		field_name = "Expense Approver"
	elif filters.get("doctype") == "Shift Allocation":
		parentfield = "shift_request_approver"
		field_name = "Shift Request Approver"
	if department_list:
		for d in department_list:
			approvers += frappe.db.sql("""select user.name, user.first_name, user.last_name from
				tabUser user, `tabDepartment Approver` approver where
				approver.parent = %s
				and user.name like %s
				and approver.parentfield = %s
				and approver.approver=user.name""",(d, "%" + txt + "%", parentfield), as_list=True)

	if len(approvers) == 0:
		error_msg = _("Please set {0} for the Employee: {1}").format(field_name, frappe.bold(employee.employee_name))
		if department_list:
			error_msg += _(" or for Department: {0}").format(frappe.bold(employee_department))
		frappe.throw(error_msg, title=_(field_name + " Missing"))

	return set(tuple(approver) for approver in approvers)
