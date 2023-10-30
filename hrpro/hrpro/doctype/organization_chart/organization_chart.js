// Copyright (c) 2021, TeamPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Organization Chart', {
	refresh:function(frm){
		frm.fields_dict.chart.$wrapper.append(frappe.render_template("organization_chart"));
	}
});