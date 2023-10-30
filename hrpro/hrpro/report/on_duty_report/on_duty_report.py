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
    attendance = get_attendance_req(conditions,filters)
    for att in attendance:
        data.append(att)
    return columns, data

def get_columns():
    columns = [
        _("ID") + ":Data:200",
        _("From Date") + ":Date:200",
        _("To Date") + ":Date:200",
        _("Employee") + ":Data:120",
        _("Employee Name") + ":Data:120",
        _("Reason") + ":Data:120",
        _("Explanation") + ":Data:120"
    ]
    return columns

def get_attendance_req(conditions,filters):
    attendance = frappe.db.sql("""Select name,employee, employee_name,from_date,to_date,reason,explanation
    From `tabAttendance Request` Where reason = "On Duty" and %s """% conditions,filters, as_dict=1)
    row = []
    for att in attendance:
        row += [(att.name,att.from_date,att.to_date,att.employee,att.employee_name,att.reason,att.explanation)]
    return row

def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"): conditions += " from_date >= %(from_date)s"
    if filters.get("to_date"): conditions += " and to_date <= %(to_date)s"
    if filters.get("company"): conditions += " and company = %(company)s"
    if filters.get("employee"): conditions += " and employee = %(employee)s"

    return conditions, filters