// Copyright (c) 2025, Ali Raza and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cost Sheet", {
    refresh: function (frm) {
        if (frm.doc.docstatus == 1) {
            const options = frappe.get_meta("Cost Sheet").fields.filter(item => item.fieldname === "status")[0].options.split("\n")
            options.forEach(option => {
                frm.add_custom_button(option, async function () {
                    await frappe.db.set_value("Cost Sheet", frm.doc.name, "status", option)
                    frm.reload_doc()
                }, __("Sample Status"))
            });
        }
    },
});
frappe.ui.form.on("Cost Sheet Item", {
    item_code: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row.item_code) {
            frappe.model.set_value(cdt, cdn, {
                item_name: "",
                uom: "",
                rate: 0,
                consumption: 0,
                total_cost: 0
            });
            return;
        }

        // Fetch item details and calculate cost
        frappe.call({
            method: "spl.spl.doctype.cost_sheet.cost_sheet.get_item_details",
            args: {
                item_code: row.item_code,
                price_list: frm.doc.price_list || "Standard Buying"
            },
            freeze: true,
            freeze_message: __("Fetching item details..."),
            callback: (r) => {
                if (!r.exc && r.message) {
                    // First update item details
                    frappe.model.set_value(cdt, cdn, {
                        item_name: r.message.item_name,
                        uom: r.message.uom,
                        rate: r.message.rate
                    });

                    // Then calculate total cost if consumption exists
                    if (row.consumption && row.consumption > 0) {
                        calculate_row_cost(frm, cdt, cdn);
                    }
                }
            }
        });
    },

    consumption: function (frm, cdt, cdn) {
        // Recalculate when consumption changes
        calculate_row_cost(frm, cdt, cdn);
    },
    qty: function (frm, cdt, cdn) {
        calculate_row_amount(frm, cdt, cdn)
    },

    rate: function (frm, cdt, cdn) {
        calculate_row_amount(frm, cdt, cdn)
    },
});

// Helper function to calculate cost for a row
function calculate_row_cost(frm, cdt, cdn) {
    const row = frappe.get_doc(cdt, cdn);

    if (!row.item_code || !row.consumption) return;

    frappe.call({
        method: "spl.spl.doctype.cost_sheet.cost_sheet.calculate_total_cost",
        args: {
            item_code: row.item_code,
            consumption: parseFloat(row.consumption) || 0
        },
        callback: (r) => {
            if (!r.exc && r.message !== undefined) {
                frappe.model.set_value(cdt, cdn, {
                    total_cost: flt(r.message)
                });
            }
        }
    });
}

function calculate_row_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn]
    console.log(row)
    if (row) {
        row.total_cost = parseFloat(row.rate) * parseFloat(row.qty)
        frappe.model.set_value(cdt, cdn, 'total_cost', row.total_cost);
    }
}
// Calculate Labor Cost
frappe.ui.form.on("Labor Cost", {
    rate: function (frm, cdt, cdn) {
        calculate_labor_cost(frm, cdt, cdn)
    }
});


function calculate_labor_cost(frm, cdt, cdn) {
    let row = locals[cdt][cdn]
    if (row) {
        row.total_cost = parseFloat(row.rate)
        frappe.model.set_value(cdt, cdn, 'total_cost', row.total_cost);
    }
}
//calculating tolling cost

frappe.ui.form.on("Tooling Cost", {
    rate: function (frm, cdt, cdn) {
        calculate_tooling_cost(frm, cdt, cdn)
    },

    no_of_sets: function (frm, cdt, cdn) {
        calculate_tooling_cost(frm, cdt, cdn)
    },
    total_pair: function (frm, cdt, cdn) {
        calculate_tooling_cost(frm, cdt, cdn)
    },
});


function calculate_tooling_cost(frm, cdt, cdn) {
    let row = locals[cdt][cdn]
    if (row) {
        row.cost = parseFloat(row.no_of_sets) * parseFloat(row.rate)
        frappe.model.set_value(cdt, cdn, 'cost', row.cost)
        row.total_cost = parseFloat(row.cost) / parseFloat(row.total_pair)
        frappe.model.set_value(cdt, cdn, 'total_cost', row.total_cost);
    }
}


