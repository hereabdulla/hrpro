// Copyright (c) 2018, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('On Duty Application', {
    onload: function (frm) {
        if (frm.doc.workflow_state == 'Review Pending') {
            frm.fields_dict.approval_mark.$wrapper.empty()
            frm.fields_dict.html.$wrapper.empty()
        }
    },
    validate(frm) {
        //     if(frm.doc.from_date){
        //     var date = frappe.datetime.add_days(frm.doc.from_date,4 )
        // 	if(frappe.datetime.nowdate() > date){
        // 		frappe.throw("On Duty should be applied within 4 days")
        // 	}
        // }
        // if (!frappe.user.has_role('HR GM')) {
        //     if (frm.doc.to_date) {
        //         frappe.db.get_single_value('HR Time Settings', 'on_duty_validation_dates').then(value=>{
        //             var date = frappe.datetime.add_days(frm.doc.to_date, value)
        //             frappe.call({
        //                 "method": "thaisummit.utils.get_server_date",
        //                 callback(r) {
        //                     if (r.message > date) {
        //                         frappe.msgprint("On Duty should be applied within 3 days")
        //                         frappe.validated = false;
        //                     }
        //                 }
        //             })
        //         })
        //     }
        // }
        var multi = frm.doc.multi_employee
        if (multi.length == 0) {
            frappe.throw('Please choose at least one Employee')
        }
    },
    refresh: function (frm) {
        frm.ignore_user_permission = false
        frm.fields_dict.html.$wrapper.empty()
        frm.fields_dict.approval_mark.$wrapper.empty()
        if (!frm.is_new()) {
            if (frm.doc.workflow_state == 'Approved') {
                frm.call('show_html').then(r => {
                    frm.fields_dict.html.$wrapper.empty().append(r.message)
                })
            }
        }
        // $(frm.fields_dict.address.input).css({ 'font-weight':'bold' })
        // $(frm.fields_dict.from_date.input).css("backgroundColor", "DarkOrange");
        // frm.set_df_property("from_date", "label", "<strong>From Date</string>")
        // frm.set_df_property("from_date", "value", "<strong>20-05-2021</string>")

        // frm.set_df_property("address", "bold",1)
        // a = frm.get_docfield("address")
        // console.log(a)

        frappe.breadcrumbs.add("HR", "On Duty Application");
        if (!frm.is_new()) {
            if (frm.doc.workflow_state == 'Approved') {
                frm.fields_dict.approval_mark.$wrapper.empty().append('<img src="/files/approved.jpg" alt="Approved" width="300" height="200">');
            }
        }
        if (frm.doc.__islocal) {
            frappe.call({
                method: 'hrpro.hrpro.doctype.on_duty_application.on_duty_application.get_employees',
                args: {

                },
                // "method": "frappe.client.get_value",
                // args: {
                //     doctype: "Employee",
                //     filters: { "user_id": frappe.session.user },
                //     fieldname: ["name", "employee_name", "department", "designation"]
                // },
                callback: function (r) {
                    frm.set_value("employee", r.message[0])
                    frm.set_value("employee_name", r.message[1])
                    frm.add_child("multi_employee", {
                        "employee": r.message[0],
                        "employee_name": r.message[1],
                        "department": r.message[2],
                        "designation": r.message[3]
                    })
                    frm.refresh_field('multi_employee')
                    if (r.message[2]) {
                        if (frappe.user.has_role('GM')) {
                            frm.call('get_ceo', { department: r.message[2] }).then(r => {
                                frm.set_value('approver', r.message)
                            })
                        }
                        else if (frappe.user.has_role('HOD')) {
                            frm.call('get_gm', { department: r.message[2] }).then(r => {
                                frm.set_value('approver', r.message)
                            })
                        }
                        else {
                            frm.call('get_hod', { department: r.message[2] }).then(r => {
                                frm.set_value('approver', r.message)
                            })
                        }
                    }
                }
            })
        }
    },
    from_date: function (frm) {
        // if(frm.doc.from_date){
        // var date = frappe.datetime.add_days(frm.doc.from_date,4 )
        // if(frappe.datetime.nowdate() > date){
        // 	frappe.throw("On Duty should be applied within 4 days")
        // }
        // }
        frm.trigger('validate_cutoff')
        frm.trigger("calculate_total_days")
        // frm.trigger("allowed_from_date")
        if (frm.doc.to_date && frm.doc.from_date) {
            if (frm.doc.from_date != frm.doc.to_date) {
                if (frm.doc.from_date < frm.doc.to_date) {
                    frm.trigger("calculate_total_days")
                } else {
                    validated = false
                    frappe.msgprint("From Date Must be Lesser than or Equal to To Date")
                    frm.set_value("from_date", "")
                }
            }
        }


    },
    to_date: function (frm) {
        // if (!frappe.user.has_role('HR GM')) {
        //     if (frm.doc.to_date) {
        //         frappe.db.get_single_value('HR Time Settings', 'on_duty_validation_dates').then(value => {
        //             var date = frappe.datetime.add_days(frm.doc.to_date, value)
        //             frappe.call({
        //                 "method": "thaisummit.utils.get_server_date",
        //                 callback(r) {
        //                     if (r.message > date) {
        //                         frappe.msgprint("On Duty should be applied within 3 days")
        //                         frappe.validated = false;
        //                     }
        //                 }
        //             })
        //         })

        //     }
        // }
        frm.trigger("calculate_total_days")
        frm.trigger("allowed_from_to_date")
        if (frm.doc.from_date && frm.doc.to_date) {
            if (frm.doc.from_date != frm.doc.to_date) {
                if (frm.doc.from_date < frm.doc.to_date) {
                    frm.trigger("calculate_total_days")
                } else {
                    validated = false
                    frappe.msgprint("To Date Must be Greater than or Equal to From Date")
                    frm.set_value("to_date", "")
                }
            }
        }
    },
    // allowed_from_date(frm) {
    //     if (frm.doc.from_date) {
    //         frappe.call({
    //             method: 'thaisummit.custom.application_allowed_from',
    //             args: {
    //                 date: frm.doc.from_date
    //             },
    //             callback(r) {
    //                 if (r.message == 'NO') {
    //                     frm.set_value('from_date', '')
    //                 }
    //             }
    //         })
    //     }
    // },
    // allowed_from_to_date(frm) {
    //     if (frm.doc.to_date) {
    //         frappe.call({
    //             method: 'thaisummit.custom.application_allowed_from',
    //             args: {
    //                 date: frm.doc.to_date
    //             },
    //             callback(r) {
    //                 if (r.message == 'NO') {
    //                     frm.set_value('to_date', '')
    //                 }
    //             }
    //         })
    //     }
    // },
    from_date_session: function (frm) {
        frm.trigger("calculate_total_days")
    },
    calculate_total_days: function (frm) {
        if (frm.doc.from_date && frm.doc.to_date && frm.doc.employee) {
            var date_dif = frappe.datetime.get_diff(frm.doc.to_date, frm.doc.from_date) + 1
            return frappe.call({
                "method": 'hrpro.hrpro.doctype.on_duty_application.on_duty_application.get_number_of_leave_days',
                args: {
                    "employee": frm.doc.employee,
                    "from_date": frm.doc.from_date,
                    "from_date_session": frm.doc.from_date_session,
                    "to_date": frm.doc.to_date,
                    "date_dif": date_dif
                },
                callback: function (r) {
                    if (r.message) {
                        frm.set_value('total_number_of_days', r.message);
                    }
                }
            });
        }
    }
});


