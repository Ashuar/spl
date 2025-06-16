// Copyright (c) 2025, Ali Raza and contributors
// For license information, please see license.txt

frappe.query_reports["Planned Vs Actual Cost"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "fieldtype": "Date",
            "label": "From Date",
            "default": frappe.utils.add_months(frappe.utils.nowdate(), -1)
        },
        {
            "fieldname": "to_date",
            "fieldtype": "Date",
            "label": "To Date",
            "default": frappe.utils.nowdate()
        },
        {
            "fieldname": "work_order",
            "fieldtype": "Link",
            "label": "Work Order",
            "options": "Work Order" 
        }
    ]
}
