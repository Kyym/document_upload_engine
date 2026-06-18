#!/bin/bash
cd /home/frappe/frappe-bench
source env/bin/activate
bench --site frontend execute frappe.utils.fixtures.sync_fixtures --args "['ocr_validator']"
echo "Exit code: $?"
