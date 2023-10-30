// Copyright (c) 2021, TeamPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shift Allocation', {
	setup: function(frm) {
		frm.set_query("approver", function() {
			return {
				query: "hrpro.hrpro.doctype.shift_allocation.shift_allocation.get_approvers",
				filters: {
					employee: frm.doc.employee,
					doctype: frm.doc.doctype
				}
			};
		});
		frm.set_query("employee", erpnext.queries.employee);
	},
});
