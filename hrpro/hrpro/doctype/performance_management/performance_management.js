// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Performance Management", {
    
    employee_code: function (frm) {
        if(frm.doc.employee_code){
        frm.clear_table("pm_observation_feedback")
        // refresh_field("pm_observation_feedback")
        frm.clear_table("competency_assessment1")
        refresh_field("competency_assessment1")
        frm.clear_table("key_result_area")
        // refresh_field("key_result_area")
        frm.trigger("hide_ob_and_feed")
        frm.trigger("appraisal_check")
        frm.trigger("readonly")
        if (frm.doc.employee_code) {
            if(!frm.doc.user_id){
                frm.set_value("user_id","emp")
            } else {
                frm.set_value("user_id","")
                setTimeout(function() { location.reload() }, 1000);
            }
            frappe.call({
                "method": "frappe.client.get",
                args: {
                    doctype: "Employee",
                    filters: { "employee_number": frm.doc.employee_code }
                },
                callback: function (r) {
                    if (r.message) {
                        var promotions = [];
                        $.each(r.message.promotion, function (i, d) {
                            promotions.push(" " + d.promotion_year);
                            frm.set_value("year_of_last_promotion", promotions.toString());
                        })
                        if((r.message.category == "Management Staff") && (r.message.pms_on_hold == 0)){
                            frm.set_value("employee_name", r.message.employee_name);
                            frm.set_value("cost_code", r.message.cost_center);
                            frm.set_value("designation", r.message.designation);
                            frm.set_value("department", r.message.department);
                            frm.set_value("date_of_joining", r.message.date_of_joining);
                            frm.set_value("location", r.message.location_name);
                            frm.set_value("business_unit", r.message.business_unit);
                            frm.set_value("grade", r.message.grade);
                        } else {
                            frm.set_value("employee_code","")
                        }

                    }
                }
            })
            frappe.call({
                "method": "frappe.client.get_list",
                args: {
                    "doctype": "Observation Feedback"
                },
                callback: function (r) {
                    if (r.message) {
                        $.each(r.message, function (i, d) {
                            frappe.call({
                                "method": "frappe.client.get",
                                args: {
                                    doctype: "Observation Feedback",
                                    name: d.name
                                },
                                callback: function (r) {
                                    if (r.message) {
                                        var row = frappe.model.add_child(frm.doc, "PM Observation Feedback", "pm_observation_feedback");
                                        row.status = r.message.status;
                                    }
                                    refresh_field("pm_observation_feedback");
                                }
                            })
                        })
                    }
                }
            })
            frappe.call({
                "method": "frappe.client.get_list",
                args: {
                    doctype: "Competency"
                },
                callback: function (r) {
                    if (r.message) {
                        $.each(r.message, function (i, d) {
                            frappe.call({
                                "method": "frappe.client.get",
                                args: {
                                    doctype: "Competency",
                                    name: d.name
                                },
                                callback: function (r) {
                                    if (r.message) {
                                        var row = frappe.model.add_child(frm.doc, "PM_Competency", "competency_assessment1");
                                        row.competency = r.message.competency;
                                        row.definition = r.message.definition;
                                        row.weightage = r.message.weightage;
                                    }
                                    refresh_field("competency_assessment1");
                                }
                            })
                        })
                    }
                }
            })

            frappe.call({
                "method": "frappe.client.get_list",
                args: {
                    doctype: "Goal Settings",
                    filters: { "employee": frm.doc.employee_code }
                },
                callback: function (r) {
                    if (r.message) {
                        $.each(r.message, function (i, d) {
                            frappe.call({
                                "method": "frappe.client.get",
                                args: {
                                    doctype: "Goal Settings",
                                    name: d.name
                                },
                                callback: function (r) {
                                    if (r.message) {
                                        $.each(r.message.goals, function (i, d) {
                                            if (r.message.goals) {
                                                var row = frappe.model.add_child(frm.doc, "PM_Goal Setting", "key_result_area");
                                                row.goal_setting_for_current_year = d.goal_setting_for_current_year;
                                                row.performance_measure = d.performance_measure;
                                                row.weightage_w_100 = d.weightage_w_100;
                                                row.self_rating = d.self_rating;
                                                row.appraiser_rating_r = d.appraiser_rating_r;
                                                row.weighted_score = d.weighted_score;
                                            }
                                        })
                                        refresh_field("key_result_area")
                                    }
                                }
                            })
                        })
                    }
                }
            })
        }
    }
    },
    readonly: function(frm){
        frappe.call({
            "method": "frappe.client.get",
            args: {
                doctype: "Employee",
                filters: { "employee_number": frm.doc.employee_code }
            },
            callback: function (r) {  
                var user_id = r.message.user_id
                if (frappe.user.has_role("One Above Manager") && frappe.user.has_role("Employee")) {
                if(user_id == frappe.session.user){
                    var df = frappe.meta.get_docfield("PM_Competency", "hod", cur_frm.doc.name);
                    df.read_only = 1;
                    var df1 = frappe.meta.get_docfield("PM_Competency", "reviewer", cur_frm.doc.name);
                    df1.read_only = 1;
                    var df4 = frappe.meta.get_docfield("PM_Competency", "appraiser_rating", cur_frm.doc.name);
                    df4.read_only = 1;
                    var df6 = frappe.meta.get_docfield("PM_Competency", "total", cur_frm.doc.name);
                    df6.read_only = 1;
                    var df7 = frappe.meta.get_docfield("PM_Goal Setting", "appraiser_rating_r", cur_frm.doc.name);
                    df7.read_only = 1;
                    var df5 = frappe.meta.get_docfield("PM_Goal Setting", "weighted_score", cur_frm.doc.name);
                    df5.read_only = 1;
                    var df2 = frappe.meta.get_docfield("PM_Goal Setting", "hod", cur_frm.doc.name);
                    df2.read_only = 1;
                    var df3 = frappe.meta.get_docfield("PM_Goal Setting", "reviewer", cur_frm.doc.name);
                    df3.read_only = 1;
                
                } else {
                    var df = frappe.meta.get_docfield("PM_Competency", "hod", cur_frm.doc.name);
                df.read_only = 1;
                var df1 = frappe.meta.get_docfield("PM_Competency", "reviewer", cur_frm.doc.name);
                df1.read_only = 1;
                var df4 = frappe.meta.get_docfield("PM_Competency", "appraisee_weightage", cur_frm.doc.name);
                df4.read_only = 1;
                var df6 = frappe.meta.get_docfield("PM_Competency", "total", cur_frm.doc.name);
                df6.read_only = 1;
                var df7 = frappe.meta.get_docfield("PM_Goal Setting", "self_rating", cur_frm.doc.name);
                df7.read_only = 1;
                var df5 = frappe.meta.get_docfield("PM_Goal Setting", "weighted_score", cur_frm.doc.name);
                df5.read_only = 1;
                var df2 = frappe.meta.get_docfield("PM_Goal Setting", "hod", cur_frm.doc.name);
                df2.read_only = 1;
                var df3 = frappe.meta.get_docfield("PM_Goal Setting", "reviewer", cur_frm.doc.name);
                df3.read_only = 1;
                var df8 = frappe.meta.get_docfield("Employee Feedback", "appraiser_remarks", cur_frm.doc.name);
                df8.read_only = 1;
                var df9 = frappe.meta.get_docfield("PM Observation Feedback", "principal_reviewer", cur_frm.doc.name);
                df9.read_only = 1;
                var df12 = frappe.meta.get_docfield("Goal Settings 1", "goal_setting_for_last_year", cur_frm.doc.name);
                df12.read_only = 1;
                var df13 = frappe.meta.get_docfield("Goal Settings 1", "performance_measure", cur_frm.doc.name);
                df13.read_only = 1;
                var df14 = frappe.meta.get_docfield("Goal Settings 1", "weightage_w_100", cur_frm.doc.name);
                df14.read_only = 1;
                var df15 = frappe.meta.get_docfield("Goal Settings 1", "self_rating", cur_frm.doc.name);
                df15.read_only = 1;
                    }
            }
            if (frappe.user.has_role("HOD") && frappe.user.has_role("Employee")) {
                if(user_id == frappe.session.user){
                    var df = frappe.meta.get_docfield("PM_Competency", "hod", cur_frm.doc.name);
                    df.read_only = 1;
                    var df1 = frappe.meta.get_docfield("PM_Competency", "appraiser_rating", cur_frm.doc.name);
                    df1.read_only = 1;
                    var df4 = frappe.meta.get_docfield("PM_Competency", "reviewer", cur_frm.doc.name);
                    df4.read_only = 1;
                    var df6 = frappe.meta.get_docfield("PM_Competency", "total", cur_frm.doc.name);
                    df6.read_only = 1;
                    var df7 = frappe.meta.get_docfield("PM_Goal Setting", "hod", cur_frm.doc.name);
                    df7.read_only = 1;
                    var df5 = frappe.meta.get_docfield("PM_Goal Setting", "appraiser_rating_r", cur_frm.doc.name);
                    df5.read_only = 1;
                    var df2 = frappe.meta.get_docfield("PM_Goal Setting", "reviewer", cur_frm.doc.name);
                    df2.read_only = 1;
                    var df3 = frappe.meta.get_docfield("PM_Goal Setting", "weighted_score", cur_frm.doc.name);
                    df3.read_only = 1;
               
                } else {
                    var df = frappe.meta.get_docfield("PM_Competency", "reviewer", cur_frm.doc.name);
                df.read_only = 1;
                var df1 = frappe.meta.get_docfield("PM_Competency", "appraiser_rating", cur_frm.doc.name);
                df1.read_only = 1;
                var df4 = frappe.meta.get_docfield("PM_Competency", "appraisee_weightage", cur_frm.doc.name);
                df4.read_only = 1;
                var df6 = frappe.meta.get_docfield("PM_Competency", "total", cur_frm.doc.name);
                df6.read_only = 1;
                var df7 = frappe.meta.get_docfield("PM_Goal Setting", "self_rating", cur_frm.doc.name);
                df7.read_only = 1;
                var df5 = frappe.meta.get_docfield("PM_Goal Setting", "weighted_score", cur_frm.doc.name);
                df5.read_only = 1;
                var df2 = frappe.meta.get_docfield("PM_Goal Setting", "reviewer", cur_frm.doc.name);
                df2.read_only = 1;
                var df3 = frappe.meta.get_docfield("PM_Goal Setting", "appraiser_rating_r", cur_frm.doc.name);
                df3.read_only = 1; 
                var df8 = frappe.meta.get_docfield("Employee Feedback", "appraisee_remarks", cur_frm.doc.name);
                df8.read_only = 1;
                var df9 = frappe.meta.get_docfield("PM Observation Feedback", "appraiser_reviewer", cur_frm.doc.name);
                df9.read_only = 1;
                var df10 = frappe.meta.get_docfield("Employee Feedback", "appraiser_remarks", cur_frm.doc.name);
                df10.read_only = 1;
                var df11 = frappe.meta.get_docfield("PM Observation Feedback", "principal_reviewer", cur_frm.doc.name);
                df11.read_only = 1;
                var df12 = frappe.meta.get_docfield("Goal Settings 1", "goal_setting_for_last_year", cur_frm.doc.name);
                df12.read_only = 1;
                var df13 = frappe.meta.get_docfield("Goal Settings 1", "performance_measure", cur_frm.doc.name);
                df13.read_only = 1;
                var df14 = frappe.meta.get_docfield("Goal Settings 1", "weightage_w_100", cur_frm.doc.name);
                df14.read_only = 1;
                var df15 = frappe.meta.get_docfield("Goal Settings 1", "self_rating", cur_frm.doc.name);
                df15.read_only = 1;
                }
            }
            if (frappe.user.has_role("Employee") && !frappe.user.has_role("Reviewer") && !frappe.user.has_role("HOD") && !frappe.user.has_role("One Above Manager")) {
                var df = frappe.meta.get_docfield("PM_Competency", "appraiser_rating", cur_frm.doc.name);
                df.read_only = 1;
                var df1 = frappe.meta.get_docfield("PM_Competency", "reviewer", cur_frm.doc.name);
                df1.read_only = 1;
                var df2 = frappe.meta.get_docfield("PM_Competency", "hod", cur_frm.doc.name);
                df2.read_only = 1;
                var df3 = frappe.meta.get_docfield("PM_Goal Setting", "hod", cur_frm.doc.name);
                df3.read_only = 1;
                var df4 = frappe.meta.get_docfield("PM_Goal Setting", "reviewer", cur_frm.doc.name);
                df4.read_only = 1;
                var df5 = frappe.meta.get_docfield("PM_Goal Setting", "appraiser_rating_r", cur_frm.doc.name);
                df5.read_only = 1;
                var df6 = frappe.meta.get_docfield("PM_Competency", "total", cur_frm.doc.name);
                df6.read_only = 1;
                var df7 = frappe.meta.get_docfield("PM_Goal Setting", "weighted_score", cur_frm.doc.name);
                df7.read_only = 1;
                var df8 = frappe.meta.get_docfield("Job Analysis", "appraiser_remarks", cur_frm.doc.name);
                df8.read_only = 1;
            }
            if (frappe.user.has_role("Reviewer") && frappe.user.has_role("Employee")) {
                if(user_id != frappe.session.user){
                var df = frappe.meta.get_docfield("PM_Competency", "hod", cur_frm.doc.name);
                df.read_only = 1;
                var df1 = frappe.meta.get_docfield("PM_Competency", "appraiser_rating", cur_frm.doc.name);
                df1.read_only = 1;
                var df4 = frappe.meta.get_docfield("PM_Competency", "appraisee_weightage", cur_frm.doc.name);
                df4.read_only = 1;
                var df6 = frappe.meta.get_docfield("PM_Competency", "total", cur_frm.doc.name);
                df6.read_only = 1;
                var df7 = frappe.meta.get_docfield("PM_Goal Setting", "self_rating", cur_frm.doc.name);
                df7.read_only = 1;
                var df5 = frappe.meta.get_docfield("PM_Goal Setting", "weighted_score", cur_frm.doc.name);
                df5.read_only = 1;
                var df2 = frappe.meta.get_docfield("PM_Goal Setting", "hod", cur_frm.doc.name);
                df2.read_only = 1;
                var df3 = frappe.meta.get_docfield("PM_Goal Setting", "appraiser_rating_r", cur_frm.doc.name);
                df3.read_only = 1;
                var df8 = frappe.meta.get_docfield("Employee Feedback", "appraisee_remarks", cur_frm.doc.name);
                df8.read_only = 1;
                var df9 = frappe.meta.get_docfield("PM Observation Feedback", "appraiser_reviewer", cur_frm.doc.name);
                df9.read_only = 1;
                var df12 = frappe.meta.get_docfield("Goal Settings 1", "goal_setting_for_last_year", cur_frm.doc.name);
                df12.read_only = 1;
                var df13 = frappe.meta.get_docfield("Goal Settings 1", "performance_measure", cur_frm.doc.name);
                df13.read_only = 1;
                var df14 = frappe.meta.get_docfield("Goal Settings 1", "weightage_w_100", cur_frm.doc.name);
                df14.read_only = 1;
                var df15 = frappe.meta.get_docfield("Goal Settings 1", "self_rating", cur_frm.doc.name);
                df15.read_only = 1;
                } else {
                    var df = frappe.meta.get_docfield("PM_Competency", "hod", cur_frm.doc.name);
                df.read_only = 1;
                var df1 = frappe.meta.get_docfield("PM_Competency", "appraiser_rating", cur_frm.doc.name);
                df1.read_only = 1;
                var df4 = frappe.meta.get_docfield("PM_Competency", "reviewer", cur_frm.doc.name);
                df4.read_only = 1;
                var df6 = frappe.meta.get_docfield("PM_Competency", "total", cur_frm.doc.name);
                df6.read_only = 1;
                var df7 = frappe.meta.get_docfield("PM_Goal Setting", "reviewer", cur_frm.doc.name);
                df7.read_only = 1;
                var df5 = frappe.meta.get_docfield("PM_Goal Setting", "weighted_score", cur_frm.doc.name);
                df5.read_only = 1;
                var df2 = frappe.meta.get_docfield("PM_Goal Setting", "hod", cur_frm.doc.name);
                df2.read_only = 1;
                var df3 = frappe.meta.get_docfield("PM_Goal Setting", "appraiser_rating_r", cur_frm.doc.name);
                df3.read_only = 1;
                }
            }
        }
    })
    },
    hide_ob_and_feed: function (frm) {
        frappe.call({
            "method": "frappe.client.get",
            args: {
                "doctype": "Employee",
                "name": frm.doc.employee_code
            },
            callback: function (r) {
                if (frappe.session.user == r.message.user_id) {
                    frm.toggle_display('observations_and_feedback');
                    frm.toggle_display('employee_feedback');
                }
            }
        })
    },
    appraisal_check: function (frm) {
        frappe.model.get_value('Performance Management', { 'employee_code': frm.doc.employee_code, 'appraisal_year': frm.doc.appraisal_year }, 'name',
            function (data) {
                if (data) {
                    show_alert(__("PM was already created for selected Employee for the Appraisal Year"))
                    frappe.set_route("Form", "Performance Management", data.name)
                }
            })
    },
    validate: function (frm) {
        frm.set_value("default_rows", "Added")
        frm.trigger("appraisal_check")
        var child = frm.doc.competency_assessment1;
        var len = child.length;
        var total = 0.0;
        var ava = 0.0;
        if (len) {
            for (var i = 0; i < len; i++) {
                total += child[i].total;
            }
            ava = ((total / len) * 10).toFixed(1)
        } else {
            ava = ava
        }
        frm.set_value("average_score_attained", ava);
        var child1 = frm.doc.key_result_area;
        var len1 = child1.length;
        var total1 = 0.0;
        var ava1 = 0.0;
        if (len1) {
            for (var i = 0; i < len1; i++) {
                total1 += child1[i].weighted_score;
            }
            ava1 = ((total1 / len1) * 10).toFixed(1)
        } else {
            ava1 = 0
        }
        frm.set_value("average_score", ava1);
    },
    onload: function (frm) {
        frm.get_field("sales_target").grid.only_sortable();
            
        frm.set_query("employee_code", function () {
        //     if (frappe.user.has_role("One Above Manager") && frappe.user.has_role("HOD") && frappe.user.has_role("Reviewer") ) {
        //         return {
        //             filters: [
        //                 ['Employee','category','=', 'Management Staff'],
        //                 ['Employee',"pms_on_hold",'=', 0],
        //                 // ['Employee',frappe.session.user,'in','one_above_manager','hod,reviewer']
        //             ]
        //         }
        //     }
            return {
                "filters": {
                    "category": 'Management Staff',
                    "pms_on_hold": 0
                }
            }
        })
        frm.trigger("make_default_row")
        cur_frm.fields_dict['sales_target'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['sales_target'].grid.wrapper.find('.grid-remove-rows').hide();
        cur_frm.fields_dict['competency_assessment1'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['competency_assessment1'].grid.wrapper.find('.grid-remove-rows').hide();

        d = new Date()
        frm.set_value("appraisal_year", String(d.getFullYear() - 1))
        if (frm.doc.__islocal) {
            for (var i = 2016; i < d.getFullYear(); i++) {
                var row = frappe.model.add_child(frm.doc, "PM Sales Target", "sales_target");
                row.year = i.toString()
            }
            refresh_field("sales_target")

        }

        var pastYear = d.getFullYear() - 1;
        d.setFullYear(pastYear);
        $('h6:contains("Goal Setting - Last Year")').text('Goal Setting - ' + (new Date().getFullYear()));
        $('h6:contains("Goal Setting - Current Year")').text('Goal Setting - ' + pastYear);

        frm.trigger("refresh")
    },
    refresh: function (frm) {
        
        // frm.trigger("make_default_row")
        // var df = frappe.meta.get_docfield("Job Analysis","appraisee_remarks",frm.doc.name);
        // df.in_list_view = 1;
        // // frm.fields_dict["job_analysis"].grid.set_df_property("appraisee_remarks", "in_list_view", 1);
        // // job_analysis_grid.set_editable_grid_column_disp("appraisee_remarks", true);
        // return df
        // var n = 3;
        // for (var i = 0; i < n; i++) {
        // 	var row = frappe.model.add_child(frm.doc, "Job Analysis", "job_analysis");
        // 	row.appraisee_remarks = "";
        // }
        // refresh_field("job_analysis");
        // var df = frappe.meta.get_docfield("Job Analysis","appraisee_remarks", cur_frm.doc.name);
        // df.in_list_view = 1;
        // var grid =  cur_frm.fields_dict["job_analysis"].grid;
        // grid.fields_dict.appraisee_remarks.$wrapper.show();
        // cur_frm.fields_dict.job_analysis.grid.fields_map. appraisee_remarks.in_list_view = 1;
        // cur_frm.refresh_field("job_analysis");

    },
    make_default_row: function (frm) {
        // if (frm.doc.employee_code) {
            for (var i = 0; i < 5; i++) {
                var row = frappe.model.add_child(frm.doc, "Job Analysis", "job_analysis");
                row.appraisee_remarks == ""
            }
            refresh_field("job_analysis")
            for (var i = 0; i < 5; i++) {
                var row = frappe.model.add_child(frm.doc, "Goal Settings 1", "key_results_area");
                row.appraisee_remarks == ""
            }
            refresh_field("key_results_area")
            for (var i = 0; i < 5; i++) {
                var row = frappe.model.add_child(frm.doc, "PM_Goal Setting", "key_result_area");
                row.appraisee_remarks == ""
            }
            refresh_field("key_result_area")
            for (var i = 0; i < 5; i++) {
                console.log(i)
                var row = frappe.model.add_child(frm.doc, "Employee Feedback", "employee_feedback1");
                row.appraisee_remarks == ""
            }
            refresh_field("employee_feedback1")
            // for (var i = 0; i < 5; i++) {
            //     var row = frappe.model.add_child(frm.doc, "Observation Feedback", "pm_observation_feedback");
            //     row.appraisee_remarks == ""
            // }
            // refresh_field("pm_observation_feedback")
        // }
    }
})

frappe.ui.form.on("PM_Competency", {
    before_competency_assessment1_remove: function (frm, cdt, cdn) {
        frappe.throw(__("Item cannot be deleted"))
	},
    reviewer: function (frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        if (child.reviewer) {
            var total = (child.reviewer * (10 / 100))
            frappe.model.set_value(child.doctype, child.name, "total", total);
        }
    },
    // hod: function(frm,cdt,cdn){
    // 	var child = locals[cdt][cdn]	
    //     if (child.hod <= child.weightage_w_100) {
    //         frappe.model.set_value(cdt, cdn, "reviewer", child.hod)

    //     } 
    // }
})
frappe.ui.form.on("PM_Goal Setting", {
    reviewer: function (frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        if (child.reviewer) {
            var total = (child.reviewer * (child.weightage_w_100 / 100))
            frappe.model.set_value(child.doctype, child.name, "weighted_score", total);
        }
    },
    // hod: function(frm,cdt,cdn){
    // 	var child = locals[cdt][cdn]	
    //     if (child.hod <= child.weightage_w_100) {
    //         frappe.model.set_value(cdt, cdn, "reviewer", child.hod)

    //     } 
    // }
})
frappe.ui.form.on("Goal Settings 1", {
    reviewer: function (frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        if (child.reviewer) {
            var total = (child.reviewer * (child.weightage_w_100 / 100))
            frappe.model.set_value(child.doctype, child.name, "weighted_score", total);
        }
    },
    // hod: function(frm,cdt,cdn){
    // 	var child = locals[cdt][cdn]	
    //     if (child.hod <= child.weightage_w_100) {
    //         frappe.model.set_value(cdt, cdn, "reviewer", child.hod)

    //     } 
    // }
})

