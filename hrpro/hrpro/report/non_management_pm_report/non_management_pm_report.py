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
    columns = get_columns()
    rating = ctc = hike = ""
    for year in range(2016,datetime.now().year+1):
        columns += [(_(year) + " Ratings::80") ]
        columns += [(_(year) + " CTC:Currency:100") ]
        columns += [(_(year) + " Hike::80") ]
    for emp in get_employees(filters):
        manager = frappe.get_value("Employee",{"user_id":emp.one_above_manager},"employee_name") 
        hod = frappe.get_value("Employee",{"user_id":emp.hod},"employee_name") 
        row = [ emp.employee,emp.employee_name,manager,hod,emp.location_name,"Jan to Dec","January"]   
        appr = frappe.db.exists("Appraisal",{"employee":emp.employee})
        if appr:
            for year in range(2016,datetime.now().year+1):
                rating,ctc,hike = get_hike(appr,year)
                row += [rating,ctc,hike]                
        data.append(row)
    return columns, data

def get_columns():
    columns = [
        _("Employee") + ":Data:80", 
        _("Employee Name") + ":Data:200",
        _("One Above Manager") + ":Data:200",
        _("HOD") + ":Data:200",
        _("Location") + ":Data:110",
         _("Assessment Period") + ":Data:90",
        _("Revision WEF") + ":Data:90"
    ]
    return columns

def get_employees(filters):
    conditions = get_conditions(filters)
    query = """SELECT 
         employee as employee,employee_name,one_above_manager,hod,location_name FROM `tabEmployee` WHERE status='Active' and category='Non-Management Staff' %s
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
        
    return conditions

def get_hike(appr,year):
    appr_hike = []
    rating = ctc = hike = ""
    ah = frappe.get_all("Appraisal Hike",{"parent":appr,"parenttype":"Appraisal"},["year","rating","ctc","hike"],order_by="year")
    for a in ah:
        if cint(a.year) == year:
            rating = a.rating
            ctc = a.ctc
            hike = a.hike
    return rating,ctc,hike


    

