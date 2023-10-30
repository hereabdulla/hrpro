// Copyright (c) 2020, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mark Attendance', {
	refresh(frm){
		frm.disable_save()
	},
	submit(frm){
		var today_date =frappe.datetime.nowdate()
		frappe.call({
			"method":"hrpro.hrpro.doctype.mark_attendance.mark_attendance.create_self_attendance",
			"args":{
				"employee_id":frm.doc.employee_id,
				"employee_name":frm.doc.employee_name,
				"in_time":frm.doc.in_time,
				"attendance_date":frm.doc.attendance_date,
				"shift":frm.doc.shift
			},
			callback: function(r){
			}	
		})
	}
	})