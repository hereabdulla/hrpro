// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Performance Management Self', {
    validate: function (frm) {
        var tot_comp = 0;
        var avg_comp = 0;
        $.each(frm.doc.competency_assessment1, function (i, d) {
            tot_comp += parseInt(d.appraisee_weightage)
        })
        if (parseInt(tot_comp) > 1) {
            var avg_comp = tot_comp / 10;
            frm.set_value("avg_comp", avg_comp)
        }
        else {
            frm.set_value("avg_comp", "0")
        }
        var tot_pre = 0;
        var child_pre = frm.doc.key_result_area;
        $.each(child_pre, function (i, d) {
            tot_pre += parseInt(d.self_rating)
        })
        if (parseInt(tot_pre) > 1) {
            var avg_pre = (tot_pre / child_pre.length).toFixed(1);
            frm.set_value("avg_pre", avg_pre)
        }
        else {
            frm.set_value("avg_pre", "0")
        }
        if (frm.doc.workflow_state == 'Draft') {
            var child1 = frm.doc.key_result_area;
            var len1 = child1.length;
            var total1 = 0;
            if (len1 != 0) {
                for (var i = 0; i < len1; i++) {
                    total1 += child1[i].weightage;
                }
                if (total1 != 100) {
                    validated = false
                    frappe.throw(__("In Previous Year Goal Setting Weightage Must be equal to 100"))
                }
            }
            var child1 = frm.doc.key_results_area;
            var len = child1.length;
            var total = 0.0;
            if (child1) {
                for (var i = 0; i < len; i++) {
                    total += child1[i].weightage;
                }
                if (total != 100) {
                    validated = false
                    frappe.throw(__("In Current Year Goal Setting Weightage Must be equal to 100"))
                }
            }
        }
        // $.each(frm.doc.job_analysis, function (i, d) {
        //     console.log(d.appraisee_remarks)
        //     if(d.appraisee_remarks == ""){
        //     validated = false
        //     frappe.throw(__("Please fill the job Analysis"))
        // }
        // })
    },
    employee_code: function (frm) {
        if (frm.doc.__islocal && !frm.doc.employee_code1) {
            frm.set_value("employee_code1", frm.doc.employee_code)
        }
        var html = [`<div class='table-responsive'>
                        <table class='table table-bordered'>
                    <tbody>`
        ]
        if (frm.doc.employee_code) {
            frm.clear_table("competency_assessment1")
            refresh_field("competency_assessment1")
            // frm.clear_table("key_result_area")
            // refresh_field("key_result_area")
            frm.trigger("appraisal_check")
            frm.trigger("readonly")
            if (frm.doc.employee_code) {
                if (!frm.doc.user_id) {
                    frm.set_value("user_id", "emp")
                } else {
                    frm.set_value("user_id", "")
                    setTimeout(function () { location.reload() }, 1000);
                }
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
                            if ((r.message.category == "Management Staff") && (r.message.pms_on_hold == 0)) {
                                frm.set_value("employee_name", r.message.employee_name);
                                frm.set_value("cost_code", r.message.cost_center);
                                frm.set_value("designation", r.message.designation);
                                frm.set_value("department", r.message.department);
                                frm.set_value("date_of_joining", r.message.date_of_joining);
                                frm.set_value("location", r.message.location_name);
                                frm.set_value("business_unit", r.message.business_unit);
                                frm.set_value("grade", r.message.grade);
                                frm.set_value("manager", r.message.one_above_manager);
                                frm.set_value("hod", r.message.hod);
                                frm.set_value("reviewer", r.message.reviewer);
                            } else {
                                frm.set_value("employee_code", "")
                            }

                        }
                    }
                })

                frappe.call({
                    "method": "frappe.client.get",
                    args: {
                        "doctype": "PM Settings",
                    },
                    callback: function (r) {
                        if (r.message) {
                            var child = r.message.competency_assess;
                            $.each(child, function (i, d) {
                                var row = frappe.model.add_child(frm.doc, "PM Competency Self", "competency_assessment1");
                                row.competency = d.competency;
                                row.definition = d.definition;
                                row.weightage = d.weightage;
                            })
                            refresh_field("competency_assessment1");
                        }
                    }
                })
                // frappe.call({
                //     "method": "frappe.client.get_list",
                //     args: {
                //         doctype: "Goal Settings",
                //         filters: { "employee": frm.doc.employee_code }
                //     },
                //     callback: function (r) {
                //         if (r.message) {
                //             $.each(r.message, function (i, d) {
                //                 frappe.call({
                //                     "method": "frappe.client.get",
                //                     args: {
                //                         doctype: "Goal Settings",
                //                         name: d.name
                //                     },
                //                     callback: function (r) {
                //                         if (r.message) {
                //                             $.each(r.message.goals, function (i, d) {
                //                                 if (r.message.goals) {
                //                                     var row = frappe.model.add_child(frm.doc, "PM Goal Setting Self", "key_result_area");
                //                                     row.goal_setting_for_current_year = d.goal_setting_for_current_year;
                //                                     row.performance_measure = d.performance_measure;
                //                                     row.weightage_w_100 = d.weightage_w_100;
                //                                     row.self_rating = d.self_rating;
                //                                 }
                //                             })
                //                             refresh_field("key_result_area")
                //                         }
                //                     }
                //                 })
                //             })
                //         }
                //     }
                // })
                var past_year = Number(frm.doc.appraisal_year) - 1
                frappe.call({
                    "method": "hrpro.custom.get_previous_year_goals",
                    args: {
                        "emp": frm.doc.employee_code,
                        "year": past_year
                    },
                    callback: function (r) {
                        console.log(past_year)
                        if (r.message == 'NA') {
                            console.log(r.message)
                            frappe.call({
                                "method": "frappe.client.get",
                                args: {
                                    doctype: "Induction Goal",
                                    filters: {
                                        "employee_id": frm.doc.employee_id
                                    }
                                },
                                callback: function (r) {
                                    console.log(r.message)
                                    if (r.message.goal) {
                                        $.each(r.message.goal, function (i, d) {
                                            var row = frappe.model.add_child(frm.doc, "PM Goal Setting Self", "key_result_area");
                                            row.goal_setting_for_current_year = d.kpi;
                                            row.performance_measure = d.performance_measure;
                                            row.weightage_w_100 = d.timeline;
                                            row.weightage = d.weightage;
                                            row.self_rating=d.self_rating;
                                            row.manager=d.manager;
                                            row.hod=d.hod;
                                            row.reviewer=d.reviewer
                                        })
                                        refresh_field("key_result_area")
                                    }
                                   

                                }
                            })
                            
                        }
                        else if(r.message != 'NA'){
                            frappe.call({
                                "method": "frappe.client.get",
                                args: {
                                    doctype: "Performance Management Self",
                                    filters: {
                                        "employee_code1": frm.doc.employee_code,
                                        "appraisal_year": String(past_year)
                                    }
                                },
                                callback: function (r) {
                                    if (r.message.key_results_area) {
                                        $.each(r.message.key_results_area, function (i, d) {
                                            var row = frappe.model.add_child(frm.doc, "PM Goal Setting Self", "key_result_area");
                                            row.goal_setting_for_current_year = d.goal_setting_for_last_year;
                                            row.performance_measure = d.performance_measure;
                                            row.weightage_w_100 = d.weightage_w_100;
                                            row.weightage = d.weightage;
                                        })
                                        refresh_field("key_result_area")
                                    }
                                    else{
                                        for (var i = 0; i < 7; i++) {
                                            var row = frappe.model.add_child(frm.doc, "PM Goal Setting Self", "key_result_area");
                                            row.self_rating == ""
                                        }
                                        refresh_field("key_result_area")
                                    }

                                }
                            })
                        }
                    }

                })


                // frappe.call({
                //     "method": "frappe.client.get",
                //     args: {
                //         doctype: "Performance Management Self",
                //         filters: {
                //             "employee_code1": frm.doc.employee_code,
                //             "appraisal_year": String(past_year)
                //         }
                //     },
                //     callback: function (r) {
                //         console.log(r)
                // frappe.db.exists('Performance Management Self',{'appraisal_year': '2018','employee_code':'DOO1'})
                //     .then(exists => {
                //         console.log(exists) // true
                //     })

                // }
                // });


            }
        }
    },

    onload_post_render: function (frm) {
        if (frm.doc.employee_code) {

        }
    },
    appraisal_check: function (frm) {
        frappe.model.get_value('Performance Management Self', { 'employee_code': frm.doc.employee_code, 'appraisal_year': frm.doc.appraisal_year }, 'name',
            function (data) {
                if (data) {
                    show_alert(__("PM was already created for selected Employee for the Appraisal Year"))
                }
            })
    },
    onload: function (frm) {
        var app_year = frm.doc.appraisal_year;
        var next_year = Number(frm.doc.appraisal_year) + 1
        // $('h6:contains("Goal Setting - Last Year")').text('Goal Setting - ' + String(next_year));
        // $('h6:contains("Goal Setting - Current Year")').text('Goal Setting - ' + app_year);
    },
    refresh: function (frm) {
        frm.get_field("sales_target").grid.only_sortable();

        frm.set_query("employee_code", function () {
            return {
                "filters": {
                    "category": 'Management Staff',
                    "pms_on_hold": 0,
                    "user_id": frappe.session.user
                }
            }
        })
        frm.trigger("make_default_row")
        // if (frm.doc.job_analysis) {
        //     frm.trigger("after_save_make_default_row")
        // }
        cur_frm.fields_dict['sales_target'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['sales_target'].grid.wrapper.find('.grid-remove-rows').hide();
        cur_frm.fields_dict['competency_assessment1'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['job_analysis'].grid.wrapper.find('.grid-remove-rows').show();
        cur_frm.fields_dict['job_analysis'].grid.wrapper.find('.grid-add-row').hide();
        // cur_frm.fields_dict['key_result_area'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['key_results_area'].grid.wrapper.find('.grid-add-row').hide();


        // cur_frm.fields_dict.key_results_area.grid.toggle_reqd("performance_measure")

        d = new Date()
        if (frm.doc.__islocal) {
            frm.set_value("appraisal_year", String(d.getFullYear() - 1))
        }
        if (frm.doc.__islocal) {
            frm.clear_table("sales_target")
            var year = String((d.getFullYear() - 3));
            for (var i = year; i < d.getFullYear(); i++) {
                var row = frappe.model.add_child(frm.doc, "PM Sales Target", "sales_target");
                row.year = i.toString()
            }
            refresh_field("sales_target")
        }
    },

    make_default_row: function (frm) {
        if (frm.doc.__islocal) {
            for (var i = 0; i < 10; i++) {
                var row = frappe.model.add_child(frm.doc, "Job Analysis Self", "job_analysis");
                row.appraisee_remarks == ""
            }
            refresh_field("job_analysis")
            for (var i = 0; i < 7; i++) {
                var row = frappe.model.add_child(frm.doc, "Previous Goal Setting Self", "key_results_area");
                row.appraisee_remarks == ""
            }
            refresh_field("key_results_area")
        }
    },
    after_save_make_default_row: function (frm) {
        var child1 = frm.doc.job_analysis;
        var len1 = child1.length;
        if (len1 == 0) {
            for (var i = 0; i < 10; i++) {
                var row = frappe.model.add_child(frm.doc, "Job Analysis Self", "job_analysis");
                row.appraisee_remarks == ""
            }
            refresh_field("job_analysis")
        }
        var child2 = frm.doc.key_results_area;
        var len2 = child2.length;
        if (len2 == 0) {
            for (var i = 0; i < 7; i++) {
                var row = frappe.model.add_child(frm.doc, "Previous Goal Setting Self", "key_results_area");
                row.appraisee_remarks == ""
            }
            refresh_field("key_results_area")
        }
        var child3 = frm.doc.key_result_area;
        var len3 = child3.length;
        if (len3 == 0) {
            for (var i = 0; i < 7; i++) {
                var row = frappe.model.add_child(frm.doc, "PM Goal Setting Self", "key_result_area");
                row.appraisee_remarks == ""
            }
            refresh_field("key_result_area")
        }
    }
});


frappe.ui.form.on("PM Competency Self", {
    before_competency_assessment1_remove: function (frm, cdt, cdn) {
        frappe.throw(__("Item cannot be deleted"))
    }
})



// frappe.ui.form.on("PM Goal Setting Self", {
//     weightage: function (frm, cdt, cdn) {
//         var child = locals[cdt][cdn];
//         console.log
//         if (child.weightage > 100) {
//             frappe.throw(__("Wightage Must be less than or equal to 100"))
//         }
// 	}
// })


// frappe.ui.form.on("Previous Goal Setting Self", {
//     weightage: function (frm, cdt, cdn) {
//         var child = locals[cdt][cdn];
//         if (child.weightage > 100) {
//             frappe.throw(__("Wightage Must be less than or equal to 100"))
//         }
// 	}
// })