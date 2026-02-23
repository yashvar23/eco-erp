# Fixtures Guide — ECO App

## 1) Fixture files and contents

- `role.json` — exported `Role` records used by ECO access model.
- `workflow_state.json` — exported `Workflow State` records for ECO lifecycle stages.
- `workflow_action.json` — exported `Workflow Action` records used in transitions.
- `workflow.json` — exported `Workflow` definitions (including transitions).
- `letter_head.json` — exported `Letter Head` branding fixture.
- `custom_field.json` — exported `Custom Field` records (currently initialized as empty array).
- `property_setter.json` — exported `Property Setter` records (currently initialized as empty array).

## 2) How to export fixtures

From the bench root, run:

```bash
bench --site erp.eco.localhost export-fixtures --app eco_app
```

This reads the `fixtures` list in `eco_app/eco_app/hooks.py` and writes JSON files into this folder.

## 3) How fixtures are imported on a fresh site

When the app is installed/migrated on a site (for example during `bench --site <site> migrate`), Frappe processes app fixtures and imports them into the site database.

In practice:

1. App is available on the site.
2. `bench migrate` runs patches and schema updates.
3. Fixture JSON files are auto-imported by framework fixture handling.

This ensures fresh environments get the same ECO roles, workflows, and related configuration from version-controlled JSON.
