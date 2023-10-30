# Copyright (c) 2013, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe,json
from datetime import datetime
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe import _
from frappe.utils.csvutils import UnicodeWriter
from frappe.model.document import Document
from frappe.utils import cstr, add_days, date_diff, getdate, cint

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()

    data = []
    row = []
    conditions, filters = get_conditions(filters)
    total = 0
    epsw = 0
    edlic = 0
    salary_slips = get_salary_slips(conditions, filters)
    for ss in salary_slips:
        pfno = frappe.db.get_value("Employee", {'employee': ss.employee}, ['uan_no' or 'uan'])
        if pfno:
            row = [pfno]
        else:
            row = [0]

        if ss.employee:
            row += [ss.employee]
        else:
            row += [0]

        if ss.employee_name:
            row += [ss.employee_name]
        else:
            row += [0]

        if ss.gp:
            row += [ss.gp]
        else:
            row += [0]

        basic = frappe.db.get_value("Salary Detail", {'abbr': 'B', 'parent': ss.name}, ['amount'])
        epsw = flt(15000)
        if basic:
            if epsw < basic:
                row += [basic, epsw, epsw]
            else:
                row += [basic, basic, basic]
        else:
            row += [0, 0, 0]

        epf1 = frappe.db.get_value("Salary Detail", {'abbr': 'EPF', 'parent': ss.name}, ['amount'])
        if epf1:
            epf = round(epf1)
            row += [epf]
        else:
            epf = 0
            row += [0]
        eps = 0
        if basic:
            if epf > 0:
                if epsw < basic:
                    eps = round(epsw*0.0833)
                    row += [eps]
                else:
                    eps = round(basic*0.0833)
                    row += [eps]
            # eps = round(basic*0.0833)
            # if eps and epf > 0:
            #     row += [eps]
            else:
                row += [0]
        else:
            row += [0]
        ee = round(epf-eps)
        if ee > 0:
            row += [ee]
        else:
            row += [0]

        if ss.lop:
            row += [ss.lop,0]
        else:
            row += [0,0]
        # frappe.errprint(row)
        if row:
            data.append(row)
    return columns, data

def get_columns():
    columns = [
        _("UAN Number") + ":Data:120",
        _("Employee") + ":Data:80",
        _("Employee Name") + ":Data:90",
        # _("Emp Category") + ":Data:100",
        _("Gross Pay") + ":Currency:100",
        _("EPF Wages") + ":Currency:100",
        _("EPS Wages") + ":Currency:100",
        _("EDLIC Wages") + ":Currency:100",
        _("EPF Contribution") + ":Currency:100",
        _("EPS Contribution") + ":Currency:100",
        _("Difference EPF & EPS ") + ":Currency:100",
        _("NCP Days ") + ":Data:100",
        _("Refund of Advances") + ":Currency:100"
    ]
    return columns

def get_salary_slips(conditions, filters):
    salary_slips = frappe.db.sql("""select ss.employee as employee,ss.employee_name as employee_name,  ss.name as name,ss.leave_without_pay as lop,ss.gross_pay as gp from `tabSalary Slip` ss 
    where %s order by employee""" % conditions, filters, as_dict=1)
    return salary_slips

def get_conditions(filters):
    # conditions = ""
    if not (filters.get("month") and filters.get("year")):
        msgprint(_("Please select month and year"), raise_exception=1)

    filters["total_days_in_month"] = monthrange(cint(filters.year), cint(filters.month))[1]

    conditions = "month(start_date) = %(month)s and year(start_date) = %(year)s"
    # if filters.get("from_date"):
    #     conditions += " start_date >= %(from_date)s"
    # if filters.get("to_date"):
    #     conditions += " and end_date >= %(to_date)s"

    return conditions, filters

@frappe.whitelist()
def get_template():
    args = frappe.local.form_dict

    w = UnicodeWriter()
    
    values = args['value']
    frappe.errprint(values)
    value_list = list(values.split(","))
    s = "#~#"
    formatted_value = s.join(value_list)
    frappe.errprint(formatted_value)

    # write out response as a type csv
    # frappe.response['result'] = cstr(formatted_value)
    # frappe.response['type'] = 'txt'
    # frappe.response['doctype'] = "PF Form"

@frappe.whitelist()
def get_years():
    year_list = frappe.db.sql_list("""select distinct YEAR(start_date) from `tabSalary Slip` ORDER BY YEAR(start_date) DESC""")
    if not year_list:
        year_list = [getdate().year]

    return "\n".join(str(year) for year in year_list)