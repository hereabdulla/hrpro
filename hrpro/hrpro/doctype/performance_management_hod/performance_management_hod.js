// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Performance Management HOD', {
    validate: function (frm) {
        var tot_hod = 0;
        var child_hod = frm.doc.key_result_area;
        $.each(child_hod, function (i, d) {
            tot_hod += parseInt(d.hod)
        })
        var avg_hod = (tot_hod / child_hod.length).toFixed(1);
        frm.set_value("avg_hod", avg_hod)


        var tot_comp_hod = 0;
        $.each(frm.doc.competency_assessment1, function (i, d) {
            tot_comp_hod += parseInt(d.hod)
        })
        var avg_comp_hod = tot_comp_hod / 10;
        frm.set_value("avg_comp_hod", avg_comp_hod)


        if (frm.doc.workflow_state == 'Draft') {
            frm.toggle_reqd('potential_hod', frm.doc.workflow_state == 'Draft')
            frm.toggle_reqd('performance_hod', frm.doc.workflow_state == 'Draft')
            frm.toggle_reqd('promotion_hod', frm.doc.workflow_state == 'Draft')
            if (frm.doc.potential_hod && frm.doc.performance_hod && frm.doc.promotion_hod) {
                var child1 = frm.doc.employee_feedback;
                var len1 = child1.length;
                if (len1 != 0) {
                    for (var i = 0; i < len1; i++) {
                        if (!child1[i].hod) {
                            validated = false
                            frappe.throw(__("HOD Remarks in Constructive Feedback is Mandatory"))
                        }
                    }
                }
            }
            var child_h = frm.doc.competency_assessment1;
            var len2 = child_h.length;
            for (var i = 0; i < len2; i++) {
                if (!child_h[i].hod) {
                    validated = false
                    frappe.throw(__("Please fill HOD ratings in Competency Assessment"))
                }
            }
            if (frm.doc.key_result_area) {
                var child_hg = frm.doc.key_result_area;
                var len4 = child_hg.length;
                for (var i = 0; i < len4; i++) {
                    if (!child_hg[i].hod) {
                        validated = false
                        frappe.throw(__("Please fill HOD ratings in Goal Setting"))
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

        var tot_man = 0;
        var child_man = frm.doc.key_result_area;
        $.each(frm.doc.key_result_area, function (i, d) {
            tot_man += parseInt(d.manager)
        })
        if (tot_man > 1) {
            var avg_man = (tot_man / child_man.length).toFixed(1);;
            frm.set_value("avg_man", avg_man)
        }
        else {
            frm.set_value("avg_man", "0")
        }

        var tot_comp_man = 0;
        $.each(frm.doc.competency_assessment1, function (i, d) {
            tot_comp_man += parseInt(d.manager)
        })
        if (tot_comp_man > 1) {
            var avg_comp_man = tot_comp_man / 10;
            frm.set_value("avg_comp_man", avg_comp_man)
        }
        else {
            frm.set_value("avg_comp_man", "0")
        }
        var tot_pre = 0;
        var child_pre = frm.doc.key_result_area;
        $.each(child_pre, function (i, d) {
            tot_pre += parseInt(d.self_rating)
            // console.log(d)
        })
        if (tot_pre > 1) {
            var avg_pre = (tot_pre / child_pre.length).toFixed(1);
            frm.set_value("avg_pre", avg_pre)
        }
        else {
            frm.set_value("avg_pre", "0")
        }

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
        cur_frm.fields_dict['sales_target'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['sales_target'].grid.wrapper.find('.grid-remove-rows').hide();
        cur_frm.fields_dict['competency_assessment1'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['competency_assessment1'].grid.wrapper.find('.grid-remove-rows').hide();

        // frm.trigger("refresh")
    }
});

frappe.ui.form.on("PM Competency HOD", {
    before_competency_assessment1_remove: function (frm, cdt, cdn) {
        frappe.throw(__("Item cannot be deleted"))
    }
})
