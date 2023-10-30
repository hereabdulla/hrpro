frappe.listview_settings['On Duty Application'] = {
	onload(listview) {
		frappe.breadcrumbs.add('On Duty Application','Home');
	listview.page.actions.find('[data-label="Edit"],[data-label="Assign To"],[data-label="Apply Assignment Rule"],[data-label="Add Tags"],[data-label="Print"]').parent().parent().remove()
	listview.page.fields_dict.workflow_state.get_query = function() {
		return {
			"filters": {
				"name": ["in", ["Pending for HOD","Pending for HR","Pending for GM","Pending for CEO","Approved","Rejected"]],
			}
		};
	}
	},
	// add_fields: ["status"],
	// get_indicator: function(doc) {
	// 	return [__(doc.status), frappe.utils.guess_colour(doc.status),
	// 		"status,=," + doc.status];
	// },

    // onload:function(listview){
	// 	frappe.model.get_value('Employee', { 'user_id': frappe.session.user }, 'employee_number',
    //         function (data) {
    //             if (data) {
    //                 me.filter_list.add_filter(me.doctype, "employee", '=', data.employee_number);
    //                 me.run()
    //             }
    //         })
    //     listview.page.add_menu_item(__("Approve"),function(){
    //         method = "hrpro.custom.bulk_onduty_approve"
    //         listview.call_for_selected_items(method,{'status':'Approved'});
    //     }),
    //     listview.page.add_menu_item(__("Reject"),function(){
    //         method = "hrpro.custom.bulk_on_duty_approve"
    //         listview.call_for_selected_items(method,{'status':'Rejected'});
    //     })
	// },
	
	
    // refresh:function(me){
	// 	me.page.sidebar.find(".list-link[data-view='Kanban']").addClass("hide");
	// 	me.page.sidebar.find(".list-link[data-view='Tree']").addClass("hide");
	// 	me.page.sidebar.find(".assigned-to-me a").addClass("hide");
	// 	frappe.model.get_value('Employee', { 'user_id': frappe.session.user }, 'employee_number',
    //         function (data) {
    //             if (data) {
    //                 me.filter_list.add_filter(me.doctype, "employee", '=', data.employee_number);
    //                 me.run()
    //             }
    //         })
	// 	frappe.call({
	// 		"method": "frappe.client.get_list",
	// 		args:{
	// 			doctype: "Employee",
	// 			filters: {"user_id": frappe.session.user}
	// 		},
	// 		callback: function(r){
	// 			n = r.message[0]
	// 			frappe.call({
	// 				"method": "frappe.client.get",
	// 				args:{
	// 					doctype: "Employee",
	// 					name: n.name
	// 				},
	// 				callback: function(r){
	// 					emp = r.message.employee_number;
	// 					if (!frappe.route_options) {
	// 						frappe.route_options = {
	// 							"employee": ["=", emp]
	// 						};
	// 				    }
	// 				}
	// 			})
	// 		}
	// 	})
	// }
    
};