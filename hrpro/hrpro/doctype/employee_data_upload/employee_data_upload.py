# -*- coding: utf-8 -*-
# Copyright (c) 2020, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class EmployeeDataUpload(Document):
	pass

@frappe.whitelist()
def mail_alert(number_of_employee,site):
	frappe.errprint(number_of_employee)
	frappe.errprint(site)
	frappe.sendmail(
				recipients=["rekha@bossmanagement.in"],
				subject= "Reg: New Employee attachment Received",
				message= """<p>Dear Sir/Madam,</p>
				<h4>Info:</h4><p>New %s Employee Data attachment received from %s site, Kindly work on it ASAP. 
				</p><br> Regards <br>ERP Team"""
                % (number_of_employee, site))