# -*- coding: utf-8 -*-
# Copyright (c) 2021, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, cstr, date_diff, flt, formatdate, getdate, get_link_to_form, \
    comma_or, get_fullname, add_days, nowdate, get_datetime_str
from frappe.model.document import Document

class FullandFinalSettlement(Document):
    pass


@frappe.whitelist()
def create_salary_slip(employee,date):
    salary_slip = frappe.new_doc("Salary Slip")
    salary_slip.update({
        "employee":employee
    }).save(ignore_permissions=True)
    frappe.db.commit()
    id = salary_slip.name
    salary_details = frappe.get_doc("Salary Slip",{"name":id},["*"])
    earnings = salary_details.earnings
    deductions = salary_details.deductions
    gross_pay = salary_details.gross_pay
    total_deduction = salary_details.total_deduction
    net_pay = salary_details.net_pay
    return(id,earnings,deductions,gross_pay,total_deduction,net_pay)
