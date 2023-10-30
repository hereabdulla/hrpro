// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Settings', {
	refresh: function(frm) {
		frm.disable_save()
		frm.set_value('from_date',frappe.datetime.nowdate())
		if (frappe.session.user != 'Administrator'){
			hide_field('mark_permission')
			hide_field('mark_on_duty')
			hide_field('section_break_8')
			hide_field('application_cut_off_dates')
			hide_field('section_break_15')
			hide_field('update_checkin_section')
		}
	},
	process_attendance(frm){
		frappe.call({
			"method": "thaisummit.mark_attendance.mark_att",
			"args":{
				"from_date" : frm.doc.from_date,
			},
			freeze: true,
			freeze_message: 'Processing Attendance....',
			callback(r){
				console.log(r.message)
				if(r.message == "ok"){
					frappe.msgprint("Attendance is Marking in the Background. Kindly check after sometime")
				}
			}
		})
	},
	process_overtime(frm){
		frappe.call({
			"method": "thaisummit.mark_attendance.process_overtime",
			"args":{
				"from_date" : frm.doc.from_date,
			},
			freeze: true,
			freeze_message: 'Processing Overtime....',
			callback(r){
				console.log(r.message)
				if(r.message == "ok"){
					frappe.msgprint("Overtime is Marking in the Background. Kindly check after sometime")
				}
			}
		})
	},
	submit_attendance(frm){
		frappe.call({
			"method": "thaisummit.mark_attendance.submit_att",
			"args":{
				"employee_type": frm.doc.employee_type,
				"from_date" : frm.doc.from_date,
			},
			freeze: true,
			freeze_message: 'Submitted Attendance....',
			callback(r){
				if(r.message == "ok"){
					// frappe.msgprint("Attendance Marked Successfully")
				}
			}
		})
	},
	update_status(frm){
		frappe.call({
			"method": "thaisummit.mark_attendance.mark_shift_status",
			args:{
				from_date :frm.doc.from_date
			},
			freeze: true,
			freeze_message: 'Updating....',
			callback(r){
				if(r.message == "ok"){
					frappe.msgprint("Updated Successfully")
				}
			}
		})
	},
	view_salary_slip(frm){
		frappe.set_route('List', 'Salary Slip','Salary Slip');
	},
	urc_to_ec(frm){
		frappe.call({
			"method": "thaisummit.mark_attendance.get_urc_to_ec",
			"args":{
				"from_date" : frm.doc.from_date,
			},
			freeze: true,
			freeze_message: 'Processing UnRegistered Employee Checkin to Employee Checkin....',
			callback(r){
				console.log(r.message)
				if(r.message == "ok"){
					frappe.msgprint("Checkin's are created in Successfully")
				}
			}
		})
	},
});
