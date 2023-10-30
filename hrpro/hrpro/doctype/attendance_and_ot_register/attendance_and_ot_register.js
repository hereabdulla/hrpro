// Copyright (c) 2020, TeamPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance and OT Register', {
	// refresh: function(frm) {

	// }
	start_date: function (frm) {
		frappe.call({
			method: 'hrpro.hrpro.doctype.attendance_and_ot_register.attendance_and_ot_register.get_end_date',
			args: {
				frequency: "monthly",
				start_date: frm.doc.start_date
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value('end_date', r.message.end_date);
				}
			}
		});
	},
	// before_save: function (frm) {
	// 	if (frm.doc.employee == null) {
	// 		frappe.call({
	// 			method: 'hrpro.hrpro.doctype.attendance_and_ot_register.attendance_and_ot_register.get_employee',
	// 			args: {
	// 				client_id: frm.doc.client_employee_no
	// 			},
	// 			callback: function (r) {
	// 				if (r.message) {
	// 					frm.set_value('employee', r.message);
	// 				}
	// 			}
	// 		});
	// 	}
	// },
	// client_employee_no: function (frm) {
	// 	if (frm.doc.employee == null) {
	// 		frappe.call({
	// 			method: 'hrpro.hrpro.doctype.attendance_and_ot_register.attendance_and_ot_register.get_employee',
	// 			args: {
	// 				client_id: frm.doc.client_employee_no
	// 			},
	// 			callback: function (r) {
	// 				if (r.message) {
	// 					frm.set_value('employee', r.message);
	// 				}
	// 			}
	// 		});
	// 	}
	// },
	after_save: function (frm) {
		if(frm.doc.canteen_charges > 0) {
			frappe.call({
				method: 'hrpro.hrpro.doctype.attendance_and_ot_register.attendance_and_ot_register.create_canteen_salary',
				args: {
					canteen: frm.doc.canteen_charges,
					payroll_date: frm.doc.start_date,
					employee : frm.doc.employee
				},
				callback: function (r) {
					if (r.message) {
					}
				}
			});
		}
		if(frm.doc.transport_charges > 0) {
			frappe.call({
				method: 'hrpro.hrpro.doctype.attendance_and_ot_register.attendance_and_ot_register.create_transport_salary',
				args: {
					transport: frm.doc.transport_charges,
					payroll_date: frm.doc.start_date,
					employee : frm.doc.employee
				},
				callback: function (r) {
					if (r.message) {
					}
				}
			});
		}
	}
});
