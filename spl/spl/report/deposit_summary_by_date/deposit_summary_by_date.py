import frappe
from frappe.utils import flt, today

def execute(filters=None):
    if not filters:
        filters = {}

    from_date = filters.get("from_date", today())
    to_date = filters.get("to_date", today())
    bank_account = filters.get("bank_account")

    columns = [
        {"label": "Bank Account", "fieldname": "bank_account", "fieldtype": "Link", "options": "Bank Account", "width": 200},
        {"label": "Account Name", "fieldname": "account_name", "fieldtype": "Data", "width": 250},
        {"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": "Customer Account", "fieldname": "customer_account", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": "Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        {"label": "Payment Reference", "fieldname": "payment_reference", "fieldtype": "Data", "width": 200},
        {"label": "Deposit Slip", "fieldname": "deposit_slip", "fieldtype": "Data", "width": 150},
        {"label": "Registration Currency", "fieldname": "registration_currency", "fieldtype": "Data", "width": 100},
        {"label": "Amount in Registration Currency", "fieldname": "amount_registration_currency", "fieldtype": "Currency", "width": 200}
    ]

    conditions = "WHERE pe.docstatus = 1 AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    params = {"from_date": from_date, "to_date": to_date}

    if bank_account:
        conditions += " AND pe.paid_from = %(bank_account)s"
        params["bank_account"] = bank_account

    payments = frappe.db.sql(f"""
        SELECT 
            pe.bank_account AS bank_account,
            ba.account_name AS account_name,
            pe.posting_date,
            pe.party AS customer_account,
            pe.party_name AS customer_name,
            pe.reference_no AS payment_reference,
            pe.reference_date AS deposit_slip,
            pe.paid_from_account_currency AS registration_currency,
            pe.paid_amount AS amount_registration_currency
        FROM `tabPayment Entry` pe
        LEFT JOIN `tabCustomer` c ON pe.party = c.name
        LEFT JOIN `tabBank Account` ba ON pe.bank_account = ba.name
        {conditions}
        ORDER BY pe.paid_from, pe.posting_date ASC
    """, params, as_dict=True)

    data = []
    grouped_data = {}
    grand_total_all_banks = 0  # NEW VARIABLE TO TRACK OVERALL TOTAL

    # Group data by Bank Account and Date
    for pay in payments:
        bank_key = pay.bank_account
        date_key = pay.posting_date

        if bank_key not in grouped_data:
            grouped_data[bank_key] = {
                "bank_account": pay.bank_account,
                "account_name": pay.account_name,
                "dates": {},
                "total": 0  # Grand total for the bank account
            }

        if date_key not in grouped_data[bank_key]["dates"]:
            grouped_data[bank_key]["dates"][date_key] = {
                "transactions": [],
                "subtotal": 0
            }

        grouped_data[bank_key]["dates"][date_key]["transactions"].append({
            "posting_date": pay.posting_date,
            "customer_account": pay.customer_account,
            "customer_name": pay.customer_name,
            "payment_reference": pay.payment_reference,
            "deposit_slip": pay.deposit_slip,
            "registration_currency": pay.registration_currency,
            "amount_registration_currency": flt(pay.amount_registration_currency or 0)
        })

        grouped_data[bank_key]["dates"][date_key]["subtotal"] += flt(pay.amount_registration_currency or 0)
        grouped_data[bank_key]["total"] += flt(pay.amount_registration_currency or 0)
        grand_total_all_banks += flt(pay.amount_registration_currency or 0)  # UPDATE GLOBAL TOTAL

    # Prepare final report data
    for bank, details in grouped_data.items():
        # Add bank account header
        data.append({"bank_account": details["bank_account"], "account_name": details["account_name"]})

        for date, date_details in details["dates"].items():
            # Add transactions for the date
            for txn in date_details["transactions"]:
                data.append({
                    "posting_date": txn["posting_date"],
                    "customer_account": txn["customer_account"],
                    "customer_name": txn["customer_name"],
                    "payment_reference": txn["payment_reference"],
                    "deposit_slip": txn["deposit_slip"],
                    "registration_currency": txn["registration_currency"],
                    "amount_registration_currency": txn["amount_registration_currency"]
                })

            # Add separator before subtotal row
            data.append({"amount_registration_currency": "──────────────────"})
            
            # Add subtotal row for the date
            data.append({
                "bank_account": "Subtotal :",
                "amount_registration_currency": date_details["subtotal"]
            })

            # Add separator after subtotal row
            data.append({"amount_registration_currency": "──────────────────"})

    # FINAL GRAND TOTAL FOR ALL BANK ACCOUNTS
    data.append({
        "bank_account": "Grand Total :",
        "amount_registration_currency": grand_total_all_banks
    })
    data.append({"amount_registration_currency": "──────────────────"})

    return columns, data
