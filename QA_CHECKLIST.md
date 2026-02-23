# ECO ERP Manual QA Checklist

## 1) Branding and Navigation
- [ ] Browser tab title shows ECO ERP naming correctly
- [ ] Browser favicon shows ECO brand icon
- [ ] Login page branding uses ECO logo and colors
- [ ] Navbar displays ECO branding and quick actions correctly
- [ ] Sidebar modules/menu labels are correct for ECO workflows

## 2) Core ECO DocTypes (All 6)
- [ ] Student Profile: create, edit, stage transitions, counselor assignment
- [ ] University Master: create, commission %, intake month validation
- [ ] Student Application: create with student+university+course links, stage/status updates
- [ ] Document Checklist: mandatory document rows, status transitions, attachment handling
- [ ] Visa Application: create from accepted application, decision handling
- [ ] Commission Record: expected/received states, amount and link integrity

## 3) Reports (All 3)
- [ ] Monthly Applications report loads and filters work
- [ ] Counselor Performance report shows expected aggregates
- [ ] Country-wise Applications report returns correct grouped data

## 4) Workspace KPIs
- [ ] ECO Workspace opens without errors
- [ ] KPI cards show expected metrics and refresh correctly
- [ ] KPI links route to correct list/report views

## 5) Email and Document Outputs
- [ ] Stage-change email triggers fire for Student Profile journey
- [ ] Visa decision notifications are sent on approve/reject
- [ ] PDF print/letterhead includes ECO branding and correct company details

## 6) Role-Based Access Validation

### ECO Manager
- [ ] Full read/write access across ECO DocTypes and reports
- [ ] Can approve/reject workflow actions (including visa)

### ECO Counselor
- [ ] Can create/edit Student Profile and Student Application
- [ ] Cannot perform restricted accounting actions

### ECO Accounts
- [ ] Can manage commission and invoicing linked flows
- [ ] Cannot perform visa-only workflow actions

### ECO Visa Officer
- [ ] Can access and process Visa Application records
- [ ] Cannot modify restricted finance records

### ECO Student
- [ ] Portal-only access is restricted to own records
- [ ] Cannot access backend desk modules and other student data
