# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe,os,base64
import requests
import datetime
import json,calendar
from datetime import datetime,timedelta,date,time
import datetime as dt
from datetime import date
from frappe.utils import cint,today,flt,date_diff,add_days,add_months,date_diff,getdate,formatdate,cint,cstr
from frappe.desk.notifications import delete_notification_count_for
from frappe import _
import xml.etree.ElementTree as ET
from erpnext.hr.utils import get_holiday_dates_for_employee
# from hrpro.hrpro.report.monthly_absenteesim.monthly_absenteesim import validate_if_attendance_not_applicable    
from frappe.email.email_body import (replace_filename_with_cid,
    get_email, inline_style_in_html, get_header)
import dateutil.parser
from dateutil.relativedelta import relativedelta
# from hrpro.update_attendance import update_att_from_shift
from json import JSONEncoder
from datetime import datetime


@frappe.whitelist()
def check_appraisal(emp,year):
    if frappe.db.exists("Performance Management Self", {"employee_code1": emp, "appraisal_year": year,"docstatus":1}):
        return year

@frappe.whitelist()
def get_previous_year_goals(emp,year):
    pm = frappe.db.exists("Performance Management Self",{"employee_code1": emp, "appraisal_year": year})
    if pm:
        return pm
    else:
        return 'NA'    

@frappe.whitelist()
def fetch_att_test(from_date,to_date,employee=None,department=None,designation=None,location=None):
    frappe.errprint(from_date)
    employees = []
    from_date = (datetime.strptime(str(from_date), '%Y-%m-%d')).date()
    to_date = (datetime.strptime(str(to_date), '%Y-%m-%d')).date()
    for preday in daterange(from_date, to_date):
        day = preday.strftime("%d%m%Y")
        date = datetime.today().strftime("%Y-%m-%d")
        exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
        auto_present_list = []
        for e in exc:
            auto_present_list.append(e.employee)
        # if employee and not department and not designation and not location:
        #     employees.append(employee)
        else:
            filters = frappe._dict({
                'status':'Active',
                'date_of_joining':('<=',preday)
            })
            if employee:
                filters.update({ "employee_number": employee})
            if department:
                filters.update({ "department": department})
            if designation:
                filters.update({ "designation": designation})
            if location:
                filters.update({ "location_name": location})
            employees = frappe.get_all('Employee',filters)
        for emp in employees:
            working_shift = frappe.db.get_value("Employee", {'employee':emp.name},['working_shift']) 
            assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                        where employee = %s and %s between from_date and to_date""", (emp.name, preday), as_dict=True)
            if assigned_shift:
                working_shift = assigned_shift[0]['shift']
            if emp.name in auto_present_list:
                doc = frappe.get_doc("Employee",emp.name)
                attendance = frappe.db.exists("Attendance", {"employee": doc.employee, "attendance_date": preday})
                if attendance:
                    frappe.db.set_value("Attendance",attendance,"status","Present")
                    frappe.db.commit()
                else:
                    attendance = frappe.new_doc("Attendance")
                    attendance.employee = doc.employee
                    attendance.employee_name = doc.employee_name
                    attendance.status = "Present"
                    attendance.first_half_status = "PR"
                    attendance.second_half_status = "PR"
                    attendance.attendance_date = preday
                    # attendance.company = doc.company
                    attendance.working_shift = working_shift,
                    attendance.late_in = "00:00:00"
                    attendance.work_time = "00:00:00"
                    attendance.early_out = "00:00:00"
                    attendance.overtime = "00:00:00"
                    attendance.save(ignore_permissions=True)
                    attendance.submit()
                    frappe.db.commit()
            else:
                try:
                    url = 'http://182.72.89.102/cosec/api.svc/v2/attendance-daily?action=get;field-name=userid,ProcessDate,firsthalf,\
                            secondhalf,punch1,punch2,workingshift,shiftstart,shiftend,latein,earlyout,worktime,overtime;date-range=%s-%s;range=user;id=%s;format=xml' % (day,day,emp.name) 
                    r = requests.get(url, auth=('sa', 'matrixx'))
                    if "No records found" in r.content:
                        attendance_id = frappe.db.exists("Attendance", {
                                "employee": emp.name, "attendance_date": preday,"docstatus":1})
                        if attendance_id:
                            pass
                        else:            
                            attendance = frappe.new_doc("Attendance")
                            attendance.update({
                                "employee": emp.name,
                                "attendance_date": preday,
                                "status": 'Absent',
                                "first_half_status": "AB",
                                "second_half_status": "AB",
                                "late_in" : "0:00:00",
                                "early_out" : "0:00:00",
                                "working_shift" : working_shift,
                                "work_time": "0:00:00",
                                "overtime":"0:00:00"
                            })
                            attendance.save(ignore_permissions=True)
                            attendance.submit()
                            frappe.db.commit() 
                    else: 
                        if not "failed: 0010102003" in r.content:  
                            root = ET.fromstring(r.content)
                            for att in root.findall('attendance-daily'):
                                userid = att.find('UserID').text
                                in_time = att.find('Punch1').text
                                out_time = att.find('Punch2').text
                                first_half_status = att.find('firsthalf').text
                                second_half_status = att.find('secondhalf').text
                                date = datetime.strptime((att.find('ProcessDate').text.replace("/","")), "%d%m%Y").date()
                                date_f = date.strftime("%Y-%m-%d")
                                if flt(att.find('WorkTime').text) > 1440:
                                    work_time = timedelta(minutes=flt('1400'))
                                else:
                                    work_time = timedelta(minutes=flt(att.find('WorkTime').text)) 
                                over_time = timedelta(minutes=flt(att.find('Overtime').text))
                                late_in = timedelta(minutes=flt(att.find('LateIn').text))
                                early_out = timedelta(minutes=flt(att.find('EarlyOut').text))
                                attendance_id = frappe.db.exists("Attendance", {
                                    "employee": emp.name, "attendance_date": date_f,"docstatus":1})
                                if out_time:
                                    out_time_f = datetime.strptime(out_time, "%d/%m/%Y %H:%M:%S")
                                if in_time:    
                                    in_time_f = datetime.strptime(in_time, "%d/%m/%Y %H:%M:%S")
                                if in_time and out_time:
                                    work_time = out_time_f - in_time_f     
                                wt_seconds = work_time.total_seconds() // 60
                                if wt_seconds > 1440:
                                    work_time = timedelta(minutes=flt('1400'))    
                                if work_time >= timedelta(hours=4):
                                    if work_time < timedelta(hours=7,minutes=45):
                                        status = 'Half Day'
                                    else:    
                                        status = 'Present'
                                else:
                                    status = 'Absent'     
                                if attendance_id:
                                    attendance = frappe.get_doc(
                                        "Attendance", attendance_id)
                                    attendance.out_time = out_time
                                    attendance.in_time = in_time
                                    attendance.status = status
                                    attendance.first_half_status = first_half_status
                                    attendance.second_half_status = second_half_status
                                    attendance.late_in = late_in
                                    attendance.early_out = early_out
                                    attendance.working_shift = working_shift
                                    attendance.work_time = work_time
                                    attendance.overtime = over_time
                                    attendance.db_update()
                                    frappe.db.commit()
                                else:
                                    attendance = frappe.new_doc("Attendance")
                                    attendance.update({
                                        "employee": emp.name,
                                        "attendance_date": date_f,
                                        "status": status,
                                        "in_time": in_time,
                                        "first_half_status":first_half_status,
                                        "second_half_status":second_half_status,
                                        "late_in" : late_in,
                                        "early_out" : early_out,
                                        "working_shift" : working_shift,
                                        "out_time": out_time,
                                        "work_time": work_time,
                                        "overtime":over_time
                                    })
                                    attendance.save(ignore_permissions=True)
                                    attendance.submit()
                                    frappe.db.commit() 
                except Exception as e:
                    frappe.msgprint(_("Connection Failed,Kindly check Matrix Server is Up"))
                    break          


@frappe.whitelist()
def fetch_att_prev():
    prev_day = add_days(today(),-1)
    fetch_att_test(prev_day,prev_day)

@frappe.whitelist()
def test():
    delete_notification_count_for("Chat")

def get_employees():            
    query = """SELECT employee,employee_name,designation FROM `tabEmployee` WHERE status='Active'
            ORDER BY employee"""
    data = frappe.db.sql(query, as_dict=1)
    return data

@frappe.whitelist()
def fetch_att():
    preday = datetime.strptime(today(), '%Y-%m-%d')
    day = preday.strftime("%d%m%Y")
    exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
    
    auto_present_list = []
    for e in exc:
        auto_present_list.append(e.employee)
    employees = frappe.get_all('Employee',{'status':'Active'})
    for emp in employees:
        working_shift = frappe.db.get_value("Employee", {'employee':emp.name},['working_shift']) 
        assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                    where employee = %s and %s between from_date and to_date""", (emp.name, preday), as_dict=True)
        if assigned_shift:
            working_shift = assigned_shift[0]['shift']
        if emp.name in auto_present_list:
            doc = frappe.get_doc("Employee",emp.name)
            attendance = frappe.db.exists("Attendance", {"employee": doc.employee, "attendance_date": preday})
            if attendance:
                frappe.db.set_value("Attendance",attendance,"status","Present")
                frappe.db.commit()
            else:
                attendance = frappe.new_doc("Attendance")
                attendance.employee = doc.employee
                attendance.employee_name = doc.employee_name
                attendance.status = "Present"
                attendance.attendance_date = preday
                # attendance.company = doc.company
                attendance.working_shift = working_shift
                attendance.late_in = "00:00:00"
                attendance.work_time = "00:00:00"
                attendance.early_out = "00:00:00"
                attendance.overtime = "00:00:00"
                attendance.save(ignore_permissions=True)
                attendance.submit()
                frappe.db.commit()
        else:
            url = 'http://182.72.89.102/cosec/api.svc/v2/attendance-daily?action=get;field-name=userid,ProcessDate,firsthalf,\
                    secondhalf,punch1,punch2,workingshift,shiftstart,shiftend,latein,earlyout,worktime,overtime;date-range=%s-%s;range=user;id=%s;format=xml' % (day,day,emp.name) 
            r = requests.get(url, auth=('sa', 'matrixx'))
            if "No records found" in r.content:
                attendance_id = frappe.db.exists("Attendance", {
                        "employee": emp.name, "attendance_date": preday,"docstatus":1})
                if attendance_id:
                    pass
                else:            
                    attendance = frappe.new_doc("Attendance")
                    attendance.update({
                        "employee": emp.name,
                        "attendance_date": preday,
                        "status": 'Absent',
                        "late_in" : "0:00:00",
                        "early_out" : "0:00:00",
                        "working_shift" : working_shift,
                        "work_time": "0:00:00",
                        "overtime":"0:00:00"
                    })
                    attendance.save(ignore_permissions=True)
                    attendance.submit()
                    frappe.db.commit() 
            else:    
                if not "failed: 0010102003" in r.content:
                    root = ET.fromstring(r.content)
                    for att in root.findall('attendance-daily'):
                        userid = att.find('UserID').text
                        in_time = att.find('Punch1').text
                        out_time = att.find('Punch2').text
                        date = datetime.strptime((att.find('ProcessDate').text.replace("/","")), "%d%m%Y").date()
                        date_f = date.strftime("%Y-%m-%d")
                        first_half_status = att.find('firsthalf').text
                        second_half_status = att.find('secondhalf').text
                        if flt(att.find('WorkTime').text) > 1440:
                            work_time = timedelta(minutes=flt('1400'))
                        else:
                            work_time = timedelta(minutes=flt(att.find('WorkTime').text)) 
                        over_time = timedelta(minutes=flt(att.find('Overtime').text))
                        late_in = timedelta(minutes=flt(att.find('LateIn').text))
                        early_out = timedelta(minutes=flt(att.find('EarlyOut').text))
                        attendance_id = frappe.db.exists("Attendance", {
                            "employee": emp.name, "attendance_date": date_f,"docstatus":1})
                        if out_time:
                                out_time_f = datetime.strptime(out_time, "%d/%m/%Y %H:%M:%S")
                        if in_time:    
                            in_time_f = datetime.strptime(in_time, "%d/%m/%Y %H:%M:%S")
                        if in_time and out_time:
                            work_time = out_time_f - in_time_f     
                        wt_seconds = work_time.total_seconds() // 60
                        if wt_seconds > 1440:
                            work_time = timedelta(minutes=flt('1400'))    
                        if work_time >= timedelta(hours=4):
                            if work_time < timedelta(hours=7,minutes=45):
                                status = 'Half Day'
                            else:    
                                status = 'Present'
                        else:
                            status = 'Absent'     
                        if attendance_id:
                            attendance = frappe.get_doc(
                                "Attendance", attendance_id)
                            attendance.out_time = out_time
                            attendance.in_time = in_time
                            attendance.status = status 
                            attendance.first_half_status = first_half_status
                            attendance.second_half_status = second_half_status
                            attendance.late_in = late_in
                            attendance.early_out = early_out
                            attendance.working_shift = working_shift
                            attendance.work_time = work_time
                            attendance.overtime = over_time
                            attendance.db_update()
                            frappe.db.commit()
                        else:
                            attendance = frappe.new_doc("Attendance")
                            attendance.update({
                                "employee": emp.name,
                                "attendance_date": date_f,
                                "status": status,
                                "in_time": in_time,
                                "late_in" : late_in,
                                "early_out" : early_out,
                                "working_shift" : working_shift,
                                "out_time": out_time,
                                "work_time": work_time,
                                "overtime":over_time
                            })
                            attendance.save(ignore_permissions=True)
                            attendance.submit()
                            frappe.db.commit() 



@frappe.whitelist()	
def fetch_employee():
    url = 'http://182.72.89.102/cosec/api.svc/v2/user?action=get;format=xml' 
    r = requests.get(url, auth=('sa', 'matrixx'))
    root = ET.fromstring(r.content)
    for emp in root.findall('user'):
        reference_code = emp.find('reference-code').text
        # if reference_code == "2057":
        if not frappe.db.exists("Employee",reference_code):
            employee = frappe.new_doc("Employee")
            employee.update({
                "employee_name": emp.find('name').text,
                "employee_number": emp.find('reference-code').text,
                "gender" : "Male",
                "reports_to" : emp.find('rg_incharge_1').text,
                "leave_approver": emp.find('rg_incharge_1').text,
                # "prefered_contact_email": emp.find('official-email').text,
                "passport_number":emp.find('passport-no').text,
                "pf_number":emp.find('pf-no').text,
                "pan_number":emp.find('pan').text,
                "uan_number":emp.find('uan').text
            })
            if emp.find('joining-date').text != None:
                employee.update({
                  "date_of_joining": (datetime.strptime(emp.find('joining-date').text, '%d%m%Y')).date(),
                })
            employee.save(ignore_permissions=True)
            frappe.db.commit()
        



def daterange(date1,date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)




@frappe.whitelist()	
def display_announcement(note,announcement):
    msgvar = """Notification.requestPermission(function (permission) 
    {
        if (permission === "granted")
     {  
         var notification = new Notification("%s"); 
         notification.onclick = function(event){
             event.preventDefault();
             frappe.set_route('Form','Announcements','%s')
         }
         }
          });""" % (note,announcement)
    user_list = frappe.get_all('User',filters={'enabled':1})
    for user in user_list:  
        frappe.publish_realtime(event='eval_js',message=msgvar,user=user['name'])

@frappe.whitelist()	
def send_birthday_wish():
    
    # """Send Employee birthday reminders if no 'Stop Birthday Reminders' is not set."""
    # if int(frappe.db.get_single_value("HR Settings", "stop_birthday_reminders") or 0):
    # 	return
    from frappe.utils.user import get_enabled_system_users
    users = None
    birthdays = get_employees_who_are_born_today()
    wish = frappe.db.sql("""select wish from `tabWishes`  order by RAND() limit 1""",as_dict=1)[0]
    if birthdays:
        if not users:
            users = [u.email_id or u.name for u in get_enabled_system_users()]
        for e in birthdays:
            age = calculate_age(e.date_of_birth)
            args = dict(employee=e.employee_name,age=age,wish=wish['wish'],company=frappe.defaults.get_defaults().company,photo=e.image)
            # frappe.sendmail(recipients=filter(lambda u: u not in (e.company_email, e.personal_email, e.user_id), users),
            frappe.sendmail(recipients=['sivaranjani.s@voltechgroup.com'],
                subject=_("Birthday Reminder for {0}").format(e.employee_name),
                # message=_("""Today is {0}'s birthday!""").format(e.employee_name),
                template = 'birthday_wish',
                args = args)

def calculate_age(dtob):
    today = date.today()
    return today.year - dtob.year - ((today.month, today.day) < (dtob.month, dtob.day))

def get_employees_who_are_born_today():
    """Get Employee properties whose birthday is today."""
    return frappe.db.sql("""select name,date_of_birth, personal_email, company_email, user_id, employee_name,image
        from tabEmployee where day(date_of_birth) = day(%(date)s)
        and month(date_of_birth) = month(%(date)s)
        and status = 'Active'""", {"date": today()}, as_dict=True)    

    # msgvar = """Notification.requestPermission(function (permission) 
    # {
    #     if (permission === "granted")
    #  {  
    #      var notification = new Notification("%s"); 
    #      }
    #       });""" % wish[0]
    # user_list = frappe.get_all('User',filters={'enabled':1})
    # for user in user_list:  
    #     frappe.publish_realtime(event='msgprint',message=wish[0],user=user['name'])
    # note = frappe.new_doc("Note")
    # note.title = 'Birthday Wishes'
    # note.public = 1
    # note.notify_on_login = 1
    # note.content = str(wish[0])
    # note.save(ignore_permissions=True)
    # frappe.db.commit()

   
@frappe.whitelist()
def update_leave_approval(doc,status):
    lap = frappe.get_doc("Leave Application",doc)    
    lap.update({
        "status":status
    })
    lap.save(ignore_permissions=True)
    lap.submit()
    frappe.db.commit()

@frappe.whitelist()
def update_onduty_approval(doc,status):
    lap = frappe.get_doc("On Duty Application",doc)    
    lap.update({
        "status":status
    })
    lap.save(ignore_permissions=True)
    lap.submit()
    frappe.db.commit()

@frappe.whitelist()
def update_miss_punch_approval(doc,status):
    mpap = frappe.get_doc("Miss Punch Application",doc)    
    mpap.update({
        "status":status
    })
    mpap.save(ignore_permissions=True)
    mpap.submit()
    frappe.db.commit()

@frappe.whitelist()
def update_movement_register(doc,status):
    tm = frappe.get_doc("Movement Register",doc)  
    tm.update({
        "status":status
    })
    tm.save(ignore_permissions=True)
    tm.submit()
    frappe.db.commit()

@frappe.whitelist()
def update_travel_approval(doc,status):
    tm = frappe.get_doc("Travel Management",doc)  
    tm.update({
        "status":status
    })
    tm.save(ignore_permissions=True)
    tm.submit()
    frappe.db.commit()

    tour = tm.tour_application
    tour_doc = frappe.get_doc("Tour Application",tour)  
    tour_doc.update({
        "status":status
    })
    tour_doc.save(ignore_permissions=True)
    tour_doc.submit()
    frappe.db.commit()

@frappe.whitelist()
def update_expense_approval(doc,status,approval_status):
    tm = frappe.get_doc("Expense Claim",doc)  
    tm.update({
        "workflow_state":status,
        "approval_status":approval_status
    })
    tm.save(ignore_permissions=True)
    # tm.submit()
    frappe.db.commit()

@frappe.whitelist()
def update_tour_approval(doc,status):
    tm = frappe.get_doc("Tour Application",doc)  
    tm.update({
        "status":status
    })    
    tm.save(ignore_permissions=True)
    tm.submit()
    frappe.db.commit()

@frappe.whitelist()
def bulk_leave_approve(names,status):
    if not frappe.has_permission("Leave Application","write"):
        frappe.throw(_("Not Permitted"),frappe.PermissionError)

    names = json.loads(names)
    for name in names:
        lap = frappe.get_doc("Leave Application",name)
        lap.update({
        "status":status
    })
    lap.save(ignore_permissions=True)
    lap.submit()
    frappe.db.commit()

@frappe.whitelist()
def bulk_travel_approve(names,status):
    if not frappe.has_permission("Travel Management","write"):
        frappe.throw(_("Not Permitted"),frappe.PermissionError)

    names = json.loads(names)
    for name in names:
        tm = frappe.get_doc("Travel Management",name)
        tm.update({
        "status":status
    })
    tm.save(ignore_permissions=True)
    tm.submit()
    frappe.db.commit()

@frappe.whitelist()
def bulk_onduty_approve(names,status):
    if not frappe.has_permission("On Duty Application","write"):
        frappe.throw(_("Not Permitted"),frappe.PermissionError)

    names = json.loads(names)
    for name in names:
        oda = frappe.get_doc("On Duty Application",name)
        oda.update({
        "status":status
    })
    oda.save(ignore_permissions=True)
    oda.submit()
    frappe.db.commit()

def update_website_context(context):
    context.update(dict(
        splash_image = '/assets/hrpro/images/hd.svg'
    ))
    return context


@frappe.whitelist()
def bulk_auto_present():
    for preday in daterange(date(2019, 1, 10), date(2019, 1, 10)):
    # #     preday = dt
    # preday = datetime.strptime(today(), '%Y-%m-%d').date()
        employee = []
        for emp in frappe.db.get_list("Auto Present Employees",fields=['employee']):
            # skip_attendance = validate_if_attendance_not_applicable(emp,preday)
            # if not skip_attendance:
            doc = frappe.get_doc("Employee",emp['employee'])
            attendance = frappe.db.exists("Attendance", {"employee": emp['employee'], "attendance_date": preday})
            if attendance:
                frappe.db.set_value("Attendance",attendance,"status","Present")
                frappe.db.commit()
            else:
                attendance = frappe.new_doc("Attendance")
                attendance.employee = doc.employee
                attendance.employee_name = doc.employee_name
                attendance.status = "Present"
                attendance.attendance_date = preday
                # attendance.company = doc.company
                attendance.late_in = "00:00:00"
                attendance.work_time = "00:00:00"
                attendance.early_out = "00:00:00"
                attendance.overtime = "00:00:00"
                attendance.save(ignore_permissions=True)
                attendance.submit()
                frappe.db.commit()



def daterange(date1,date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

def log_error(method, message):
    # employee = message["userid"]
    message = frappe.utils.cstr(message) + "\n" if message else ""
    d = frappe.new_doc("Error Log")
    d.method = method
    d.error = message
    d.insert(ignore_permissions=True)   

@frappe.whitelist()
def validate_if_attendance_not_applicable(employee, attendance_date):
    # Check if attendance_date is a Holiday
    if is_holiday(employee, attendance_date):
        return True
    # Check if employee on Leave
    leave_record = frappe.db.sql("""select half_day from `tabLeave Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1""", (employee, attendance_date), as_dict=True)
    if leave_record:
        return True

    return False

@frappe.whitelist()
def in_punch_alert():
    day =  today()
    exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
    employees_list = []
    for e in exc:
        employees_list.append(e.employee)
    employees = frappe.get_all('Employee',{'status':'Active'})
    for emp in employees:
        if emp.name not in employees_list:
            skip_attendance = validate_if_attendance_not_applicable(emp.name,day)
            if not skip_attendance:
                # frappe.sendmail(
                #     recipients=['sivaranjani.s@voltechgroup.com'],
                #     subject='Missed IN Punch Alert for %s' +
                #     formatdate(today()),
                #     message=""" 
                #     <h3>Missed In Punch Alert</h3>
                #     <p>Dear %s,</p>
                #     <h4>Info:</h4>
                #     <p>This is the reminder for Missed In Punch for today %s</p>
                #     """ % (frappe.get_value("Employee",emp.name,"employee_name"),formatdate(day))
                #     )    
                att = frappe.db.exists("Attendance",{"employee":emp.name,"attendance_date":day})
                if not att:
                    attendance = frappe.new_doc("Attendance")
                    attendance.update({
                        "employee": emp.name,
                        "attendance_date": day,
                        "status": 'Absent',
                        "late_in" : "0:00:00",
                        "early_out" : "0:00:00",
                        "working_shift" : frappe.get_value("Employee",emp.name,"working_shift"),
                        "work_time": "0:00:00",
                        "overtime":"0:00:00"
                    })
                    attendance.save(ignore_permissions=True)
                    attendance.submit()
                    frappe.db.commit() 

@frappe.whitelist()
def out_punch_alert():
    day =  today()
    exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
    employees_list = []
    for e in exc:
        employees_list.append(e.employee)
    employees = frappe.get_all('Employee',{'status':'Active'})
    for emp in employees:
        if emp.name not in employees_list:
            att_record = frappe.db.sql("""select name from `tabAttendance`
            where employee = %s and in_time > '0' and out_time is null and attendance_date = %s
            and docstatus = 1""", (emp.name, day), as_dict=True)
            # if att_record:
            #     frappe.sendmail(
            #         recipients=['sivaranjani.s@voltechgroup.com'],
            #         subject='Missed Out Punch Alert for %s' +
            #         formatdate(today()),
            #         message=""" 
            #         <h3>Missed Out Punch Alert</h3>
            #         <p>Dear %s,</p>
            #         <h4>Info:</h4>
            #         <p>This is the reminder for Missed Out Punch for today %s</p>
            #         """ % (frappe.get_value("Employee",emp.name,"employee_name"),formatdate(day))
            #         )     

@frappe.whitelist()
def continuous_absentees():
    # day =  today()
    exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
    employees_list = []
    for e in exc:
        employees_list.append(e.employee)
    query = """select name,employee,attendance_date from `tabAttendance` where \
    status='Absent' and attendance_date between '%s' and '%s' """ % (add_days(today(),-3),today())
    employees = frappe.db.sql(query,as_dict=True) 
    for emp in employees:
        if emp.employee not in employees_list:
            print(emp)


def validate_if_attendance_not_applicable(employee, attendance_date):
    # Check if attendance is Present
    att_record = frappe.db.sql("""select name from `tabAttendance`
            where employee = %s and in_time > '0' and attendance_date = %s
            and docstatus = 1""", (employee, attendance_date), as_dict=True)
    if att_record:
        return "att",True        
    # Check if attendance_date is a Holiday
    if is_holiday(employee, attendance_date):
        return "holiday",True
    # Check if employee on Leave
    leave_record = frappe.db.sql("""select half_day from `tabLeave Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1""", (employee, attendance_date), as_dict=True)
    if leave_record:
        return "leave",True
    # Check if employee on On-Duty
    od_record = frappe.db.sql("""select half_day from `tabOn Duty Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1""", (employee, attendance_date), as_dict=True)
    if od_record:
        return "od",True    
    # Check if employee on On-Travel
    tm_record = frappe.db.sql("""select half_day from `tabTravel Management`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1""", (employee, attendance_date), as_dict=True)
    if tm_record:
        return "tm",True     

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


def calculate_comp_off():
    # day = add_days(today(),-1)
    # from_date = (datetime.strptime('2018-12-25', '%Y-%m-%d')).date()
    # to_date = (datetime.strptime('2019-01-24', '%Y-%m-%d')).date()
    # for preday in daterange(from_date,to_date):
    #     for emp in frappe.get_all("Employee",{"status":"Active","coff_eligible":1}):
    #         if is_holiday(emp, preday):
    #             coff_hours = frappe.get_value("Attendance",{"attendance_date":preday,"employee":emp.name},["work_time"])
    #             if coff_hours:
    #                 coff_id = frappe.db.exists("Comp Off Balance",{"employee":emp.name,"comp_off_date":preday})
    #                 if coff_id:
    #                     coff = frappe.get_doc("Comp Off Balance",coff_id)
    #                 else:    
    #                     coff = frappe.new_doc("Comp Off Balance")
    #                 coff.update({
    #                     "employee":emp.name,
    #                     "hours":coff_hours,
    #                     "comp_off_date":preday,
    #                     "validity":add_months(preday,3)
    #                 })
    #                 coff.save(ignore_permissions=True)
    #                 frappe.db.commit()
    from_date = (datetime.strptime('2019-10-25', '%Y-%m-%d')).date()
    to_date = (datetime.strptime('2019-12-24', '%Y-%m-%d')).date()
    for preday in daterange(from_date,to_date):
        employee = frappe.db.sql("""select name,employee_name,department,designation,category from `tabEmployee`
                            where status ="Active" and coff_eligible=1 """, as_dict=True)
        for emp in employee:
            #C-off for Holiday Work
            if is_holiday(emp, preday):
                ot = frappe.get_value("Attendance",{"attendance_date":preday,"employee":emp.name},["work_time"])
                if ot > (timedelta(hours = 3)):
                    calculate_ot(emp.name,preday,ot)
            #C-Off for OT
            ews = frappe.db.get_value("Employee", emp.name, ["working_shift"])
            assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                                where employee = %s and %s between from_date and to_date""", (emp.name, preday), as_dict=True)
            if assigned_shift:
                ews = assigned_shift[0]['shift']
            ws = frappe.get_doc("Working Shift", ews)  
            if not ws.name == 'FS4':
                actual_in_time = ws.out_time
                actual_out_time = ws.in_time
                actual_work_hours = ws.out_time - ws.in_time
                if frappe.db.exists("Attendance", {"employee":emp.name,"attendance_date": preday}):
                    attendance = frappe.get_doc("Attendance", {"employee":emp.name,"attendance_date": preday})
                    if attendance.work_time > actual_work_hours:
                        ot = attendance.work_time - actual_work_hours
                        print(emp.name,preday,ot)
                        if emp.category == "Management Staff":
                            if ot > (timedelta(hours = 3)):
                                calculate_ot(emp.name,preday,ot)
                        else:
                            if ot > (timedelta(hours = 2)):
                                calculate_ot(emp.name,preday,ot)

def update_comp_off(doc,method):
    emp = doc.employee
    preday = doc.comp_off_date
    ot = doc.hours.split(":")
    ot = timedelta(hours =cint(ot[0]),minutes=cint(ot[1]))
    calculate_ot(emp,preday,ot)

def calculate_ot(emp,preday,ot):
    pre = []
    ot_time = []
    pre.append(preday)
    ot_time.append(ot)
    child = []
    emp = frappe.get_doc("Employee",emp)     
    coff_id = frappe.db.exists("Comp Off Details",{"employee":emp.name})
    if coff_id:
        coff = frappe.get_doc("Comp Off Details",coff_id)
        child = coff.comp_off_calculation_details
        comp_off_child_date = []
        comp_off_child_time = []
        for c in child:
            cdate = (c.comp_off_date).strftime('%Y-%m-%d')
            ctime = c.hours
            comp_off_child_date.append(cdate)
            comp_off_child_time.append(ctime)
        date_result = (set(comp_off_child_date) & set(pre))
        time_result = (set(comp_off_child_time) & set(ot_time))
        if (not date_result and not time_result) or (date_result and not time_result):
            child_row = coff.append("comp_off_calculation_details",{
                "comp_off_date": preday,
                "hours": ot,
                "validity": add_months(preday,3)
            }) 
    else:    
        coff = frappe.new_doc("Comp Off Details")
        coff.update({
            "employee":emp.name,
            "employee_name":emp.employee_name,
            "department":emp.department,
            "designation":emp.designation
        })
        child_row = coff.append("comp_off_calculation_details",{
            "comp_off_date": preday,
            "hours": ot,
            "validity": add_months(preday,3)
        })
        child = coff.comp_off_calculation_details
    t = timedelta(minutes = 0)
    for c in child:
        t = t + c.hours                       
    t1 = t.total_seconds()  
    minutes = t1 // 60
    hours = minutes // 60
    t3 =  "%02d:%02d:%02d" % (hours, minutes % 60, t1 % 60)
    coff.update({
        "total_hours": t3
    })
    coff.save(ignore_permissions=True)
    frappe.db.commit()

@frappe.whitelist()
def get_coff(employee):
    t_hours = 0
    if frappe.db.exists("Comp Off Details",{"employee":employee}):
        coff_hours = frappe.get_value("Comp Off Details",{"employee":employee},["total_hours"])
        frappe.errprint(coff_hours)
        # minutes = (coff_hours%3600) // 60
        return coff_hours
    else:
        return "No Data"
@frappe.whitelist()
def att_permission(employee):
    if frappe.db.exists("Attendance",{"employee":employee}):
        # att = frappe.get_value("Attendance",{"employee":emttendance_date'])
        frappe.errprint(att)

@frappe.whitelist()
def att_adjust(employee,attendance_date,name,in_time,out_time,status_p,status_a,status_ph,status_wo,status_first_half_present,status_second_half_present,status_first_half_absent,status_second_half_absent):
    if name:
        itime = otime = ""
        att = frappe.get_doc("Attendance",name)
        fdate = datetime.strptime(attendance_date,'%Y-%m-%d').strftime('%d/%m/%Y')
        if in_time:
            itime = fdate + ' '+ in_time
        if out_time:    
            otime = fdate + ' '+ out_time
        if att and status_p == "1":
            att.update({
                "status":"Present",
                "admin_approved_status": "Present",
                "in_time": itime,
                "out_time": otime
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
        elif att and status_a == "1":
            att.update({
                "status":"Absent",
                "admin_approved_status": "Absent",
                "in_time": itime,
                "out_time": otime
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
        elif att and status_ph == "1":
            att.update({
                "status":"Absent",
                "admin_approved_status": "PH",
                "in_time": itime,
                "out_time": otime
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
        elif att and status_wo == "1":
            att.update({
                "status":"Absent",
                "admin_approved_status": "WO",
                "in_time": itime,
                "out_time": otime
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
        elif att and status_first_half_present == "1":
            if att.status == 'Present':
                att.update({
                    "status":"Present",
                    "first_half_status":"PR",
                    "admin_approved_status": "First Half Present",
                    "in_time": itime,
                    "out_time": otime
                }) 
            if att.status == 'Half Day':
                admin_approved_status = "First Half Present"
                aas = frappe.get_value("Attendance",{"employee":employee,"attendance_date":attendance_date},"admin_approved_status")
                if aas == 'Second Half Present':
                    admin_approved_status = 'Present'

                sh_status = get_sh(employee,attendance_date)
                if sh_status == 'PR':
                    status = 'Present'
                else:
                    status = 'Half Day'    
                att.update({
                    "status":status,
                    "first_half_status":"PR",
                    "second_half_status":sh_status,
                    "admin_approved_status": admin_approved_status,
                    "in_time": itime,
                    "out_time": otime
                }) 
            if att.status == 'Absent':
                att.update({
                    "status":"Half Day",
                    "first_half_status":"PR",
                    "admin_approved_status": "First Half Present",
                    "in_time": itime,
                    "out_time": otime
                })     
            att.save(ignore_permissions=True)
            frappe.db.commit()       
        elif att and status_second_half_present == "1":
            if att.status == 'Present':
                att.update({
                    "second_half_status":"PR",
                    "admin_approved_status": "Second Half Present",
                    "in_time": itime,
                    "out_time": otime
                }) 
            if att.status == 'Half Day':
                admin_approved_status = "Second Half Present"
                aas = frappe.get_value("Attendance",{"employee":employee,"attendance_date":attendance_date},"admin_approved_status")
                if aas == 'First Half Present':
                    admin_approved_status = 'Present'
                fh_status = get_fh(employee,attendance_date)
                if fh_status == 'PR':
                    status = 'Present'
                else:
                    status = 'Half Day' 
                att.update({
                    "status":status,
                    "first_half_status":fh_status,
                    "second_half_status":"PR",
                    "admin_approved_status": admin_approved_status,
                    "in_time": itime,
                    "out_time": otime
                }) 
            if att.status == 'Absent':
                att.update({
                    "status":"Half Day",
                    "second_half_status":"PR",
                    "admin_approved_status": "Second Half Present",
                    "in_time": itime,
                    "out_time": otime
                })
            att.save(ignore_permissions=True)
            frappe.db.commit() 
        elif att and status_first_half_absent == "1":
            if att.status == 'Present':
                att.update({
                    "status":"Half Day",
                    "first_half_status":"AB",
                    "admin_approved_status": "First Half Absent",
                    "in_time": itime,
                    "out_time": otime
                }) 
            if att.status == 'Half Day':
                att.update({
                    "first_half_status":"AB",
                    "admin_approved_status": "First Half Absent",
                    "in_time": itime,
                    "out_time": otime
                }) 
            if att.status == 'Absent':
                att.update({
                    "first_half_status":"AB",
                    "admin_approved_status": "First Half Absent",
                    "in_time": itime,
                    "out_time": otime
                })     
            att.save(ignore_permissions=True)
            frappe.db.commit()     
        elif att and status_second_half_absent == "1":
            if att.status == 'Present':
                att.update({
                    "status":"Half Day",
                    "second_half_status":"AB",
                    "admin_approved_status": "Second Half Absent",
                    "in_time": itime,
                    "out_time": otime
                }) 
            if att.status == 'Half Day':
                att.update({
                    "second_half_status":"AB",
                    "admin_approved_status": "Second Half Absent",
                    "in_time": itime,
                    "out_time": otime
                }) 
            if att.status == 'Absent':
                att.update({
                    "second_half_status":"AB",
                    "admin_approved_status": "Second Half Absent",
                    "in_time": itime,
                    "out_time": otime
                })     
            att.save(ignore_permissions=True)
            frappe.db.commit()            
        elif att and in_time or out_time:
            att.update({
                "admin_approved_status": "Present",
                "in_time": itime,
                "out_time": otime
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
    return True

@frappe.whitelist()
def get_sh(employee,attendance_date):
    shs = frappe.get_value("Attendance",{"employee":employee,"attendance_date":attendance_date},"second_half_status")
    out_time = frappe.db.get_value("Attendance", {"employee": employee, "attendance_date": attendance_date},["out_time"])
    dt = datetime.strptime(out_time, "%d/%m/%Y %H:%M:%S")
    emp_out_time = dt.time()
    emp_out_time = timedelta(hours=emp_out_time.hour,minutes=emp_out_time.minute,seconds=emp_out_time.second)
    working_shift = frappe.db.get_value("Employee", {'employee':employee},['working_shift']) 
    assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                where employee = %s and %s between from_date and to_date""", (employee, attendance_date), as_dict=True)
    if assigned_shift:
        working_shift = assigned_shift[0]['shift']
    shift_out_time = frappe.db.get_value("Working Shift",working_shift,"out_time") + frappe.db.get_value("Working Shift",working_shift,"grace_out_time")
    if emp_out_time >= shift_out_time:
        shs = 'PR'
    return shs    

def get_fh(employee,attendance_date):
    fhs = frappe.get_value("Attendance",{"employee":employee,"attendance_date":attendance_date},"first_half_status")
    in_time = frappe.db.get_value("Attendance", {"employee": employee, "attendance_date": attendance_date},["in_time"])
    dt = datetime.strptime(in_time, "%d/%m/%Y %H:%M:%S")
    emp_in_time = dt.time()
    emp_in_time = timedelta(hours=emp_in_time.hour,minutes=emp_in_time.minute,seconds=emp_in_time.second)
    working_shift = frappe.db.get_value("Employee", {'employee':employee},['working_shift']) 
    assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                where employee = %s and %s between from_date and to_date""", (employee, attendance_date), as_dict=True)
    if assigned_shift:
        working_shift = assigned_shift[0]['shift']
    shift_in_time = frappe.db.get_value("Working Shift",working_shift,"in_time") + frappe.db.get_value("Working Shift",working_shift,"grace_in_time")
    if emp_in_time <= shift_in_time:
        fhs = 'PR'
    return fhs     

@frappe.whitelist()
def updated_att_adjust():
    attendance = frappe.db.sql("""select name from `tabAttendance` where docstatus =1 and attendance_date between '2019-03-25' and '2019-04-24'  """, as_dict = 1)
    for a in attendance:
        att = frappe.get_doc("Attendance",a.name)
        admin_approved_status = att.admin_approved_status
        print(att)
        if att and admin_approved_status == "Present":
            att.update({
                "status":"Present",
                "first_half_status":"PR",
                "second_half_status":"PR",
                "admin_approved_status": "Present",
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
        elif att and admin_approved_status == "Absent":
            att.update({
                "status":"Absent",
                "first_half_status":"AB",
                "second_half_status":"AB",
                "admin_approved_status": "Absent",
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
        elif att and admin_approved_status == "PH":
            att.update({
                "status":"Absent",
                "admin_approved_status": "PH",
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
        elif att and admin_approved_status == "WO":
            att.update({
                "status":"Absent",
                "admin_approved_status": "WO"
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
        elif att and admin_approved_status == "First Half Present":
            if att.status == 'Present':
                att.update({
                    "status":"Present",
                    "first_half_status":"PR",
                    "admin_approved_status": "First Half Present"
                }) 
            if att.status == 'Half Day' and admin_approved_status == "First Half Present":
                att.update({
                    # "status":"Present",
                    "first_half_status":"PR",
                    "admin_approved_status": "First Half Present"
                }) 
            if att.status == 'Absent' and admin_approved_status == "First Half Present":
                att.update({
                    "status":"Half Day",
                    "first_half_status":"PR",
                    "admin_approved_status": "First Half Present"
                })     
            att.save(ignore_permissions=True)
            frappe.db.commit()       
        elif att and admin_approved_status == "Second Half Present":
            if att.status == 'Present':
                att.update({
                    "second_half_status":"PR",
                    "admin_approved_status": "Second Half Present"
                }) 
            if att.status == 'Half Day' and admin_approved_status == "Second Half Present":
                att.update({
                    "second_half_status":"PR",
                    "admin_approved_status": "Second Half Present"
                }) 
            if att.status == 'Absent' and admin_approved_status == "Second Half Present":
                att.update({
                    "status":"Half Day",
                    "second_half_status":"PR",
                    "admin_approved_status": "Second Half Present"
                })
            att.save(ignore_permissions=True)
            frappe.db.commit() 
        elif att and admin_approved_status == "First Half Absent":
            if att.status == 'Present' and admin_approved_status == "First Half Absent":
                att.update({
                    "status":'Half Day',
                    "first_half_status":"AB",
                    "admin_approved_status": "First Half Absent"
                }) 
            if att.status == 'Half Day' and admin_approved_status == "First Half Absent":
                att.update({
                    "first_half_status":"AB",
                    "admin_approved_status": "First Half Absent"
                }) 
            if att.status == 'Absent' and admin_approved_status == "First Half Absent":
                att.update({
                    "first_half_status":"AB",
                    "admin_approved_status": "First Half Absent",
                })     
            att.save(ignore_permissions=True)
            frappe.db.commit()     
        elif att and admin_approved_status == "Second Half Absent":
            if att.status == 'Present' and admin_approved_status == "Second Half Absent":
                att.update({
                    "status":'Half Day',
                    "second_half_status":"AB",
                    "admin_approved_status": "Second Half Absent",
                }) 
            if att.status == 'Half Day' and admin_approved_status == "Second Half Absent":
                att.update({
                    "second_half_status":"AB",
                    "admin_approved_status": "Second Half Absent",
                }) 
            if att.status == 'Absent' and admin_approved_status == "Second Half Absent":
                att.update({
                    "second_half_status":"AB",
                    "admin_approved_status": "Second Half Absent",
                })     
            att.save(ignore_permissions=True)
            frappe.db.commit()                             


@frappe.whitelist()
def bulk_att_adjust(from_date,to_date,status,location=None,employee=None):
    if location:
        att = frappe.db.sql("""
        select `tabAttendance`.name from `tabAttendance` 
        join `tabEmployee` on `tabEmployee`.name = `tabAttendance`.employee 
        where 
        `tabEmployee`.location_name = %s
        and `tabAttendance`.attendance_date between %s and %s""", (location,from_date, to_date), as_dict=1)
        for a in att:
            if a:
                att = frappe.get_doc("Attendance",a)
                if att:
                    att.update({
                        "admin_approved_status": status
                    })
                    frappe.errprint(att.admin_approved_status)
                    att.save(ignore_permissions=True)
                    frappe.db.commit()
        return True
    if employee:
        att = frappe.db.sql("""select name from `tabAttendance`
                where employee=%s
                and attendance_date between %s and %s""", (employee,from_date, to_date), as_dict=1)
        for a in att:
            if a:
                att = frappe.get_doc("Attendance",a)
                if att:
                    att.update({
                        "admin_approved_status": status
                    })
                    frappe.errprint(att.admin_approved_status)
                    att.save(ignore_permissions=True)
                    frappe.db.commit()
        return True    

# @frappe.whitelist()
# def bulk_admin_att():
#     attendance = frappe.get_all("Attendance",{"admin_approved_status":("not like","")},['admin_approved_status'])
#     for att in attendance:
#         att1 = frappe.get_doc("Attendance",att)
#         att1.update({
#             "status":att['admin_approved_status']
#         })
#         att1.db_update()
#         frappe.db.commit()



@frappe.whitelist()
def fetch_att_temp():
    from_date = (datetime.strptime('2019-05-07', '%Y-%m-%d')).date()
    to_date = (datetime.strptime('2019-05-24', '%Y-%m-%d')).date()
    emp = '1321'
    emp = frappe.get_doc('Employee',emp)
    for preday in daterange(from_date,to_date):
        day = preday.strftime("%d%m%Y")
        exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
        auto_present_list = []
        for e in exc:
            auto_present_list.append(e.employee)
        # employees = frappe.get_all('Employee',{'status':'Active','date_of_joining':('<=',preday)})
        # for emp in employees:
        working_shift = frappe.db.get_value("Employee", {'employee':emp.name},['working_shift']) 
        assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                    where employee = %s and %s between from_date and to_date""", (emp.name, preday), as_dict=True)
        if assigned_shift:
            working_shift = assigned_shift[0]['shift']
        if emp.name in auto_present_list:
            doc = frappe.get_doc("Employee",emp.name)
            attendance = frappe.db.exists("Attendance", {"employee": doc.employee, "attendance_date": preday})
            if attendance:
                frappe.db.set_value("Attendance",attendance,"status","Present")
                frappe.db.commit()
            else:
                attendance = frappe.new_doc("Attendance")
                attendance.employee = doc.employee
                attendance.employee_name = doc.employee_name
                attendance.status = "Present"
                attendance.attendance_date = preday
                # attendance.company = doc.company
                attendance.working_shift = working_shift,
                attendance.late_in = "00:00:00"
                attendance.work_time = "00:00:00"
                attendance.early_out = "00:00:00"
                attendance.overtime = "00:00:00"
                attendance.save(ignore_permissions=True)
                attendance.submit()
                frappe.db.commit()
        else:            
            url = 'http://182.72.89.102/cosec/api.svc/v2/attendance-daily?action=get;field-name=userid,ProcessDate,firsthalf,\
                                secondhalf,punch1,punch2,workingshift,shiftstart,shiftend,latein,earlyout,worktime,overtime;date-range=%s-%s;range=user;id=%s;format=xml' % (day,day,emp.name) 
            r = requests.get(url, auth=('sa', 'matrixx'))
            if "No records found" in r.content:
                attendance_id = frappe.db.exists("Attendance", {
                        "employee": emp.name, "attendance_date": preday,"docstatus":1})
                if attendance_id:
                    pass
                else:            
                    attendance = frappe.new_doc("Attendance")
                    attendance.update({
                        "employee": emp.name,
                        "attendance_date": preday,
                        "status": 'Absent',
                        "late_in" : "0:00:00",
                        "early_out" : "0:00:00",
                        "working_shift" : frappe.get_value("Employee",emp.name,"working_shift"),
                        "work_time": "0:00:00",
                        "overtime":"0:00:00"
                    })
                    attendance.save(ignore_permissions=True)
                    attendance.submit()
                    frappe.db.commit() 
            else: 
                if not "failed: 0010102003" in r.content:
                    root = ET.fromstring(r.content)
                    for att in root.findall('attendance-daily'):
                        userid = att.find('UserID').text
                        in_time = att.find('Punch1').text
                        out_time = att.find('Punch2').text
                        first_half_status = att.find('firsthalf').text
                        second_half_status = att.find('secondhalf').text
                        date = datetime.strptime((att.find('ProcessDate').text.replace("/","")), "%d%m%Y").date()
                        date_f = date.strftime("%Y-%m-%d")
                        # print userid,date_f
                        work_time = timedelta(minutes=flt(att.find('WorkTime').text))
                        over_time = timedelta(minutes=flt(att.find('Overtime').text))
                        late_in = timedelta(minutes=flt(att.find('LateIn').text))
                        early_out = timedelta(minutes=flt(att.find('EarlyOut').text))
                        working_shift = att.find('WorkingShift').text
                        attendance_id = frappe.db.exists("Attendance", {
                            "employee": emp.name, "attendance_date": date_f,"docstatus":1})
                        if out_time:
                            out_time_f = datetime.strptime(out_time, "%d/%m/%Y %H:%M:%S")
                        if in_time:    
                            in_time_f = datetime.strptime(in_time, "%d/%m/%Y %H:%M:%S")
                        if in_time and out_time:
                            work_time = out_time_f - in_time_f    
                        if work_time >= timedelta(hours=4) :
                            if work_time < timedelta(hours=7,minutes=45):
                                status = 'Half Day'
                            else:    
                                status = 'Present'
                        else:
                            status = 'Absent'   
                        if attendance_id:
                            attendance = frappe.get_doc(
                                "Attendance", attendance_id)
                            attendance.out_time = out_time
                            attendance.in_time = in_time
                            attendance.status = status
                            attendance.first_half_status = first_half_status
                            attendance.second_half_status = second_half_status
                            attendance.late_in = late_in
                            attendance.early_out = early_out
                            attendance.working_shift = working_shift
                            attendance.work_time = work_time
                            attendance.overtime = over_time
                            attendance.db_update()
                            frappe.db.commit()
                        else:
                            attendance = frappe.new_doc("Attendance")
                            attendance.update({
                                "employee": emp.name,
                                "attendance_date": date_f,
                                "status": status,
                                "in_time": in_time,
                                "late_in" : late_in,
                                "early_out" : early_out,
                                "working_shift" : working_shift,
                                "out_time": out_time,
                                "work_time": work_time,
                                "overtime":over_time
                            })
                            attendance.save(ignore_permissions=True)
                            attendance.submit()
                            frappe.db.commit()
                 

@frappe.whitelist()
def shift_assignment(employee,attendance_date,shift):
    if employee:
        shift_assignment = frappe.db.exists("Shift Assignment", {"employee": employee})
        shift = shift.split("(")
        shift = shift[0]
        if shift_assignment:
            sa = frappe.db.sql("""select name from `tabShift Assignment`
                        where employee = %s and %s between from_date and to_date""", (employee, attendance_date), as_dict=True)
            if sa:
                for s in sa:
                    doc = frappe.get_doc("Shift Assignment",s)
                    doc.update({
                        "shift":shift
                    })
                    doc.save(ignore_permissions=True)
                    frappe.db.commit()
            else:       
                doc = frappe.get_doc("Employee",employee)     
                sa = frappe.new_doc("Shift Assignment")
                sa.update({
                    "employee": employee,
                    "employee_name": doc.employee_name,
                    "business_unit": doc.business_unit,
                    "location": doc.location_name,
                    "department": doc.department,
                    "category": doc.category,
                    "from_date":attendance_date,
                    "to_date":attendance_date,
                    "shift":shift
                })
                sa.save(ignore_permissions=True)
                frappe.db.commit()
        else:       
                doc = frappe.get_doc("Employee",employee)     
                sa = frappe.new_doc("Shift Assignment")
                sa.update({
                    "employee": employee,
                    "employee_name": doc.employee_name,
                    "business_unit": doc.business_unit,
                    "location": doc.location_name,
                    "department": doc.department,
                    "category": doc.category,
                    "from_date":attendance_date,
                    "to_date":attendance_date,
                    "shift":shift
                })
                sa.save(ignore_permissions=True)
                frappe.db.commit()
        # update_att_from_shift(employee,attendance_date,shift)
        if frappe.db.exists("Attendance", {
                            "employee": employee, "attendance_date": attendance_date,"docstatus":1}): 
            attendance_id = frappe.db.exists("Attendance", {
                        "employee": employee, "attendance_date": attendance_date,"docstatus":1})    
            if attendance_id:
                attendance = frappe.get_doc(
                    "Attendance", attendance_id)
                shift_in_time = frappe.db.get_value("Working Shift",shift,"in_time")
                shift_out_time = frappe.db.get_value("Working Shift",shift,"out_time")  
                grace_in_time = frappe.db.get_value("Working Shift",shift,"grace_in_time")   
                grace_out_time = frappe.db.get_value("Working Shift",shift,"grace_out_time")
                work_time = over_time = late_in = early_out = "0:00:00"
                shift_in_time += grace_in_time
                shift_out_time -= grace_out_time
                first_half_status = second_half_status  = ""
                status = attendance.status 
                if attendance.in_time:
                    in_time = attendance.in_time
                    dt = datetime.strptime(in_time, "%d/%m/%Y %H:%M:%S")
                    from_time = dt.time()                          
                    emp_in_time = timedelta(hours=from_time.hour,minutes=from_time.minute,seconds=from_time.second)
                    #Check Movement Register
                    if get_mr_in1(employee,attendance_date):
                        mr_status_in = True
                        emp_in_time = emp_in_time - get_mr_in1(employee,attendance_date)
                    if emp_in_time > shift_in_time:
                        first_half_status = 'AB'
                        if second_half_status == "AB":
                            status = "Absent"
                        elif second_half_status == "PR":                   
                            status = "Half Day"
                        late_in = (emp_in_time - shift_in_time) + grace_in_time
                    else:
                        first_half_status = 'PR'
                        if second_half_status == "AB":
                            status = "Half Day"
                        elif second_half_status == "PR":                   
                            status = "Present"
                        late_in = timedelta(seconds=0)

                if attendance.out_time:
                    if attendance.in_time:
                        out_time = attendance.out_time
                        dt = datetime.strptime(out_time, "%d/%m/%Y %H:%M:%S")
                        end_time = dt.time()
                        emp_out_time = timedelta(hours=end_time.hour,minutes=end_time.minute,seconds=end_time.second)
                        #Check Movement Register
                        if get_mr_out1(employee,attendance_date):
                            mr_status_out = True
                            emp_out_time = emp_out_time + get_mr_out1(employee,attendance_date)
                        if emp_out_time < shift_out_time:
                            second_half_status = 'AB'
                            if first_half_status == "AB":
                                status = "Absent"
                            elif first_half_status == "PR":
                                status = "Half Day"
                            early_out = (shift_out_time - emp_out_time) - grace_out_time
                        else:
                            second_half_status = 'PR'
                            if first_half_status == "AB":
                                status = "Half Day"
                            elif first_half_status == "PR":
                                status = "Present"
                            early_out = timedelta(seconds=0)  
                if attendance.in_time and attendance.out_time:
                    in_time = attendance.in_time
                    out_time = attendance.out_time
                    out_time_f = datetime.strptime(out_time, "%d/%m/%Y %H:%M:%S")
                    in_time_f = datetime.strptime(in_time, "%d/%m/%Y %H:%M:%S")
                    work_time = (out_time_f - in_time_f).total_seconds() // 60
                    
                    if work_time < 1440:
                        work_time = timedelta(minutes=flt(work_time))
                    else:
                        work_time = timedelta(minutes=flt('1400')) 
                    if emp_out_time > shift_out_time:
                        over_time = (emp_out_time  - shift_out_time).total_seconds() // 60
                        if over_time < 1440:
                            over_time = timedelta(minutes=flt(over_time))
                        else:
                            over_time = timedelta(minutes=flt('1400'))                 
                attendance.update({
                    "status": status,
                    "late_in" : late_in,
                    "early_out" : early_out,
                    "working_shift" : shift,
                    "work_time": work_time,
                    "overtime":over_time,
                    "first_half_status": first_half_status,
                    "second_half_status":second_half_status
                })
                frappe.errprint(status)
                attendance.db_update()
                frappe.db.commit()      
    return "OK" 


def get_mr_out1(emp,day):
    from_time = to_time = 0
    day = (datetime.strptime(str(day), '%Y-%m-%d')).date()
    dt = datetime.combine(day, datetime.min.time())
    mrs = frappe.db.sql("""select from_time,to_time from `tabMovement Register` where employee= '%s' and docstatus=1 and status='Approved' and from_time between '%s' and '%s' """ % (emp,dt,add_days(dt,1)),as_dict=True)
    for mr in mrs:
        from_time = mr.from_time
        to_time = mr.to_time
    out_time = frappe.get_value("Attendance",{"employee":emp,"attendance_date":day},["out_time"])  
    if out_time:
        att_out_time = datetime.strptime(out_time,'%d/%m/%Y %H:%M:%S')
        if from_time:
            if att_out_time >= (from_time + timedelta(minutes=-10)) :
                return to_time - from_time

def get_mr_in1(emp,day):
    from_time = to_time = 0
    day = (datetime.strptime(str(day), '%Y-%m-%d')).date()
    dt = datetime.combine(day, datetime.min.time())
    mrs = frappe.db.sql("""select from_time,to_time from `tabMovement Register` where employee= '%s' and docstatus=1 and status='Approved' and from_time between '%s' and '%s' """ % (emp,dt,add_days(dt,1)),as_dict=True)
    for mr in mrs:
        from_time = mr.from_time
        to_time = mr.to_time
    in_time = frappe.get_value("Attendance",{"employee":emp,"attendance_date":day},["in_time"])
    if in_time:    
        att_in_time = datetime.strptime(in_time,'%d/%m/%Y %H:%M:%S')
        if from_time:
            if att_in_time >= (from_time + timedelta(minutes=-10)):
                return to_time - from_time




        
@frappe.whitelist()
def send_announcement(name):
    doc = frappe.get_doc('Employee', name)
    experience = doc.external_work_history
    edu = doc.education
    if doc.one_above_manager:
        report_manager_doc = frappe.get_doc('Employee', {"user_id": doc.one_above_manager})
    else:
        report_manager_doc = " "
    for i in range(1):
        content = """
        <h1><br></h1>
        <h1 align="center"><u><span style="font-size: 14px;">&nbsp;</span></u></h1>
        <h1 align="center"><br><u><span style="font-size: 14px;"></span></u></h1>
        <h1 align="center"><u><span style="font-size: 14px;">ORGANIZATIONAL ANNOUNCE</span></u><span style="font-size: 14px;">﻿</span><u><span style="font-size: 14px;">MENT</span></u><span style="font-size: 14px;"></span><span style="font-size: 14px;"></span></h1>
        <center><div><span style="font-size: 12px;">HDI/HR&amp;ADM/QA-150</span></div></center>
        <center><div><span style="font-size: 12px;">February 22,2019</span></div></center>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><span style="font-size: 14px;">I&nbsp; have great pleasure in Welcoming&nbsp;<b> %s . %s</b>, who has joined in our organization on <b>%s</b> as <b>%s</b> based out of <b>%s</b>.</span></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><span style="font-size: 14px;">Before joinnig HDI, he was working as<b> %s </b>with<b> %s</b>.&nbsp; <b>%s</b> has completed&nbsp;<b> %s</b> and he shall Report to <b>%s . %s, %s.</b></span></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><span style="font-size: 14px;"><br></span></div>
        <div align="left"><span style="font-size: 14px;">Email </span><a><span style="font-size: 14px;">ID:<u>%s</u></span></a></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><span style="font-size: 14px;">I extend him warm welcome to our Hunter Douglas India Family and sure that all of you will add on the same.</span></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><b><span style="font-size: 14px;">Best Wishes,</span></b></div>
        <div align="left"><b><span style="font-size: 12px;"><br></span></b></div>
        <div align="left"><b><span style="font-size: 12px;"><br></span></b></div>
        <div align="left"><b><span style="font-size: 12px;"><br></span></b></div>
        <div align="left"><b><span style="font-size: 14px;">(S.Raghavan)</span></b></div>
        <div align="left"><b><span style="font-size: 12px;"><span style="font-size: 14px;"> Financial Controller</span><br></span></b></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        </center><center><div><br></div>
        <div><br></div>
        </center> 
        """ %(doc.salutation,doc.employee_name,doc.date_of_joining,doc.designation,doc.location_name,experience[0].designation,
        experience[0].company_name,doc.employee_name,edu[0].qualification,report_manager_doc.salutation,report_manager_doc.employee_name,report_manager_doc.designation,doc.user_id)
        frappe.sendmail(
            recipients=['ramya.a@voltechgroup.com'],
            subject='Announcement For All',
            message=""" %s""" % (content))
    # return content






# @frappe.whitelist()
# def submit_leave_application():
#     leave = frappe.get_all("Leave Application",{"docstatus":0, "status": "Approved"},['name'])
#     for l in leave:
#         doc = frappe.get_doc("Leave Application",l)
#         frappe.errprint(doc.status)
        # doc.save(ignore_permissions=True)
        # doc.submit()

# def get_mr_in(doc,method):
#     from_time = to_time = 0
#     dt = datetime.combine(day, datetime.min.time())
#     mrs = frappe.db.sql("""select from_time,to_time from `tabMovement Register` where employee= '%s' and docstatus=1 and status='Approved' and from_time between '%s' and '%s' """ % (emp,dt,add_days(dt,1)),as_dict=True)
#     for mr in mrs:
#         from_time = mr.from_time
#         to_time = mr.to_time
#     in_time = frappe.get_value("Attendance",{"employee":emp,"attendance_date":day},["in_time"])
#     if in_time:    
#         att_in_time = datetime.strptime(in_time,'%d/%m/%Y %H:%M:%S')
#         if from_time:
#             if att_in_time >= (from_time + timedelta(minutes=-10)):
#                 return to_time - from_time


@frappe.whitelist()
def check_attendance_status(employee,from_date,to_date):
    query = """select name,employee,attendance_date,status from `tabAttendance` where employee=%s and attendance_date between '%s' and '%s' """ % (employee,from_date,to_date)
    attendance = frappe.db.sql(query,as_dict=True)
    for a in attendance:
        doc = frappe.get_doc("Attendance",a.name)
        doc.update({
            "status": "Absent"
        })
        doc.save(ignore_permissions=True)
        doc.submit()
        frappe.db.commit()
        frappe.errprint(doc.status)
        return "Ok"

@frappe.whitelist()
def update_ecode():
    pmm = frappe.get_all("Performance Management Reviewer",fields=['name','employee_code'])
    for pm in pmm:
        # print loop.index
        # print pm['name']
        frappe.db.set_value("Performance Management Reviewer",pm['name'],"employee_code1",pm['employee_code'])
        frappe.db.commit()









@frappe.whitelist()
def update_mis(employee,date_of_joining=None,gender=None,date_of_birth=None,department=None,salary_mode=None,bank_name=None,bank_ac_no=None,ifsc_code=None,working_shift=None,pan_number=None,
uan_number=None,cell_number=None,father_name=None,husband_wife_name=None,permanent_address_is=None,permanent_address=None,current_address_is=None,current_address=None):
    if employee:
        emp_doc = frappe.get_doc("Employee",employee)
        eiu = frappe.new_doc("Employee Info Update")
        eiu.update({
            "employee_code": employee,
            "employee_name":emp_doc.employee_name,
            "date_of_joining":date_of_joining,
            "gender":gender,
            "date_of_birth": date_of_birth,
            "department": department,
            "salary_mode": salary_mode,
            "bank_name": bank_name,
            "bank_ac_no": bank_ac_no,
            "ifsc_code": ifsc_code,
            "working_shift":working_shift,
            "pan_number": pan_number,
            "uan_number":uan_number,
            "cell_number":cell_number,
            "father_name":father_name,
            "husband_wife_name":husband_wife_name,
            "permanent_address_is":permanent_address_is,
            "permanent_address":permanent_address,
            "current_address_is":current_address_is,
            "current_address":current_address
        })
        eiu.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.sendmail(
            recipients=['hr.hdi@hunterdouglas.asia'],
            subject='RE:MIS Update',
            message=""" <h4>Request for MIS Update</h4>
                         <p>Employee %s Request to update data in MIS. Request file ID is %s.</p>
                         <p>You can Approve/Reject the Request by clicking the below Link </p>
                        <a href="{{ frappe.utils.get_url_to_form("Employee Info Update", %s ) }}">Open On Duty Application</a>
                         """%(employee,eiu.name,eiu.name)
        )
    return "Ok"


@frappe.whitelist()
def update_main_mis(name,employee,status):
    if status == "Approved":
        eiu = frappe.get_doc("Employee Info Update",name)
        emp_doc = frappe.get_doc("Employee",employee)
        if eiu.date_of_joining:
            date_of_joining = eiu.date_of_joining
        else:
            date_of_joining = emp_doc.date_of_joining
        if eiu.gender:
            gender = eiu.gender
        else:
            gender = emp_doc.gender
        if eiu.date_of_birth:
            date_of_birth = eiu.date_of_birth
        else:
            date_of_birth = emp_doc.date_of_birth
        if eiu.department:
            department = eiu.department
        else:
            department = emp_doc.department
        if eiu.salary_mode:
            salary_mode = eiu.salary_mode
        else:
            salary_mode = emp_doc.salary_mode
        if eiu.bank_name:
            bank_name = eiu.bank_name
        else:
            bank_name = emp_doc.bank_name
        if eiu.bank_ac_no:
            bank_ac_no = eiu.bank_ac_no
        else:
            bank_ac_no = emp_doc.bank_ac_no
        if eiu.ifsc_code:
            ifsc_code = eiu.ifsc_code
        else:
            ifsc_code = emp_doc.ifsc_code
        if eiu.working_shift:
            working_shift = eiu.working_shift
        else:
            working_shift = emp_doc.working_shift
        if eiu.pan_number:
            pan_number = eiu.pan_number
        else:
            pan_number = emp_doc.pan_number
        if eiu.uan_number:
            uan_number = eiu.uan_number
        else:
            uan_number = emp_doc.uan_number
        if eiu.cell_number:
            cell_number = eiu.cell_number
        else:
            cell_number = emp_doc.cell_number
        if eiu.father_name:
            father_name = eiu.father_name
        else:
            father_name = emp_doc.father_name
        if eiu.husband_wife_name:
            husband_wife_name = eiu.husband_wife_name
        else:
            husband_wife_name = emp_doc.husband_wife_name
        if eiu.permanent_address_is:
            permanent_address_is = eiu.permanent_address_is
        else:
            permanent_address_is = emp_doc.permanent_accommodation_type
        if eiu.permanent_address:
            permanent_address = eiu.permanent_address
        else:
            permanent_address = emp_doc.permanent_address
        if eiu.current_address_is:
            current_address_is = eiu.current_address_is
        else:
            current_address_is = emp_doc.current_accommodation_type
        if eiu.current_address:
            current_address = eiu.current_address
        else:
            current_address = emp_doc.current_address
        emp_doc.update({
            "date_of_joining":date_of_joining,
            "gender":gender,
            "date_of_birth": date_of_birth,
            "department": department,
            "salary_mode": salary_mode,
            "bank_name": bank_name,
            "bank_ac_no": bank_ac_no,
            "ifsc_code": ifsc_code,
            "working_shift":working_shift,
            "pan_number": pan_number,
            "uan_number":uan_number,
            "cell_number":cell_number,
            "father_name":father_name,
            "husband_wife_name":husband_wife_name,
            "permanent_address_is":permanent_address_is,
            "permanent_address":permanent_address,
            "current_address_is":current_address_is,
            "current_address":current_address
        })
        emp_doc.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.sendmail(
            recipients=[emp_doc.user_id],
            subject='RE:MIS Update',
            message=""" <h4>Replay for MIS Update</h4>
                         <p>Your MIS update request was Approved """
        )
    else:
        frappe.sendmail(
            recipients=[emp_doc.user_id],
            subject='RE:MIS Update',
            message=""" <h4>Replay for MIS Update</h4>
                         <p>Your MIS update request was Rejected """
        )
    return "Ok"


@frappe.whitelist(allow_guest=True)
def update_attendance_by_app(employee,from_date,to_date,from_date_session,to_date_session,m_status):
    query = """select name from `tabAttendance` where employee=%s and attendance_date between '%s' and '%s' """ % (employee,from_date,to_date)
    attendance = frappe.db.sql(query,as_dict=True)
    from_date = (datetime.strptime(str(from_date), '%Y-%m-%d')).date()
    to_date = (datetime.strptime(str(to_date), '%Y-%m-%d')).date()
    for a in attendance:
        doc = frappe.get_doc("Attendance",a.name)
        attendance_date = (datetime.strptime(str(doc.attendance_date), '%Y-%m-%d')).date()
        first_half_status = doc.first_half_status
        second_half_status = doc.second_half_status
        status = doc.status
        if from_date == to_date:
            if doc.attendance_date == from_date:
                if from_date_session == "First Half":
                    first_half_status = m_status,
                    if second_half_status == "AB":
                        status = "Half Day"
                    elif second_half_status == "PR":                   
                        status = "Present"
                elif from_date_session == "Second Half":
                    second_half_status = m_status
                    if first_half_status == "AB":
                        status = "Half Day"
                    elif first_half_status == "PR":
                        status = "Present"
                else:
                    first_half_status = second_half_status = m_status,
                    status = "Present"
        else:
            if doc.attendance_date == from_date:
                if from_date_session == "Second Half":
                    second_half_status = m_status
                    if first_half_status == "AB":
                        status = "Half Day"
                    elif first_half_status == "PR":
                        status = "Present"
                elif from_date_session == "Full Day":
                    first_half_status = second_half_status = m_status,
                    status = "Present"
            elif doc.attendance_date == to_date:
                if to_date_session == "First Half":
                    first_half_status = m_status,
                    if second_half_status == "AB":
                        status = "Half Day"
                    elif second_half_status == "PR":                   
                        status = "Present"
                elif to_date_session == "Full Day":
                    first_half_status = second_half_status = m_status,
                    status = "Present"
            else:
                first_half_status = second_half_status = m_status,
        doc.update({
            "first_half_status": first_half_status,
            "second_half_status": second_half_status,
            # "status": status
        })
        doc.save(ignore_permissions=True)
        doc.submit()
        frappe.db.commit()




@frappe.whitelist()
def update_mr_in_att(employee,from_time,to_time,total_permission_hour):
    mr_in_time = mr_out_time = ''
    frappe.errprint(employee)
    frappe.errprint(from_time)
    frappe.errprint(to_time)
    frappe.errprint(total_permission_hour)

    att_date = (datetime.strptime(str(from_time), '%Y-%m-%d %H:%M:%S')).date()
    att = frappe.get_doc("Attendance",{"employee": employee,"attendance_date": att_date})   
    mr_in = mr_out = ""
    if att:
        work_time = att.work_time
        frappe.errprint(work_time)
        # if att.first_half_status == "AB":
        mr_in = get_mr_in(employee,att_date)
        if mr_in:
            mr_in_time = mr_in
            work_time = mr_in + att.work_time  
        # if att.second_half_status == "AB":
        mr_out = get_mr_out(employee,att_date) 
        if mr_out:
            mr_out_time = mr_out
            work_time = mr_out + att.work_time        
        wt_seconds = work_time.total_seconds() // 60
        if wt_seconds > 1440:
            work_time = timedelta(minutes=flt('1400'))    
        if work_time >= timedelta(hours=4):
            if work_time < timedelta(hours=7,minutes=45):
                status = 'Half Day'
            else:    
                status = 'Present'
        else:
            status = 'Absent'
        att.status = status
        att.work_time = work_time
        att.mr_in_time = mr_in_time
        att.mr_out_time = mr_out_time
        att.db_update()
        frappe.db.commit()


def get_mr_out(emp,day):
    from_time = to_time = 0
    day = (datetime.strptime(str(day), '%Y-%m-%d')).date()
    dt = datetime.combine(day, datetime.min.time())
    mrs = frappe.db.sql("""select from_time,to_time from `tabMovement Register` where employee= '%s' and  from_time between '%s' and '%s' """ % (emp,dt,add_days(dt,1)),as_dict=True)
    for mr in mrs:   
        from_time = mr.from_time
        to_time = mr.to_time
        if from_time and to_time:
            return to_time - from_time


def get_mr_in(emp,day):
    from_time = to_time = 0
    day = (datetime.strptime(str(day), '%Y-%m-%d')).date()
    dt = datetime.combine(day, datetime.min.time())
    mrs = frappe.db.sql("""select from_time,to_time from `tabMovement Register` where employee= '%s' and docstatus=1 and status='Approved' and from_time between '%s' and '%s' """ % (emp,dt,add_days(dt,1)),as_dict=True)
    for mr in mrs:
        from_time = mr.from_time
        to_time = mr.to_time
        if from_time and to_time:
            return to_time - from_time


def update_designation():
    att = frappe.get_all("Attendance")
    for at in att:
        at_id = frappe.get_doc("Attendance",at) 
        des = frappe.get_value("Employee",at_id.employee,"designation")
        at_id.designation = des
        at_id.db_update()
        frappe.db.commit()
        # frappe.set_value('Attendance',at_id.name,"designation",des) 

def remove_att_for_left_emp():
    emp = frappe.get_all("Employee",{"status":'Left','employee':'1147'},['employee','relieving_date'])
    for e in emp:
        att = frappe.db.sql("""select name as name,employee as emp,attendance_date as att_date from `tabAttendance` where employee = %s and attendance_date > %s """,(e.employee,e.relieving_date),as_dict=True)
        for a in att:
            atid = frappe.get_doc("Attendance",a.name)
            atid.cancel()
            frappe.delete_doc('Attendance',atid.name)


def des_update_from_old():
    emp = frappe.get_all("Designation_new",{"parent":"1107"},['parent','effective_from','data_1'])
    for e in emp:
        att = frappe.db.sql("""select name as name,employee as emp,attendance_date as att_date,designation as des from `tabAttendance` where employee = %s and attendance_date <= %s """,(e.parent,e.effective_from),as_dict=True)
        for a in att:
            at_id = frappe.get_doc("Attendance",a.name) 
            at_id.designation = e.data_1
            at_id.db_update()
            frappe.db.commit()

def retirement_alert():
    year_start = (datetime.today()).date()
    year_end = add_months(year_start,12)
    print(year_start)
    employees = frappe.db.sql("""select name,employee_name,company_email,date_of_retirement FROM `tabEmployee` where date_of_retirement BETWEEN '%s' AND '%s' ANd status = "Active" """ %(year_start,year_end),as_dict=True)    
    for emp in employees:
        print(emp.company_email)
        frappe.sendmail(
            recipients= [ "%s" ] ,
            subject='Retirement Announcement' ,
            message="""<p>Dear %s,</p>
            <p> It saddens us to announce the retirement of %s. %s contributions will always be valued and remembered. %s hard work, commitment, and dedication are worthy of admiration. 
On behalf of every one, I would like to wish %s the best of luck. </p>""" % (emp.company_email,emp.employee_name,emp.employee_name,emp.employee_name,emp.employee_name))

@frappe.whitelist()
def get_six_month(date):
    ex_date = add_months(date,6)
    return ex_date


def create_hooks():
    job = frappe.db.exists('Scheduled Job Type', 'payroll_date_change_automatic')
    if not job:
        sjt = frappe.new_doc("Scheduled Job Type")  
        sjt.update({
            "method" : 'hrpro.custom.payroll_date_automatic',
            "frequency" : 'Cron',
            "cron_format" : '0 7 26 * *'
        })
        sjt.save(ignore_permissions=True)
        
@frappe.whitelist()
def payroll_date_automatic():
    today = getdate(datetime.now())
    cur_day = today.day
    if cur_day == 26:
        month = today.month
        month_name = datetime.strftime(today, '%B')
        next_month = today.month + 1
        if next_month > 12:
            next_month = 1
            year = today.year + 1
        else:
            year = today.year
        next_month_25th = getdate(datetime(year, next_month, 25))
        frappe.db.set_value('Payroll Dates','PAYROLL OT PERIOD DATE 0001','payroll_start_date',today)
        frappe.db.set_value('Payroll Dates','PAYROLL OT PERIOD DATE 0001','payroll_end_date',next_month_25th)
        frappe.db.set_value('Payroll Dates','PAYROLL OT PERIOD DATE 0001','Month',month_name)


@frappe.whitelist()
def qr_checkin():
    emp = frappe.db.get_value('Employee',{'status':'Active','employee':'TSAI0324'},['name','basic','ctc','employee_type'])
    start_date = frappe.db.get_value('Payroll Dates',{'name':'PAYROLL OT PERIOD DATE 0001'},['payroll_start_date'])
    end_date = frappe.db.get_value('Payroll Dates',{'name':'PAYROLL OT PERIOD DATE 0001'},['payroll_end_date'])
    holidays = len(get_holiday_dates_for_employee(emp[0],start_date,end_date))
    total_working_days = date_diff(end_date,start_date) - holidays
    per_day_salary = emp[1] /total_working_days
    per_day_ctc = emp[2] /total_working_days 
    print(per_day_salary)
    print(total_working_days)
    print(per_day_ctc)
    print(holidays)





