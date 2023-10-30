// Copyright (c) 2020, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Induction Goal', {
	before_load:function(frm){
		if(frappe.user.has_role("Employee") && frappe.user.has_role("HOD") ){
			var df = frappe.meta.get_docfield("Goal Induction", "reviewer", cur_frm.doc.name);
			df.hidden = 1;
		}
		else if(frappe.user.has_role("Employee") && frappe.user.has_role("One Above Manager") ){
			var df = frappe.meta.get_docfield("Goal Induction", "reviewer", cur_frm.doc.name);
			df.hidden = 1;
			var df = frappe.meta.get_docfield("Goal Induction", "hod", cur_frm.doc.name);
			df.hidden = 1;
		}
		else if(frappe.user.has_role("Employee") && frappe.user.has_role("Reviewer") ){
			var df = frappe.meta.get_docfield("Goal Induction", "reviewer", cur_frm.doc.name);
			df.hidden = 0;
			var df = frappe.meta.get_docfield("Goal Induction", "hod", cur_frm.doc.name);
			df.hidden = 0;
			var df = frappe.meta.get_docfield("Goal Induction", "manager", cur_frm.doc.name);
			df.hidden = 0;
		}
		else{
			var df = frappe.meta.get_docfield("Goal Induction", "manager", cur_frm.doc.name);
			df.hidden = 1;
			var df = frappe.meta.get_docfield("Goal Induction", "reviewer", cur_frm.doc.name);
			df.hidden = 1;
			var df = frappe.meta.get_docfield("Goal Induction", "hod", cur_frm.doc.name);
			df.hidden = 1;
			frm.refresh_fields();
		}
		
		
	},
	refresh: function(frm) {
		frm.toggle_display("reviewer",false)
		frm.toggle_display("reviewer_rating",false)
		frm.toggle_display("hod_rating",false)
		frm.toggle_display("manager_rating",false)
		if(frappe.user.has_role("Employee") && frappe.user.has_role("HOD") ){
			frm.toggle_display("hod_rating",true)
			frm.toggle_display("manager_rating",true)
			frm.toggle_display("self_rating",true)
		}
		else if(frappe.user.has_role("Employee") && frappe.user.has_role("One Above Manager") ){
			frm.toggle_display("manager_rating",true)
			frm.toggle_display("self_rating",true)
		}
		else if(frappe.user.has_role("Employee") && frappe.user.has_role("Reviewer") ){
			frm.toggle_display("reviewer",true)
			frm.toggle_display("reviewer_rating",true)
			frm.toggle_display("hod_rating",true)
			frm.toggle_display("manager_rating",true)
			frm.toggle_display("self_rating",true)
		}
		else{
			frm.toggle_display("self_rating",true)
		}	
		var child1 = frm.doc.goal;
        var len1 = child1.length;
        if (len1 == 0) {
            for (var i = 0; i < 5; i++) {
				var row = frappe.model.add_child(frm.doc, "Goal Induction", "goal");
            }
			refresh_field("goal")
		}

	},
	
	// make_default_row: function (frm) {
    //     var child1 =[]
		
	// },
	before_submit(frm) {
		if (frappe.user.has_role("Reviewer")) {
			if(frm.doc.reviewer=="Confirmed"){
				frappe.db.set_value("Employee", frm.doc.employee_id, "status", "Active")
			}
		}
		
	},
	validate: function (frm) {
		var total = 0;
		var sr= 0;
		var mr =0;
		var hd =0 ;
		var rv= 0;
		$.each(frm.doc.goal, function (i, d) {
			total += Number(d.weightage)
			sr += Number(d.self_rating)
			mr += Number(d.manager)
			hd += Number(d.hod)
			rv += Number(d.reviewer)
		})
		frm.set_value("self_rating",sr)
		frm.set_value("manager_rating",mr)
		frm.set_value("hod_rating",hd)
		frm.set_value("reviewer_rating",rv)
		if (total != 100) {
			frappe.throw("Weightage should be 100")
		}
	}
});
