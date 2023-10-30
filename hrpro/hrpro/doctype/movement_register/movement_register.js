// Copyright (c) 2018, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Movement Register', {
	refresh:function(frm){
		// var from_time_picker = frm.fields_dict.from_time.datepicker;
		// var pre = frappe.datetime.add_days(frappe.datetime.now_date(), -5);
		// var nxt = frappe.datetime.add_days(frappe.datetime.now_date(), 5);
		// from_time_picker.update({
		// 	showSecond: false,
		// 	maxSeconds: 00,
		// 	minDate: frappe.datetime.str_to_obj(pre),
		// 	maxDate: frappe.datetime.str_to_obj(nxt)
		// })
		// var to_time_picker = frm.fields_dict.to_time.datepicker;
		// to_time_picker.update({
		// 	showSecond: false,
		// 	maxSeconds: 00,
		// 	minDate: frappe.datetime.str_to_obj(pre),
		// 	maxDate: frappe.datetime.str_to_obj(nxt)
		// })
		if(frm.doc.is_from_ar){
            frm.add_custom_button(__('Back'), function () {
                frappe.set_route("query-report", "Attendance recapitulation")
            });
        }
	},
	validate: function(frm){
		// var from_time_picker = frm.fields_dict.from_time.datepicker;
		// var to_time_picker = frm.fields_dict.to_time.datepicker.date;
		// var pre = frappe.datetime.add_days(frappe.datetime.now_date(), -2);
		// var nxt = frappe.datetime.add_days(frappe.datetime.now_date(), 2);
		// console.log(from_time_picker)
		// console.log(pre)
		// if(from_time_picker < pre || to_time_picker > nxt){
		// 	frappe.msgprint(__("Date Exceeds Maximum Application Period"));
		// 	validated = false;
		// }
		if(frm.doc.is_from_ar == "Yes"){
            frappe.set_route("query-report", "Attendance recapitulation")
        }
	},
	// onload: function(frm){
	// 	frappe.call({
	// 		"method": "hrpro.custom.update_mr_in_att",
	// 		args:{
	// 			"employee": frm.doc.employee,
	// 			"from_time": frm.doc.from_time,
	// 			"to_time": frm.doc.to_time,
	// 			"total_permission_hour": frm.doc.total_permission_hour
	// 		},
	// 		callback: function(r){

	// 		}
	// 	})
	// }
});
