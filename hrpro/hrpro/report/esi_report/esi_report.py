# Copyright (c) 2013, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, add_days, date_diff, getdate, cint

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()

    data = []
    row = []
    conditions, filters = get_conditions(filters)
    total = 0
    salary_slips = get_salary_slips(conditions, filters)

    for ss in salary_slips:
        esino = frappe.db.get_value("Employee", {'employee': ss.employee}, ['esi_no'])
        if esino:
            row = [esino]
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

        if ss.md:
            row += [ss.md]
        else:
            row += [0]

        if ss.gp:
            row += [ss.gp]
        else:
            row += [0]
        esic = frappe.db.get_value(
            "Salary Detail", {'abbr': 'ESI', 'parent': ss.name}, ['amount'])
        if esic:
            row += [esic,"",""]
        else:
            row += ["","",""]

        # eesi = round(ss.gp * 0.0325)
        # if eesi:
        #     row += [eesi]
        # else:
        #     row += [""]
        # frappe.errprint(row)
        if row:
            data.append(row)

    return columns, data


def get_columns():
    columns = [
        _("ESI Number") + ":Data:120",
        _("Employee") + ":Data:120",
        _("Employee Name") + ":Data:90",
        _("Payment Days") + ":Int:50",
        _("Gross Pay") + ":Currency:100",
        _("ESI") + ":Currency:100",
        # _("Employer ESI") + ":Currency:100",
        _("Reason Code") + ":Currency:100",
        _("Last Working Days") + ":Currency:100"
    ]
    return columns

def get_salary_slips(conditions, filters):
    salary_slips = frappe.db.sql("""select ss.employee as employee,ss.employee_name as employee_name,ss.name as name,ss.payment_days as md,ss.gross_pay as gp from `tabSalary Slip` ss 
    where %s order by employee""" % conditions, filters, as_dict=1)
    return salary_slips

def get_conditions(filters):
    if not (filters.get("month") and filters.get("year")):
        msgprint(_("Please select month and year"), raise_exception=1)

    filters["total_days_in_month"] = monthrange(cint(filters.year), cint(filters.month))[1]

    conditions = "month(start_date) = %(month)s and year(start_date) = %(year)s"
    # if filters.get("from_date"):
    #     conditions += "start_date >= %(from_date)s"
    # if filters.get("to_date"):
    #     conditions += " and end_date >= %(to_date)s"

    return conditions, filters

@frappe.whitelist()
def get_years():
    year_list = frappe.db.sql_list("""select distinct YEAR(start_date) from `tabSalary Slip` ORDER BY YEAR(start_date) DESC""")
    if not year_list:
        year_list = [getdate().year]

    return "\n".join(str(year) for year in year_list)