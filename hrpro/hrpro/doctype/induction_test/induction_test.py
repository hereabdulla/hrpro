# -*- coding: utf-8 -*-
# Copyright (c) 2020, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from dateutil.relativedelta import relativedelta
from frappe.utils import today
from datetime import datetime
import random

class InductionTest(Document):
    def on_submit(self):
        if self.total_score < 50:
            frappe.msgprint("Redo the induction")
            self.cancel()
            qs = frappe.get_doc("Induction Question set")
            result1=[]
            res=[]
            for que in qs.questions:
                qt=que.question
                result1.append(qt)
            s=random.sample(result1,10)
            # frappe.errprint(s)
            it=frappe.new_doc("Induction Test")
            # frappe.errprint(employee_id)
            it.employee_id=self.employee_id
            it.email_id=self.email_id
            for i in s:
                # frappe.errprint(i)
                it.append("questions",{"question":i})
            it.save(ignore_permissions="True")
            frappe.db.commit()
        if not int(self.total_score) < 50:
            if not frappe.db.exists("Induction Goal",{'employee_id':self.employee_id}):
                ig=frappe.new_doc("Induction Goal")
                ig.employee_id=self.employee_id
                ig.save(ignore_permissions=True)
                frappe.db.commit()

def create_feedback():
    employees =frappe.get_all("Employee",{"employment_type":"Probation"},["probation_start_date","name","employee_name","probation_end_date","prefered_email"])
    for emp in employees:
        t=relativedelta(months=3)
        three_month=emp.probation_start_date+t
        # print(three_month)
        today=datetime.today()
        # print(today.date())
        if(three_month==today.date()):
            # print(emp)
            pf=frappe.new_doc("Probation Feedback")
            pf.employee_id=emp.name
            pf.employee_name=emp.employee_name
            # print(pf.employee_name)
            pf.save(ignore_permissions=True)
            frappe.db.commit()
        if(emp.probation_end_date==today.date()):
           frappe.sendmail(
            recipients=["%s"],
            subject='Probation Period Date' ,
            message="""<p>Dear Admin,</p>
            <p> Probation period date ended today for  %s %s employee  </p>""" % (emp.prefered_email,emp.name,emp.employee_name))

@frappe.whitelist()
def get_end_date():
    s =relativedelta(months=6)
    today=datetime.today()
    six_month=today.date()+s
    # frappe.errprint(six_month)
    probation_end_date=six_month
    return probation_end_date
    # print(probation_end_date) 


        
       
        
