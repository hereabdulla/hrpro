# Copyright (c) 2013, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import print_function, unicode_literals
from six import string_types
import frappe
import json
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from datetime import datetime, date
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint, getdate
from itertools import count

day_abbr = [
    "Mon",
    "Tue",
    "Wed",
    "Thu",
    "Fri",
    "Sat",
    "Sun"
]

def execute(filters=None):
    if not filters: filters = {}

    if filters.hide_year_field == 1:
        filters.year = 2020

    conditions, filters = get_conditions(filters)
    columns = get_columns(filters)
    data = []
    row = []
    employee_list = frappe.get_all('Employee',{"status":"Active"},["*"])
    for emp in employee_list:
        row = []
        row += [emp.name,emp.employee_name,emp.department]
        frappe.errprint(row)
        for day in range(filters["total_days_in_month"]):
            att_date = date(cint(filters.year),cint(filters.month),day+1)
            attendance = frappe.db.sql("""select in_time, out_time from `tabAttendance` where employee = %s and attendance_date = %s""",(emp.name,att_date))
            frappe.errprint(attendance)
            att_time = attendance
            frappe.errprint(att_time)
            if att_time:
                in_time = att_time
            else:
                in_time = 0
            if att_time:
                out_time = att_time
            else:
                out_time = 0
            row += [str(in_time)+"/"+str(out_time)]
        data.append(row)
    return columns, data

def get_columns(filters):
    columns = [
        _("Employee") + ":Data:200",
        _("Employee Name") + ":Data:200",
        _("Department") + ":Data:200"
    ]
    days = []
    for day in range(filters["total_days_in_month"]):
        date = str(filters.year) + "-" + str(filters.month)+ "-" + str(day+1)
        day_name = day_abbr[getdate(date).weekday()]
        days.append(cstr(day+1)+ " " +day_name +"::65")
    if days:
        frappe.errprint(days)
        columns += days
    return columns

def get_conditions(filters):
    if not (filters.get("month") and filters.get("year")):
        msgprint(_("Please select month and year"), raise_exception=1)

    filters["total_days_in_month"] = monthrange(cint(filters.year), cint(filters.month))[1]

    conditions = " and month(attendance_date) = %(month)s and year(attendance_date) = %(year)s"

    if filters.get("company"): conditions += " and company = %(company)s"
    if filters.get("employee"): conditions += " and employee = %(employee)s"

    return conditions, filters