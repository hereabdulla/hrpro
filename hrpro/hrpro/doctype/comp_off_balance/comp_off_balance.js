// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Comp Off Balance', {
	comp_off_date: function(frm) {
		var validity = frappe.datetime.add_months(frm.doc.comp_off_date, 3)
		frm.set_value("validity", validity)
	}
});
