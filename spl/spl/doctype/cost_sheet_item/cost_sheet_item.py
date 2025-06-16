# Copyright (c) 2025, Ali Raza and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CostSheetItem(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        item_code: DF.Link
        item_group: DF.ReadOnly | None
        item_name: DF.ReadOnly | None
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        qty: DF.Float
        rate: DF.Currency
        total_cost: DF.Currency
        uom: DF.ReadOnly | None
    # end: auto-generated types
    pass

