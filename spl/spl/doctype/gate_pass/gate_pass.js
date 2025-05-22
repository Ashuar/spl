// Copyright (c) 2024, Ali Raza and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gate Pass", {
    refresh(frm) {
        if (frm.doc.docstatus == 0) {
            frm.add_custom_button(__('Purchase Order'), () => {
                const dialog = new frappe.ui.form.MultiSelectDialog({
                    doctype: "Purchase Order",
                    target: frm,
                    setters: {
                        status: null
                    },
                    add_filters_group: 1,
                    allow_child_item_selection: 1,
                    child_fieldname: "items",
                    child_columns: ["item_code", "item_name", "qty"],
                    get_query() {
                        return {
                            filters: [
                                ['docstatus', '!=', 2],
                                ['status', 'in', ['To Receive and Bill', 'To Bill', 'To Receive']]
                            ]
                        }
                    },
                    action(selections) {
                        let values = selections;
                        if (values.length === 0) {
                            frappe.msgprint(__("Please select Purchase Orders"));
                            return;
                        }
                        frm.set_value('gate_pass_detail', [])
                        selections.forEach(order_id => {
                            frappe.db.get_doc('Purchase Order', order_id).then(purchase_order => {
                                purchase_order.items.forEach(item => {
                                    frm.add_child('gate_pass_detail', {
                                        document_type: 'Purchase Order',
                                        document_name: order_id,
                                        item: item.item_code,
                                        accepted_qty: item.qty,
                                        ordered_qty: item.qty
                                    });
                                });
                                frm.refresh_field('gate_pass_detail');
                            });
                        });
                        dialog.dialog.hide()
                    }
                });
            }, __('Get Items From'));

            frm.add_custom_button(__('Delivery Note'), () => {
                const dialog = new frappe.ui.form.MultiSelectDialog({
                    doctype: "Delivery Note",
                    target: frm,
                    setters: {
                        status: null
                    },
                    add_filters_group: 1,
                    allow_child_item_selection: 1,
                    child_fieldname: "items",
                    child_columns: ["item_code", "item_name", "qty"],
                    get_query() {
                        return {
                            filters: [
                                ['docstatus', '!=', 2],
                                ['status', '=', 'To Bill']
                            ]
                        }
                    },
                    action(selections) {
                        let values = selections;
                        if (values.length === 0) {
                            frappe.msgprint(__("Please select Delivery Notes"));
                            return;
                        }
                        frm.set_value('gate_pass_detail', [])
                        selections.forEach(order_id => {
                            frappe.db.get_doc('Delivery Note', order_id).then(purchase_order => {
                                purchase_order.items.forEach(item => {
                                    frm.add_child('gate_pass_detail', {
                                        document_type: 'Delivery Note',
                                        document_name: order_id,
                                        item: item.item_code,
                                        accepted_qty: item.qty,
                                        ordered_qty: item.qty
                                    });
                                });
                                frm.refresh_field('gate_pass_detail');
                            });
                        });
                        dialog.dialog.hide()
                    }
                });
            }, __('Get Items From'));
        }

        if (frm.doc.docstatus === 1 && frm.doc.type === 'IGP') {
            frm.add_custom_button('Create Purchase Receipt', () => {

            }).addClass('primary')
        }

        frm.set_query('document_type', 'gate_pass_detail', () => {
            return {
                filters: {
                    name: ['IN', ['Purchase Order', 'Delivery Note']]
                }
            }
        });
    },
});

frappe.ui.form.on('Gate Pass Item', {
    document_type: (frm, cdt, cdn) => {
        const row = frappe.get_doc(cdt, cdn);
        if (!row) return;
        frm.fields_dict['gate_pass_detail'].grid.get_field('document_name').get_query = function (doc, cdt, cdn) {
            let filters = [];

            if (row.document_type === 'Purchase Order') {
                filters = [
                    ['docstatus', '!=', 2],
                    ['status', 'in', ['To Receive and Bill', 'To Bill', 'To Receive']]
                ];
            } else if (row.document_type === 'Delivery Note') {
                filters = [
                    ['docstatus', '!=', 2],
                    ['status', '=', 'To Bill']
                ];
            }

            return {
                filters
            };
        };
        frm.refresh_field('gate_pass_detail');
    }
});
