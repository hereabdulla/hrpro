# Copyright (c) 2013, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime
from frappe import _
from frappe.utils import cint

def execute(filters=None):
    if not filters:
        filters = {}
    data = []
    self_row = []
    manager_row = []
    hod_row = []
    reviewer_row = []
    self_completed = 0
    manager_pending = 0
    manager_completed = 0
    hod_pending = 0
    hod_completed = 0
    self_pending = 0
    reviewer_completed = 0
    reviewer_pending = 0
    columns = get_columns()
    employee_list = get_employees(filters)
    if employee_list:
        self_row = ["Performance Management Self"]
        manager_row = ["Performance Management Manager"]
        hod_row = ["Performance Management HOD"]
        reviewer_row = ["Performance Management Reviewer"]
        for emp in employee_list:
            if frappe.db.exists("Performance Management Self",{"employee_code": emp.employee,"docstatus":1}):
                self_completed += 1
            else:
                self_pending += 1
            
            if frappe.db.exists("Performance Management HOD",{"employee_code": emp.employee,"docstatus":1}):
                hod_completed += 1
            else:
                hod_pending += 1
            if frappe.db.exists("Performance Management Reviewer",{"employee_code": emp.employee,"docstatus":1}):
                reviewer_completed += 1
            else:
                reviewer_pending += 1
        for e in get_employees_without_manager(filters):
            if frappe.db.exists("Performance Management Manager",{"employee_code": e.employee,"docstatus":1}):
                manager_completed += 1
            else:
                manager_pending += 1
        self_row += [self_pending]
        self_row += [self_completed]
        manager_row += [manager_pending]
        manager_row += [manager_completed]
        hod_row += [hod_pending]
        hod_row += [hod_completed]
        reviewer_row += [reviewer_pending]
        reviewer_row += [reviewer_completed]
    data.append(self_row)
    data.append(manager_row)
    data.append(hod_row)
    data.append(reviewer_row)
    return columns, data

def get_columns():
    columns = [
        _("PM Type") + ":Data:300", 
        _("Pending") + ":Data:100",
        _("Completed") + ":Data:100",
    ]
    return columns

def get_employees(filters):
    conditions = get_conditions(filters)
    query = """SELECT 
        employee,employee_name,business_unit,location_name FROM `tabEmployee` WHERE status='Active' and pms_on_hold=0 and category='Management Staff' %s
        Group BY employee""" % conditions
    data = frappe.db.sql(query, as_dict=1)
    return data


def get_employees_without_manager(filters):
    conditions = get_conditions(filters)
    query = """SELECT 
        employee,employee_name,business_unit,location_name,one_above_manager FROM `tabEmployee` WHERE status='Active' and pms_on_hold=0 and one_above_manager IS not NULL and category='Management Staff' %s
        Group BY employee""" % conditions
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