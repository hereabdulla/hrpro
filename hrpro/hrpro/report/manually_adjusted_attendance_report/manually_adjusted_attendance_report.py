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
        _("ID") + ":Link/Attendance:200",
        _("Attendance Date") + ":Data:200",
        _("Employee") + ":Data:120",
        _("Employee Name") + ":Data:120",
        # _("Plant") + ":Data:120",
        _("Shift") + ":Data:120",
        _("In Time") + ":Datetime:120",
        _("Out Time") + ":Datetime:120"
    ]
    return columns

def get_attendance(conditions,filters):
    attendance = frappe.db.sql("""Select * From `tabAttendance` Where modified_by != "Administrator" and %s group by employee,attendance_date"""% conditions,filters, as_dict=1)
    row = []
    for att in attendance:
        row += [(att.name,att.attendance_date,att.employee,att.employee_name,att.shift,att.in_time,att.out_time)]
    return row

def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"): conditions += " attendance_date between %(from_date)s and %(to_date)s"
    if filters.get("company"): conditions += " and company = %(company)s"
    if filters.get("employee"): conditions += " and employee = %(employee)s"
    if filters.get("plant"): conditions += " and plant = %(plant)s"

    return conditions, filters