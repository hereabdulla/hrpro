# Copyright (c) 2013, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from six import string_types
import frappe
import json
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from datetime import datetime
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint, getdate
from itertools import count

def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()
    data = []
    row = []
    conditions, filters = get_conditions(filters)
    contractor = get_employee_list(conditions,filters)
    for emp_list in contractor:
        data.append(emp_list)
    return columns, data

def get_columns():
    columns = [
        _("Employee") + ":Link/Employee:100",
        _("Employee Name") + ":Data:200",
        _("Gender") + ":Data:120",
        _("Date of Join") + ":Date:100",
        _("Contractor") + ":Data:120",
        _("Department") + ":Data:200",
        _("Designation") + ":Data:120",
        # _("Biomertic PIN") + ":Data:120"
    ]
    return columns

def get_employee_list(conditions,filters):
    employee = frappe.db.sql("""Select name, employee_name, gender,date_of_birth,date_of_joining,department,designation,contractor
    From `tabEmployee` Where status = "Active" and %s order by contractor"""% conditions, filters, as_dict=1)
    row = []
    for emp in employee:
        if emp.contractor:
            row += [(emp.name,emp.employee_name,emp.gender,emp.date_of_joining,emp.contractor,emp.department,emp.designation)]
    return row

def get_conditions(filters):
    conditions = ""
    if filters.get("company"): conditions += " company = %(company)s"
    if filters.get("employee"): conditions += " and employee = %(employee)s"
    if filters.get("department"): conditions += " and department = %(department)s"
    if filters.get("contractor"): conditions += " and contractor_id = %(contractor)s"

    return conditions, filters