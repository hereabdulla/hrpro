# -*- coding: utf-8 -*-
# Copyright (c) 2019, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AttendanceSettings(Document):
	def mark_permission(self):
		permission_request = frappe.db.sql("""SELECT * FROM `tabPermission Request` 
		WHERE docstatus=1 and attendance_date between %s and %s """,
		(self.from_date,self.to_date),as_dict=True)
		for per_req in permission_request:
			attendance = frappe.db.exists("Attendance",{"employee":per_req.employee,"attendance_date":per_req.attendance_date,"docstatus":1},["*"])
			if attendance:
				update_attendance = frappe.get_doc("Attendance",attendance)
				if update_attendance.status == "Absent" or update_attendance.status == "Half Day":
					update_attendance.status = "Present"
				update_attendance.permission_request = per_req.name
				update_attendance.save(ignore_permissions =True)
				update_attendance.submit()
				frappe.db.commit()
	
	def mark_od(self):
		od_application = frappe.db.sql("""SELECT * FROM `tabOn Duty Application` 
		WHERE docstatus=1 and from_date >= %s and to_date <= %s """,
		(self.from_date,self.to_date),as_dict=True)
		for od_app in od_application:
			attendance = frappe.db.sql("""SELECT * FROM `tabAttendance` 
			WHERE docstatus=1 and attendance_date between %s and %s """,
			(self.from_date,self.to_date),as_dict=True)
			for att in attendance:
				if att:
					update_attendance = frappe.get_doc("Attendance",att.name)
					if update_attendance.status == "Absent" or update_attendance.status == "Half Day":
						update_attendance.status = "Present"
					update_attendance.on_duty_application = od_app.name
					update_attendance.save(ignore_permissions =True)
					update_attendance.submit()
					frappe.db.commit()