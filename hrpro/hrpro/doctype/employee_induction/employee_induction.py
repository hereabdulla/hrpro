# -*- coding: utf-8 -*-
# Copyright (c) 2020, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import random
from frappe.model.document import Document

class EmployeeInduction(Document):
    pass
@frappe.whitelist()
def create_questions_entry(employee_id,email_id):
    # frappe.errprint("hi")
    qs = frappe.get_doc("Induction Question set")
    # frappe.errprint(qs.questions)
    result1=[]
    res=[]
    # k=10
    for que in qs.questions:
        # frappe.errprint(que.question)
        qt=que.question
        # result=list(str(qt))
        # result=''.join(result)
        result1.append(qt)
    s=random.sample(result1,10)
    frappe.errprint(s)
        # frappe.errprint(result)
        # res=''.join(random.sample(result1,10))
    if not frappe.db.exists("Induction Test",{'employee_id':employee_id}):
        it=frappe.new_doc("Induction Test")
        frappe.errprint(employee_id)
        it.employee_id=employee_id
        it.email_id=email_id
        for i in s:
            frappe.errprint(i)
            it.append("questions",{"question":i})
        it.save(ignore_permissions="True")
        frappe.db.commit()