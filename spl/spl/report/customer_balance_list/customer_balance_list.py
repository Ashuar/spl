import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if not from_date or not to_date:
        frappe.throw("Please select From Date and To Date")

    data = frappe.db.sql("""
        SELECT 
            gl.party AS customer_account, 
            c.customer_name AS customer_name,
            c.customer_group AS sales_group,
            SUM(CASE WHEN gl.posting_date < %(from_date)s THEN gl.debit - gl.credit ELSE 0 END) AS opening_balance,
            SUM(CASE WHEN gl.posting_date = %(to_date)s THEN gl.debit ELSE 0 END) AS debit_on_date,
            SUM(CASE WHEN gl.posting_date = %(to_date)s THEN gl.credit ELSE 0 END) AS credit_on_date,
            SUM(CASE WHEN gl.posting_date BETWEEN %(from_date)s AND %(to_date)s THEN gl.debit ELSE 0 END) AS total_debit,
            SUM(CASE WHEN gl.posting_date BETWEEN %(from_date)s AND %(to_date)s THEN gl.credit ELSE 0 END) AS total_credit,
            SUM(CASE WHEN gl.posting_date BETWEEN %(from_date)s AND %(to_date)s THEN gl.debit ELSE 0 END)-SUM(CASE WHEN gl.posting_date BETWEEN %(from_date)s AND %(to_date)s THEN gl.credit ELSE 0 END) AS total_balance,
            SUM(CASE WHEN gl.posting_date < %(from_date)s THEN gl.debit - gl.credit ELSE 0 END)+SUM(CASE WHEN gl.posting_date BETWEEN %(from_date)s AND %(to_date)s THEN gl.debit ELSE 0 END)-SUM(CASE WHEN gl.posting_date BETWEEN %(from_date)s AND %(to_date)s THEN gl.credit ELSE 0 END)AS closing_balance
        FROM `tabCustomer` c
        LEFT JOIN `tabGL Entry` gl ON c.name = gl.party AND gl.party_type = 'Customer'
        WHERE c.disabled = 0
        GROUP BY c.name
        ORDER BY total_balance DESC
    """, {"from_date": from_date, "to_date": to_date}, as_dict=True)

    columns = [
        {"label": "Customer Account", "fieldname": "customer_account", "fieldtype": "Link", "options": "Customer", "width": 120},
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        {"label": "Sales Group", "fieldname": "sales_group", "fieldtype": "Data", "width": 150},  
        {"label": f"Opening Balance ({from_date})", "fieldname": "opening_balance", "fieldtype": "Currency", "width": 150},
        {"label": f"Debit ({to_date})", "fieldname": "debit_on_date", "fieldtype": "Currency", "width": 120},
        {"label": f"Credit ({to_date})", "fieldname": "credit_on_date", "fieldtype": "Currency", "width": 120},
        {"label": f"Total Debit ({from_date} to {to_date})", "fieldname": "total_debit", "fieldtype": "Currency", "width": 150},
        {"label": f"Total Credit ({from_date} to {to_date})", "fieldname": "total_credit", "fieldtype": "Currency", "width": 150},
        {"label": "Total Balance", "fieldname": "total_balance", "fieldtype": "Currency", "width": 120},
        {"label": f"Closing Balance ({to_date})", "fieldname": "closing_balance", "fieldtype": "Currency", "width": 150}
    ]

    return columns, data
