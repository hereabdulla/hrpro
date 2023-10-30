# -*- coding: utf-8 -*-
# Copyright (c) 2019, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PerformanceManagement(Document):
    pass


def lead_query(doctype, txt, searchfield, start, page_len, filters):
        return frappe.db.sql("""select name, lead_name, company_name from `tabLead`
            where docstatus < 2
                and ifnull(status, '') != 'Converted'
                and ({key} like %(txt)s
                    or lead_name like %(txt)s
                    or company_name like %(txt)s)
                {mcond}
            order by
                if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
                if(locate(%(_txt)s, lead_name), locate(%(_txt)s, lead_name), 99999),
                if(locate(%(_txt)s, company_name), locate(%(_txt)s, company_name), 99999),
                idx desc,
                name, lead_name
            limit %(start)s, %(page_len)s""".format(**{
                'key': searchfield,
                'mcond':get_match_cond(doctype)
            }), {
                'txt': "%%%s%%" % txt,
                '_txt': txt.replace("%", ""),
                'start': start,
                'page_len': page_len
            }) 