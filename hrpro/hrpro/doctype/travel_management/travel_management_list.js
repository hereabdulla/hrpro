frappe.listview_settings['Travel Management'] = {
    onload:function(listview){
        listview.page.add_menu_item(__("Approve"),function(){
            method = "hrpro.custom.bulk_travel_approve"
            listview.call_for_selected_items(method,{'status':'Approved'});
        }),
        listview.page.add_menu_item(__("Reject"),function(){
            method = "hrpro.custom.bulk_travel_approve"
            listview.call_for_selected_items(method,{'status':'Rejected'});
        })
    },
    refresh:function(me){
		me.page.sidebar.find(".list-link[data-view='Kanban']").addClass("hide");
		me.page.sidebar.find(".list-link[data-view='Tree']").addClass("hide");
		me.page.sidebar.find(".assigned-to-me a").addClass("hide");
		if(!frappe.user.has_role("Travel Desk")){
			frappe.call({
				"method": "frappe.client.get_list",
				args:{
					doctype: "Employee",
					filters: {"user_id": frappe.session.user}
				},
				callback: function(r){
					frappe.call({
						"method": "frappe.client.get",
						args:{
							doctype: "Employee",
							name: r.message[0].name
						},
						callback: function(r){
							emp = r.message.employee_number;
							if (!frappe.route_options) {
								frappe.route_options = {
									"employee": ["=", emp]
								};
							}
						}
					})
				}
			})
	    }
	}
    
};