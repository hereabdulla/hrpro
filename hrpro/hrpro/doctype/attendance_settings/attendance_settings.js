// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Settings', {
	refresh: function(frm) {
		frm.disable_save()
		frm.set_value('from_date',frappe.datetime.nowdate())
	},
	// mark_permission(frm){
	// 	frm.call({
	// 		doc: frm.doc,
	// 		method: 'mark_permission',
	// 		freeze: true,
	// 		callback: () => {
	// 			frappe.msgprint(__("Permission Marked Success"));
	// 		}
	// 	})
	// },
	// mark_on_duty(frm){
	// 	console.log("hi")
	// 	frm.call({
	// 		doc: frm.doc,
	// 		method: 'mark_od',
	// 		freeze: true,
	// 		callback: () => {
	// 			frappe.msgprint(__("On Duty Marked Success"));
	// 		}
	// 	})
	// },
	process_attendance(frm){
		frappe.call({
			"method": "thaisummit.mark_attendance.mark_att",
			"args":{
				"from_date" : frm.doc.from_date,
			},
			freeze: true,
			freeze_message: 'Processing Attendance....',
			callback(r){
				if(r.message == "ok"){
					// frappe.msgprint("Attendance Marked Successfully")
				}
			}
		})
	}
});
