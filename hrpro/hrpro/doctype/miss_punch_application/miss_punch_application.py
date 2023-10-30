# -*- coding: utf-8 -*-
# Copyright (c) 2019, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import frappe,os,base64
import requests
import datetime
import json,calendar
from datetime import datetime,timedelta,date,time
import datetime as dt
from frappe.utils import cint,today,flt,date_diff,add_days,add_months,date_diff,getdate,formatdate,cint,cstr
from frappe.desk.notifications import delete_notification_count_for
from frappe.utils import cstr, cint, getdate,get_first_day, get_last_day, today
from frappe import _


class MissPunchApplication(Document):
    def validate(self):
        date = datetime.strptime(str(self.attendance_date), '%Y-%m-%d').date()
        d = date.strftime('%d')
        if int(d) <= 25:
            last_month = add_months(date,-1)
        else:
            last_month = date
        last_month_start = get_first_day(last_month)
        allowed_from = add_days(last_month_start,25)
        cur_month_start = get_first_day(date)
        allowed_till = add_days(cur_month_start,24)
        count = frappe.db.sql("select count(*) as count from `tabMiss Punch Application` where employee = '%s' and attendance_date between '%s' and '%s' and name != '%s' "%(self.employee,allowed_from,allowed_till,self.name),as_dict=True)
        roles = frappe.get_roles(frappe.session.user)
        frappe.errprint([allowed_from,allowed_till])
        if 'HR GM' not in roles:
            if count[0].count >= 2:
                frappe.throw("Only two Miss Punch correction is allowed in a month")

    @frappe.whitelist()
    def get_att(self):
        emp = self.employee
        if emp:
            atts = frappe.db.sql("select * from `tabAttendance` where employee = '%s' and attendance_date = '%s' "%(emp,self.attendance_date),as_dict=True)
            att_list = []
            for att in atts:
                if not frappe.db.exists("Miss Punch Application",{'attendance_date':att.attendance_date,'employee':att.employee}):
                    att_list.append(att)
            return att_list
            
    def on_submit(self):
        if self.workflow_state == "Approved":
            frappe.db.set_value("Attendance",self.attendance,"in_time",self.in_time)
            frappe.db.set_value("Attendance",self.attendance,"out_time",self.out_time)
            frappe.db.set_value("Attendance",self.attendance,"qr_shift",self.qr_shift)
            frappe.db.set_value("Attendance",self.attendance,"status","Present")
            if not frappe.db.get_value("Attendance",self.attendance,"shift"):
                if self.qr_shift:
                    frappe.db.set_value("Attendance",self.attendance,"shift",self.qr_shift)
                else:
                    frappe.db.set_value("Attendance",self.attendance,"shift",'1')