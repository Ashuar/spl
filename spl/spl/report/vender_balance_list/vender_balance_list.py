import frappe

def execute(filters=None):
    if not filters:
        frappe.throw("Filters cannot be empty")

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if not from_date or not to_date:
        frappe.throw("Please select From Date and To Date")

    frappe.logger().info(f"Fetching data from {from_date} to {to_date}")

    data = frappe.db.sql("""
        SELECT 
            gl.party AS vendor_account, 
            s.supplier_name AS vendor_name,
            SUM(CASE WHEN gl.posting_date < %(from_date)s THEN gl.debit - gl.credit ELSE 0 END) AS opening_balance,
            SUM(CASE WHEN gl.posting_date = %(to_date)s THEN gl.debit ELSE 0 END) AS debit_date,
            SUM(CASE WHEN gl.posting_date = %(to_date)s THEN gl.credit ELSE 0 END) AS credit_date,
            SUM(CASE WHEN gl.posting_date BETWEEN %(from_date)s AND %(to_date)s THEN gl.debit ELSE 0 END) AS debit_period,
            SUM(CASE WHEN gl.posting_date BETWEEN %(from_date)s AND %(to_date)s THEN gl.credit ELSE 0 END) AS credit_period,
            SUM(CASE WHEN gl.posting_date BETWEEN %(from_date)s AND %(to_date)s THEN gl.debit ELSE 0 END)-SUM(CASE WHEN gl.posting_date BETWEEN %(from_date)s AND %(to_date)s THEN gl.credit ELSE 0 END) AS total_balance,
            SUM(CASE WHEN gl.posting_date < %(from_date)s THEN gl.debit - gl.credit ELSE 0 END)+SUM(CASE WHEN gl.posting_date BETWEEN %(from_date)s AND %(to_date)s THEN gl.debit ELSE 0 END)-SUM(CASE WHEN gl.posting_date BETWEEN %(from_date)s AND %(to_date)s THEN gl.credit ELSE 0 END)AS closing_balance
        FROM `tabSupplier` s
        LEFT JOIN `tabGL Entry` gl ON s.name = gl.party AND gl.party_type = 'Supplier'
        WHERE s.disabled = 0
        GROUP BY gl.party, s.supplier_name
        ORDER BY closing_balance DESC
    """, {"from_date": from_date, "to_date": to_date}, as_dict=True)

    columns = [
        {"label": "Vendor Account", "fieldname": "vendor_account", "fieldtype": "Link", "options": "Supplier", "width": 120},
        {"label": "Vendor Name", "fieldname": "vendor_name", "fieldtype": "Data", "width": 200},
        {"label": "Opening Balance", "fieldname": "opening_balance", "fieldtype": "Currency", "width": 150},
        {"label": f"Debit ({to_date})", "fieldname": "debit_date", "fieldtype": "Currency", "width": 120},
        {"label": f"Credit ({to_date})", "fieldname": "credit_date", "fieldtype": "Currency", "width": 120},
        {"label": f"Debit ({from_date} to {to_date})", "fieldname": "debit_period", "fieldtype": "Currency", "width": 150},
        {"label": f"Credit ({from_date} to {to_date})", "fieldname": "credit_period", "fieldtype": "Currency", "width": 150},
        {"label": "Total", "fieldname": "total_balance", "fieldtype": "Currency", "width": 150},
        {"label": "Closing Balance", "fieldname": "closing_balance", "fieldtype": "Currency", "width": 150}
    ]

    return columns, data
