// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Performance Management Reviewer', {
    validate:function(frm){
        // if (frm.doc.workflow_state == 'Draft') {
        //     var child_r = frm.doc.competency_assessment1;
        //     var len2 = child_r.length;
        //     for (var i = 0; i < len2; i++) {
        //         if (!child_r[i].reviewer) {
        //             validated = false
        //             frappe.throw(__("Please fill HOD ratings in Competency Assessment"))
        //         }
        //     }
        // }

    },
    onload: function (frm) {
        var tot_man = 0;
        var child_man = frm.doc.key_result_area;
        $.each(child_man, function (i, d) {
            tot_man += parseInt(d.appraiser_rating_r)
        })
        if (parseInt(tot_man) > 1) {
        var avg_man = (tot_man/child_man.length).toFixed(1);
        frm.set_value("avg_man",avg_man)
        }
        else{
            frm.set_value("avg_man","0")
        }
        var tot_comp_man = 0;
        $.each(frm.doc.competency_assessment1, function (i, d) {
            tot_comp_man += parseInt(d.appraiser_rating)
        })
        var avg_comp_man = tot_comp_man/10;
        frm.set_value("avg_comp_man",avg_comp_man)

        var tot_hod = 0;
        var child_hod = frm.doc.key_result_area;
        $.each(child_hod, function (i, d) {
            tot_hod += parseInt(d.hod)
        })
        if (parseInt(tot_hod) > 1) {
        var avg_hod = (tot_hod/child_hod.length).toFixed(1);
        frm.set_value("avg_hod",avg_hod)
        }
        else{
            frm.set_value("avg_hod","0")
        }
        var tot_rev = 0;
        var child_rev = frm.doc.key_result_area;
        $.each(child_rev, function (i, d) {
            tot_rev += parseInt(d.reviewer)
        })
        if (parseInt(tot_rev) > 1) {
        var avg_rev = (tot_rev/child_rev.length).toFixed(1);
        frm.set_value("average_score",avg_rev)
        }
        else{
            frm.set_value("average_score","0")
        }

        var tot_comp_hod = 0;
        $.each(frm.doc.competency_assessment1, function (i, d) {
            tot_comp_hod += parseInt(d.hod)
        })
        var avg_comp_hod = tot_comp_hod/10;
        frm.set_value("avg_comp_hod",avg_comp_hod)

        var tot_comp_rev = 0;
        $.each(frm.doc.competency_assessment1, function (i, d) {
            tot_comp_rev += parseInt(d.reviewer)
        })
        var avg_comp_rev = tot_comp_rev/10;
        frm.set_value("average_score_attained",avg_comp_rev)

        var tot_comp = 0;
        $.each(frm.doc.competency_assessment1, function (i, d) {
            tot_comp += parseInt(d.appraisee_weightage)
        })
        var avg_comp = tot_comp/10;
        frm.set_value("avg_comp",avg_comp)

        var tot_pre = 0;
        var child_pre = frm.doc.key_result_area;
        $.each(child_pre, function (i, d) {
            tot_pre += parseInt(d.self_rating)
            // console.log(d)
        })
        if (parseInt(tot_pre) > 1) {
        var avg_pre = (tot_pre/child_pre.length).toFixed(1);
        frm.set_value("avg_pre",avg_pre)
        }else{
            frm.set_value("avg_pre","0")
        }
        if(!frm.doc.manager){
            hide_field("avg_comp_man")
            hide_field("avg_man")
        }
        frm.trigger("calculate_avg")
        frm.get_field("sales_target").grid.only_sortable();   
        // frm.get_field("management_pm_details").grid.only_sortable();           
        frm.set_query("employee_code", function () {
            return {
                "filters": {
                    "category": 'Management Staff',
                    "pms_on_hold": 0
                }
            }
        })
        cur_frm.fields_dict['sales_target'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['sales_target'].grid.wrapper.find('.grid-remove-rows').hide();
        // cur_frm.fields_dict['management_pm_details'].grid.wrapper.find('.grid-add-row').hide();
        // cur_frm.fields_dict['management_pm_details'].grid.wrapper.find('.grid-remove-rows').hide();
        cur_frm.fields_dict['competency_assessment1'].grid.wrapper.find('.grid-add-row').hide();
        // cur_frm.fields_dict['competency_assessment1'].grid.wrapper.find('.grid-remove-rows').hide();

        // d = new Date()
        // frm.set_value("appraisal_year", String(d.getFullYear() - 1))
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
        frm.trigger("refresh")
        if(!frm.doc.small_text_12){
            frm.set_value("small_text_12", "-")
        }
        if(!frm.doc.small_text_14){
            frm.set_value("small_text_14", "-")
        }
        if(!frm.doc.small_text_16){
            frm.set_value("small_text_16", "-")
        }
        if(!frm.doc.small_text_18){
            frm.set_value("small_text_18", "-")
        }
        if(!frm.doc.required__job_knowledge){
            frm.set_value("required__job_knowledge", "-")
        }
        if(!frm.doc.training_required_to_enhance_job_knowledge){
            frm.set_value("training_required_to_enhance_job_knowledge", "-")
        }
        if(!frm.doc.required_skills){
            frm.set_value("required_skills", "-")
        }
        if(!frm.doc.training_required__to_enhance_skills_competencies){
            frm.set_value("training_required__to_enhance_skills_competencies", "-")
        }
        if(!frm.doc.potential_reviewer){
            frm.set_value("potential_reviewer", frm.doc.potential_hod)
        }
        if(!frm.doc.performance_reviewer){
            frm.set_value("performance_reviewer", frm.doc.performance_hod)
        }
        if(!frm.doc.promotion_reviewer){
            frm.set_value("promotion_reviewer", frm.doc.promotion_hod)
        }
        // if(!frm.doc.any_other_observations_reviewer){
        //     frm.set_value("any_other_observations_reviewer", frm.doc.any_other_observations_hod)
        // }
        // $.each(frm.doc.employee_feedback || [], function(i, v) {
		// 	if (!v.appraiser_remarks) {
		// 		frappe.model.set_value(v.doctype, v.name, "appraiser_remarks", v.hod)
		// 	}			
		// })
    },
    after_save: function(frm){
        if(frm.doc.docstatus == 1){
            setTimeout(function () { window.history.back(); }, 1000);
        }
    },
    calculate_avg: function(frm){
        com_av_total = 0.0
		goal_av_total = 0.0
		$.each(frm.doc.competency_assessment1 || [], function(i, v) {
			if (v.reviewer) {
				var total = ((v.reviewer * 10)/ 100)
				frappe.model.set_value(v.doctype, v.name, "total", total)
			}
			if (v.total) {
                com_av_total += v.total
                final_com_av_total = (com_av_total).toFixed(2); 
			}
			
		})
        // frm.set_value("average_score_attained",final_com_av_total)
        frm.set_value("avg_score_ca",final_com_av_total)
		$.each(frm.doc.key_result_area || [], function(i, u) {
			if (u.reviewer) {
				var total = ((u.weightage  * u.reviewer) / 100)
				frappe.model.set_value(u.doctype, u.name, "weighted_score", total)
			}
			if (u.weighted_score) {
                goal_av_total += u.weighted_score
                final_goal_av_total = (goal_av_total).toFixed(2);
			}
			
		})
        // frm.set_value("average_score",final_goal_av_total)
        frm.set_value("avg_score_gs",final_goal_av_total)
    },
    validate: function(frm){
        if(frm.doc.reviewer == frappe.session.user){
            frm.set_value("status","Completed")
        }
    }
})

frappe.ui.form.on("PM_Competency", {

    // before_competency_assessment1_remove: function (frm, cdt, cdn) {
    //     frappe.throw(__("Item cannot be deleted"))
	// },
    reviewer: function (frm, cdt, cdn) {
		var child = locals[cdt][cdn];
        if (child.reviewer) {
            var total = ((child.reviewer * 10)/ 100)
            frappe.model.set_value(child.doctype, child.name, "total", total);
        }
        frm.trigger("calculate_avg")
    },
})
frappe.ui.form.on("PM_Goal Setting", {
    reviewer: function (frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        if (child.reviewer) {
            var total = (child.reviewer * (child.weightage_w_100 / 100))
            frappe.model.set_value(child.doctype, child.name, "weighted_score", total);
        }
        frm.trigger("calculate_avg")
    },
    // hod: function(frm,cdt,cdn){
    // 	var child = locals[cdt][cdn]	
    //     if (child.hod <= child.weightage_w_100) {
    //         frappe.model.set_value(cdt, cdn, "reviewer", child.hod)

    //     } 
    // }
})


