// Copyright (c) 2021, TeamPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Full and Final Settlement', {
	employee: function(frm) {
			if (frm.doc.employee) {
				frappe.call({
					method: "erpnext.hr.doctype.leave_application.leave_application.get_leave_details",
					args: {
						employee: frm.doc.employee,
						date: frm.doc.posting_date
					},
					callback: function(r) {
						$.each(r.message["leave_allocation"], function (i, d) {
							var row = frappe.model.add_child(frm.doc, "Leave Balance List", "leave_balance_list")
							row.leave_type = i
							row.total_allocated_leaves = d.total_leaves
							row.used_leaves = d.leaves_taken
							row.leave_balance = d.remaining_leaves
						})
						refresh_field("leave_balance_list")
					}
				})
				frappe.call({
					method: "hrpro.hrpro.doctype.full_and_final_settlement.full_and_final_settlement.create_salary_slip",
					args: {
						employee: frm.doc.employee,
						date: frm.doc.posting_date
					},
					callback: function(r) {
						frm.set_value("salary_slip_id",r.message[0])
						frm.set_value("gross_pay",r.message[3])
						frm.set_value("total_deduction",r.message[4])
						frm.set_value("net_pay",r.message[5])
						$.each(r.message[1], function (i, d) {
							var row = frappe.model.add_child(frm.doc, "FNF Earnings", "fnf_earnings")
							row.salary_component = d.salary_component
							row.amount = d.amount
						})
						refresh_field("fnf_earnings")
						$.each(r.message[2], function (i, d) {
							var row = frappe.model.add_child(frm.doc, "FNF Deductions", "fnf_deductions")
							row.salary_component = d.salary_component
							row.amount = d.amount
						})
						refresh_field("fnf_deductions")
					}
				})
		}
	}
});
