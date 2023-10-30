// Copyright (c) 2016, TeamPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["PF Report"] = {
	"filters": [
        {
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"reqd": 1 ,
			"options": [
				{ "value": 1, "label": __("Jan") },
				{ "value": 2, "label": __("Feb") },
				{ "value": 3, "label": __("Mar") },
				{ "value": 4, "label": __("Apr") },
				{ "value": 5, "label": __("May") },
				{ "value": 6, "label": __("June") },
				{ "value": 7, "label": __("July") },
				{ "value": 8, "label": __("Aug") },
				{ "value": 9, "label": __("Sep") },
				{ "value": 10, "label": __("Oct") },
				{ "value": 11, "label": __("Nov") },
				{ "value": 12, "label": __("Dec") },
			],
			"default": frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth() + 1,
		},
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Select",
			"reqd": 1,
		},
    ],

onload : function(report,filters) {
	report.page.add_inner_button(__('Download TXT File'), function() {
        values = []
		data=[]
        columns = []
        report_data = report.data
        console.log(report_data)
		console.log(filters[0])
		for(i=0;i< report_data.length;i++){
			for(j=0;j< 1;j++){
				console.log(report_data[i])
				values.push(Object.values(report_data[i]))
			}
			data.push([values])
		};
        
        // window.location.href = repl(frappe.request.url +
		// 	'?cmd=%(cmd)s&column=%(column)s&value=%(value)s', {
		// 	cmd: "hrpro.hrpro.report.pf_report.pf_report.get_template",
        //     column: columns,
        //     value: data,
		// });
        
	});
    return  frappe.call({
        method: "hrpro.hrpro.report.pf_report.pf_report.get_years",
        callback: function(r) {
            var year_filter = frappe.query_report.get_filter('year');
            year_filter.df.options = r.message;
            year_filter.df.default = r.message.split("\n")[0];
            year_filter.refresh();
            year_filter.set_input(year_filter.df.default);
        }
    });
}
};