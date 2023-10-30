// Copyright (c) 2016, VHRS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["PM Pending List"] = {
	"filters": [
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options":"Employee"
		},
		{
			"fieldname":"department",
			"label": __("Depratment"),
			"fieldtype": "Link",
			"options":"Department"
		},
		{
			"fieldname":"location",
			"label": __("Location"),
			"fieldtype": "Link",
			"options":"Location"
		},
		{
			"fieldname":"business_unit",
			"label": __("Business Unit"),
			"fieldtype": "Select",
			"options":"\nG&A\nAP\nWCP\nTMI"
		}

	],
	"formatter": function (row, cell, value, columnDef, dataContext, default_formatter) {
		value = default_formatter(row, cell, value, columnDef, dataContext);
		if (columnDef.id == "Self Status") {
			if (dataContext["Self Status"] === "Completed") {
				value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
			}
		}
		if (columnDef.id == "Manager Status") {
		if (dataContext["Manager Status"] === "Completed") {
			value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
		}
		}	
		if (columnDef.id == "HOD Status") {
		if (dataContext["HOD Status"] === "Completed") {
			value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
		}
	}
	if (columnDef.id == "Reviewer Status") {
		if (dataContext["Reviewer Status"] === "Completed") {
			value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
		}
	}
		return value;
	},
}
