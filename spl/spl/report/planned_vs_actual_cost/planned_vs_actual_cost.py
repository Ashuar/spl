# Copyright (c) 2025, Ali Raza and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today

def execute(filters=None):
    columns = get_columns()
    data = get_report_data(filters)  # Get properly structured data
    return columns, data

def get_report_data(filters):
    filters = frappe.parse_json(filters) if filters else None
    data = []
    
    # Get all submitted Stock Entries
    stock_entries = frappe.get_all("Stock Entry",
        filters={"docstatus": 1, "stock_entry_type": "Manufacture"},
        fields=["name", "work_order", "posting_date", "bom_no"]
    )
    
    
    for entry in stock_entries:
        # Get items for each Stock Entry
        items = frappe.get_all("Stock Entry Detail",
            filters={"parent": entry.name,
                     "item_code":["not in", frappe.get_all("Item",
                                filters={"item_group": ["in"
									,["SFG Lasting", "SFG Stitching", "SFG Cutting", "Finished", "Local Shoes"]]
                                    },
                                    pluck="name"
                                )]
                    },
            fields=["item_code", "item_name", "basic_rate", "qty", "amount"]
        )
        planned_items = {}
        if entry.bom_no:
            bom_items = frappe.get_all("BOM Item", filters={"parent": entry.bom_no,},
                fields=["item_code", "rate", "amount", "qty"])
            planned_items = {item.item_code: item for item in bom_items}
        for item in items:
            # Create a dictionary for each row
            planned_data = planned_items.get(item.item_code, {})
            row = {
                "stock_entry": entry.name,
                "posting_date": entry.posting_date,
                "work_order": entry.work_order,
                "item_code": item.get("item_code"),
                "item_name": item.get("item_name"),
                "estimated_qty": planned_data.get("qty"),
                "estimated_amount": planned_data.get("amount", 0),
                "total_estimated": planned_data.get("rate", 0) * item.get("qty"),
                "qty": item.get("qty", 0),
                "rate": item.get("basic_rate", 0),
                "amount": item.get("amount", 0)
            }
            data.append(row)
    
    return data

def get_columns():
    return [
        {"fieldname": "posting_date", "label": "Posting Date", "fieldtype": "Date", "width": 130},
		{"fieldname": "stock_entry", "label": "Stock Entry", "fieldtype": "Link", "options": "Stock Entry", "width": 190},
        {"fieldname": "work_order", "label": "Work Order", "fieldtype": "Link", "options": "Work Order", "width": 120},
        {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Link", "options": "Item", "width": 170},
        {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 170},
        {"fieldname": "estimated_qty", "label": "Estimated Quantity", "fieldtype": "Float", "width": 120},
        {"fieldname": "estimated_amount", "label": "Estimated Cost", "fieldtype": "Currency", "width": 150},
        {"fieldname": "total_estimated", "label": "Total Estimated Cost", "fieldtype": "Currency", "width": 150},
        {"fieldname": "qty", "label": "Actual Quantity", "fieldtype": "Float", "width": 120},
        {"fieldname": "rate", "label": "Actual Cost", "fieldtype": "Currency", "width": 150},
        {"fieldname": "amount", "label": "Total Actual Cost", "fieldtype": "Currency", "width": 120},
    ]