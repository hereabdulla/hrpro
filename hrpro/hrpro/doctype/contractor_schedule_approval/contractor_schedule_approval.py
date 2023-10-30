# -*- coding: utf-8 -*-
# Copyright (c) 2021, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ContractorScheduleApproval(Document):
    def fetch_count(self):
        dept = frappe.get_all("User Permission",{"user":frappe.session.user,"allow":"Department"},["for_value"])
        dept_list = []
        roles = frappe.get_roles()
        if 'HOD' in roles:
            count = '`tabManpower Count`.manpower_count'
        elif 'Plant Head' in roles:
            count = '`tabManpower Count`.hod'
        elif 'General Manager' in roles:
            count = '`tabManpower Count`.plant_head'
        elif 'VP' in roles:
            count = '`tabManpower Count`.gm'
        elif 'WTD' in roles:
            count = '`tabManpower Count`.vp'
        for d in dept:
            dept_list.append(d.for_value)
        csrs = frappe.db.sql("""select `tabContractor Schedule Request`.name, `tabManpower Count`.department,`tabManpower Count`.shift_type,`tabManpower Count`.contract_type ,""" +count+""" as count from `tabContractor Schedule Request` 
        LEFT JOIN `tabManpower Count` on `tabContractor Schedule Request`.name = `tabManpower Count`.parent
        where start_date = %s and contractor = %s and plant = %s and `tabManpower Count`.department in %s """,(self.start_date,self.contractor,self.plant,dept_list),as_dict=True)
        return csrs

    def submit_count(self):
        roles = frappe.get_roles()
        for d in self.manpower_count:
            doc = frappe.get_doc("Contractor Schedule Request",d.id)
            for c in doc.manpower_count:
                if c.department == d.department:
                    if c.shift_type == d.shift_type:
                        if c.contract_type == d.contract_type:
                            if 'HOD' in roles:
                                c.hod = d.manpower_count
                                doc.save(ignore_permissions=True)
                            if 'Plant Head' in roles:
                                c.plant_head = d.manpower_count
                                doc.save(ignore_permissions=True)
                            if 'General Manager' in roles:
                                c.gm = d.manpower_count
                                doc.save(ignore_permissions=True)
                            if 'VP' in roles:
                                c.vp = d.manpower_count
                                doc.save(ignore_permissions=True)
                            if 'WTD' in roles:
                                c.wtd = d.manpower_count
                                doc.save(ignore_permissions=True)