# Copyright (c) 2013, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import print_function, unicode_literals
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
    salary = get_salary_slip(conditions,filters)
    for ss in salary:
        data.append(ss)
    return columns, data

def get_columns():
    columns = [
        # _("ID") + ":Data:200",
        _("From Date") + ":Date:120",
        _("To Date") + ":Date:120",
        _("Employee") + ":Link/Employee:120",
        _("Employee Name") + ":Data:120",
        _("Department") + ":Data:120",
        _("Date of Join") + ":Date:120",
        _("Income") + ":Currency:120",
        _("Actual Aount") + ":Currency:120",
        _("PT Deduct Amount") + ":Currency:120",        
    ]
    return columns

def get_salary_slip(conditions,filters):
    row = []
    ss_net_pay = frappe.db.sql("""Select sum(net_pay) as total, employee, employee_name, department, designation, date_of_join,start_date,end_date, net_pay 
        From `tabSalary Slip` Where %s group by employee"""% conditions,filters, as_dict=1)
    pt = frappe.db.sql("""select `tabSalary Slip`.employee as employee,`tabSalary Detail`.salary_component,sum(`tabSalary Detail`.amount) as amount from `tabSalary Slip` left join 
    `tabSalary Detail` on `tabSalary Slip`.name = `tabSalary Detail`.parent where `tabSalary Detail`.salary_component = 'Professional Tax' 
    group by `tabSalary Slip`.employee """, as_dict = 1)
    for ss in ss_net_pay:
        pt_slab = frappe.get_value("Professional Tax Slab",{"enable":1},["name"])
        pt_slab_list = frappe.get_all("Professional Tax Slab List",{"parent":pt_slab},["*"])
        for slab in pt_slab_list:
            if ss.total >= slab.from_amount and ss.total <= slab.to_amount:
                pt_amount = slab.tax_amount
                for pt_ded in pt:
                    if pt_ded.employee == ss.employee:
                        row += [(filters.from_date,filters.to_date,ss.employee,ss.employee_name,ss.department,ss.date_of_join,ss.total,pt_amount,pt_ded.amount)]
    return row

def get_conditions(filters):
    conditions = ""
    if filters.get("from_date" and "to_date"): conditions += " start_date between %(from_date)s and %(to_date)s"
    if filters.get("from_date" and "to_date"): conditions += " and end_date between %(from_date)s and %(to_date)s"
    if filters.get("company"): conditions += " and company = %(company)s"
    if filters.get("employee"): conditions += " and employee = %(employee)s"
    if filters.get("department"): conditions += " and department = %(department)s"

    return conditions, filters