// Copyright (c) 2020, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Induction Test', {
	refresh: function (frm) {
		if (frappe.user.has_role("Employee")) {
			cur_frm.toggle_display("total_score", false)
			var df = frappe.meta.get_docfield("Test Questions", "score", cur_frm.doc.name);
			df.read_only = 1;
			// console.log(df)
			var df = frappe.meta.get_docfield("Test Questions", "question", cur_frm.doc.name);
			df.read_only = 1;
			
		}
		
		if (frappe.user.has_role("HOD")) {
			cur_frm.toggle_display("total_score", true)
			var df = frappe.meta.get_docfield("Test Questions", "question", cur_frm.doc.name);
			df.read_only = 1;
			var df = frappe.meta.get_docfield("Test Questions", "answers", cur_frm.doc.name);
			df.read_only = 1;
			var df = frappe.meta.get_docfield("Test Questions", "score", cur_frm.doc.name);
			df.read_only = 0;
		}
		cur_frm.fields_dict['questions'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['questions'].grid.wrapper.find('.grid-remove-rows').hide();
	},
	validate(frm) {
		$.each(frm.doc.questions, function (i, d) {
			if(d.answers== ''){
				frappe.throw("Need to fill all rows in answers")
				frappe.validated =false;
			}
			else{
				frappe.validated=true;
			}
		})
		var total = 0
		$.each(frm.doc.questions, function (i, d) {
			if(d.score!= ''){
				total += Number(d.score)
				console.log(total)
			}
			else {
				frappe.throw("Need to fill all rows in score")
			}
		})
		frm.set_value("total_score", total)
		if (total > 50) {
			var today_date =frappe.datetime.nowdate()
			
			
			frappe.call({
				"method":"hrpro.hrpro.doctype.induction_test.induction_test.get_end_date",
				"args":{
				
				},
				callback: function(r){
					console.log(r)
					frappe.db.set_value('Employee', frm.doc.employee_id, {
						'employment_type': 'Probation',
						'probation_start_date': today_date,
						'probation_end_date' : r.message
					})
				}	
			})
		}
	},
    // before_submit(frm){
	// 	if (frm.doc.total_score < 50) {
	// 		frappe.validated=false
	// 		frappe.throw("Redo the induction")
	// 	}
	// },
});