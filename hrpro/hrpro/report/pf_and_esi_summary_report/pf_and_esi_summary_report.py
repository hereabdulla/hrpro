# Copyright (c) 2013, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
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
    summary = get_summary(conditions,filters)
    for sum_list in summary:
        data.append(sum_list)
    return columns, data

def get_columns():
    columns = [
        _("Start Date") + ":Date:120",
        _("End Date") + ":Date:120",
        _("Name") + ":Data:200",
        _("Employee PF") + ":Currency:200",
        _("Employer PF") + ":Currency:120",
        _("Service Charge") + ":Currancy:120",
        _("Total") + ":Currancy:120",
    ]
    return columns

def get_summary(conditions,filters):
    salary_slips_epf = frappe.db.sql("""select ss.start_date as start_date,ss.end_date as end_date, 
    sd.salary_component as salary_component, sum(sd.amount) as amount from `tabSalary Slip` ss 
    left join `tabSalary Detail` sd on sd.parent = ss.name where %s and sd.salary_component = 'EPF' group by start_date""" % conditions, filters, as_dict=1)
    salary_slips_esi = frappe.db.sql("""select ss.start_date as start_date,ss.end_date as end_date, 
    sd.salary_component as salary_component, sum(sd.amount) as amount from `tabSalary Slip` ss 
    left join `tabSalary Detail` sd on sd.parent = ss.name where %s and sd.salary_component = 'ESI' group by start_date""" % conditions, filters, as_dict=1)
    ss_list=[]
    for ss in salary_slips_epf:
        Service_charge = round((ss.amount/100)*1)
        total = ss.amount+ss.amount+Service_charge
        ss_list.append([str(ss.start_date),str(ss.end_date),ss.salary_component,ss.amount,ss.amount,Service_charge,total])
        if salary_slips_esi:
            for ss_esi in salary_slips_esi:
                esi_amount = (ss_esi.amount/0.75)*100
                employer_esi = round((esi_amount/100)*3.25)
                Service_charge = 0
                total = ss_esi.amount+employer_esi+Service_charge
                ss_list.append([str(ss_esi.start_date),str(ss_esi.end_date),ss_esi.salary_component,ss_esi.amount,employer_esi,Service_charge,total])
    return ss_list

def get_conditions(filters):
    if not (filters.get("month") and filters.get("year")):
        msgprint(_("Please select month and year"), raise_exception=1)

    filters["total_days_in_month"] = monthrange(cint(filters.year), cint(filters.month))[1]

    conditions = "month(ss.start_date) = %(month)s and year(ss.start_date) = %(year)s"
    if filters.get("company"): conditions += " and company = %(company)s"
    return conditions, filters

@frappe.whitelist()
def get_years():
    year_list = frappe.db.sql_list("""select distinct YEAR(start_date) from `tabSalary Slip` ORDER BY YEAR(start_date) DESC""")
    if not year_list:
        year_list = [getdate().year]

    return "\n".join(str(year) for year in year_list)