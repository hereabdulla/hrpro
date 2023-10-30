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
    shift_list = frappe.get_all('Shift Type')
    for shift in shift_list:
        row = []
        monthly_count = 0
        row += ["Shift - "+shift.name]
        for day in range(filters["total_days_in_month"]):
            att_date = date(cint(filters.year),cint(filters.month),day+1)
            attendance = frappe.db.sql("""select sum(name) as shift_count from `tabAttendance` where shift = %s and 
            attendance_date = %s""",(shift.name,att_date))
            att_count = attendance[0][0]
            if att_count:
                row += [att_count]
                monthly_count = monthly_count + att_count
            else:
                row += [0]            
            # frappe.errprint(att_count)
            # frappe.errprint(att_date)
            # frappe.errprint(day)
            # row += [day]
        row += [monthly_count]
        data.append(row)
    frappe.errprint(row)
    
    return columns, data

def get_columns(filters):
    columns = [
        _("Shift") + ":Data:200"
    ]
    days = []
    for day in range(filters["total_days_in_month"]):
        date = str(filters.year) + "-" + str(filters.month)+ "-" + str(day+1)
        day_name = day_abbr[getdate(date).weekday()]
        days.append(cstr(day+1)+ " " +day_name +"::65")
    if days:
        frappe.errprint(days)
        columns += days
    columns += [
        _("Monthly Head Count") + ":Data:200"
    ]
    return columns

def get_conditions(filters):
    if not (filters.get("month") and filters.get("year")):
        msgprint(_("Please select month and year"), raise_exception=1)

    filters["total_days_in_month"] = monthrange(cint(filters.year), cint(filters.month))[1]

    conditions = " and month(attendance_date) = %(month)s and year(attendance_date) = %(year)s"

    if filters.get("company"): conditions += " and company = %(company)s"
    if filters.get("employee"): conditions += " and employee = %(employee)s"

    return conditions, filters