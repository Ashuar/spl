// Copyright (c) 2025, Ali Raza and contributors
// For license information, please see license.txt

frappe.query_reports["Deposit Summary by Date"] = {
	filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            "default": frappe.datetime.add_days(frappe.datetime.nowdate(), -30),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        },
        {
            fieldname: "bank_account",
            label: __("Bank Account"),
            fieldtype: "Link",
            options: "Bank Account",
            reqd: 0
        }
    ],

    formatter: function(value, row, column, data, default_formatter) {
        if (column.fieldname === "amount_registration_currency" && typeof value === "string" && value.includes("──────────────")) {
            return `<span style="color: gray; font-weight: bold;">${value}</span>`;
        }
        return default_formatter(value, row, column, data);
    }
};
