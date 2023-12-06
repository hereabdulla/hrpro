# -*- coding: utf-8 -*-
# Copyright (c) 2018, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta,date
from frappe import _
from frappe.utils import today,flt,add_days,date_diff,getdate,cint,formatdate, getdate, get_link_to_form, \
	comma_or, get_fullname
from hrpro.custom import update_attendance_by_app
from frappe.utils import get_first_day, get_last_day, format_datetime,get_url_to_form

class LeaveApproverIdentityError(frappe.ValidationError): pass
class OverlapError(frappe.ValidationError): pass
class InvalidApproverError(frappe.ValidationError): pass
class AttendanceAlreadyMarkedError(frappe.ValidationError): pass    

class OnDutyApplication(Document):
	def validate(self):
		for emp in self.multi_employee:
			no_of_days = date_diff(add_days(self.to_date, 1),self.from_date )
			dates = [add_days(self.from_date, i) for i in range(0, no_of_days)]
			for date in dates:
				att = frappe.db.exists("Attendance",{"attendance_date":date,"employee":emp.employee,"docstatus":1})
				if att:
					frappe.throw(_('Attendance Closed for this %s day %s'%(emp.employee,date)))      	

	def on_submit(self):
		if self.status == "Applied":
			frappe.throw(_("Only Applications with status 'Approved' and 'Rejected' can be submitted"))
		if self.workflow_state == "Approved":
			no_of_days = date_diff(add_days(self.to_date, 1),self.from_date )
			dates = [add_days(self.from_date, i) for i in range(0, no_of_days)]
			for emp in self.multi_employee:
				for date in dates:
					att = frappe.db.exists("Attendance",{"attendance_date":date,"employee":emp.employee,"docstatus":["!=","2"]})
					if att:
						doc = frappe.get_doc("Attendance",att)
						frappe.errprint(doc)
						if doc.docstatus == 0:
							doc.status = 'Present'
							hh = check_holiday(date)
							if hh:
								if hh == 'WW':
									doc.shift_status = "ODW"
								else:
									doc.shift_status = "ODH"
							else:
								doc.shift_status = "OD"
							doc.on_duty_application = self.name
							doc.save(ignore_permissions=True)
							doc.submit()
							frappe.db.commit()
						elif doc.docstatus == 1:
							doc.cancel()
							doc = frappe.new_doc("Attendance")
							doc.employee = emp.employee
							doc.attendance_date = date
							doc.status = 'Present'
							hh = check_holiday(date)
							if hh:
								if hh == 'WW':
									doc.shift_status = "ODW"
								else:
									doc.shift_status = "ODH"
							else:
								doc.shift_status = "OD"
							doc.on_duty_application = self.name
							doc.save(ignore_permissions=True)
							doc.submit()
							frappe.db.commit()
	def on_cancel(self):
		attendance_list = frappe.get_doc("Attendance", {'employee': self.employee, 'on_duty_application': self.name})
		if attendance_list:
			for attendance in attendance_list:
				attendance_obj = frappe.get_doc("Attendance", attendance['name'])
				attendance_obj.cancel()

	def after_insert(self):
		if self.workflow_state == 'Pending for HOD':
			table = ''
			link = get_url_to_form("On Duty Application", self.name)
			content="""<p>Dear Sir,<br>Kindly find the below On Duty Application from %s (%s).</p><br>"""%(self.employee,self.employee_name)
			for idx,emp in enumerate(self.multi_employee):
				header = """<table class=table table-bordered><tr><td style = 'border: 1px solid black'>Serial No</td><th colspan='7' style = 'border: 1px solid black;background-color:#ffedcc;'><center>On Duty Application</center></th><tr>"""
				table += """<tr><td style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>Employee ID</th><td style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>Employee Name</th><td style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>Department</th><td style = 'border: 1px solid black'>%s</td></tr>
				"""%(idx+1,emp.employee,emp.employee_name,emp.department)
			data = """ </table><br><table class=table table-bordered><th colspan='6' style = 'border: 1px solid black;background-color:#ffedcc;'><center>On Duty Application Details</center></th><tr>
			<tr><th style = 'border: 1px solid black'>From Date</th><td style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>To Date</th><td style = 'border: 1px solid black'>%s</td></tr>
			<tr><th style = 'border: 1px solid black'>From Time</th><td style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>To Time</th><td style = 'border: 1px solid black'>%s</td></tr>
			<tr><th style = 'border: 1px solid black'>Total Number of Days</th><td style = 'border: 1px solid black'>%s</td><th style = 'border: 1px solid black'>Session</th><td style = 'border: 1px solid black'>%s</td></tr>
			<tr><th colspan='4' style = 'border: 1px solid black;background-color:#ffedcc;'><center><a href='%s'>VIEW</a></center></th></tr>
			</table><br>"""%(format_datetime(self.from_date),format_datetime(self.to_date),format_datetime(self.from_time),format_datetime(self.to_time),self.total_number_of_days,self.from_date_session,link)
			regards = "Thanks & Regards,<br>hrPRO"
			frappe.sendmail(
			recipients=[self.approver,'mohan.pan@thaisummit.co.in'],
			subject='Reg.On Duty Application Approval' ,
			message = content+header+table+data+regards)
	
	@frappe.whitelist()
	def show_html(self):
		if self.vehicle_request:
			html = "<h2><center>ON DUTY APPLICATION WITH VEHICLE</center></h2><table class='table table-bordered'><tr><th>From Date</th><th>To Date</th></tr><tr><td><h2>%s</h2></td><td><h2>%s</h2></td></tr><tr><th>From Time</th><th>To Time</th></tr><tr><td><h2>%s</h2></td><td><h2>%s</h2></td></tr></table>"%(frappe.utils.format_date(self.from_date),frappe.utils.format_date(self.to_date),self.from_time,self.to_time)
		else:
			html = "<h2><center>ON DUTY APPLICATION</center></h2><table class='table table-bordered'><tr><th>From Date</th><th>To Date</th></tr><tr><td><h2>%s</h2></td><td><h2>%s</h2></td></tr><tr><th>From Time</th><th>To Time</th></tr><tr><td><h2>%s</h2></td><td><h2>%s</h2></td></tr></table>"%(frappe.utils.format_date(self.from_date),frappe.utils.format_date(self.to_date),self.from_time,self.to_time)
		return html

	# @frappe.whitelist()
	# def validate_approver(self):
	#     if not frappe.session.user == 'hr.hdi@hunterdouglas.asia':
	#         employee = frappe.get_doc("Employee", self.employee)
	#         approvers = [l.leave_approver for l in employee.get("leave_approvers")]

	#         if len(approvers) and self.approver not in approvers:
	#             frappe.throw(_("Approver must be one of {0}")
	#                 .format(comma_or(approvers)), InvalidApproverError)

	#         elif self.approver and not frappe.db.sql("""select name from `tabHas Role`
	#             where parent=%s and role='Leave Approver'""", self.approver):
	#             frappe.throw(_("{0} ({1}) must have role 'Approver'")\
	#                 .format(get_fullname(self.approver), self.approver), InvalidApproverError)

	#         elif self.docstatus==0 and len(approvers) and self.approver != frappe.session.user:
	#             self.status = 'Applied'
				
	#         elif self.docstatus==1 and len(approvers) and self.approver != frappe.session.user:
	#             frappe.throw(_("Only the selected Approver can submit this Application"),
	#                 LeaveApproverIdentityError)
	
	# @frappe.whitelist()
	# def validate_od_overlap(self):
	#     if not self.name:
	#         # hack! if name is null, it could cause problems with !=
	#         self.name = "New On Duty Application"

	#     for d in frappe.db.sql("""
	#         select
	#             name, on_duty_type, posting_date, from_date, to_date, total_number_of_days, half_day_date
	#         from `tabOn Duty Application`
	#         where employee = %(employee)s and docstatus < 2 and status in ("Open","Applied", "Approved")
	#         and to_date >= %(from_date)s and from_date <= %(to_date)s
	#         and name != %(name)s""", {
	#             "employee": self.employee,
	#             "from_date": self.from_date,
	#             "to_date": self.to_date,
	#             "name": self.name
	#         }, as_dict = 1):

	#         if cint(self.half_day)==1 and getdate(self.half_day_date) == getdate(d.half_day_date) and (
	#             flt(self.total_number_of_days)==0.5
	#             or getdate(self.from_date) == getdate(d.to_date)
	#             or getdate(self.to_date) == getdate(d.from_date)):

	#             total_leaves_on_half_day = self.get_total_leaves_on_half_day()
	#             if total_leaves_on_half_day >= 1:
	#                 self.throw_overlap_error(d)
	#         else:
	#             self.throw_overlap_error(d)

	@frappe.whitelist()
	def throw_overlap_error(self, d):
		msg = _("Employee {0} has already applied for {1} between {2} and {3}").format(self.employee,
			d['on_duty_type'], formatdate(d['from_date']), formatdate(d['to_date'])) \
			+ """ <br><b><a href="#Form/On Duty Application/{0}">{0}</a></b>""".format(d["name"])
		leave_count_on_half_day_date = frappe.db.sql("""select count(name) from `tabOn Duty Application`
			where employee = %(employee)s
			and docstatus < 2
			and status in ("Open","Applied", "Approved")
			and half_day = 1
			and half_day_date = %(half_day_date)s
			and name != %(name)s""", {
				"employee": self.employee,
				"half_day_date": self.half_day_date,
				"name": self.name
			})[0][0]

		return leave_count_on_half_day_date * 0.5

	@frappe.whitelist()
	def get_ceo(self,department):
		ceo = frappe.db.get_value('Department',department,"ceo")
		return ceo
	
	@frappe.whitelist()
	def get_gm(self,department):
		gm = frappe.db.get_value('Department',department,"gm")
		return gm

	@frappe.whitelist()
	def get_hod(self,department):
		hod = frappe.db.get_value('Department',department,"hod")
		return hod

	# @frappe.whitelist()
	# def get_validation_dates():
	#     validation_days  = frappe.db.get_single_value('HR Time Settings','on_duty_validation_dates')
	#     return validation_days
				

# @frappe.whitelist()
# def on_duty_mark(doc,method):
#     if doc.status == "Approved": 
#         request_days = date_diff(doc.to_date, doc.from_date) +1
#         for number in range(request_days):
#             attendance_date = add_days(doc.from_date, number)
#             skip_attendance = validate_if_attendance_not_applicable(doc.employee,attendance_date)
#             if not skip_attendance:
#                 att = frappe.db.exists("Attendance",{"employee":doc.employee,"attendance_date":attendance_date})
#                 if doc.half_day and date_diff(getdate(doc.half_day_date), getdate(attendance_date)) == 0:
#                     status = "Half Day"
#                 else:
#                     status = "On Duty"
#                 if att:
#                     attendance = frappe.get_doc("Attendance",att)
#                     attendance.update({
#                     "status":status,
#                     "on_duty_application":doc.name
#                     })
#                     attendance.db_update()
#                     frappe.db.commit()
#                 else:
#                     attendance = frappe.new_doc("Attendance")
#                     attendance.employee = doc.employee
#                     attendance.employee_name = doc.employee_name
#                     attendance.status = status
#                     attendance.attendance_date = attendance_date
#                     attendance.late_in = "00:00:0"
#                     attendance.work_time = "00:00:0"
#                     attendance.early_out = "00:00:0"
#                     attendance.overtime = "00:00:0"
#                     attendance.on_duty_application = doc.name
#                     attendance.company = doc.company
#                     attendance.save(ignore_permissions=True)
#                     attendance.submit()

def validate_if_attendance_not_applicable(employee, attendance_date):
	# Check if attendance_date is a Holiday
	if is_holiday(employee, attendance_date):
		frappe.msgprint(_("Attendance not submitted for {0} as it is a Holiday.").format(attendance_date), alert=1)
		return True
	# Check if employee on Leave
	leave_record = frappe.db.sql("""select half_day from `tabLeave Application`
			where employee = %s and %s between from_date and to_date
			and docstatus = 1""", (employee, attendance_date), as_dict=True)
	if leave_record:
		frappe.msgprint(_("Attendance not submitted for {0} as {1} on leave.").format(attendance_date, employee), alert=1)
		return True

	return False

def get_holiday_list_for_employee(employee, raise_exception=True):
	if employee:
		holiday_list, company = frappe.db.get_value("Employee", employee, ["holiday_list", "company"])
	else:
		holiday_list=''
		company=frappe.db.get_value("Global Defaults", None, "default_company")

	if not holiday_list:
		holiday_list = frappe.get_cached_value('Company',  company,  "default_holiday_list")

	if not holiday_list and raise_exception:
		frappe.throw(_('Please set a default Holiday List for Employee {0} or Company {1}').format(employee, company))

	return holiday_list

def is_holiday(employee, date=None):
	'''Returns True if given Employee has an holiday on the given date
	:param employee: Employee `name`
	:param date: Date to check. Will check for today if None'''

	holiday_list = get_holiday_list_for_employee(employee)
	if not date:
		date = today()

	if holiday_list:
		return frappe.get_all('Holiday List', dict(name=holiday_list, holiday_date=date)) and True or False


@frappe.whitelist()
def get_number_of_leave_days(employee, from_date, to_date,from_date_session=None,  to_date_session=None, date_dif=None):
	number_of_days = 0
	if from_date == to_date:
		if from_date_session != 'Full Day':
			number_of_days = 0.5
		else:
			number_of_days = 1
	else:
		if from_date_session == "Full Day" and to_date_session == "Full Day":
			number_of_days = flt(date_dif)
		if from_date_session == "Full Day" and to_date_session == "First Half":
			number_of_days = flt(date_dif) - 0.5
		if from_date_session == "Second Half" and to_date_session == "Full Day":
			number_of_days = flt(date_dif) - 0.5
		if from_date_session == "Second Half" and to_date_session == "First Half":
			number_of_days = flt(date_dif) - 1
	return number_of_days


@frappe.whitelist()
def check_attendance(employee, from_date, to_date):
	if employee:
		attendance = frappe.db.sql("""select status,attendance_date from `tabAttendance`
					where employee = %s and attendance_date between %s and %s
					and docstatus = 1""", (employee, from_date, to_date), as_dict=True)
		return attendance

@frappe.whitelist()
def validate_cutoff(from_date):
	cur_mon = datetime.strptime(today(), "%Y-%m-%d").strftime("%B")
	frappe.errprint(cur_mon)
	c = frappe.get_value("Application Cut Off Date",{'month':cur_mon},['cut_off_date','from_date','to_date'])
	curday = date.today()
	fromdate = datetime.strptime(str(from_date),"%Y-%m-%d").date()
	if fromdate < c[1]:
		return 'Expired'
	if fromdate > c[1] and fromdate < c[2]:
		frappe.errprint('true')

@frappe.whitelist()
def get_employees():
	data = []
	employee = frappe.db.get_value('Employee',{'status':'Active','user_id':frappe.session.user},["name", "employee_name", "department", "designation"])
	data.append(employee[0])
	data.append(employee[1])
	data.append(employee[2])
	data.append(employee[3])
	return data

@frappe.whitelist()
def check_holiday(date):
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = 'Holiday List - 2021' and holiday_date = '%s' """%(date),as_dict=True)
	if holiday:
		if holiday[0].weekly_off == 1:
			return "WW"
		else:
			return "HH"
		