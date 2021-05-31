// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Miss Punch Application', {
	refresh: function (frm) {
		frm.disable_save()
	},
	// validate: function (frm) {
	// 	if ((frm.doc.attendance_date >= frappe.datetime.nowdate()) && frm.doc.attendance_date) {
	// 		validated = false
	// 		frm.set_value("attendance_date", "")
	// 		frappe.throw("Attendance Can't be marked for Future Date")
	// 	}
	// 	if (frm.doc.attendance_date < frappe.datetime.nowdate()) {
	// 		frappe.call({
	// 			"method": "hrpro.hrpro.doctype.miss_punch_application.miss_punch_application.check_attendance",
	// 			args: {
	// 				"attendance_date": frm.doc.attendance_date,
	// 				"employee": frm.doc.employee
	// 			},
	// 			callback: function (r) {
	// 				if (r.message != "OK") {
	// 					if (r.message.in_time && r.message.out_time) {
	// 						validated = false;
	// 						frappe.msgprint("Attendance Already Marked")
	// 					} else {
	// 						if (frm.doc.reason.length <= 50) {
	// 							frappe.validated = false;
	// 							frappe.msgprint("Reason must contain 50 charaters")
	// 						} 
	// 						else{
	// 						frm.set_value("status", "Applied")
	// 						frappe.msgprint("Miss Punch Applied Successfully")

	// 					}
	// 				}
	// 			}
	// 			}
	// 		})
	// 	}

	// },
	// employee: function (frm) {
	// 	frappe.call({
	// 		method: 'frappe.client.get',
	// 		args: {
	// 			doctype: 'Employee',
	// 			name: frm.doc.employee
	// 		},
	// 		callback: function (r) {
	// 			var LA = r.message.leave_approvers
	// 			frm.set_value("approver", LA[0].leave_approver)
	// 			frm.set_value("employee_name", r.message.employee_name)
	// 		}
	// 	})
	// },
	// before_submit: function (frm) {
	// 	if (frappe.session.user != frm.doc.approver) {
	// 		frappe.validated = false;
	// 		frappe.msgprint(__("The Selected Approver only can submit this Document"));
	// 	}
	// },
	// onload: function (frm) {
	// 	hide_field(['in_time','out_time','reason'])
	// 	// frm.set_df_property("employee","read_only",1)
	// 	// frm.set_df_property("approver","read_only",1)
	// 	// frm.set_df_property("employee_name","read_only",1)
	// 	if (frappe.session.user == frm.doc.approver) {
	// 		frm.set_df_property('status', 'read_only', 0);
	// 	}
	// },
	// attendance_date: function (frm) {
	// 	frappe.call({
	// 		"method": "hrpro.hrpro.doctype.miss_punch_application.miss_punch_application.check_attendance",
	// 		args: {
	// 			"attendance_date": frm.doc.attendance_date,
	// 			"employee": frm.doc.employee
	// 		},
	// 		callback: function (r) {
	// 			if (r.message != "OK") {
	// 				unhide_field(['in_time','out_time','reason'])
	// 				if (r.message[0]) {
	// 					frm.set_value("in_time", (r.message[0]))
	// 					frm.set_df_property("in_time","read_only",1)
	// 				}
	// 				else {
	// 					frm.set_value("in_time", "")
	// 				}
	// 				if (r.message[1]) {
	// 					frm.set_value("out_time", (r.message[1]))
	// 					frm.set_df_property("out_time","read_only",1)
	// 				}
	// 				else {
	// 					frm.set_value("out_time", "")
	// 				}
	// 			}
	// 		}
	// 	})
	// }
});
