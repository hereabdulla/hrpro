// Copyright (c) 2018, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Travel Management', {
	 
	from_date: function(frm) {
        frm.trigger("calculate_total_days");
    },
    to_date: function(frm) {
        frm.trigger("calculate_total_days");
    },
    to_date_session: function(frm){
        frm.trigger("calculate_total_days")
    },
    from_date_session: function(frm){
        frm.trigger("calculate_total_days")
        if(frm.doc.from_date == frm.doc.to_date){
            frm.set_value("to_date_session", frm.doc.from_date_session)
        }
    },
    calculate_total_days: function(frm) {
        if(frm.doc.from_date && frm.doc.to_date && frm.doc.employee) {
            var date_dif = frappe.datetime.get_diff(frm.doc.to_date, frm.doc.from_date) + 1
            return frappe.call({
                "method": 'hrpro.hrpro.doctype.travel_management.travel_management.get_number_of_leave_days',
                args: {
                    "employee": frm.doc.employee,
                    "from_date": frm.doc.from_date,
                    "from_date_session":frm.doc.from_date_session,
                    "to_date": frm.doc.to_date,
                    "to_date_session":frm.doc.to_date_session,
                    "date_dif": date_dif
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('total_number_of_days', r.message);
                        frm.trigger("get_leave_balance");
                    }
                }
            });
        }
    },
    validate: function(frm){
        frappe.call({
            "method": 'hrpro.hrpro.doctype.on_duty_application.on_duty_application.check_attendance',
            args: {
                "employee": frm.doc.employee,
                "from_date": frm.doc.from_date,
                "to_date": frm.doc.to_date
            },
            callback: function(r) {
                if (r.message) {
                    $.each(r.message, function(i, d) {
                        if(d.status == "Present"){
                            frappe.msgprint("Attendance already Marked as Present for "+d.attendance_date)
                            frappe.validated = false;
                        } else if(d.status == "Half Day"){
                            if(frm.doc.from_date == frm.doc.to_date){
                                if(frm.doc.from_date_session == "Full Day"){
                                    frappe.msgprint("Attendance already Marked as Half Day for "+d.attendance_date)
                                    frappe.validated = false;
                                } 
                            } else if(frm.doc.from_date != frm.doc.to_date){
                                if((frm.doc.from_date_session == "Full Day") || (frm.doc.to_date_session == "Full Day")){
                                    frappe.msgprint("Attendance already Marked as Half Day for "+d.attendance_date)
                                    frappe.validated = false;
                                }
                            
                        }
                    }
                    })
                }
            }
        });
    },
    // after_save: function(frm){
    //         if(frm.doc.docstatus != 1){
    //             frappe.call({
    //                 "method": 'hrpro.hrpro.doctype.travel_management.travel_management.create_tour_application',
    //                 args:{
    //                     "travel_management": frm.doc.name
    //                 },
    //                 callback: function(r){
    //                 console.log(r.message)    
    //                 frappe.call({
    //                     "method": "frappe.client.set_value",
    //                     "args": {
    //                     "doctype": "Travel Management",
    //                     "name": frm.doc.name,
    //                     "fieldname": "tour_application",
    //                     "value":r.message
    //                     },
    //                 })
    //                 }
    //             })

    //         }
            
        
    // },
   
});
