// Copyright (c) 2016, VHRS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attendance recapitulation"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"
		},
		{
			"fieldname": "location",
			"label": __("Location"),
			"fieldtype": "Link",
			"options": "Location"
		},
		// {
		// 	"fieldname": "status_absent",
		// 	"label": __("Absent"),
		// 	"fieldtype": "Check"
		// },
		// {
		// 	"fieldname": "status_in",
		// 	"label": __("In"),
		// 	"fieldtype": "Check"
		// },
		{
			"fieldname": "user",
			"label": __("Employee"),
			"fieldtype": "Data",
			"default": frappe.session.user,
			"hidden": 1
		},

	],

	"formatter": function (row, cell, value, columnDef, dataContext, default_formatter) {

		if (columnDef.id == "Name" && frappe.user.has_role("System Manager")) {
			value = dataContext.Name
			columnDef.df.link_onclick =
				"frappe.query_reports['Attendance recapitulation'].open_att_adjust(" + JSON.stringify(dataContext) + ")";
		}
		if (columnDef.id == "Name" && frappe.user.has_role("Employee")) {
			value = dataContext.Name
			columnDef.df.link_onclick =
				"frappe.query_reports['Attendance recapitulation'].open_att_adjust1(" + JSON.stringify(dataContext) + ")";
		}
		if (columnDef.id == "Shift" && frappe.user.has_role("System Manager")) {
			value = dataContext.Shift
			columnDef.df.link_onclick =
				"frappe.query_reports['Attendance recapitulation'].open_att_adjust2(" + JSON.stringify(dataContext) + ")";
		}
		value = default_formatter(row, cell, value, columnDef, dataContext);
		if (columnDef.id == "Session1") {
			if (dataContext["Session1"] === "AB") {
					var con = JSON.stringify(dataContext)
					// console.log(`Fifteen is ${a + b} and not ${2 * a + b}.`);
					// console.log(frappe.query_reports[\'Attendance recapitulation\'].open_att_adjust1(${con})')
					value = '<a onclick="frappe.query_reports[\'Attendance recapitulation\'].open_att_adjust1()"><span style="color:red!important;font-weight:bold">' + value + "</a></span>";
			}
			if (dataContext["Session1"] === "PR") {
				value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
			}
			if (dataContext["Session1"] === "CL") {
				value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
			}
		}
		if (columnDef.id == "Session2") {
			if (dataContext["Session2"] === "AB") {
				value = '<a onclick="frappe.query_reports[\'Attendance recapitulation\'].open_att_adjust1()"><span style="color:red!important;font-weight:bold">' + value + "</a></span>";
			}
			if (dataContext["Session2"] === "PR") {
				value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
			}
			if (dataContext["Session2"] === "CL" || dataContext["Session2"] === "PL" || dataContext["Session2"] === "SL") {
				value = "<span style='color:blue!important;font-weight:bold'>" + value + "</span>";
			}
		}
		return value;
	},
	//added to block employees from accessing attendance
	"block_employee": function (data) {

		
	},

	"open_att_adjust": function (data) {

		if (data['In Time'] == '-') {
			data['In Time'] = ""
		}
		if (data['Out Time'] == '-') {
			data['Out Time'] = ""
		}
		var in_out_time = "";
		var d = new frappe.ui.Dialog({
			'fields': [
				{ 'fieldname': 'ht', 'fieldtype': 'HTML' },
				{ label: "Mark P", 'fieldname': 'present', 'fieldtype': 'Check' },
				{ label: "Mark AB", 'fieldname': 'absent', 'fieldtype': 'Check' },
				{ label: "Mark PH", 'fieldname': 'ph', 'fieldtype': 'Check' },
				{ label: "Mark WO", 'fieldname': 'wo', 'fieldtype': 'Check' },
				{ label: "Mark First Half Present", 'fieldname': 'first_half_present', 'fieldtype': 'Check' },
				{ label: "Mark Second Half Present", 'fieldname': 'second_half_present', 'fieldtype': 'Check' },
				{ label: "Mark First Half Absent", 'fieldname': 'first_half_absent', 'fieldtype': 'Check' },
				{ label: "Mark Second Half Absent", 'fieldname': 'second_half_absent', 'fieldtype': 'Check' },
				{ fieldtype: "Column Break", fieldname: "cb1", label: __(""), reqd: 0 },
				{ fieldtype: "Data", fieldname: "in_time", label: __("In Time"), default: data['In Time'], reqd: 0 },
				{ fieldtype: "Button", fieldname: "apply_od", label: __("Apply OD"), reqd: 0 },
				{ fieldtype: "Button", fieldname: "apply_leave", label: __("Apply Leave"), reqd: 0 },
				{ fieldtype: "Button", fieldname: "apply_mr", label: __("Apply Movement Register"), reqd: 0 },
				{ fieldtype: "Button", fieldname: "apply_tour", label: __("Apply Tour Application"), reqd: 0 },
				{ fieldtype: "Button", fieldname: "apply_mp", label: __("Apply Missed Punch"), reqd: 0 },
				{ fieldtype: "Column Break", fieldname: "cb2", label: __(""), reqd: 0 },
				{ fieldtype: "Data", fieldname: "out_time", label: __("Out Time"), default: data['Out Time'], reqd: 0 },
				{ fieldtype: "Section Break", fieldname: "sb1", label: __(""), reqd: 0 },
				
			],
			primary_action: function () {
				var status = d.get_values()
				if (!status.out_time) {
					status.out_time = ""
				}
				if (!status.in_time) {
					status.in_time = ""
				}
				if ((status.present) || (status.absent) || (status.ph) || (status.wo) || (status.in_time) || (status.out_time) || (status.first_half_present) || (status.second_half_present) || (status.first_half_absent) || (status.second_half_absent)) {
					frappe.call({
						method: "hrpro.custom.att_adjust",
						args: {
							'employee': data['Employee'],
							'attendance_date': data['Attendance Date'],
							'name': data['Name'],
							"in_time": status.in_time,
							"out_time": status.out_time,
							"status_p": status.present,
							"status_a": status.absent,
							"status_ph": status.ph,
							"status_wo": status.wo,
							"status_first_half_present": status.first_half_present,
							"status_second_half_present": status.second_half_present,
							"status_first_half_absent": status.first_half_absent,
							"status_second_half_absent": status.second_half_absent
						},
						callback: function (r) {
							frappe.query_report.refresh();
							show_alert(__("Attendance Updated"))
							d.hide()
						}
					})
				}
				else {
					d.hide()
				}
			}
		});

		// $(d.fields_dict.assign.input).css("backgroundColor", "DarkOrange");
		// d.fields_dict.assign.input.onclick = function () {
		// 	var val = d.get_values()
		// 	frappe.call({
		// 		method: "hrpro.custom.shift_assignment",
		// 		args: {
		// 			"employee": data['Employee'],
		// 			"attendance_date": data['Attendance Date'],
		// 			"shift": val.shift
		// 		},
		// 		callback: function (r) {
		// 			if (r.message) {
		// 				d.hide()
		// 				frappe.msgprint("Shift Assigned Successfully")
		// 			}
		// 		}
		// 	})
		// }
		d.fields_dict.ht.$wrapper.html('Modify Attendance?');
		// d.fields_dict.ht1.$wrapper.html('Shift Assignment?');
		d.show();
	},
	"open_att_adjust1": function (data) {
		var d1 = new frappe.ui.Dialog({
			'fields': [
				{ fieldtype: "Button", fieldname: "apply_od", label: __("Apply OD"), reqd: 0 },
				{ fieldtype: "Button", fieldname: "apply_leave", label: __("Apply Leave"), reqd: 0 },
				{ fieldtype: "Button", fieldname: "apply_mr", label: __("Apply Movement Register"), reqd: 0 },
				{ fieldtype: "Button", fieldname: "apply_tour", label: __("Apply Tour Application"), reqd: 0 },
				{ fieldtype: "Button", fieldname: "apply_mp", label: __("Apply Missed Punch"), reqd: 0 },

			],
			primary_action: function () {
				var status = d1.get_values()
			}
		})
		
		d1.fields_dict.apply_od.input.onclick = function () {
			frappe.set_route("Form", "On Duty Application", "New On Duty Application", { "is_from_ar": "Yes" })
		}
		d1.fields_dict.apply_leave.input.onclick = function () {
			frappe.set_route("Form", "Leave Application", "New Leave Application", { "is_from_ar": "Yes" })
		}
		d1.fields_dict.apply_mr.input.onclick = function () {
			frappe.set_route("Form", "Movement Register", "New Movement Register", { "is_from_ar": "Yes" })
		}
		d1.fields_dict.apply_tour.input.onclick = function () {
			frappe.set_route("Form", "Tour Application", "New Tour Application", { "is_from_ar": "Yes" })
		}
		d1.fields_dict.apply_mp.input.onclick = function () {
			
			var att_date = data["Attendance Date"]
			m = moment(data["Attendance Date"])
			var att_date = m.format('DD-MM-YYYY')
			var att_date_f = new Date(att_date);
			frappe.set_route("Form", "Miss Punch Application", "New Miss Punch Application",{ "is_from_ar": "No","attendance_date": att_date })
		}
		d1.show();
	},
	"open_att_adjust2": function (data) {
		var d2 = new frappe.ui.Dialog({
			'fields': [
				{ 'fieldname': 'ht1', 'fieldtype': 'HTML' },
				{ fieldtype: "Date", fieldname: "date", label: __("Date"), default: data['Attendance Date'], reqd: 0 },
				{ fieldtype: "Column Break", fieldname: "cb3", label: __(""), reqd: 0 },
				{ fieldtype: "Button", fieldname: "assign", label: __("Assign"), reqd: 0 },
				{ fieldtype: "Select", fieldname: "shift", label: __("Shift"), options: ["GF1(8:00:00 - 16:30:00)", "GF2(9:00:00 - 17:30:00)","GF3(5:00:00 - 13:30:00)","GF4(7:30:00 - 16:00:00)", "GO1(8:00:00 - 16:45:00)", "GO2(9:00:00 - 17:45:00)", "GO3(10:00:00 - 18:45:00)","FS1(6:00:00 - 14:30:00)", "FS2(7:00:00 - 15:30:00)", "FS3(15:00:00 - 23:00:00)", "FS4(23:00:00 - 7:00:00)"], reqd: 0 }

			],
			primary_action: function () {
				var val = d2.get_values()

			}
		})
		$(d2.fields_dict.assign.input).css("backgroundColor", "DarkOrange");
		d2.fields_dict.assign.input.onclick = function () {
			var val = d2.get_values()
			frappe.call({
				method: "hrpro.custom.shift_assignment",
				args: {
					"employee": data['Employee'],
					"attendance_date": data['Attendance Date'],
					"shift": val.shift
				},
				callback: function (r) {
					if (r.message) {
						d2.hide()
						frappe.msgprint("Shift Assigned Successfully")
						frappe.query_report.refresh();
					}
				}
			})
		}
		d2.fields_dict.ht1.$wrapper.html('Shift Assignment?');
		d2.show();
	},
	"onload": function () {
		return frappe.call({
			method: "hrpro.hrpro.report.attendance_recapitulation.attendance_recapitulation.get_filter_dates",
			callback: function (r) {
				var from_date_filter = frappe.query_report_filters_by_name.from_date;
				var to_date_filter = frappe.query_report_filters_by_name.to_date;
				from_date_filter.df.default = r.message[0];
				to_date_filter.df.default = r.message[1];
				from_date_filter.refresh();
				to_date_filter.refresh();
				from_date_filter.set_input(from_date_filter.df.default);
				to_date_filter.set_input(to_date_filter.df.default);
			}
		});
	}
}