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
        # _("Department") + ":Data:120",
        # _("Plant") + ":Data:120",
        _("Shift") + ":Data:120",
        _("Shift Time") + ":Data:120",
        _("Out Time") + ":Data:120",
        _("Early By") + ":Data:120"
    ]
    return columns

def get_attendance(conditions,filters):
    attendance = frappe.db.sql("""Select name,employee, employee_name, department, attendance_date, early_exit,shift,status, out_time
     From `tabAttendance` Where status = "Present" and %s group by employee,attendance_date"""% conditions,filters, as_dict=1)
    shift_type = frappe.db.get_all("Shift Type",["name","start_time","end_time"])
    row = []
    for att in attendance:
        if att.out_time:
            out_time = att.out_time.time()
            date = att.out_time.date()       
        for shift in shift_type:
            shift_time = datetime.strptime(str(shift.end_time), '%H:%M:%S')
            actual_time = shift_time.time()
            if att.out_time:
                test = datetime.combine(date, actual_time)
            if shift.name == att.shift:
                if att.out_time and att.early_exit:
                    if actual_time >= out_time:
                        early_by = test - att.out_time
                        row += [(att.name,att.attendance_date,att.employee,att.employee_name,att.shift,shift.end_time,att.out_time,early_by)]
    return row

def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"): conditions += " attendance_date >= %(from_date)s"
    if filters.get("to_date"): conditions += " and attendance_date <= %(to_date)s"
    if filters.get("company"): conditions += " and company = %(company)s"
    if filters.get("employee"): conditions += " and employee = %(employee)s"
    # if filters.get("department"): conditions += " and department = %(department)s"
    # if filters.get("plant"): conditions += " and plant = %(plant)s"

    return conditions, filters