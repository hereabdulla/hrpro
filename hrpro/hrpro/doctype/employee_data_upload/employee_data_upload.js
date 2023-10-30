// Copyright (c) 2020, TeamPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Data Upload', {
	// refresh: function(frm) {

	// }
	after_save: function (frm) {
		frappe.call({
			method: 'hrpro.hrpro.doctype.employee_data_upload.employee_data_upload.mail_alert',
			args: {
				number_of_employee: frm.doc.number_of_employee,
				site: frm.doc.site
			},
			callback: function (r) {
				if (r.message) {
					// frm.set_value('end_date', r.message.end_date);
					
				}
			}
		});
	},
});
