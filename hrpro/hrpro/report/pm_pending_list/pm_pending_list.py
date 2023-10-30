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
    data = row = []	
    manager = ""
    columns = get_columns()
    for emp in get_employees(filters):
        if emp.one_above_manager:
            manager = frappe.get_value("Employee",{"user_id":emp.one_above_manager},"employee_name") 
        else:
            manager = "-"
        hod = frappe.get_value("Employee",{"user_id":emp.hod},"employee_name") 
        row = [emp.employee,emp.employee_name,manager,hod,emp.location_name] 
        if frappe.db.exists("Performance Management Self",{"employee_code":emp.employee}):
            pm_self_doc = frappe.db.get_value("Performance Management Self",{"employee_code":emp.employee},"docstatus")
            if pm_self_doc == 1:
                row += [ "Completed" ]
            else:
                row += [ "Pending"]
        else:
                row += [ "Pending"]
        if manager == "-":
            row += ["-"]
        elif frappe.db.exists("Performance Management Manager",{"employee_code":emp.employee}):
                pm_manager_doc = frappe.db.get_value("Performance Management Manager",{"employee_code":emp.employee},"docstatus")
                if pm_manager_doc == 1:
                    row += [ "Completed" ]
                else:
                    row += [ "Pending"]
        else:
                row += [ "Pending"]
        if frappe.db.exists("Performance Management HOD",{"employee_code":emp.employee}):
            pm_hod_doc = frappe.db.get_value("Performance Management HOD",{"employee_code":emp.employee},"docstatus")
            if pm_hod_doc == 1:
                row += [ "Completed" ]
            else:
                row += [ "Pending"]
        else:
                row += [ "Pending"]
        if frappe.db.exists("Performance Management Reviewer",{"employee_code":emp.employee}):
            pm_reviewer_doc = frappe.db.get_value("Performance Management Reviewer",{"employee_code":emp.employee},"docstatus")
            if pm_reviewer_doc == 1:
                row += [ "Completed" ]
            else:
                row += [ "Pending"]
        else:
                row += [ "Pending"]
        data.append(row)
    return columns, data

def get_columns():
    columns = [
        _("Employee") + ":Link/Employee:80", 
        _("Employee Name") + ":Data:200",
        _("Manager") + ":Data:200",
        _("HOD") + ":Data:200",
        _("Location") + ":Data:200",
        _("Self Status") + ":Data:100", 
        _("Manager Status") + ":Data:100", 
        _("HOD Status") + ":Data:100",
        _("Reviewer Status") + ":Data:100",
    ]
    return columns

def get_employees(filters):
    conditions = get_conditions(filters)
    query = """SELECT 
         employee as employee,employee_name,one_above_manager,hod,location_name FROM `tabEmployee` WHERE status='Active' and pms_on_hold=0 and category='Management Staff' %s
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