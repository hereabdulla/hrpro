# -*- coding: utf-8 -*-
# Copyright (c) 2018, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta
from frappe import _
from frappe.utils import today,flt,add_days,date_diff,getdate,cint,formatdate, getdate, get_link_to_form, \
    comma_or, get_fullname
from hrpro.hrpro.doctype.on_duty_application.on_duty_application import validate_if_attendance_not_applicable
from frappe.utils.background_jobs import enqueue

class LeaveApproverIdentityError(frappe.ValidationError): pass
class OverlapError(frappe.ValidationError): pass

class TravelManagement(Document):
    def on_submit(self):
        if self.status == "Applied":
            frappe.throw(_("Only Applications with status 'Approved' and 'Rejected' can be submitted"))
        # self.send_ticket_copy()
    
    # def on_update_after_submit(self):
    #     if self.get_attachments():
    #         attachments = self.get_attachments()
    #         print attachments
    #         email_args = {
    #             'recipients':'abdulla.pi@voltechgroup.com',
    #             'attachments':[self.get_attachments()], 
    #             'subject':'Ticket Copy  for %s' % self.name,
    #             'message':""" <p><em><strong>Ticket Requisition</strong></em></p>
    #                         <ul style="list-style-type: circle;">
    #                         <li>Employee Code: <strong>%s</strong></li>
    #                         <li>Employee Name: <strong>%s</strong></li>
    #                         <li>Status: <strong>%s</strong></li>
    #                         <li>Approved By: <strong>%s</strong></li>
    #                         <li>Travel Date: <strong>%s</strong></li>
    #                         <li>From Place: <strong>%s</strong></li>
    #                         <li>To Place: <strong>%s </strong></li>
    #                         </ul>"""%(self.employee,self.employee_name,self.status,self.approver,formatdate(self.from_date),self.from_place,self.to_place),
    #             'now':True,
    #         }
    #         enqueue(method=frappe.sendmail, queue='short', timeout=300, is_async=True, **email_args)
        
    # def get_attachments(self):
    #     employee = frappe.get_doc("Employee", self.employee)
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
    #                 LeaveApproverIdentityError)n frappe.get_doc("File",{'attached_to_doctype':self.doctype,'attached_to_name':self.name})

    def validate(self):
        # self.validate_approver()	
        self.validate_tm_overlap()

    def validate_approver(self):
        if not frappe.session.user == 'hr.hdi@hunterdouglas.asia':
            employee = frappe.get_doc("Employee", self.employee)
            approvers = [l.leave_approver for l in employee.get("leave_approvers")]
            if len(approvers) and self.approver not in approvers:
                frappe.throw(_("Approver must be one of {0}")
                    .format(comma_or(approvers)), InvalidApproverError)

            elif self.approver and not frappe.db.sql("""select name from `tabHas Role`
                where parent=%s and role='Leave Approver'""", self.approver):
                frappe.throw(_("{0} ({1}) must have role 'Approver'")\
                    .format(get_fullname(self.approver), self.approver), InvalidApproverError)

            elif self.docstatus==0 and len(approvers) and self.approver != frappe.session.user:
                self.status = 'Applied'

            elif self.docstatus==1 and len(approvers) and self.approver != frappe.session.user:
                frappe.throw(_("Only the selected Approver can submit this Application"),
                    LeaveApproverIdentityError)

    def validate_tm_overlap(self):
        if not self.docstatus == 1:
            if not self.name:
                # hack! if name is null, it could cause problems with !=
                self.name = "New Travel Management"

            for d in frappe.db.sql("""
                select
                    name, total_number_of_days, from_date, to_date, half_day_date
                from `tabTravel Management`
                where employee = %(employee)s and docstatus < 2 and status in ("Open","Applied", "Approved")
                and to_date >= %(from_date)s and from_date <= %(to_date)s
                and name != %(name)s""", {
                    "employee": self.employee,
                    "from_date": self.from_date,
                    "to_date": self.to_date,
                    "name": self.name
                }, as_dict = 1):

                if cint(self.half_day)==1 and getdate(self.half_day_date) == getdate(d.half_day_date) and (
                    flt(self.total_leave_days)==0.5
                    or getdate(self.from_date) == getdate(d.to_date)
                    or getdate(self.to_date) == getdate(d.from_date)):

                    total_leaves_on_half_day = self.get_total_leaves_on_half_day()
                    if total_leaves_on_half_day >= 1:
                        self.throw_overlap_error(d)
                else:
                    self.throw_overlap_error(d)

    def throw_overlap_error(self, d):
        msg = _("Employee {0} has already applied for Travel between {1} and {2}").format(self.employee,formatdate(d['from_date']), formatdate(d['to_date'])) \
            + """ <br><b><a href="#Form/Travel Management/{0}">{0}</a></b>""".format(d["name"])
        frappe.throw(msg, OverlapError)

    # def on_submit(self):
    #     self.travel_att_mark()

    def on_cancel(self):
        attendance_list = frappe.get_list("Attendance", {'employee': self.employee, 'travel_application': self.name})
        if attendance_list:
            for attendance in attendance_list:
                attendance_obj = frappe.get_doc("Attendance", attendance['name'])
                attendance_obj.cancel()

@frappe.whitelist()
def travel_att_mark(doc,method):
    if doc.status == "Approved": 
        request_days = date_diff(doc.to_date, doc.from_date) +1
        for number in range(request_days):
            attendance_date = add_days(doc.from_date, number)
            skip_attendance = validate_if_attendance_not_applicable(doc.employee,attendance_date)
            if not skip_attendance:
                att = frappe.db.exists("Attendance",{"employee":doc.employee,"attendance_date":attendance_date})
                if doc.half_day and date_diff(getdate(doc.half_day_date), getdate(attendance_date)) == 0:
                    status = "Half Day"
                else:
                    status = "On Duty"
                if att:
                    attendance = frappe.get_doc("Attendance",att)
                    attendance.update({
                    "status":status,
                    "travel_application":doc.name
                    })
                    attendance.db_update()
                    frappe.db.commit()
                else:
                    attendance = frappe.new_doc("Attendance")
                    attendance.employee = doc.employee
                    attendance.employee_name = doc.employee_name
                    attendance.status = status
                    attendance.attendance_date = attendance_date
                    attendance.late_in = "00:00:0"
                    attendance.work_time = "00:00:0"
                    attendance.early_out = "00:00:0"
                    attendance.overtime = "00:00:0"
                    attendance.travel_application = doc.name
                    attendance.save(ignore_permissions=True)
                    attendance.submit()

# def validate_if_attendance_not_applicable(employee, attendance_date):
#     # Check if attendance_date is a Holiday
# 	if is_holiday(employee, attendance_date):
# 		frappe.msgprint(_("Attendance not submitted for {0} as it is a Holiday.").format(attendance_date), alert=1)
# 		return True
#     # Check if employee on Leave
# 	leave_record = frappe.db.sql("""select half_day from `tabLeave Application`
# 			where employee = %s and %s between from_date and to_date
# 			and docstatus = 1""", (employee, attendance_date), as_dict=True)
# 	if leave_record:
# 		frappe.msgprint(_("Attendance not submitted for {0} as {1} on leave.").format(attendance_date, employee), alert=1)
# 		return True

# 	return False

# def get_holiday_list_for_employee(employee, raise_exception=True):
# 	if employee:
# 		holiday_list, company = frappe.db.get_value("Employee", employee, ["holiday_list", "company"])
# 	else:
# 		holiday_list=''
# 		company=frappe.db.get_value("Global Defaults", None, "default_company")

# 	if not holiday_list:
# 		holiday_list = frappe.get_cached_value('Company',  company,  "default_holiday_list")

# 	if not holiday_list and raise_exception:
# 		frappe.throw(_('Please set a default Holiday List for Employee {0} or Company {1}').format(employee, company))

# 	return holiday_list

# def is_holiday(employee, date=None):
# 	'''Returns True if given Employee has an holiday on the given date
# 	:param employee: Employee `name`
# 	:param date: Date to check. Will check for today if None'''

# 	holiday_list = get_holiday_list_for_employee(employee)
# 	if not date:
# 		date = today()

# 	if holiday_list:
# 		return frappe.get_all('Holiday List', dict(name=holiday_list, holiday_date=date)) and True or False


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
def update_tm(tm_id,expense_claim):
    if tm_id:
        frappe.errprint(tm_id)
        tvm = frappe.get_doc("Travel Management",tm_id)
        if not tvm.expense_claim:
            tvm.update({
                "expense_claim":expense_claim
            })
            tvm.save()
    return "OK"


@frappe.whitelist()
def create_tour_application(travel_management):
    tr = frappe.get_doc("Travel Management",travel_management)
    tour = frappe.new_doc("Tour Application")
    tour.update({
        "employee": tr.employee,
        "employee_name": tr.employee_name,
        "approver_name": tr.approver_name,
        "approver": tr.approver,
        "from_date": tr.from_date,
        "to_date": tr.to_date,
        "half_day": tr.half_day,
        "half_day_date": tr.half_day_date,
        "from_date_session": tr.from_date_session,
        "to_date_session": tr.to_date_session,
        "description": tr.description,
        "department": tr.department,
        "grade": tr.grade,
        "location": tr.location,
        "business_unit": tr.business_unit,
        "category": tr.category,
        "follow_via_email": 0

    })
    tour.save(ignore_permissions=True)
    frappe.db.commit()
    return tour.name


@frappe.whitelist()
def delete_tour_application(doc, method):
    tr = frappe.db.exists("Tour Application",doc.tour_application)
    if tr:
        doc = frappe.get_doc("Tour Application",tr)
        if doc.docstatus == 1:
            doc.cancel()
        frappe.delete_doc("Tour Application",tr)    