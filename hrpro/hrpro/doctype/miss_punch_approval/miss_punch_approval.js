// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Miss Punch Approval', {
        refresh: function (frm) {
                frm.disable_save();
        },
        onload: function (frm, cdt, cdn) {
                frappe.breadcrumbs.add("HR");
                $(".grid-add-row").hide();
                $(".grid-remove-rows").hide();
                $(":input[data-fieldname='approved']").addClass('btn-success');
                $(":input[data-fieldname='rejected']").addClass('btn-danger');
                frappe.call({
                        "method": "frappe.client.get_list",
                        args: {
                                "doctype": "Miss Punch Application",
                                filters: { "docstatus": 0, "status": "Applied" }
                        },
                        callback: function (r) {
                                if (r.message) {
                                        $.each(r.message, function (i, d) {
                                                frappe.call({
                                                        "method": "frappe.client.get",
                                                        args: {
                                                                "doctype": "Miss Punch Application",
                                                                "name": d.name
                                                        },
                                                        callback: function (r) {
                                                                if (r.message) {
                                                                        if ((frappe.session.user == r.message.approver) || (frappe.user.has_role("System Manager"))) {
                                                                                var row = frappe.model.add_child(frm.doc, "Miss Punch Approval Process", "miss_punch_approval_process");
                                                                                row.miss_punch_application = r.message.name;
                                                                                row.employee_name = r.message.employee_name;
                                                                                row.in_time = r.message.in_time;
                                                                                row.out_time = r.message.out_time;
                                                                                row.attendance_date = r.message.attendance_date;
                                                                                row.reason = r.message.reason;
                                                                                row.approved = 0;
                                                                                row.rejected = 0;
                                                                        }
                                                                        refresh_field("miss_punch_approval_process");
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
                                "doctype": "Miss Punch Application",
                                filters: { "docstatus": 1, "status": "Approved" }
                        },
                        callback: function (r) {
                                if (r.message) {
                                        $.each(r.message, function (i, d) {
                                                frappe.call({
                                                        "method": "frappe.client.get",
                                                        args: {
                                                                "doctype": "Miss Punch Application",
                                                                "name": d.name
                                                        },
                                                        callback: function (r) {
                                                                if (r.message) {
                                                                        if ((frappe.session.user == r.message.approver) || (frappe.user.has_role("System Manager"))) {
                                                                                var row = frappe.model.add_child(frm.doc, "Miss Punch Approval Process1", "miss_punch_approval_process1");
                                                                                row.miss_punch_application = r.message.name;
                                                                                row.employee_name = r.message.employee_name;
                                                                                row.in_time = r.message.in_time;
                                                                                row.out_time = r.message.out_time;
                                                                                row.attendance_date = r.message.attendance_date;
                                                                                row.reason = r.message.reason;
                                                                                row.approved = 0;
                                                                                row.rejected = 0;
                                                                        }
                                                                        refresh_field("miss_punch_approval_process1");
                                                                }
                                                        }
                                                })
                                        })
                                }
                        }
                })
        },
        approved: function (frm, cdt, cdn) {
                var grid = frm.fields_dict["miss_punch_approval_process"].grid;
                if (grid.get_selected_children().length !== 0) {
                        $.each(grid.get_selected_children(), function (i, d) {
                                frappe.call({
                                        "method": "hrpro.custom.update_miss_punch_approval",
                                        "args": {
                                                "doc": d.miss_punch_application,
                                                "status": "Approved"
                                        },
                                        callback: function (r) {
                                        }
                                })
                        })
                        frappe.msgprint("Status Updated Successfully")
                        //    setTimeout(function() { location.reload() }, 3000);

                }
        },
        rejected: function (frm, cdt, cdn) {
                var grid = frm.fields_dict["miss_punch_approval_process"].grid;
                if (grid.get_selected_children().length !== 0) {
                        $.each(grid.get_selected_children(), function (i, d) {
                                frappe.call({
                                        "method": "hrpro.custom.update_miss_punch_approval",
                                        "args": {
                                                "doc": d.on_duty_application,
                                                "status": "Rejected"
                                        },
                                        callback: function (r) {
                                        }
                                })
                        })
                        frappe.msgprint("Status Updated Successfully")
                        //   setTimeout(function() { location.reload() }, 3000);

                }
        },

})	