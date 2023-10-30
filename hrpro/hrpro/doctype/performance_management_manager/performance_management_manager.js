// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Performance Management Manager', {
    validate: function (frm) {
        var tot_man = 0;
        var child_man = frm.doc.key_result_area;
        $.each(child_man, function (i, d) {
            tot_man += parseInt(d.manager)
        })
        if (tot_man > 1) {
            var avg_man = (tot_man / child_man.length).toFixed(1);
            frm.set_value("avg_man", avg_man)
        }
        else {
            frm.set_value("avg_man", "0")
        }
        var tot_comp_man = 0;
        $.each(frm.doc.competency_assessment1, function (i, d) {
            tot_comp_man += parseInt(d.manager)
        })
        var avg_comp_man = tot_comp_man / 10;
        frm.set_value("avg_comp_man", avg_comp_man)
        if (frm.doc.workflow_state == 'Draft') {
            frm.toggle_reqd('potential', frm.doc.workflow_state == 'Draft')
            frm.toggle_reqd('performance', frm.doc.workflow_state == 'Draft')
            frm.toggle_reqd('promotion', frm.doc.workflow_state == 'Draft')
            if (frm.doc.potential && frm.doc.performance && frm.doc.promotion) {
                var child1 = frm.doc.employee_feedback;
                var len1 = child1.length;
                if (len1 != 0) {
                    for (var i = 0; i < len1; i++) {
                        if (child1[i].appraisee_remarks == " ") {
                            validated = false
                            frappe.throw(__("Appraisee Remarks in Constructive Feedback is Mandatory"))
                        }
                    }
                }
                var child2 = frm.doc.job_analysis;
                var len2 = child2.length;
                if (len2 != 0) {
                    for (var i = 0; i < len2; i++) {
                        if (!child2[i].appraiser_remarks) {
                            validated = false
                            frappe.throw(__("Appraiser Remarks in Job Analysis is Mandatory"))
                        }
                    }
                }

            }
            if (frm.doc.competency_assessment1) {
                var child_m = frm.doc.competency_assessment1;
                var len3 = child_m.length;
                for (var i = 0; i < len3; i++) {
                    if (!child_m[i].manager) {
                        validated = false
                        frappe.throw(__("Please fill Manager ratings in Competency Assessment"))
                    }
                }
            }
            if (frm.doc.key_result_area) {
                var child_mg = frm.doc.key_result_area;
                var len4 = child_mg.length;
                for (var i = 0; i < len4; i++) {
                    if (!child_mg[i].manager) {
                        validated = false
                        frappe.throw(__("Please fill Manager ratings in Goal Setting"))
                    }
                }
            }
        }
    },

    refresh: function (frm) {

    },
    onload: function (frm) {
        var tot_comp = 0;
        $.each(frm.doc.competency_assessment1, function (i, d) {
            tot_comp += parseInt(d.appraisee_weightage)
        })
        var avg_comp = tot_comp / 10;
        frm.set_value("avg_comp", avg_comp)

        var tot_pre = 0;
        var child_pre = frm.doc.key_result_area;
        $.each(child_pre, function (i, d) {
            tot_pre += parseInt(d.self_rating)
        })
        if (tot_pre > 1) {
            var avg_pre = (tot_pre / child_pre.length).toFixed(1)
            frm.set_value("avg_pre", avg_pre)
        }
        else {
            frm.set_value("avg_pre", "0")
        }
        var child1 = frm.doc.pm_observation_feedback;
        var len1 = child1.length;
        if (!len1) {
            // frappe.call({
            // 	"method": "frappe.client.get_list",
            // 	args: {
            // 		"doctype": "Observation Feedback"
            // 	},
            // 	callback: function (r) {
            // 		if (r.message) {
            // 			$.each(r.message, function (i, d) {
            // 				frappe.call({
            // 					"method": "frappe.client.get",
            // 					args: {
            // 						doctype: "Observation Feedback",
            // 						name: d.name
            // 					},
            // 					callback: function (r) {
            // 						if (r.message) {
            // 							var row = frappe.model.add_child(frm.doc, "PM Observation Feedback", "pm_observation_feedback");
            // 							row.status = r.message.status;
            // 						}
            // 						refresh_field("pm_observation_feedback");
            // 					}
            // 				})
            // 			})
            // 		}
            // 	}
            // })
            for (var i = 0; i < 4; i++) {
                var row = frappe.model.add_child(frm.doc, "PM Observation Feedback", "pm_observation_feedback");
                if (i = 0) {
                    row.status = "Potential (High/Medium/Low)";
                }
                if (i = 1) {
                    row.status = "Performance (Excellent/Meets Expectation/Average/Under Performance";
                }
                if (i = 2) {
                    row.status = "Promoted to next grade/ May be considered after 1or 2 years/Not yet ready ";
                }
                if (i = 3) {
                    row.status = "Any other observations ";
                }
            }
            refresh_field("pm_observation_feedback");
        }
        // d = new Date()
        //     frm.set_value("appraisal_year", String(d.getFullYear() - 1))
        if (frm.doc.__islocal) {
            for (var i = 2016; i < d.getFullYear(); i++) {
                var row = frappe.model.add_child(frm.doc, "PM Sales Target", "sales_target");
                row.year = i.toString()
            }
            refresh_field("sales_target")

        }

        var app_year = frm.doc.appraisal_year;
        var next_year = Number(frm.doc.appraisal_year) + 1
        // $('h6:contains("Goal Setting - Last Year")').text('Goal Setting - ' + String(next_year));
        // $('h6:contains("Goal Setting - Current Year")').text('Goal Setting - ' + app_year);
        cur_frm.fields_dict['sales_target'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['sales_target'].grid.wrapper.find('.grid-remove-rows').hide();
        cur_frm.fields_dict['competency_assessment1'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['competency_assessment1'].grid.wrapper.find('.grid-remove-rows').hide();
        frm.trigger("refresh")
        var child = frm.doc.employee_feedback;
        var len = child.length;
        if (!len) {
            if (frm.doc.employee_code) {
                for (var i = 0; i < 5; i++) {
                    var row = frappe.model.add_child(frm.doc, "Employee Feedback", "employee_feedback");
                    row.appraisee_remarks == ""
                }
                refresh_field("employee_feedback")
            }
        }
    },
    on_submit: function (frm) {
        var child1 = frm.doc.key_result_area;
        var len1 = child1.length;
        var total1 = 0.0;
        if (len1) {
            for (var i = 0; i < len1; i++) {
                total1 += child1[i].weightage;
            }
            if (total1 != 100) {
                validated = false
                frappe.throw(__("In Goal Setting Weightage Must be equal to 100"))
            }
        }
        var child = frm.doc.key_results_area;
        var len = child.length;
        var total = 0.0;
        if (len) {
            for (var i = 0; i < len; i++) {
                total += child[i].weightage;
            }
            if (total != 100) {
                validated = false
                frappe.throw(__("In Previous Goal Setting Weightage Must be equal to 100"))
            }
        }
    },
});

frappe.ui.form.on("PM Competency Manager", {
    before_competency_assessment1_remove: function (frm, cdt, cdn) {
        frappe.throw(__("Item cannot be deleted"))
    }
})
