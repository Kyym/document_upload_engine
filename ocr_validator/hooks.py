app_name = "ocr_validator"
app_title = "OCR Validator"
app_publisher = "CCI Global"
app_description = "CCI Global OCR Document Validation Framework"
app_email = "kevin.mwaura@ccikenya.co.ke"
app_license = "mit"

# Fixture data – loaded via `bench import-fixtures`
fixtures = ["OCR Compare"]

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "ocr_validator",
# 		"logo": "/assets/ocr_validator/logo.png",
# 		"title": "OCR Validator",
# 		"route": "/ocr_validator",
# 		"has_permission": "ocr_validator.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ocr_validator/css/ocr_validator.css"
# app_include_js = "/assets/ocr_validator/js/ocr_validator.js"

# include js, css files in header of web template
# web_include_css = "/assets/ocr_validator/css/ocr_validator.css"
# web_include_js = "/assets/ocr_validator/js/ocr_validator.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ocr_validator/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "ocr_validator/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "ocr_validator.utils.jinja_methods",
# 	"filters": "ocr_validator.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "ocr_validator.install.before_install"
# after_install = "ocr_validator.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "ocr_validator.uninstall.before_uninstall"
# after_uninstall = "ocr_validator.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "ocr_validator.utils.before_app_install"
# after_app_install = "ocr_validator.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "ocr_validator.utils.before_app_uninstall"
# after_app_uninstall = "ocr_validator.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "ocr_validator.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ocr_validator.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"ocr_validator.tasks.all"
# 	],
# 	"daily": [
# 		"ocr_validator.tasks.daily"
# 	],
# 	"hourly": [
# 		"ocr_validator.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ocr_validator.tasks.weekly"
# 	],
# 	"monthly": [
# 		"ocr_validator.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "ocr_validator.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "ocr_validator.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ocr_validator.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ocr_validator.task.get_dashboard_data"
# }

# App screen shortcut (Frappe v15+)
add_to_apps_screen = [
	{
		"name": "ocr_validator",
		"logo": "/assets/ocr_validator/images/logo.png",
		"title": "OCR Validator",
		"route": "/ocr-validator",
	}
]

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["ocr_validator.utils.before_request"]
# after_request = ["ocr_validator.utils.after_request"]

# Job Events
# ----------
# before_job = ["ocr_validator.utils.before_job"]
# after_job = ["ocr_validator.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"ocr_validator.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

# Website Routes
website_route_rules = [{"from_route": "/ocr-test", "to_route": "ocr_test"}]
