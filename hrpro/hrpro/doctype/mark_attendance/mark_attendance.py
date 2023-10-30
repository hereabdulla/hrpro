# -*- coding: utf-8 -*-
# Copyright (c) 2020, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime,timedelta
import time
from frappe.utils import today
from frappe.model.document import Document

class MarkAttendance(Document):
    pass
@frappe.whitelist()
def create_self_attendance(employee_id,employee_name,in_time,attendance_date,shift):
    sa=frappe.new_doc("Attendance")
    sa.employee=employee_id
    sa.employee_name=employee_name
    sa.attendance_date=attendance_date
    sa.in_time=in_time
    sa.is_self_attendance = 1
    sa.status = "Present"
    sa.shift = shift
    # sa.out_time= "04:45:00"
    sa.save(ignore_permissions=True)
    frappe.db.commit()
    return sa
def auto_outtime():
    today=datetime.today()
    d=frappe.db.sql("""select name, employee_name,employee,out_time,attendance_date from `tabAttendance` where is_self_attendance = 1""",as_dict=True)
    for i in d:
        date=today.date()
        if(i.attendance_date==date):
            frappe.db.set_value('Attendance',i.name,'out_time',"04:45:00")
