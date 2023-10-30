// Copyright (c) 2021, teamPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shift Register', {
	refresh: function(frm) {
		frm.add_custom_button(
			'Mark Attendance',
			() => frm.call({
				doc: frm.doc,
				method: 'process_auto_attendance',
				freeze: true,
				callback: () => {
					frappe.msgprint(__("Attendance has been marked as per employee check-ins"));
				}
			})
		);
	}
});
