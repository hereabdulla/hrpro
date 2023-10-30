// Copyright (c) 2020, TeamPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Client Invoice', {
	// refresh: function(frm) {

	// }
	// company_name:function(frm){
	// 	if (frm.doc.company_name)
	// 	{
	// 		frappe.call({
	// 			method:"boss.boss.doctype.client_invoice.client_invoice.get_default_company_address",
	// 			args:{name:frm.doc.company_name, existing_address: frm.doc.company_address},
	// 			callback: function(r){
	// 				if (r.message){
	// 					console.log(r.message)
	// 					frm.set_value("company_address",r.message)
	// 				}
	// 				else {
	// 					frm.set_value("company_address","")
	// 				}
	// 			}
	// 		})
	// 	}
	// },
	start_date: function (frm) {
		frappe.call({
			method: 'hrpro.hrpro.doctype.client_invoice.client_invoice.get_end_date',
			args: {
				frequency: "monthly",
				start_date: frm.doc.start_date
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value('end_date', r.message.end_date);
				}
			}
		});
	},
	get_details: function (frm) {
		frappe.call({
			method: 'hrpro.hrpro.doctype.client_invoice.client_invoice.invoice_item',
			args: {
				start_date: frm.doc.start_date,
				end_date: frm.doc.end_date,
				company: frm.doc.company_name,
				client: frm.doc.client_name,
				site: frm.doc.site
			},
			callback: function (r) {
				if (r.message) {
					frm.add_child('items', {
						item: 'Manpower Deployment charges',
						description: r.message[8],
						quantity: r.message[3],
						amount:r.message[2]
					});
					frm.add_child('items',{
						item: 'Over Time Cost',
						description: r.message[0]+" OT Hours",
						quantity: r.message[4],
						amount:r.message[1]
					});
					frm.refresh_field('items');
					frm.add_child('taxes',{
						item: 'CGST @ 9%',
						amount:r.message[6]
					});
					frm.add_child('taxes',{
						item: 'SGST @ 9%',
						amount:r.message[6]
					});
					frm.refresh_field('taxes');
					frm.set_value('net_amount', r.message[5]);
					frm.set_value('tax_amount', r.message[6]+r.message[6]);
					frm.set_value('grand_total', r.message[7]);
					frm.set_value('total_in_words', r.message[9]);				
					console.log(r.message[0])
					console.log(r.message[1])
					console.log(r.message[2])
					console.log(r.message[3])
					console.log(r.message[4])
					console.log(r.message[5])
					console.log(r.message[6])
					console.log(r.message[7])
					// frm.set_value('end_date', r.message.end_date);
				}
			}
		});
	}
});
