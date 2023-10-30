// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Performance Management Calibration', {
	refresh: function(frm) {

	},
	employee_code: function(frm){
		d = new Date()
        frm.set_value("appraisal_year", String(d.getFullYear() - 1))
		frappe.call({
			"method": "frappe.client.get",
			args: {
				doctype: "Employee",
				filters: { "employee_number": frm.doc.employee_code },

			},
			callback: function (r) {
				if (r.message) {
					var promotions = [];
                            $.each(r.message.promotion, function (i, d) {
                                promotions.push(" " + d.promotion_year);
                                frm.set_value("year_of_last_promotion", promotions.toString());
							})
					var no_of_promo = promotions.length
					if ((r.message.category == "Management Staff") && (r.message.pms_on_hold == 0)) {
						frm.set_value("employee_name", r.message.employee_name);
						frm.set_value("cost_code", r.message.cost_center);
						frm.set_value("designation", r.message.designation);
						frm.set_value("department", r.message.department);
						frm.set_value("date_of_joining", r.message.date_of_joining);
						frm.set_value("location", r.message.location_name);
						frm.set_value("business_unit", r.message.business_unit);
						frm.set_value("grade", r.message.grade);
						frm.set_value("no_of_promotion", no_of_promo);
					}
				}
			}
		})
	},
// 	validate: function(frm){
// 		// frm.trigger("calculate_ctc")
// 		var child = frm.doc.management_pm_details
// 		var len = child.length
// 		if(len != 0)
// 		for(var i=0;i<len;i++){
// 			if(child[i].year == frm.doc.appraisal_year){
// 				var diff = frm.doc.new_annual_ctc - child[i].ctc
// 				var per = (diff * 100) / child[i].ctc
// 				frm.set_value("increment_percentage", per)
// 			}
// 		}
// 	},
// 	calculate_ctc: function(frm){
// 		var total = 0.0
// 		if(frm.doc.basic || frm.doc.hra || frm.doc.special_allowance || frm.doc.transport || frm.doc.education || frm.doc.food_allowance || frm.doc.medical || frm.doc.relocation_allowance || 
// 			frm.doc.communication_allowance || frm.doc.washing_allowance || frm.doc.site_allowance || frm.doc.car_allowance || frm.doc.driver_salary || frm.doc.bus_allowance || frm.doc.pf_contribution || frm.doc.lta || frm.doc.gratuity ||
// 			frm.doc.exgratia || frm.doc.acco || frm.doc.sales_project_support_incentive || frm.doc.performance_incentive){
// 			 total = frm.doc.basic+frm.doc.hra+frm.doc.special_allowance+frm.doc.transport+frm.doc.education+frm.doc.food_allowance+frm.doc.medical+frm.doc.relocation_allowance+ 
// 			 frm.doc.communication_allowance+frm.doc.washing_allowance+frm.doc.site_allowance+frm.doc.car_allowance+frm.doc.driver_salary+frm.doc.bus_allowance+frm.doc.pf_contribution+frm.doc.lta+frm.doc.gratuity+
// 			 frm.doc.exgratia+frm.doc.acco+frm.doc.sales_project_support_incentive+frm.doc.performance_incentive
// 			frm.set_value("new_annual_ctc",total)
			
// 	}
// }
});
