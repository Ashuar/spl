# Copyright (c) 2024, Ali Raza and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class GatePass(Document):
    def validate(self):
        # self.validate_type()
        self.validate_duplicates()
        # if self.type == "IGP":
        #     self.validate_igp_qty()
        if self.type == "OGP":
            self.validate_delivery_qty()

    def validate_type(self):
        if self.type == "IGP":
            for i in self.get("gate_pass_detail"):
                pass
                # if not i.document_type:
                #     frappe.throw(
                #         _("Document Type is required at row {0}".format(i.idx))
                #     )
                # if not i.document_name:
                #     frappe.throw(
                #         _("Document Type is required at row {0}".format(i.idx))
                #     )
                # if not i.document_type == "Purchase Order":
                #     frappe.throw(
                #         _(
                #             "For type IGP, purchase order must be in row {0}".format(
                #                 i.idx
                #             )
                #         )
                #     )
        elif self.type == "OGP":
            for i in self.get("gate_pass_detail"):
                if not i.document_type:
                    frappe.throw(
                        _("Document Type is required at row {0}".format(i.idx))
                    )
                if not i.document_name:
                    frappe.throw(
                        _("Document Type is required at row {0}".format(i.idx))
                    )
                if not i.document_type == "Delivery Note":
                    frappe.throw(
                        _(
                            "For type OGP, Delivery Note must be required in row {0}".format(
                                i.idx
                            )
                        )
                    )
        else:
            pass

    def validate_duplicates(self):
        unique_items = set()
        for row in self.get("gate_pass_detail"):
            item_key = (row.document_type, row.document_name, row.item)
            if item_key in unique_items:
                frappe.throw(_("Duplicate item found at row {0}".format(row.idx)))
            unique_items.add(item_key)

    def validate_igp_qty(self):
        remaining_qty_per_item = {}
        for row in self.get("gate_pass_detail"):
            document_type = row.document_type
            document_name = row.document_name
            item_code = row.item
            item_qty = row.accepted_qty
            ordered_qty = row.ordered_qty
            if item_code not in remaining_qty_per_item:
                remaining_qty_per_item[item_code] = ordered_qty
            previous_gate_pass_items = frappe.get_all(
                "Gate Pass Item",
                filters={
                    "document_type": document_type,
                    "document_name": document_name,
                    "item": item_code,
                    "docstatus": 1,
                },
                fields=["accepted_qty"],
            )
            for previous_item in previous_gate_pass_items:
                remaining_qty_per_item[item_code] -= previous_item.accepted_qty
            if item_qty > remaining_qty_per_item[item_code]:
                frappe.throw(
                    f"Quantity for item {frappe.bold(item_code)} in document {document_name} exceeds the remaining allowed quantity. "
                    f"Only {remaining_qty_per_item[item_code]} units are allowed."
                )
                row.accepted_qty = remaining_qty_per_item[item_code]
            remaining_qty_per_item[item_code] -= item_qty

    def validate_delivery_qty(self):
        remaining_qty_per_item = {}
        for row in self.get("gate_pass_detail"):
            document_type = row.document_type
            document_name = row.document_name
            item_code = row.item
            item_qty = row.accepted_qty
            ordered_qty = row.ordered_qty
            if item_code not in remaining_qty_per_item:
                remaining_qty_per_item[item_code] = ordered_qty
            previous_delivery_items = frappe.get_all(
                "Gate Pass Item",
                filters={
                    "document_type": document_type,
                    "document_name": document_name,
                    "item": item_code,
                    "docstatus": 1,
                },
                fields=["accepted_qty"],
            )
            for previous_item in previous_delivery_items:
                remaining_qty_per_item[item_code] -= previous_item.accepted_qty
            if item_qty > remaining_qty_per_item[item_code]:
                frappe.throw(
                    f"Quantity for item {frappe.bold(item_code)} in delivery note {document_name} exceeds the remaining allowed quantity. "
                    f"Only {remaining_qty_per_item[item_code]} units are allowed."
                )
                row.accepted_qty = remaining_qty_per_item[item_code]
            remaining_qty_per_item[item_code] -= item_qty
