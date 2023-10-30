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
    attendance = get_attendance(conditions,filters)
    for att in attendance:
        data.append(att)
    return columns, data

def get_columns():
    columns = [
        _("ID") + ":Data:200",
        _("From Date") + ":Data:200",
        _("To Date") + ":Data:200",
        _("Employee") + ":Data:120",
        _("Employee Name") + ":Data:120",
        _("Department") + ":Data:120",
        _("Status") + ":Data:120",
    ]
    return columns

def get_attendance(conditions,filters):
    attendance = frappe.db.sql("""Select name,employee, employee_name, department,attendance_date, shift,status
    From `tabAttendance` Where status = "Present" and %s group by employee,attendance_date"""% conditions,filters, as_dict=1)
    employee = frappe.db.get_all("Employee",{"status":"Active"},["name"])
    row = []
    emp_count = 0
    import pandas as pd
    mydates = pd.date_range(filters.from_date, filters.to_date).tolist()
    date_count = len(mydates) - 1
    for emp in employee:
        for date in mydates:
            for att in attendance:
                att_date = date.date()
                if emp.name == att.employee:
                    emp_count += 1
                    if emp_count == date_count:
                        row += [(att.name,filters.from_date,filters.to_date,att.employee,att.employee_name,att.department,att.status)]
    return row

def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"): conditions += " attendance_date >= %(from_date)s"
    if filters.get("to_date"): conditions += " and attendance_date <= %(to_date)s"
    if filters.get("company"): conditions += " and company = %(company)s"
    if filters.get("employee"): conditions += " and employee = %(employee)s"
    if filters.get("department"): conditions += " and department = %(department)s"

    return conditions, filters
