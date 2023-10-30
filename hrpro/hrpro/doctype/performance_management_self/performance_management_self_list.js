frappe.listview_settings['Performance Management Self'] = {
    // onload:function(frm){
    //     console.log("helo")
    // },
    refresh: function (me) {
       
        var emp = ""
        me.page.sidebar.find(".list-link[data-view='Kanban']").addClass("hide");
        me.page.sidebar.find(".list-link[data-view='Kanban']").addClass("hide");
        me.page.sidebar.find(".assigned-to-me a").addClass("hide");

        frappe.model.get_value('Employee', { 'user_id': frappe.session.user }, 'employee_number',
            function (data) {
                if (data) {
                    me.filter_list.add_filter(me.doctype, "employee_code", '=', data.employee_number);
                    me.run()
                }
            })

        frappe.call({
            "method": "frappe.client.get_list",
            args: {
                doctype: "Employee",
                filters: { "user_id": frappe.session.user }
            },
            callback: function (r) {
                emp = r.message[0].name
                frappe.model.get_value('Performance Management Self', { 'appraisal_year': apy,'employee_code':emp }, 'name',
                    function (data) {
                        if (data) {
                            me.page.btn_primary.hide()
                        }
                    })
                if (!frappe.user.has_role("System Manager")) {
                    d = new Date()
                    var apy = d.getFullYear() - 1
                    if (!frappe.route_options) {
                        frappe.route_options = {
                            "employee_code1": ["=", emp],
                            "appraisal_year": ["=", apy]
                        };
                    }
                }
            }
        })

    }




};