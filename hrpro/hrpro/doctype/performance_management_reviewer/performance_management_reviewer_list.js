frappe.listview_settings['Performance Management Reviewer'] = {
    // onload:function(frm){
    //     frm.trigger("refresh")
    // },
    refresh: function (me) {
    //     if(!frappe.user.has_role("System Manager")){
    //     d = new Date()
    //     var apy = d.getFullYear() - 1
    //     console.log(apy)
    //     frappe.route_options = {
    //         "appraisal_year": ["=", apy],
    //     };
    // }
        me.page.sidebar.find(".list-link[data-view='Kanban']").addClass("hide");
        me.page.sidebar.find(".list-link[data-view='Tree']").addClass("hide");
        me.page.sidebar.find(".assigned-to-me a").addClass("hide");
        // if(!frappe.user.has_role("System Manager")){
        //     if (!frappe.route_options) {
        //         frappe.route_options = {
        //             "reviewer": ["=", frappe.session.user]
        //         };
        //     }
        // }
    }

};