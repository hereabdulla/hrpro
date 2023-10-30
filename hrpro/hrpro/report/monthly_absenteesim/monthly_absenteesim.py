# Copyright (c) 2013, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import math
from calendar import monthrange
from datetime import datetime,timedelta,date
from dateutil.rrule import * 
from frappe.utils import getdate, cint, add_months, date_diff, add_days, nowdate, \
    get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds,today

def execute(filters=None):
    if not filters:
        filters = {}
    data = row = []
    filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
        "Dec"].index(filters.month) + 1  
    columns = [_("User ID") + ":Data:100",_("Name") + ":Data:150",_("Designation") + ":Data:150",_("Full Day Absents") + ":Data:300",_("Half Day Absents") + ":Data:250",_("Total Absent Days") + ":Data:100"] 
    month = filters.month - 1
    year = filters.year
    if month == 0:
        month = 12
        year = cint(filters.year) - 1
    # frappe.errprint(cint(filters.year))
    # frappe.errprint(month)
    # frappe.errprint(filters.year)    
    tdm = monthrange(cint(filters.year), month)[1]
    days = range(25,tdm+1) + range(1,25)
    exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
    auto_present_list = []
    for e in exc:
        auto_present_list.append(e.employee)
    employees = get_employees(filters)
    late_in = early_out = shift_in_time = 0
    for emp in get_employees(filters):
        if str(emp.employee) not in auto_present_list:
            # frappe.errprint(emp.employee)
            emp_status = [] 
            halfday_status = []      
            for day in days:
                if day in range(25,32):
                    day_f = str(year) +'-'+str(month)+'-'+str(day)
                else:
                    day_f = str(filters.year) +'-'+str(filters.month)+'-'+str(day)
                query = """select att.status,att.attendance_date,att.in_time,att.out_time from `tabAttendance` att where att.employee = '%s' and att.attendance_date='%s'""" % (emp.employee,day_f)
                attend = frappe.db.sql(query,as_dict=1)     
                at = frappe.get_value("Attendance",{"employee":emp.employee,"attendance_date":day_f},['admin_approved_status','name','attendance_date','status','late_in','early_out','first_half_status','second_half_status','employee','in_time','out_time','work_time','overtime'],as_dict=True)

                # if attend:
                #     for at in attend:
                if at:        
                    holiday_list = frappe.db.get_value("Employee", {'employee':emp.employee},['holiday_list'])
                    holiday_date = frappe.db.get_all("Holiday", filters={'holiday_date':at.attendance_date,'parent': holiday_list},fields=['holiday_date','name','is_ph'])         
                    working_shift = frappe.db.get_value("Employee", {'employee':emp.employee},['working_shift'])   
                    assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                        where employee = %s and %s between from_date and to_date""", (at.employee, at.attendance_date), as_dict=True)
                    if assigned_shift:
                        working_shift = assigned_shift[0]['shift'] 
                    if at.in_time:
                        dt = datetime.strptime(at.in_time, "%d/%m/%Y %H:%M:%S")
                        from_time = dt.time()
                        shift_in_time = frappe.db.get_value("Working Shift",working_shift,"in_time")
                        emp_in_time = timedelta(hours=from_time.hour,minutes=from_time.minute,seconds=from_time.second)
                        #Check Movement Register
                        if get_mr_in(at.employee,at.attendance_date):
                            emp_in_time = emp_in_time - get_mr_in(at.employee,at.attendance_date)

                        if emp_in_time > shift_in_time:
                            late_in = emp_in_time - shift_in_time
                        else:
                            late_in = timedelta(seconds=0)  

                    if at.out_time:
                        dt = datetime.strptime(at.out_time, "%d/%m/%Y %H:%M:%S")
                        end_time = dt.time()
                        shift_out_time = frappe.db.get_value("Working Shift",working_shift,"out_time")
                        emp_out_time = timedelta(hours=end_time.hour,minutes=end_time.minute,seconds=end_time.second)
                        #Check Movement Register
                        if get_mr_out(at.employee,at.attendance_date):
                            emp_out_time = emp_out_time + get_mr_out(at.employee,at.attendance_date)

                        if emp_out_time < shift_out_time:
                            early_out = shift_out_time - emp_out_time
                        else:
                            early_out = ''
                    
                    if at.admin_approved_status == 'First Half Present':
                        late_in = timedelta(seconds=0)  
                    if at.admin_approved_status == 'Second Half Present':
                        early_out = timedelta(seconds=0)    
                    if at.admin_approved_status == 'First Half Absent':
                        late_in = timedelta(hours=1)  
                    if at.admin_approved_status == 'Second Half Absent':
                        early_out = timedelta(hours=1)     

                    if holiday_date:
                        for h in holiday_date:
                            if get_continuous_absents(emp.employee,at.attendance_date):
                                emp_status.append(at.attendance_date.strftime("%d"))
                            if check_prefix_suffix(at.employee,at.attendance_date): 
                                emp_status.append(at.attendance_date.strftime("%d"))   

                    elif at.status == "Absent":
                        ab_record = validate_if_attendance_not_applicable(emp.employee,at.attendance_date)
                        admin_status = False
                        if at.admin_approved_status == 'Present' or at.admin_approved_status == 'WO' or at.admin_approved_status == 'PH':
                            admin_status = True  
                        if not ab_record and not admin_status:
                            emp_status.append(at.attendance_date.strftime("%d"))
                                
                    elif at.status == "Present":
                        hd_record = validate_if_attendance_not_applicable(emp.employee,at.attendance_date)
                        admin_status = False
                        if at.admin_approved_status == 'Present' or at.admin_approved_status == 'WO' or at.admin_approved_status == 'PH':
                            admin_status = True 
                        if not hd_record and not admin_status:                            
                            if late_in and late_in > timedelta(minutes=15) and early_out and early_out > timedelta(minutes=5):
                                emp_status.append(at.attendance_date.strftime("%d"))
                            elif late_in and late_in > timedelta(minutes=15):
                                halfday_status.append(at.attendance_date.strftime("%d"))
                            elif early_out and early_out > timedelta(minutes=5):
                                halfday_status.append(at.attendance_date.strftime("%d"))
                            # else:
                            #     frappe.errprint(at.attendance_date)
                    elif at.status == "Half Day":           
                        hd_record = validate_if_attendance_not_applicable(emp.employee,at.attendance_date)
                        admin_status = False
                        if at.admin_approved_status == 'Present' or at.admin_approved_status == 'WO' or at.admin_approved_status == 'PH':
                            admin_status = True
                        if not hd_record and not admin_status:
                            if late_in and late_in > timedelta(minutes=15) and early_out and early_out > timedelta(minutes=5):
                                emp_status.append(at.attendance_date.strftime("%d"))
                            elif late_in and late_in > timedelta(minutes=15):
                                halfday_status.append(at.attendance_date.strftime("%d"))
                            elif early_out and early_out > timedelta(minutes=15):
                                halfday_status.append(at.attendance_date.strftime("%d"))
                            elif at.first_half_status == 'AB':
                                halfday_status.append(at.attendance_date.strftime("%d"))
                            elif at.second_half_status == 'AB':    
                                halfday_status.append(at.attendance_date.strftime("%d"))
                            # else:
                            #     halfday_status.append(at.attendance_date.strftime("%d"))

            if emp_status or halfday_status:
                emp_status1 = ','.join(emp_status)
                halfday_status1 = ','.join(halfday_status)
                # frappe.errprint(emp_status1)
                row = [emp.employee,emp.employee_name,emp.designation,emp_status1,halfday_status1]    
                ab = len(emp_status)
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
    query = """SELECT employee,employee_name,designation FROM `tabEmployee` WHERE status='Active' %s
        ORDER BY employee""" % conditions
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
    
def validate_if_attendance_not_applicable(employee, attendance_date):
    status = ""
    
    if is_holiday(employee, attendance_date):
        # frappe.errprint(attendance_date)
        # frappe.errprint("holiday")
        return True
    # Check if employee on Leave
    leave_record = frappe.db.sql("""select half_day from `tabLeave Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True)
    if leave_record:
        # frappe.errprint(attendance_date)
        # frappe.errprint("Leave")
        return True
    # Check if employee on On-Duty
    od_record = frappe.db.sql("""select half_day,from_date_session,to_date_session from `tabOn Duty Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True)
    if od_record:
        return True 
    # for o in od_record:
    #     if o.from_date_session == 'First Half':
    #         # frappe.errprint(attendance_date)
    #         # frappe.errprint("OD")
    #         return True  
    #     else:
    #         return False    
    # Check if employee on C-Off
    coff_record = frappe.db.sql("""select half_day from `tabCompensatory Off Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True)
    if coff_record:
        return True   
    # # Check if employee on On-Travel
    # tm_record = frappe.db.sql("""select half_day from `tabTravel Management`
    #         where employee = %s and %s between from_date and to_date
    #         and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True)
    # if tm_record:
    #     frappe.errprint("TM")
    #     return True
    tm_record = frappe.db.sql("""select half_day from `tabTour Application`
                    where employee = %s and %s between from_date and to_date
                    and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True) 
    if tm_record:
        # frappe.errprint(attendance_date)
        # frappe.errprint("TR")
        return True 

    if attendance_date == today():
        return True
    # admin_approved_status = frappe.db.sql("""select admin_approved_status as status from `tabAttendance`
    #         where employee = %s and attendance_date = %s
    #         and docstatus = 1""", (employee, attendance_date), as_dict=True)
    # for a in admin_approved_status:
    #     status = a.status
    # if admin_approved_status:
    #     frappe.errprint(attendance_date)    
    # if status == 'Present' or status == 'WO' or status == 'PH':
    #     return True    

    return False


def get_attendance(filters):
    attendance = frappe.db.sql("""select att.first_half_status as first_half_status,att.second_half_status as second_half_status,att.name as name,att.employee_name as employee_name,att.attendance_date as attendance_date,att.work_time as work_time,att.overtime as overtime,att.employee as employee, att.employee_name as employee_name,att.status as status,
    att.in_time as in_time,att.out_time as out_time from `tabAttendance` att 
    left join `tabEmployee` emp on att.employee = emp.employee  
    where where  docstatus = 1 """, as_dict=1)
    return attendance

    

def get_holiday_list_for_employee(employee, raise_exception=True):
    if employee:
        holiday_list, company = frappe.db.get_value("Employee", employee, ["holiday_list", "company"])
    else:
        holiday_list=''
        company=frappe.db.get_value("Global Defaults", None, "default_company")

    if not holiday_list:
        holiday_list = frappe.get_value('Company',  company,  "default_holiday_list")

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
        test = frappe.get_all('Holiday List', dict(name=holiday_list, holiday_date=date)) and True or False
        return frappe.get_all('Holiday List', dict(name=holiday_list, holiday_date=date)) and True or False

def get_mr_out(emp,day):
    from_time = to_time = 0
    dt = datetime.combine(day, datetime.min.time())
    mrs = frappe.db.sql("""select from_time,to_time from `tabMovement Register` where employee= '%s' and from_time between '%s' and '%s' """ % (emp,dt,add_days(dt,1)),as_dict=True)
    for mr in mrs:
        from_time = mr.from_time
        to_time = mr.to_time
    out_time = frappe.get_value("Attendance",{"employee":emp,"attendance_date":day},["out_time"])  
    if out_time:
        att_out_time = datetime.strptime(out_time,'%d/%m/%Y %H:%M:%S')
        if from_time:
            if att_out_time >= (from_time + timedelta(minutes=-10)) :
                return to_time - from_time

def get_mr_in(emp,day):
    from_time = to_time = 0
    dt = datetime.combine(day, datetime.min.time())
    mrs = frappe.db.sql("""select from_time,to_time from `tabMovement Register` where employee= '%s' and from_time between '%s' and '%s' """ % (emp,dt,add_days(dt,1)),as_dict=True)
    for mr in mrs:
        from_time = mr.from_time
        to_time = mr.to_time
    in_time = frappe.get_value("Attendance",{"employee":emp,"attendance_date":day},["in_time"])
    if in_time:    
        att_in_time = datetime.strptime(in_time,'%d/%m/%Y %H:%M:%S')
        if from_time:
            if att_in_time >= (from_time + timedelta(minutes=-10)):
                return to_time - from_time

def get_continuous_absents(emp,day):
    previous_day = False
    preday = day
    postday = day

    while validate_for_pre_day(emp,preday):
        preday = add_days(preday,-1)

    prev_day = frappe.db.get_value("Attendance",{"attendance_date":preday,"employee":emp},["status"]) 
    prev_day_sh = frappe.db.get_value("Attendance",{"attendance_date":preday,"employee":emp},["second_half_status"])   
    prev_day_admin_status = frappe.db.get_value("Attendance",{"attendance_date":preday,"employee":emp},["admin_approved_status"])
    if prev_day == 'Absent' or prev_day_sh == 'AB':
        previous_day = True

    while validate_for_next_day(emp,postday):
        postday = add_days(postday,1)
       
    next_day = frappe.db.get_value("Attendance",{"attendance_date":postday,"employee":emp},["status"])
    next_day_sh = frappe.db.get_value("Attendance",{"attendance_date":postday,"employee":emp},["first_half_status"])  
    next_day_admin_status = frappe.db.get_value("Attendance",{"attendance_date":postday,"employee":emp},["admin_approved_status"]) 
    if previous_day and next_day == 'Absent':
        if next_day_admin_status in ["WO","PH","Present","First Half Present"] or prev_day_admin_status in ["WO","PH","Present","Second Half Present"]:
            return False
        else:
            return True
    return False    
    
def get_other_day(emp,day):
    holiday = False  
    if is_holiday(emp,day):
        holiday = True

    return holiday
        


def validate_for_pre_day(employee, attendance_date):
    status = ""
    
    if is_holiday(employee, attendance_date):
        return True

    pre_leave_record = frappe.db.sql("""select half_day,from_date_session,to_date_session from `tabLeave Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True)
    if pre_leave_record:
        for o in pre_leave_record:
            if o.from_date_session == 'Full Day' or o.from_date_session == 'Second Half':
                return True
            else:
                return False

    # Check if employee on On-Duty
    od_record = frappe.db.sql("""select half_day,from_date_session,to_date_session from `tabOn Duty Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True)
    if od_record:
        for o in od_record:
            if o.from_date_session == 'Second Half' or o.from_date_session == 'Full Day':
                return True
            else:
                return False

    # Check if employee on C-Off
    coff_record = frappe.db.sql("""select half_day,from_date_session,to_date_session from `tabCompensatory Off Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True)
    if coff_record:
        for o in coff_record:
            if o.from_date_session == 'Second Half' or o.from_date_session == 'Full Day':
                return True
            else:
                return False

    # # Check if employee on On-Travel
    tm_record = frappe.db.sql("""select half_day,from_date_session,to_date_session from `tabTour Application`
                    where employee = %s and %s between from_date and to_date
                    and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True) 
    if tm_record:
        for o in tm_record:
            if o.from_date_session == 'Second Half' or o.from_date_session == 'Full Day':
                return True
            else:
                return False

    if attendance_date == today():
        return True 

    return False

def validate_for_next_day(employee, attendance_date):
    status = ""
    
    if is_holiday(employee, attendance_date):
        return True
    
    post_leave_record = frappe.db.sql("""select half_day,from_date_session,to_date_session from `tabLeave Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True)
    if post_leave_record:
        for o in post_leave_record:
            if o.from_date_session == 'Full Day' or o.from_date_session == 'First Half':
                return True
            else:
                return False

    # Check if employee on On-Duty
    od_record = frappe.db.sql("""select half_day,from_date_session,to_date_session from `tabOn Duty Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True)
    if od_record:
        for o in od_record:
            if o.from_date_session == 'First Half' or o.from_date_session == 'Full Day':
                return True
            else:
                return False    
  
    # Check if employee on C-Off
    coff_record = frappe.db.sql("""select half_day,from_date_session,to_date_session from `tabCompensatory Off Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True)
    if coff_record:
        for o in coff_record:
            if o.from_date_session == 'First Half' or o.from_date_session == 'Full Day':
                return True
            else:
                return False   
                
    # # Check if employee on On-Travel
    tm_record = frappe.db.sql("""select half_day,from_date_session,to_date_session from `tabTour Application`
                    where employee = %s and %s between from_date and to_date
                    and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True) 
    if tm_record:
        for o in tm_record:
            if o.from_date_session == 'First Half' or o.from_date_session == 'Full Day':
                return True
            else:
                return False

    if attendance_date == today():
        return True

    return False

def check_prefix_suffix(emp,day):
    previous_day = next_day = False 
    preday = day
    postday = day

    while is_holiday(emp,preday):
        preday = add_days(preday,-1)

    while is_holiday(emp,postday):
        postday = add_days(postday,1)

    # Check if employee on Leave
    pre_leave_record = frappe.db.sql("""select half_day,from_date_session,to_date_session from `tabLeave Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1 and status='Approved'""", (emp, preday), as_dict=True)
    if pre_leave_record:
        for o in pre_leave_record:
            if o.from_date_session == 'Full Day' or o.from_date_session == 'Second Half':
                previous_day =  True
    post_leave_record = frappe.db.sql("""select half_day,from_date_session,to_date_session from `tabLeave Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1 and status='Approved'""", (emp, postday), as_dict=True)
    if post_leave_record:
        for o in post_leave_record:
            if o.from_date_session == 'Full Day' or o.from_date_session == 'First Half':
                next_day =  True
    if previous_day and next_day:
        return True   
    return False        