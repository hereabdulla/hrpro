frappe.ui.form.on('On Duty Approval', {
	onload: function (frm, cdt, cdn) {
		frappe.breadcrumbs.add("HR");
		$(".grid-add-row").hide();
		$(".grid-remove-rows").hide();
		$(":input[data-fieldname='approved']").addClass('btn-success');
		$(":input[data-fieldname='rejected']").addClass('btn-danger');
		frappe.call({
			"method": "frappe.client.get_list",
			args: {
				"doctype": "On Duty Application",
				filters: { "docstatus": 0, "status": ["in",["Applied","Approved"]]},
				limit_page_length:50
			},
			callback: function (r) {
				if (r.message) {
					$.each(r.message, function (i, d) {
						frappe.call({
							"method": "frappe.client.get",
							args: {
								"doctype": "On Duty Application",
								"name": d.name
							},
							callback: function (r) {
								if (r.message) {
									if ((frappe.session.user == r.message.approver) || (frappe.user.has_role("System Manager"))) {
										var row = frappe.model.add_child(frm.doc, "On Duty Approval Process", "on_duty_application_management_process");
										row.on_duty_application = r.message.name;
										row.employee_name = r.message.employee_name;
										row.from_date = r.message.from_date;
										row.to_date = r.message.to_date;
										row.no_of_days = r.message.total_number_of_days;
										row.reason = r.message.description;
										row.approved = 0;
										row.rejected = 0;
									}
									refresh_field("on_duty_application_management_process");
								}
							}
						})
					})
				}
			}
		})
		frappe.call({
			"method": "frappe.client.get_list",
			args: {
				"doctype": "On Duty Application",
				filters: { "docstatus": 1, "status": "Approved"},
				limit_page_length:50
			},
			callback: function (r) {
				if (r.message) {
					$.each(r.message, function (i, d) {
						frappe.call({
							"method": "frappe.client.get",
							args: {
								"doctype": "On Duty Application",
								"name": d.name
							},
							callback: function (r) {
								if (r.message) {
									if ((frappe.session.user == r.message.approver) || (frappe.user.has_role("System Manager"))) {
										var row = frappe.model.add_child(frm.doc, "On Duty Approval Process", "on_duty_approval_process");
										row.on_duty_application = r.message.name;
										row.employee_name = r.message.employee_name;
										row.from_date = r.message.from_date;
										row.to_date = r.message.to_date;
										row.no_of_days = r.message.total_number_of_days;
										row.reason = r.message.description;
										row.approved = 0;
										row.rejected = 0;
									}
									refresh_field("on_duty_approval_process");
								}
							}
						})
					})
				}
			}
		})
	},
	refresh: function (frm) {
		frm.disable_save();
	},
	approved: function (frm, cdt, cdn) {
		var grid = frm.fields_dict["on_duty_application_management_process"].grid;
		if (grid.get_selected_children().length !== 0) {
			$.each(grid.get_selected_children(), function (i, d) {
				frappe.call({
					"method": "hrpro.custom.update_onduty_approval",
					"args": {
						"doc": d.on_duty_application,
						"status": "Approved"
					},
					callback: function (r) {
					}
				})
			})
			frappe.msgprint("Status Updated Successfully")
			setTimeout(function () { location.reload() }, 3000);

		}
	},
	rejected: function (frm, cdt, cdn) {
		var grid = frm.fields_dict["on_duty_application_management_process"].grid;
		if (grid.get_selected_children().length !== 0) {
			$.each(grid.get_selected_children(), function (i, d) {
				frappe.call({
					"method": "hrpro.custom.update_onduty_approval",
					"args": {
						"doc": d.on_duty_application,
						"status": "Rejected"
					},
					callback: function (r) {
					}
				})
			})
			frappe.msgprint("Status Updated Successfully")
			setTimeout(function () { location.reload() }, 3000);

		}
	},
	to_date: function (frm) {
		frm.trigger("filtered")
	},
	from_date: function (frm) {
		frm.trigger("filtered")
	},

	filtered:function(frm){
	frm.clear_table("on_duty_application_management_process");
		frm.clear_table("on_duty_approval_process");
		frappe.call({
			"method": "frappe.client.get_list",
			args: {
				"doctype": "On Duty Application",
				filters: { "docstatus": 0, "status": "Applied", "from_date":['>=',frm.doc.from_date],"to_date":['<=',frm.doc.to_date] },
				limit_page_lengt:50
			},
			callback: function (r) {
				if (r.message) {
					$.each(r.message, function (i, d) {
						frappe.call({
							"method": "frappe.client.get",
							args: {
								"doctype": "On Duty Application",
								"name": d.name
							},
							callback: function (r) {
								if (r.message) {
									if ((frappe.session.user == r.message.approver) && ((frm.doc.from_date <= r.message.from_date) && (frm.doc.to_date >= r.message.to_date)) || (frappe.user.has_role("System Manager"))) {
										var row = frappe.model.add_child(frm.doc, "On Duty Approval Process", "on_duty_application_management_process");
										row.on_duty_application = r.message.name;
										row.employee_name = r.message.employee_name;
										row.from_date = r.message.from_date;
										row.to_date = r.message.to_date;
										row.no_of_days = r.message.total_number_of_days;
										row.approved = 0;
										row.rejected = 0;
									}
									refresh_field("on_duty_application_management_process");
								}
							}
						})
					})
				}
			}
		})
		frappe.call({
			"method": "frappe.client.get_list",
			args: {
				"doctype": "On Duty Application",
				filters: { "docstatus": 1, "status": "Approved","from_date":['>=',frm.doc.from_date],"to_date":['<=',frm.doc.to_date]}
			},
			callback: function (r) {
				if (r.message) {
					$.each(r.message, function (i, d) {
						frappe.call({
							"method": "frappe.client.get",
							args: {
								"doctype": "On Duty Application",
								"name": d.name
							},
							callback: function (r) {
								if (r.message) {
									if ((frappe.session.user == r.message.approver) && ((frm.doc.from_date <= r.message.from_date) && (frm.doc.to_date >= r.message.to_date)) || (frappe.user.has_role("System Manager"))) {
										var row = frappe.model.add_child(frm.doc, "On Duty Approval Process", "on_duty_approval_process");
										row.on_duty_application = r.message.name;
										row.employee_name = r.message.employee_name;
										row.from_date = r.message.from_date;
										row.to_date = r.message.to_date;
										row.no_of_days = r.message.total_number_of_days;

										row.approved = 0;
										row.rejected = 0;
									}
									refresh_field("on_duty_approval_process");
								}
							}
						})
					})
				}
			}
		})
	}
})	