// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('PM Merit Increase', {
	refresh: function(frm) {
		frm.disable_save()
	},
	onload: function(frm){
		var d = new Date()
		var emp = frappe.session.user
		frm.set_value("appraisal_year", String(d.getFullYear() - 1))
		if (!frm.doc.user_id) {
			frm.set_value("user_id", emp)
		} 
		frappe.call({
			"method": "frappe.client.get",
			args: {
				doctype: "Employee",
				filters: { "user_id": frappe.session.user},

			},
			callback: function (r) {
				if (r.message) {
					frm.set_value("employee_code1", r.message.name);
					if(frm.doc.employee_code1){
						frm.set_df_property('employee_code1', 'read_only', 1);
					}
					var promotions = [];
					$.each(r.message.promotion, function (i, d) {
						promotions.push(" " + d.promotion_year);
					})
					var no_of_promo = promotions.length
					if ((r.message.category == "Management Staff") && (r.message.pms_on_hold == 0)) {
						frm.set_value("employee_name", r.message.employee_name);
					}

				}
			}
		})
		$(cur_frm.fields_dict.print.input).css("backgroundColor", "Orange");
		$(cur_frm.fields_dict.print.input).addClass("btn-ls");
		
	},
	print: function(frm){
		if(frm.doc.employee_code1){
            frappe.call({
                "method": "frappe.client.get",
                args:{
                    "doctype": "Performance Management Calibration",
                    filters:{
                        "employee_code":frm.doc.employee_code1,
                    }
                },
                callback: function(r){
					var me = this;
					var doc = "Performance Management Calibration"
					// frappe.call({
					//     "method": "frappe.client.get",
					//     args:{
					//         "doctype": "Performance Management Calibration",
					//         filters:{
					//             "employee_code": frm.doc.employee_code,
					//             "pm_year": frm.doc.pm_year
					//         }
					//     },
					//     callback: function(r){
							var f_name = r.message.name
							var print_format = "Annexure";
					var w = window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
					+"doctype="+encodeURIComponent("Performance Management Calibration")
					+"&name="+encodeURIComponent(f_name)
					+"&trigger_print=1"
					+"&format=" + print_format
					+"&no_letterhead=0"
					+(me.lang_code ? ("&_lang="+me.lang_code) : "")));
				}
			})
		}
	}
});
