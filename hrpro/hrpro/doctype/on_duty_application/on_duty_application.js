// Copyright (c) 2018, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('On Duty Application', {
    onload:function(frm){
        if(frm.doc.workflow_state == 'Review Pending'){
            frm.fields_dict.approval_mark.$wrapper.empty()
            frm.fields_dict.html.$wrapper.empty()
        }
        
    },
    refresh: function (frm) {
        frm.fields_dict.html.$wrapper.empty()
        frm.fields_dict.approval_mark.$wrapper.empty()
        if(!frm.is_new()){
        if (frm.doc.workflow_state == 'Approved') {
            frm.call('show_html').then(r=>{
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

        frappe.breadcrumbs.add("HR","On Duty Application");
        if(!frm.is_new()){
        if(frm.doc.workflow_state == 'Approved'){
            frm.fields_dict.approval_mark.$wrapper.empty().append('<img src="/files/approved.jpg" alt="Approved" width="300" height="200">');
        }
    }
        if(frm.doc.__islocal){
        frappe.call({
            "method":"frappe.client.get_value",
            args: {
				doctype: "Employee",
				filters: {"user_id": frappe.session.user},
				fieldname: ["name","employee_name","department","designation"]
			},
			callback: function(r){
                frm.add_child("multi_employee",{
                    "employee":r.message.name,
                    "employee_name":r.message.employee_name,
                    "department":r.message.department,
                    "designation":r.message.designation
                })
                frm.refresh_field('multi_employee')
                frappe.call({
                    "method":"frappe.client.get_value",
                    args: {
                        doctype: "Department",
                        filters: {"name": r.message.department},
                        fieldname: ["on_duty_approver"]
                    },
                    callback: function(r){
                        if (r.message){
                            frm.set_value("approver",r.message.on_duty_approver)
                        }
                    }
                })
            }
        })
    }
    },
    from_date: function (frm) {
        frm.trigger('validate_cutoff')
        frm.trigger("calculate_total_days")
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
        frm.trigger("calculate_total_days")
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


