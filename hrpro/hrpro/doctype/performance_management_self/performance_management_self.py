# -*- coding: utf-8 -*-
# Copyright (c) 2019, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe,json
from frappe.model.document import Document

class PerformanceManagementSelf(Document):
	pass



@frappe.whitelist()
def sort_r(table):
    in_time = {}
    in_time = json.loads(table)
    sort = sorted(in_time, key=lambda k: k['competency'],reverse=True)
    return sort