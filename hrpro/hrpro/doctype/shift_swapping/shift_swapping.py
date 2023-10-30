# -*- coding: utf-8 -*-
# Copyright (c) 2021, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ShiftSwapping(Document):
	def on_submit(self):
		if self.status not in ["Approved", "Rejected"]:
			frappe.throw(("Only Shift Allocation with status 'Approved' and 'Rejected' can be submitted"))
		if self.status == "Approved":
			for shift in self.shift_detail:
				shift_assignment_list = frappe.get_list("Shift Assignment", {'employee': shift.employee, 'start_date': shift.shift_date, 'end_date': shift.shift_date})
				if shift_assignment_list:
					for shift_ass in shift_assignment_list:
						shift_assignment_doc = frappe.get_doc("Shift Assignment", shift_ass['name'])
						shift_assignment_doc.cancel()
						assignment_doc = frappe.new_doc("Shift Assignment")
						assignment_doc.company = self.company
						assignment_doc.shift_type = shift.shift_assign_to
						assignment_doc.employee = shift.employee
						assignment_doc.start_date = shift.shift_date
						assignment_doc.end_date = shift.shift_date
						assignment_doc.shift_swapping = self.name
						assignment_doc.insert()
						assignment_doc.submit()
						frappe.msgprint(("Shift Swapping: {0} created for Employee: {1}").format(frappe.bold(assignment_doc.name), frappe.bold(shift.employee)))

	def on_cancel(self):
		shift_assignment_list = frappe.get_list("Shift Assignment", {'employee': self.employee, 'shift_swapping': self.name})
		if shift_assignment_list:
			for shift in shift_assignment_list:
				shift_assignment_doc = frappe.get_doc("Shift Assignment", shift['name'])
				shift_assignment_doc.cancel()

@frappe.whitelist()
def allocated_shift(employee,shift_date):
	shift = frappe.db.sql("""select shift_type,start_date,end_date from `tabShift Assignment` where employee = '%s' and '%s' between start_date and end_date"""%(employee, shift_date),as_dict = 1)
	return shift

@frappe.whitelist()
def shift_details(employee,shift_date,swap_to):
	emp = frappe.db.sql("""select employee,shift_type,start_date,end_date from `tabShift Assignment` where employee = '%s' and '%s' between start_date and end_date"""%(employee, shift_date),as_dict = 1)
	swap_emp = frappe.db.sql("""select employee,shift_type,start_date,end_date from `tabShift Assignment` where employee = '%s' and '%s' between start_date and end_date"""%(swap_to, shift_date),as_dict = 1)
	return emp,swap_emp