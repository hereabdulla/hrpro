# Copyright (c) 2013, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import print_function, unicode_literals
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
    attendance = get_attendance(conditions,filters)
    for att in attendance:
        data.append(att)
    return columns, data

def get_columns():
    columns = [
        _("Employee") + ":Link/Employee:200",
        _("Employee Name") + ":Data:200",
        _("Department") + ":Data:200",
        _("Absent Dates") + ":Data:300",
        _("Total Absent Days") + ":Data:100"
    ]
    return columns

def get_attendance(conditions,filters):
    row = []
    attendance = frappe.db.sql("""Select * From `tabAttendance` Where status = "Absent" and %s order by employee"""% conditions,filters, as_dict=1)
    employee = frappe.get_all("Employee",{"status":"Active"},["*"])
    for emp in employee:
        att_date = []
        for att in attendance:
            if emp.name == att.employee:
                att_date += [cint(att.attendance_date.day)]
        count = len(att_date)
        if count:
            row += [(emp.name,emp.employee_name,emp.department,str(att_date),count)]
    return row

def get_conditions(filters):
    if not (filters.get("month") and filters.get("year")):
        msgprint(_("Please select month and year"), raise_exception=1)

    filters["total_days_in_month"] = monthrange(cint(filters.year), cint(filters.month))[1]

    conditions = "month(attendance_date) = %(month)s and year(attendance_date) = %(year)s"

    if filters.get("company"): conditions += " and company = %(company)s"
    if filters.get("employee"): conditions += " and employee = %(employee)s"

    return conditions, filters