// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Performance Management Self', {
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
                                            // html.push(`<tr><td><b>${r.message.competency}</b></td><td>${r.message.definition}</td></tr></table>`)
                                            var row = frappe.model.add_child(frm.doc, "PM Competency Self", "competency_assessment1");
                                            row.competency = r.message.competency;
                                            row.definition = r.message.definition;
                                            row.weightage = r.message.weightage;
                                        }

                                        // $(frm.fields_dict['html_3'].wrapper).html(html);
                                        refresh_field("competency_assessment1");
                                        // refresh_field("html_3");

                                    }
                                })

                            })
                        }
                    }
                })
                // console.log(html)
                // $(frm.fields_dict['html_3'].wrapper).html(html);
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
                                                    var row = frappe.model.add_child(frm.doc, "PM Goal Setting Self", "key_result_area");
                                                    row.goal_setting_for_current_year = d.goal_setting_for_current_year;
                                                    row.performance_measure = d.performance_measure;
                                                    row.weightage_w_100 = d.weightage_w_100;
                                                    row.self_rating = d.self_rating;
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
        var past_year = Number(frm.doc.appraisal_year) - 1
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
                if (r.message) {
                    if (r.message.key_results_area) {
                        $.each(r.message.key_results_area, function (i, d) {
                            var row = frappe.model.add_child(frm.doc, "PM Goal Setting Self", "key_result_area");
                            row.goal_setting_for_current_year = d.goal_setting_for_last_year;
                            row.performance_measure = d.performance_measure;
                            row.weightage_w_100 = d.weightage_w_100;
                            row.weightage = d.weightage;
                        })
                    }
                    refresh_field("key_result_area")
                }
                else{
                    for (var i = 0; i < 5; i++) {
                        var row = frappe.model.add_child(frm.doc, "PM Goal Setting Self", "key_result_area");
                        row.appraisee_remarks == ""
                    }
                    refresh_field("key_result_area")
                }
            }
        })
    },

    appraisal_check: function (frm) {
        frappe.model.get_value('Performance Management Self', { 'employee_code': frm.doc.employee_code, 'appraisal_year': frm.doc.appraisal_year }, 'name',
            function (data) {
                if (data) {
                    show_alert(__("PM was already created for selected Employee for the Appraisal Year"))
                }
            })
    },
    // validate: function (frm) {
    //     frm.trigger("appraisal_check")
    // },
    before_submit: function (frm) {
        var child1 = frm.doc.key_result_area;
        var len1 = child1.length;
        var total1 = 0;
        if (child1) {
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
        if (child1) {
            for (var i = 0; i < len; i++) {
                total += child[i].weightage;
            }
            if (total != 100) {
                validated = false
                frappe.throw(__("In Previous Goal Setting Weightage Must be equal to 100"))
            }
        }
    },
    onload:function(frm){
        var app_year = frm.doc.appraisal_year;
        var next_year = Number(frm.doc.appraisal_year) + 1
        $('h6:contains("Goal Setting - Last Year")').text('Goal Setting - ' + String(next_year));
        $('h6:contains("Goal Setting - Current Year")').text('Goal Setting - ' + app_year);
    },
    refresh: function (frm) {

        if (frm.doc.employee_code) {
            frappe.call({
                "method": "frappe.client.get",
                args: {
                    "doctype": "Performance Management Calibration",
                    filters: {
                        "employee_code": frm.doc.employee_code,
                        "pm_year": frm.doc.pm_year
                    }
                },
                callback: function (r) {
                    if (r.message.docstatus == 0) {
                        frm.add_custom_button(__('Print'), function () {
                            // if (frm.doc.docstatus == "1"){
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
                                + "doctype=" + encodeURIComponent("Performance Management Calibration")
                                + "&name=" + encodeURIComponent(f_name)
                                + "&trigger_print=1"
                                + "&format=" + print_format
                                + "&no_letterhead=0"
                                + (me.lang_code ? ("&_lang=" + me.lang_code) : "")));
                            // }
                            // })
                        })
                    }
                }
            })
        }

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
        if (frm.doc.job_analysis) {
            frm.trigger("after_save_make_default_row")
        }
        cur_frm.fields_dict['sales_target'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['sales_target'].grid.wrapper.find('.grid-remove-rows').hide();
        cur_frm.fields_dict['competency_assessment1'].grid.wrapper.find('.grid-add-row').hide();
        // cur_frm.fields_dict['competency_assessment1'].grid.wrapper.find('.grid-remove-rows').hide();

        d = new Date()
        if (frm.doc.__islocal) {
            frm.set_value("appraisal_year", String(d.getFullYear() - 1))
        }
        if (frm.doc.__islocal) {
            for (var i = 2016; i < d.getFullYear(); i++) {
                var row = frappe.model.add_child(frm.doc, "PM Sales Target", "sales_target");
                row.year = i.toString()
            }
            refresh_field("sales_target")

        }

        

    },

    make_default_row: function (frm) {
        if (frm.doc.__islocal) {
            for (var i = 0; i < 5; i++) {
                var row = frappe.model.add_child(frm.doc, "Job Analysis Self", "job_analysis");
                row.appraisee_remarks == ""
            }
            refresh_field("job_analysis")
            for (var i = 0; i < 5; i++) {
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
            for (var i = 0; i < 5; i++) {
                var row = frappe.model.add_child(frm.doc, "Job Analysis Self", "job_analysis");
                row.appraisee_remarks == ""
            }
            refresh_field("job_analysis")
        }
        var child2 = frm.doc.key_results_area;
        var len2 = child2.length;
        if (len2 == 0) {
            for (var i = 0; i < 5; i++) {
                var row = frappe.model.add_child(frm.doc, "Previous Goal Setting Self", "key_results_area");
                row.appraisee_remarks == ""
            }
            refresh_field("key_results_area")
        }
        var child3 = frm.doc.key_result_area;
        var len3 = child3.length;
        if (len3 == 0) {
            for (var i = 0; i < 5; i++) {
                var row = frappe.model.add_child(frm.doc, "PM Goal Setting Self", "key_result_area");
                row.appraisee_remarks == ""
            }
            refresh_field("key_result_area")
        }
    }
});


// frappe.ui.form.on("PM Competency Self", {
//     before_competency_assessment1_remove: function (frm, cdt, cdn) {
//         frappe.throw(__("Item cannot be deleted"))
//     }
// })

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