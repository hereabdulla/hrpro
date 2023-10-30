# Copyright (c) 2013, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns()
	data = get_employees(filters)
	return columns, data

def get_columns():
	return [
		_("Employee") + ":Link/Employee:120", _("Name") + ":Data:200", _("Gender") + "::60", _("Date of Joining")+ ":Date:100",
		_("Branch") + ":Link/Branch:120", _("Department") + ":Link/Department:120",
		_("Designation") + ":Link/Designation:120", _("Company") + ":Link/Company:120"
	]

def get_employees(filters):
	employees = frappe.db.sql("""select name, employee_name, gender, date_of_joining,
	branch, department, designation, company
	from `tabEmployee` 
	where status = 'Active' and date_of_joining between %s and %s and company = %s""",(filters["from_date"],filters["to_date"],filters["company"]))
	return employees