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
    leave = get_lop(conditions,filters)
    for lop in leave:
        data.append(lop)
    return columns, data

def get_columns():
    columns = [
        _("ID") + ":Data:200",
        _("From Date") + ":Date:200",
        _("To Date") + ":Date:200",
        _("Employee") + ":Data:120",
        _("Employee Name") + ":Data:120",
        _("Leave Type") + ":Data:120",
        _("Status") + ":Data:120",
        _("Reason") + ":Data:120"
    ]
    return columns

def get_lop(conditions,filters):
    leave_app = frappe.db.sql("""Select name,employee, employee_name,from_date,status,to_date,leave_type,description
    From `tabLeave Application` Where leave_type = "Leave Without Pay" and %s """% conditions,filters, as_dict=1)
    row = []
    for el in leave_app:
        row += [(el.name,el.from_date,el.to_date,el.employee,el.employee_name,el.leave_type,el.status,el.description)]
    return row

def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"): conditions += " from_date >= %(from_date)s"
    if filters.get("to_date"): conditions += " and to_date <= %(to_date)s"
    if filters.get("company"): conditions += " and company = %(company)s"
    if filters.get("employee"): conditions += " and employee = %(employee)s"
    if filters.get("department"): conditions += " and department = %(department)s"

    return conditions, filters