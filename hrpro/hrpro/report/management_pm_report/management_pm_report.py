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
    promotion= potential = performance = pm =rating = ctc = hike = ""
    for year in range(2010,datetime.now().year+1):
        columns += [(_(year) + " Promotion::150") ]
        columns += [(_(year) + " Hike:150") ]
        columns += [(_(year) + " CTC:Currency:150") ]
        columns += [(_(year) + " Potential::150") ]
        columns += [(_(year) + " Rating::150") ]
        columns += [(_(year) + " Performance::150") ]
    for emp in get_employees(filters):
        # manager = frappe.get_value("Employee",{"user_id":emp.one_above_manager},"employee_name") 
        # hod = frappe.get_value("Employee",{"user_id":emp.hod},"employee_name") 
        row = [ emp.employee,emp.employee_name,emp.gender,emp.date_of_joining,emp.designation,emp.cost_center,emp.department,emp.location_name,"Jan to Dec","January"]   
        pm = frappe.db.exists("Performance Management Reviewer",{"employee_code":emp.employee})
        if pm:
            for year in range(2010,datetime.now().year+1):
                promotion,hike,ctc,potential,rating,performance = get_hike(pm,year)
                row += [promotion,hike,ctc,potential,rating,performance]                
        data.append(row)
    return columns, data

def get_columns():
    columns = [
        _("Employee") + ":Data:200", 
        _("Employee Name") + ":Data:200",
        _("Gender") + ":Data:100",
        _("Date of Joining") + ":Date:200",
        _("Designation") + ":Data:200",
        _("Cost Center") + ":Data:200",
        _("Department") + ":Data:200",
        _("Location") + ":Data:110",
         _("Assessment Period") + ":Data:90",
        _("Revision WEF") + ":Data:90"
    ]
    return columns

def get_employees(filters):
    conditions = get_conditions(filters)
    query = """SELECT 
         employee as employee,employee_name,gender,date_of_joining,designation,cost_center,department,one_above_manager,hod,location_name FROM `tabEmployee` WHERE status='Active' and category='Management Staff' %s
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

def get_hike(pm,year):
    appr_hike = []
    promotion = hike = ctc = potential = rating = performance = ""
    ah = frappe.get_all("Management PM Details",{"parent":pm,"parenttype":"Performance Management Reviewer"},["year","promotion","hike","ctc","potential","rating","performance"],order_by="year")
    for a in ah:
        if cint(a.year) == year:
            promotion = a.promotion
            hike = a.hike
            ctc = a.ctc
            potential = a.potential
            rating = a.rating
            performance = a.performance
    return promotion,hike,ctc,potential,rating,performance


    

