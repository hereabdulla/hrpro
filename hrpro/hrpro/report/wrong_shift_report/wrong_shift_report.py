# Copyright (c) 2013, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt

def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()
    data = []
    row = []
    conditions, filters = get_conditions(filters)
    attendance = get_attendance(conditions,filters)
    frappe.errprint(attendance)
    for att in attendance:
        frappe.errprint(att)
        data.append(att)
    return columns, data

def get_columns():
    columns = [
        _("ID") + ":Data:200",
        _("Attendance Date") + ":Data:200",
        _("Employee") + ":Data:120",
        _("Employee Name") + ":Data:120",
        _("Department") + ":Data:120",
        _("Assigned Shift") + ":Data:120",
        _("Present Shift") + ":Data:120"
    ]
    return columns

def get_attendance(conditions,filters):
    attendance = frappe.db.sql("""Select name,employee, employee_name, department,attendance_date, shift
    From `tabAttendance` Where %s order by attendance_date"""% conditions,filters, as_dict=1)
    row = []
    for att in attendance:
        sa = frappe.db.exists("Shift Assignment",{'date':att.attendance_date,'employee':att.employee})
        if sa:
            sa1 = frappe.get_value("Shift Assignment",sa,['shift_type'])
            if not att.shift == sa1:
                row += [(att.name,att.attendance_date,att.employee,att.employee_name,att.department,sa1,att.shift)]
    return row

def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"): conditions += " attendance_date >= %(from_date)s"
    if filters.get("to_date"): conditions += " and attendance_date <= %(to_date)s"
    if filters.get("company"): conditions += " and company = %(company)s"
    if filters.get("employee"): conditions += " and employee = %(employee)s"
    if filters.get("department"): conditions += " and department = %(department)s"

    return conditions, filters