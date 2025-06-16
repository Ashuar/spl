# Copyright (c) 2025, Ali Raza and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, flt, cint


class CostSheet(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from spl.spl.doctype.cost_sheet_item.cost_sheet_item import CostSheetItem
        from spl.spl.doctype.labor_cost.labor_cost import LaborCost
        from spl.spl.doctype.tooling_cost.tooling_cost import ToolingCost

        accessories_item: DF.Table[CostSheetItem]
        accessory_total: DF.Currency
        amended_from: DF.Link | None
        bottom_item: DF.Table[CostSheetItem]
        bottom_total: DF.Currency
        chemical_item: DF.Table[CostSheetItem]
        chemical_total: DF.Currency
        construction: DF.Data | None
        currency: DF.Link | None
        customer_article: DF.Data
        grand_total_cost: DF.Currency
        item: DF.Table[CostSheetItem]
        labor_cost: DF.Table[LaborCost]
        lining_item: DF.Table[CostSheetItem]
        lining_total: DF.Currency
        naming_series: DF.Literal[None]
        posting_time: DF.Time | None
        price: DF.Float
        sample_code: DF.Data
        sample_image: DF.AttachImage | None
        size_range: DF.Data
        status: DF.Literal["", "Cutting", "Stitching", "Lasting", "Finished"]
        tooling_cost: DF.Table[ToolingCost]
        total_labor_cost: DF.Currency
        total_material_cost: DF.ReadOnly | None
        total_tooling_cost: DF.Currency
        transaction_date: DF.Date
        upper_total: DF.Currency
    # end: auto-generated types
    def validate(self):
        self.validate_price()
        self.validate_tooling_cost()
        self.validate_labor_cost()
        self.validate_lining_total()
        self.validate_accessories_total()
        self.validate_bottom_total()
        self.validate_chemical_total()
        self.validate_material_total()
        self.validate_grand_total_cost()

    def validate_price(self):
        upper_total = 0
        for item in self.item:
            item.total_cost = flt(item.qty) * flt(item.rate)
            upper_total += item.total_cost
            
        self.upper_total = upper_total
    
    def validate_lining_total(self):
        lining_total = 0
        for item in self.lining_item:
            item.total_cost = flt(item.qty) * flt(item.rate)
            lining_total += item.total_cost
            
        self.lining_total = lining_total
    
    def validate_accessories_total(self):
        accessory_total = 0
        for item in self.accessories_item:
            item.total_cost = flt(item.qty) * flt(item.rate)
            accessory_total += item.total_cost
            
        self.accessory_total = accessory_total

    def validate_chemical_total(self):
        chemical_total = 0
        for item in self.chemical_item:
            item.total_cost = flt(item.qty) * flt(item.rate)
            chemical_total += item.total_cost
            
        self.chemical_total = chemical_total
    
    def validate_bottom_total(self):
        bottom_total = 0
        for item in self.bottom_item:
            item.total_cost = flt(item.qty) * flt(item.rate)
            bottom_total += item.total_cost
            
        self.bottom_total = bottom_total
    
    def validate_material_total(self):
        self.total_material_cost = flt(self.upper_total) + flt(self.lining_total) + flt(self.accessory_total) + flt(self.bottom_total) + flt(self.chemical_total)

    def validate_tooling_cost(self):
        total_cost = 0
        for item in self.tooling_cost:
            item.cost = flt(item.no_of_sets) * flt(item.rate)
            item.total_cost = flt(item.cost) / flt(item.total_pair)
            total_cost += item.total_cost
        
        self.total_tooling_cost = total_cost
    
    def validate_labor_cost(self):
        total_cost = 0
        for item in self.labor_cost:
            item.total_cost = flt(item.rate)
            total_cost += item.total_cost
        
        self.total_labor_cost= total_cost

    def validate_grand_total_cost(self):
        self.grand_total_cost = round(flt(self.total_material_cost) + flt(self.total_labor_cost) + flt(self.total_tooling_cost))


@frappe.whitelist()
def get_item_details(item_code, price_list="Standard Buying"):
    """
    Fetch item details
    Args:
        item_code (str): Item code to lookup
        price_list (str): Price list to use (default: "Standard Buying")
    Returns:
        dict: {item_name, uom, rate}
    """
    if not item_code:
        return {}
    
    # Get basic item details
    item = frappe.get_cached_value("Item", item_code, ["item_name", "stock_uom"], as_dict=True) or {}
    
    # Get price
    price = frappe.db.get_value(
        "Item Price",
        {
            "item_code": item_code,
            "price_list": price_list,
            "valid_from": ("<=", frappe.utils.nowdate())
        },
        "price_list_rate",
        order_by="valid_from desc"
    )
    
    return {
        "item_name": item.get("item_name") or item_code,
        "uom": item.get("stock_uom") or "",
        "rate": float(price) if price else 0
    }

@frappe.whitelist()
def calculate_total_cost(item_code, consumption):
    """Calculate total cost based on item rate and consumption"""
    # 1. Get the item details (including rate)
    item_details = get_item_details(item_code=item_code, price_list="Standard Buying")
    
    # 2. Extract the rate (with safety check)
    rate = item_details.get("rate", 0) if item_details else 0
    
    # 3. Calculate total cost
    total_cost = rate * (consumption or 0)  # Handle None/False consumption
    
    return total_cost
