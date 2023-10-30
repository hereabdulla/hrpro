# Copyright (c) 2013, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import time
import math
from datetime import datetime,timedelta
from calendar import monthrange
from frappe.utils import getdate, cint, add_months, date_diff, add_days, nowdate, \
    get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds

def execute(filters=None):
    if not filters:
        filters = {}
    data = row = []
    filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
        "Dec"].index(filters.month) + 1  
    columns = [_("User ID") + ":Data:100",_("Name") + ":Data:150",_("Designation") + ":Data:150",_("Full Day Absents") + ":Data:200",_("Half Day Absents") + ":Data:150",_("Total Absent Days") + ":Data:100"] 
    month = filters.month - 1
    year = cint(filters.year) - 1
    if month == 0:
        month = 12
        year = cint(filters.year) - 1
    # frappe.errprint(cint(filters.year))
    # frappe.errprint(month)
    # frappe.errprint(filters.year)    
    tdm = monthrange(cint(filters.year), month)[1]
    days = range(25,tdm+1) + range(1,25)
    employees = get_employees(filters)
    for emp in get_employees(filters):
        emp_status = [] 
        halfday_status = []      
        for day in days:
            row = [emp.employee,emp.employee_name,emp.designation]    
            if day in range(25,32):
                day_f = str(year) +'-'+str(month)+'-'+str(day)
            else:
                day_f = str(filters.year) +'-'+str(filters.month)+'-'+str(day)
            query = """select att.status,att.attendance_date from `tabAttendance` att where att.status = 'Absent' and att.employee = '%s' and att.attendance_date='%s'""" % (emp.employee,day_f)
            attend = frappe.db.sql(query,as_dict=1)     
            # if attend:
            #     for at in attend:
            #         holiday_list = frappe.db.get_value("Employee", {'employee':emp.employee},['holiday_list'])
            #         hd = frappe.db.get_all("Holiday", filters={'holiday_date':at.attendance_date,'parent': holiday_list},fields=['name','holiday_date'])                   
            #         if not hd:
            #             leave_record =  frappe.db.sql("""select name,employee from `tabLeave Application`  where status = "Approved" and employee = %s and %s between from_date and to_date and docstatus = 1""" % (emp.employee,at.attendance_date) ,as_dict=1)      
            #             frappe.errprint(leave_record)
            #             if not leave_record:
            #                 emp_status.append(at.attendance_date.strftime("%d"))
            # half_day_attendance = frappe.db.sql(
            #         """select att.status,att.attendance_date from `tabAttendance` att where att.status = 'Half Day' and att.employee = '%s' and att.attendance_date='%s'""" % (emp.employee,day_f) ,as_dict=1)      
            # if half_day_attendance:
            #     for hda in half_day_attendance:
            #         holiday_list1 = frappe.db.get_value("Employee", {'employee':emp.employee},['holiday_list'])
            #         hds = frappe.db.get_all("Holiday", filters={'holiday_date':hda.attendance_date,'parent': holiday_list1},fields=['name','holiday_date'])
            #         if not hds:
            #             halfday_record =  frappe.db.sql("""select name,employee from `tabLeave Application`  where status = "Approved" and  employee = %s and %s between from_date and to_date and docstatus = 1""" % (emp.employee,hda.attendance_date) ,as_dict=1)      
            #             if not halfday_record:
            #                 halfday_status.append(hda.attendance_date.strftime("%d"))
        row += [emp_status]
        ab = len(emp_status)
        row += [halfday_status]
        h_total = len(halfday_status)      
        ht = h_total / 2.0
        total = ab + ht
        row += [total] 
        data.append(row)  
    return columns, data
   
# def get_attendance(filters):
#     att = frappe.db.sql(
#         """select `tabAttendance`.employee,`tabAttendance`.employee_name,`tabAttendance`.attendance_date,`tabEmployee`.department,`tabEmployee`.designation,`tabEmployee`.working_shift  from `tabAttendance`  
#         LEFT JOIN `tabEmployee` on `tabAttendance`.employee = `tabEmployee`.employee
#         WHERE `tabAttendance`.status = "Present" group by `tabAttendance`.employee order by `tabAttendance`.employee""",as_dict = 1)
#     return att

def get_employees(filters):
    conditions = get_conditions(filters)
    query = """SELECT 
         employee as employee,employee_name,designation FROM `tabEmployee` WHERE status='Active' %s
        ORDER BY employee""" %conditions
    data = frappe.db.sql(query, as_dict=1)
    return data




def get_conditions(filters):
    conditions = ""

    if filters.get("employee"):
        conditions += "AND employee = '%s'" % filters["employee"]

    if filters.get("department"):
        conditions += " AND department = '%s'" % filters["department"]
                
    if filters.get("location"):
        conditions += " AND location_name = '%s'" % filters["location"]
    
    if filters.get("business_unit"):
        conditions += " AND business_unit = '%s'" % filters["business_unit"]
        
    return conditions