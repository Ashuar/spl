frappe.listview_settings['Cost Sheet'] = {
    add_fields: ["sample_code", "posting_date", "status"],
    get_indicator(doc) {
        switch (doc.status) {
            case "Cutting":
                return [__("Cutting"), "yellow", "status,=,Cutting"];
            case "Stitching":
                return [__("Stitching"), 'orange', "status=Stitching"]
            case "Lasting":
                return [__("Lasting"), 'blue', "status=Lasting"]
            default:
                return [__("Finished"), "green", "status,=,Finished"];
        }
    },
};