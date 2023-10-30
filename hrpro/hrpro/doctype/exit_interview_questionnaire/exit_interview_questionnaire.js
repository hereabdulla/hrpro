// Copyright (c) 2020, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Exit Interview Questionnaire', {
    refresh: function (frm) {

    },
    onload: function (frm) {
        var List =
            [{ dept: "Higher salary" },
            { dept: "Dissatisfied with Remuneration and Benefits" },
            { dept: "Career advancement / change" },
            { dept: "Transportation problems" },
            { dept: "Lack of child care" },
            { dept: "Dissatisfaction with supervision / leadership" },
            { dept: "Received an employment offer without actively seeking another job" },
            { dept: "Family Concern" },
            { dept: "Dissatisfied with organizational culture" },
            { dept: "Dissatisfied with work hours" },
            { dept: "Dissatisfied with job fulfillment " },
            { dept: "Dissatisfied with training and development opportunities" },
            { dept: "Leaving the employment market" },
            { item: "Other Comments" }
            ]
        if (!frm.doc.exit1) {
            frm.clear_table('exit1');
            $.each(List, function (i, d) {
                let row = frm.add_child('exit1', {
                    data2: d.dept,
                    data_1: d.item

                })
            })

            refresh_field("exit1");
        };
        var exit = [
            { dep: "Having a good boss" },
            { dep: "Good salary" },
            { dep: "Good benefits" },
            { dep: "Opportunities to grow and learn professionally" },
            { dep: "A flexible working environment" },
            { dep: "Recognition for skills and accomplishments" },
            { dep: "Good relationships with co-workers" },
            { dep: "Working with up-to-date technology" },
            { dep1: "Other Comments" }]
        if (!frm.doc.exit2) {
            frm.clear_table('exit2');
            $.each(exit, function (i, d) {
                let row = frm.add_child('exit2', {
                    data2: d.dep,
                    data_1: d.dep1

                })
            })

            refresh_field("exit2");
        };
        var e = [
            { l1: "Provided feedback on my performance" },
            { l1: "Treated me with respect and courtesy" },
            { l1: "Led by example" },
            { l1: "Helped me solve problems." },
            { l1: "Was available when I needed help" },
            { l1: "Followed policies and practices and applied them fairly" },
            { l1: "Provided positive feedback and recognition" },
            { l1: "Resolved complaints and problems" },
            { l1: "Represented the position accurately when interviewed" },
            { l1: "Training opportunities were available inside the department" },
            { l1: "Training opportunities were available outside the department" },
            // {l1:"Other Comments:"}
        ]
        if (!frm.doc.exit3) {
            frm.clear_table('exit3');
            $.each(e, function (i, d) {
                let row = frm.add_child('exit3', {
                    data_1: d.l1

                })
            })

            refresh_field("exit3");
        };
        var s = [
            { l2: "My physical work area was appropriate for the work that I did" },
            { l2: "I had adequate materials to do my work (tools, computer, phones, etc)" },
            { l2: "My work schedule was convenient" },
            { l2: "Overtime demands were reasonable" },
            { l2: "Relationship with co-workers" },
            { l2: "Relationship with customers (consignees, underwriters, agents / contractors)" },
            { l2: "Office atmosphere and morale" },
            { l2: "Adequate guidance in resolving work-related or personal problems" }
        ]
        if (!frm.doc.exit4) {
            frm.clear_table('exit4');
            $.each(s, function (i, d) {
                let row = frm.add_child('exit4', {
                    data_1: d.l2

                })
            })

            refresh_field("exit4");
        };
    },
    validate:function(frm) {
        var d1 = []
        $.each(frm.doc.exit1, function (i, d) {
            console.log(d.data_1)
            d1.push(d.data_1)
        })
        var d2 = []
        $.each(frm.doc.exit2, function (i, d) {
            console.log(d.data_1)
            d2.push(d.data_1)
        })
        var a = findDuplicates(d1)
        if (a.length != 0) {
            frappe.throw(" values should not repeate");
        }
        var b = findDuplicates(d2)
        if (b.length != 0) {
            frappe.throw(" values should not repeate");
        }
        checks = []
        $.each(frm.doc.exit3, function (i, row) {
            check = row.excellent + row.good + row.fair + row.poor
            checks.push(check)
        })
    
        console.log(checks)
        if(checks.includes(0)){
            frappe.throw(" values should not repeate ");
        }
        else if(checks.includes(2)){
            frappe.throw(" values should not repeate ");
        }
        else if(checks.includes(3)){
            frappe.throw(" values should not repeate ");
        }
        else if(checks.includes(4)){
            frappe.throw(" values should not repeate ");
        }
        checks1 =[]
        $.each(frm.doc.exit4, function (i, row) {
            check = row.excellent + row.good + row.fair + row.poor
            checks1.push(check)
        })
        if(checks1.includes(0)){
            frappe.throw(" values should not repeate ");
        }
        else if(checks1.includes(2)){
            frappe.throw(" values should not repeate ");
        }
        else if(checks1.includes(3)){
            frappe.throw(" values should not repeate ");
        }
        else if(checks1.includes(4)){
            frappe.throw(" values should not repeate ");
        }
    }
});
const findDuplicates = (arr) => {
    let sorted_arr = arr.slice().sort();
    // (we use slice to clone the array so the
    // original array won't be modified)
    let results = [];
    for (let i = 0; i < sorted_arr.length - 1; i++) {
        if (sorted_arr[i + 1] == sorted_arr[i]) {
            results.push(sorted_arr[i]);

        }
    }
    return results

}
