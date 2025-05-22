import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data

def get_columns():
    return [
        {"fieldname": "customer_account", "label": "Customer Account", "fieldtype": "Data", "width": 120},
        {"fieldname": "customer_name", "label": "Name", "fieldtype": "Data", "width": 150},
        {"fieldname": "currency", "label": "Currency", "fieldtype": "Data", "width": 80},
        {"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 100},
        {"fieldname": "bank_account", "label": "Bank Account", "fieldtype": "Data", "width": 150},
        {"fieldname": "payment_reference", "label": "Payment Reference", "fieldtype": "Data", "width": 150},
        {"fieldname": "deposit_slip", "label": "Deposit Slip", "fieldtype": "Data", "width": 120},
        {"fieldname": "currency_type", "label": "Transaction Currency", "fieldtype": "Data", "width": 100},
        {"fieldname": "amount", "label": "Amount in Transaction", "fieldtype": "Currency", "width": 150},
        {"fieldname": "amount", "label": "Amount", "fieldtype": "Currency", "width": 150}
    ]

def get_data(filters):
    conditions = "pe.docstatus = 1"
    
    if filters.get("from_date"):
        conditions += f" AND pe.posting_date >= '{filters.get('from_date')}'"
    if filters.get("to_date"):
        conditions += f" AND pe.posting_date <= '{filters.get('to_date')}'"
    if filters.get("customer"):
        conditions += f" AND pe.party = '{filters.get('customer')}'"

    query = f"""
        SELECT 
            pe.party AS customer_account,
            c.customer_name AS customer_name,
            pe.paid_from_account_currency AS currency,
            pe.posting_date AS date,
            pe.paid_to AS bank_account,
            pe.reference_no AS payment_reference,
            pe.reference_date AS deposit_slip,
            pe.paid_to_account_currency AS currency_type,
            pe.paid_amount AS amount
        FROM 
            `tabPayment Entry` pe
        JOIN 
            `tabCustomer` c ON pe.party = c.name
        WHERE {conditions}
        ORDER BY pe.party, pe.posting_date;
    """

    raw_data = frappe.db.sql(query, as_dict=True)
    processed_data = []
    
    total_amount = 0  # Grand total
    customer_total = 0
    last_customer = None

    for row in raw_data:
        if last_customer and last_customer != row["customer_account"]:
            # Insert separator before total row
            processed_data.append({
                "customer_account": "",
                "customer_name": "",
                "currency": "",
                "date": "",
                "bank_account": "",
                "payment_reference": "",
                "deposit_slip": "",
                "currency_type": "",
                "amount": "──────────────"
            })

            # Insert subtotal row
            processed_data.append({
                "customer_account": "Total :",
                "customer_name": "",
                "currency": "",
                "date": "",
                "bank_account": "",
                "payment_reference": "",
                "deposit_slip": "",
                "currency_type": "",
                "amount": customer_total  # Subtotal per customer
            })

            # Insert separator after total row
            processed_data.append({
                "customer_account": "",
                "customer_name": "",
                "currency": "",
                "date": "",
                "bank_account": "",
                "payment_reference": "",
                "deposit_slip": "",
                "currency_type": "",
                "amount": "──────────────"
            })
            
            customer_total = 0  # Reset for next customer

        processed_data.append(row)
        total_amount += row["amount"]  # Add to grand total
        customer_total += row["amount"]  # Add to customer total
        last_customer = row["customer_account"]

    # Add last customer's total row with separators
    if last_customer:
        processed_data.append({
            "customer_account": "",
            "customer_name": "",
            "currency": "",
            "date": "",
            "bank_account": "",
            "payment_reference": "",
            "deposit_slip": "",
            "currency_type": "",
            "amount": "──────────────"
        })
        processed_data.append({
            "customer_account": "Total :",
            "customer_name": "",
            "currency": "",
            "date": "",
            "bank_account": "",
            "payment_reference": "",
            "deposit_slip": "",
            "currency_type": "",
            "amount": customer_total
        })
        processed_data.append({
            "customer_account": "",
            "customer_name": "",
            "currency": "",
            "date": "",
            "bank_account": "",
            "payment_reference": "",
            "deposit_slip": "",
            "currency_type": "",
            "amount": "──────────────"
        })

    # Add grand total row
    processed_data.append({
        "customer_account": "Grand Total :",
        "customer_name": "",
        "currency": "",
        "date": "",
        "bank_account": "",
        "payment_reference": "",
        "deposit_slip": "",
        "currency_type": "",
        "amount": total_amount
    })

    return processed_data
