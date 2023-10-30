// Copyright (c) 2021, TeamPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shift Swapping', {
	// refresh: function(frm) {

	// }
	shift_date:function(frm){
		if(frm.doc.shift_date){
			frappe.call({
				method: 'hrpro.hrpro.doctype.shift_swapping.shift_swapping.allocated_shift',
				args: {
					employee: frm.doc.employee,
					shift_date: frm.doc.shift_date
				},
				callback: function (r) {
					if (r.message) {
						frm.set_value('shift_type', r.message[0].shift_type);
					}
				}
			});
		}
	},
	swap_to:function(frm){
		if (frm.doc.swap_to){
			frappe.call({
				method: 'hrpro.hrpro.doctype.shift_swapping.shift_swapping.shift_details',
				args: {
					employee: frm.doc.employee,
					shift_date: frm.doc.shift_date,
					swap_to: frm.doc.swap_to
				},
				callback: function (r) {
					if (r.message) {
						var emp_shift = r.message[1][0].shift_type
						var swap_shift = r.message[0][0].shift_type
						frm.clear_table("shift_detail");
						$.each(r.message[0], function(i, d) {
							frm.add_child('shift_detail', {
								employee: d.employee,
								shift_date: d.start_date,
								allocated_shift:d.shift_type,
								shift_assign_to:swap_shift
							});
						})
						$.each(r.message[1], function(i, d) {
							frm.add_child('shift_detail', {
								employee: d.employee,
								shift_date: d.start_date,
								allocated_shift:d.shift_type,
								shift_assign_to:emp_shift
							});
							frm.refresh_field('shift_detail');
						})
					}
				}
			});
		}
	}
});
