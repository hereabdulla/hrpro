# Copyright (c) 2013, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from six import string_types
import frappe
import json
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from datetime import datetime
from datetime import timedelta, time,date
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
        _("ID") + ":Link/Attendance:150",
        _("Attendance Date") + ":Data:120",
        _("Employee") + ":Data:120",
        _("Employee Name") + ":Data:120",
        # _("Department") + ":Data:120",
        # _("Plant") + ":Data:120",
        _("Shift") + ":Data:100",
        _("Shift Time") + ":Data:120",
        _("In Time") + ":Data:150",
        _("Late By") + ":Data:150"
    ]
    return columns

def get_attendance(conditions,filters):
    row = []
    attendance = frappe.db.sql("""Select name,employee, employee_name, department, attendance_date, late_entry,shift,status,in_time
     From `tabAttendance` Where status = "Present" and %s group by employee,attendance_date"""% conditions,filters, as_dict=1)
    shift_type = frappe.db.get_all("Shift Type",["name","start_time","end_time"])
    row = []
    for att in attendance:
        if att.in_time:
            in_time = att.in_time.time()
        for shift in shift_type:
            shift_time = datetime.strptime(str(shift.start_time), '%H:%M:%S')
            actual_time = shift_time.time()
            if shift.name == att.shift:
                if att.in_time and att.late_entry:
                    if actual_time <= in_time:
                        late = att.in_time - shift.start_time
                        late_by = late
                        row += [(att.name,att.attendance_date,att.employee,att.employee_name,att.shift,shift.start_time,att.in_time,late_by)]
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