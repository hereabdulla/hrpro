// Copyright (c) 2020, TeamPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Statutory Detail', {
	// refresh: function(frm) {

	// },
	get_details: function (frm) {
		frappe.call({
			method: 'hrpro.hrpro.doctype.statutory_detail.statutory_detail.statutory_item',
			args: {
				employee: frm.doc.employee
			},
			callback: function (r) {
				if (r.message) {
					$.each(r.message, function(i, d) {
						frm.add_child('item', {
							salary_slip: d.salary_slip,
							month: d.month,
							year:d.year,
							basic_and_da:d.basic + d.da,
							pf: d.pf,
							esi: d.esi,
							pt: d.pt,
							bonus: d.bonus
						});
						frm.refresh_field('item');
					})
				}
			}
		});
	},
	employee: function (frm){
		var age = calculate_age(frm.doc.date_of_join)
		console.log("age")
		console.log(age)
		frm.set_value('employment_age', age);
	},
	calculate_gratuity: function (frm) {
		frappe.call({
			method: 'hrpro.hrpro.doctype.statutory_detail.statutory_detail.get_gratuity',
			args: {
				employee: frm.doc.employee,
				age: frm.doc.employment_age,
				join: frm.doc.date_of_join
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value('gratuity_amount', r.message);
				}
			}
		});
	},
});

let calculate_age = function (birth) {		
	let ageMS = Date.parse(Date()) - Date.parse(birth);
	let age = new Date();
	age.setTime(ageMS);
	let years = age.getFullYear() - 1970;
	return years
};
