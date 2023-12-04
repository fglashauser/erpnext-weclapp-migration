// Copyright (c) 2023, PC-Giga (Florian Glashauser) and contributors
// For license information, please see license.txt

frappe.ui.form.on("Weclapp Migration", {
	refresh(frm) {
        frm.add_custom_button(__("Cache all WeClapp Data"), function() {
            frm.call('cache_weclapp_data');
            frappe.msgprint(__("Caching all WeClapp Data. This may take a while. Please watch the logs for progress.") +
                __(' <a href="/app/weclapp-migration-log">Click here</a> to view the Weclapp Migration Log'));
        });
        frm.add_custom_button(__("Migrate selected Data"), function() {
            //frm.save();
            frm.call('migrate_weclapp_data');
            frappe.msgprint(__("Migrates selected WeClapp Data (should be cached before). This may take a while. Please watch the logs for progress.") +
                __(' <a href="/app/weclapp-migration-log">Click here</a> to view the Weclapp Migration Log'));
        });
        frm.add_custom_button(__("Clear migrated Data"), function() {
            //frm.save();
            frm.call('clear_migrated_data');
            frappe.msgprint(__("Clears selected migrated WeClapp Data. This may take a while. Please watch the logs for progress.") +
                __(' <a href="/app/weclapp-migration-log">Click here</a> to view the Weclapp Migration Log'));
        });
	},
});