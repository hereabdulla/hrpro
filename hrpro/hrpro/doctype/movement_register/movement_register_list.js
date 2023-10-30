frappe.listview_settings['Movement Register'] = {
	add_fields: ["status"],
	get_indicator: function(doc) {
		return [__(doc.status), frappe.utils.guess_colour(doc.status),
			"status,=," + doc.status];
	},
    onload:function(listview){
    },
    refresh:function(me){
		me.page.sidebar.find(".list-link[data-view='Kanban']").addClass("hide");
		me.page.sidebar.find(".list-link[data-view='Tree']").addClass("hide");
		me.page.sidebar.find(".assigned-to-me a").addClass("hide");
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
								"employee": ["=", emp],
							};
					    }
					}
				})
			}
		})
	}
    
};