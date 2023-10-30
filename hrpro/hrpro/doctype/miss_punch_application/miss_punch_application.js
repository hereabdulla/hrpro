// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Miss Punch Application', {
    refresh: function (frm) {
        // frm.disable_save()
        if (frm.doc.__islocal) {
            frappe.call({
                "method": "frappe.client.get_value",
                "args": {
                    "doctype": "Employee",
                    "filters": {
                        "user_id": frappe.session.user
                    },
                    "fieldname": ["employee", "employee_name"]
                },
                callback(r) {
                    if (r.message) {
                        frm.set_value("employee", r.message.employee)
                        frm.set_value("employee_name", r.message.employee_name)
                    }
                }
            })
        }
    },
    employee(frm) {
        if (frm.doc.attendance_date) {
            frm.trigger('get_att')
        }
    },
    attendance_date(frm) {
        if (frm.doc.attendance_date) {
            frm.trigger('get_att')
            var date = frappe.datetime.add_days(frm.doc.attendance_date, 2)
            if (!frappe.user.has_role('HR GM')) {
                frappe.call({
                    "method": "thaisummit.utils.get_server_dates",
                    "args":
                    {
                        from_date:frm.doc.attendance_date
                    },
                    callback(r) {
                        if (r.message == "ok") {
                            frm.disable_save();
                            frappe.msgprint("You cannot apply for Miss Punch ,because the period has Already Expired")
                            frappe.validated = false;
                        }
                    }
                })
            }
        }
    },
    get_att(frm) {
        frm.call('get_att')
            .then((att_list) => {
                if (att_list.message) {
                    console.log(att_list.message)
                    $.each(att_list.message, function (i, d) {
                        if (frm.doc.employee_type != 'WC') {
                            var c_list = [d.in_time, d.out_time, d.qr_shift]
                            if (c_list.includes(null)) {
                                frm.set_value('show_time', 1)
                                frm.set_value('attendance', d.name)
                                frm.set_value('in_time', d.in_time)
                                frm.set_value('out_time', d.out_time)
                                frm.set_value('qr_shift', d.qr_shift)
                            }
                            else {
                                frm.set_value('show_time', 0)
                                frm.set_value('attendance', d.name)
                                frm.set_value('in_time', '')
                                frm.set_value('out_time', '')
                                frm.set_value('qr_shift', '')
                            }
                        }
                        if (frm.doc.employee_type == 'WC') {
                            var c_list = [d.in_time, d.out_time]
                            console.log(c_list)
                            if (c_list.includes(null)) {
                                frm.set_value('show_time', 1)
                                frm.set_value('attendance', d.name)
                                frm.set_value('in_time', d.in_time)
                                frm.set_value('out_time', d.out_time)
                            }
                            else {
                                frm.set_value('show_time', 0)
                                frm.set_value('attendance', d.name)
                                frm.set_value('in_time', '')
                                frm.set_value('out_time', '')
                                frm.set_value('qr_shift', '')
                            }
                        }
                    })
                }
                else {
                    frm.set_value('show_time', 0)
                    frm.set_value('attendance', '')
                    frm.set_value('in_time', '')
                    frm.set_value('out_time', '')
                    frm.set_value('qr_shift', '')
                }
            })
    },
    validate: function (frm) {
        frm.trigger("attendance_date")
    }
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
