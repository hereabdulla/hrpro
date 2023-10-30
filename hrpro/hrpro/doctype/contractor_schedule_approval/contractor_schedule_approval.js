// Copyright (c) 2021, TeamPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Contractor Schedule Approval', {
	refresh: function(frm) {
		frm.disable_save()
	},
	start_date: function(frm) {
		if(frm.doc.start_date){
		frappe.call({
			method: 'erpnext.payroll.doctype.payroll_entry.payroll_entry.get_end_date',
			args: {
				frequency: "Monthly",
				start_date: frm.doc.start_date
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value('end_date', r.message.end_date);
					if(frm.doc.contractor && frm.doc.plant){
						frm.trigger('fetch')
				}
				}
			}
		});
	}
	},
	contractor(frm){
		if(frm.doc.start_date && frm.doc.end_date && frm.doc.plant){
				frm.trigger('fetch')
		}
	},
	plant(frm){
		if(frm.doc.start_date && frm.doc.end_date && frm.doc.contractor){
				frm.trigger('fetch')
		}
	},
	fetch(frm){
		frm.call('fetch_count')
		.then(r=>{
			frm.clear_table('manpower_count')
			console.log(r.message)
			$.each(r.message,function(i,v){
				frm.add_child('manpower_count', {
					department: v.department,
					shift_type:v.shift_type,
					contract_type:v.contract_type,
					manpower_count:v.count,
					id:v.name
				});
				frm.refresh_field('manpower_count');
			})
		})
	},
	submit(frm){
		frm.call('submit_count')
		.then(r=>{
			
		})
	}
});