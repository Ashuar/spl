frappe.query_reports["Deposit Summary by Customer"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.nowdate(), -30)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            default: frappe.datetime.get_today()
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer"
        }
    ],
    "formatter": function(value, row, column, data, default_formatter) {
    if (column.fieldname === "amount" && value === "──────────────") {
        return `<div style="text-align: right; font-weight: bold;">${value}</div>`;
    }
    return default_formatter(value, row, column, data);
},
    "onload": function(report) {
        report.page.add_inner_button(__("Export to Excel"), function() {
            let data = frappe.query_report.data;
            let columns = frappe.query_report.columns;

            let csvContent = "data:text/csv;charset=utf-8," + columns.map(col => col.label).join(",") + "\n";
            data.forEach(row => {
                let rowData = columns.map(col => row[col.fieldname] || "").join(",");
                csvContent += rowData + "\n";
            });

            let encodedUri = encodeURI(csvContent);
            let link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "Deposit_Summary_by_Customer.csv");
            document.body.appendChild(link);
            link.click();
        });

        // frappe.msgprint("Report Loaded Successfully!");
    }
};
