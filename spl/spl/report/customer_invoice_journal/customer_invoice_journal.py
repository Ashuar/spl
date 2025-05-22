# Copyright (c) 2025, Ali Raza and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data
import frappe
from frappe.utils import flt, today

def execute(filters=None):
    if not filters:
        filters = {}

    from_date = filters.get("from_date", today())
    to_date = filters.get("to_date", today())

    columns = [
        {"label": "Invoice", "fieldname": "invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 180},
        {"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": "Number Sequence Group", "fieldname": "number_seq", "fieldtype": "Data", "width": 150},
        {"label": "Invoice Account", "fieldname": "invoice_account", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": "Invoicing Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        {"label": "Line Discount", "fieldname": "line_discount", "fieldtype": "Currency", "width": 120},
        {"label": "Total Charges", "fieldname": "total_charges", "fieldtype": "Currency", "width": 120},
        {"label": "Selected Misc. Charges", "fieldname": "misc_charges", "fieldtype": "Currency", "width": 150},
        {"label": "Total Discount Charges", "fieldname": "discount_charges", "fieldtype": "Currency", "width": 150},
        {"label": "Sales Tax", "fieldname": "sales_tax", "fieldtype": "Currency", "width": 120},
        {"label": "Sum Line Qty", "fieldname": "sum_qty", "fieldtype": "Float", "width": 120},
        {"label": "Currency", "fieldname": "currency", "fieldtype": "Data", "width": 100},
        {"label": "Invoice Amount (Currency)", "fieldname": "invoice_amount_currency", "fieldtype": "Currency", "width": 150},
        {"label": "Invoice Amount", "fieldname": "invoice_amount", "fieldtype": "Currency", "width": 150}
    ]

    invoices = frappe.db.sql("""
        SELECT 
            naming_series AS invoice,
            posting_date,
            customer AS invoice_account,
            customer_name,
            additional_discount_percentage AS line_discount,
            total_taxes_and_charges AS total_charges,
            0 AS misc_charges,  
            discount_amount AS discount_charges,  
            total_taxes_and_charges AS sales_tax,
            (SELECT SUM(qty) FROM `tabSales Invoice Item` WHERE parent = si.name) AS sum_qty,
            currency,
            base_grand_total AS invoice_amount_currency,
            grand_total AS invoice_amount
        FROM `tabSales Invoice` si
        WHERE posting_date BETWEEN %(from_date)s AND %(to_date)s
        ORDER BY posting_date ASC
    """, {"from_date": from_date, "to_date": to_date}, as_dict=True)


    data = []
    for inv in invoices:
        data.append({
            "invoice": inv.invoice,
            "posting_date": inv.posting_date,
            "number_seq": inv.invoice.replace("SalesCN_", ""),  
            "invoice_account": inv.invoice_account,
            "customer_name": inv.customer_name,
            "line_discount": flt(inv.line_discount or 0),
            "total_charges": flt(inv.total_charges or 0),
            "misc_charges": flt(inv.misc_charges or 0),
            "discount_charges": flt(inv.discount_charges or 0),
            "sales_tax": flt(inv.sales_tax or 0),
            "sum_qty": flt(inv.sum_qty or 0),
            "currency": inv.currency,
            "invoice_amount_currency": flt(inv.invoice_amount_currency or 0),
            "invoice_amount": flt(inv.invoice_amount or 0)
        })

    return columns, data
