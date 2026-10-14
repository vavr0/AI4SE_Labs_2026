# Software Requirements

**Automated review:** Needs attention
**Sources processed:** 20
**Feedback revisions:** 2/2

## Priority scale

- **High:** Essential functionality, safety, compliance, or explicitly high priority.
- **Medium:** Important supporting functionality.
- **Low:** Useful enhancement or explicitly optional functionality.

## Requirements

### REQ-001 — Material volume reporting

Report material volume for a specified library at current or historical points in time, counting items located there. Show separate counts for new acquisitions, items on the shelf or checked in, and items in circulation or checked out, plus totals. Support category breakdowns such as total items, holds, adult fiction, board books, fiction/non-fiction, and format; allow libraries to customize categories and filter by acquisition date, including configurable periods such as 30, 60, or 90 days.

**Priority:** High (Inferred)
**Priority reason:** A source calls this a key requirement and ties it to board reporting and collection management.
**Sources:** `conversations/conv_pines014_material_volume.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`

### REQ-002 — Branch capacity overview

Provide a system-wide interface showing the capacity of all branches, with a high-level summary and drill-down to individual branches. Support aggregation across branches, sorting and filtering by region, library type, and current load, trend information about growth or decline, and CSV export. Account for an overview of approximately 286 locations; grouping by system or region and filtering are suggested approaches for managing a crowded display. Color-coded status indicators are optional: green for under capacity, yellow for getting full, and red for at or over capacity.

**Priority:** Medium (Inferred)
**Priority reason:** The overview supports planning and resource allocation; color-coding is expressly optional.
**Sources:** `conversations/conv_pines015_capacity_interface.eml`, `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### REQ-003 — Capacity metric definition

Establish what defines branch capacity before building the capacity interface. The sources raise item count versus shelf space, physical item count versus a configured limit, and circulation volume versus processing capacity without selecting one.

**Priority:** Medium (Inferred)
**Priority reason:** A source says the capacity measure must be established before the interface is built.
**Sources:** `conversations/conv_pines015_capacity_interface.eml`

### REQ-004 — Shelf-space utilization reporting

For each genre and format, compare the percentage of total circulations, the percentage of the collection, and the percentage of total shelf space. Make results available per library and system, allow library results to be viewed relative to the system average, and support date-range filtering, such as comparing Q1 and Q2. A side-by-side comparison of libraries is optional.

**Priority:** Medium (Inferred)
**Priority reason:** The report supports collection management and planning; side-by-side comparison is expressly optional.
**Sources:** `conversations/conv_pines016_shelf_space.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### REQ-005 — Shelf-space estimation

Support estimating shelf space by genre and format because it is not directly tracked in the database. Item dimensions and item count as a proxy are proposed alternatives; neither method is selected.

**Priority:** Medium (Inferred)
**Priority reason:** An estimate is needed for the requested shelf-space percentage, but the sources do not choose a method.
**Sources:** `conversations/conv_pines016_shelf_space.eml`

### REQ-006 — Batch item transfers

Provide a utility for transferring batches of items among branches and other locations, including mobile libraries, outreach programs, temporary event locations, and just-in-time warehouses. Let users query candidate items, save and share queries for reuse, manually select items from results, update selected item locations, and generate pull lists. Support changing location fields and generating pull lists, and retain original locations when transfers may later be reverted.

**Priority:** Medium (Inferred)
**Priority reason:** The utility supports recurring collection balancing and temporary transfers; the sources do not set a formal priority level.
**Sources:** `conversations/conv_pines018_item_transfer.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`, `survey_results_2009.txt`

### REQ-007 — Transfer review and permissions

Before applying a transfer, show a preview including item count, source, and destination, and require confirmation. Restrict transfer capability to authorized roles such as managers, administrators, or transfer coordinators. Provide an undo function for erroneous transfers.

**Priority:** High (Inferred)
**Priority reason:** Confirmation and role restrictions reduce the risk of unauthorized or mistaken batch changes.
**Sources:** `conversations/conv_pines018_item_transfer.eml`

### REQ-008 — Automatic transfer reversion

Support returning transferred items to their original locations automatically after a configured date or duration, or when configured item events or status criteria occur. Examples include an item becoming sold or returned, or being checked out at the destination. Use a scheduled task or equivalent background process where needed. Temporary event and program transfers may be reverted after the event or program.

**Priority:** Medium (Inferred)
**Priority reason:** Automatic returns support temporary transfers; time- and event-based reversion are requested capabilities.
**Sources:** `conversations/conv_pines018_item_transfer.eml`, `interview_cataloging_2009-05-08.txt`, `survey_results_2009.txt`

### REQ-009 — Transfer records and notifications

Maintain an auditable transfer log and item transfer history, including counts of transfers during a specified period. Generate printable pull lists and transit labels or barcodes, and provide alerts when transfers are delayed or encounter issues.

**Priority:** Medium (Inferred)
**Priority reason:** These features support transfer coordination, accountability, and troubleshooting.
**Sources:** `conversations/conv_pines018_item_transfer.eml`

### REQ-010 — Safe and scalable transfer processing

Apply batch location updates transaction-safely and process large collections efficiently, including the stated scale of 9.6 million items. Use smaller processing batches where needed to avoid locking the database.

**Priority:** High (Inferred)
**Priority reason:** Consistent updates and avoiding database locks are necessary to prevent transfer errors and operational disruption.
**Sources:** `conversations/conv_pines018_item_transfer.eml`

### REQ-011 — Missing and damaged item reports

Provide missing- and damaged-item reports by branch for inventory auditing, accountability, and collection management. Reports should be able to include condition notes, such as water damage or vandalism, and may support configurable date ranges for trend analysis.

**Priority:** Medium (Inferred)
**Priority reason:** The reports support audits and collection decisions; date filtering is described as an additional capability.
**Sources:** `conversations/conv_pines019_020_missing_intransit.eml`, `interview_cataloging_2009-05-08.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### REQ-012 — Overdue in-transit reports

List items in transit beyond a configurable number of days, with seven days suggested as a default. The technical description identifies items with a null arrival date and a departure date older than the configured threshold. Provide results by branch and system, combine transit-to and transit-from items in one report, and allow sorting by due date so the oldest items can be addressed first.

**Priority:** High (Inferred)
**Priority reason:** The report is specified for delivery coordination, with defined thresholds, scope, and merged transit directions.
**Sources:** `conversations/conv_pines019_020_missing_intransit.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### REQ-013 — Purge candidate identification

Provide utilities and reports to identify item records for purging using customizable status-based, time-based, and activity-based criteria. Examples include missing, discard/weed, or damaged status; time spent in a status; and time since last circulation. Allow criteria to be combined, including conjunctive conditions such as missing for more than six months and not circulated for two years. Candidate reports must be read-only and must not delete records directly. Support weeding reports, which are identified as frequently used.

**Priority:** Medium (Inferred)
**Priority reason:** The capability supports a frequently used weeding and cleanup workflow while separating candidate identification from deletion.
**Sources:** `conversations/conv_pines021_item_purging.eml`, `interview_cataloging_2009-05-08.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### REQ-014 — Batch item status conversion

Provide a report or workflow to assist with changing item statuses in batches, such as converting items from missing to discard/weed.

**Priority:** Medium (Inferred)
**Priority reason:** Batch conversion supports the described weeding workflow and reduces manual work.
**Sources:** `conversations/conv_pines021_item_purging.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`

### REQ-015 — Last-copy reporting

Identify records that are the only copy within a selected scope, supporting both a library or branch view and a whole-system or consortium view. The report should help catalogers identify last copies before deletion or other modification and update corresponding WorldCat entries. Where available, report deleted items that were the last copy in a facility or system.

**Priority:** High (Inferred)
**Priority reason:** A source calls the report critical and describes the risk of deleting a consortium's only copy.
**Sources:** `conversations/conv_pines021_item_purging.eml`, `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `interview_cataloging_2009-05-08.txt`

### REQ-016 — Record cleanup and deletion safeguards

Provide an efficient cleanup method for deleting volume entries together with associated copy entries, and for deleting records with no attached items. Require a separate confirmation before actual deletions, including to protect against accidental deletion of an entire collection. Purge scheduling is optional.

**Priority:** High (Inferred)
**Priority reason:** Deletion confirmation is expressly a safety measure; scheduling is explicitly only a possible capability.
**Sources:** `conversations/conv_pines021_item_purging.eml`, `interview_cataloging_2009-05-08.txt`

### REQ-017 — Deletion audit trail

Persist deletion events in an audit record and track deletion counts, including item, patron, bibliographic, and other record types. Capture record type, record ID, deletion timestamp, deleting user, and that user's location or branch. The audit may also capture deletion context, such as the record's status before deletion, as an optional field. A database trigger is identified as an implementation method in one source.

**Priority:** High (Inferred)
**Priority reason:** The sources identify deletion tracking as necessary for accountability, troubleshooting, and audit evidence.
**Sources:** `conversations/conv_pines021_item_purging.eml`, `conversations/conv_pines022_deletions.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`, `survey_results_2009.txt`

### REQ-018 — Deletion activity reporting

Provide an interface for reviewing deletion activity from audit records. Support reporting by location and system, date range, user, and record type; show totals for periods such as month, quarter, or year; break results down by record type and location; and identify or rank users with high deletion counts. Tracking denied deletion attempts is helpful but not mandatory.

**Priority:** Medium (Inferred)
**Priority reason:** Reporting supports accountability and investigation; denied-attempt tracking is explicitly described as helpful rather than mandatory.
**Sources:** `conversations/conv_pines022_deletions.eml`

### REQ-019 — Patron characteristic reporting

Support filtering and grouping or aggregation by patron age range, ZIP or postal code, county of residence, home branch, patron type, and preferred language. Allow multiple patron-characteristic filters together and support both AND and OR logic. Age brackets must be configurable per report and calculated from birth date at query time. Include null values for missing optional demographic fields rather than silently excluding those records.

**Priority:** Medium (Inferred)
**Priority reason:** The sources identify these fields and behaviors as important for program planning, without assigning a formal priority level.
**Sources:** `conversations/conv_pines023_patron_characteristics.eml`, `early_draft_srs_galecia.txt`

### REQ-020 — Patron circulation-history filters

Allow reporting queries to filter patrons by circulation history, such as no checkouts during a specified preceding period, including in combination with demographic filters.

**Priority:** Medium (Inferred)
**Priority reason:** The source requests this as a combined query capability.
**Sources:** `conversations/conv_pines023_patron_characteristics.eml`

### REQ-021 — Inactive patron reporting

Generate reports of patrons with no circulation or electronic activity during a configurable number of preceding days. Electronic activity may include OPAC or patron-account logins, online hold placements, online renewals, and use of integrated digital collections or resources when that activity is logged or integrated. Allow reporting or grouping by system, home library, county, and other organizational levels as needed. Include current mailing addresses for outreach; separately track inactive patrons with outstanding fines; allow exclusion of specified categories such as do-not-disturb, VIP, staff, or communication-opt-out patrons; and support CSV export. This includes reporting patrons with inactive status.

**Priority:** Medium (Inferred)
**Priority reason:** The report supports database cleanup and outreach; the inactivity period is configurable rather than fixed.
**Sources:** `conversations/conv_pines024_inactive_patrons.eml`, `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`

### REQ-022 — Large patron report processing

Run inactive-patron reports in the background and cache results to address performance concerns for a population of approximately 3.5 million records.

**Priority:** Medium (Inferred)
**Priority reason:** Background processing and caching are identified as performance measures for the stated population scale.
**Sources:** `conversations/conv_pines024_inactive_patrons.eml`

### REQ-023 — Consortium-scale operation

Support operation at consortium scale, including the stated 286 locations, 17 million annual circulations, and purchasing and processing of more than 900,000 items annually. Searches and reports should preferably run during open hours without disrupting other system functions.

**Priority:** High (Explicit)
**Priority reason:** The early draft explicitly marks the consortium operating environment High Priority.
**Sources:** `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### REQ-024 — Supported server environments

Operate on Linux or Solaris server environments. The technical interview further identifies Red Hat Enterprise Linux and Solaris 10 on SPARC hardware as environments that the reporting system must support.

**Priority:** High (Explicit)
**Priority reason:** The early draft explicitly marks the server environment High Priority.
**Sources:** `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### REQ-025 — Client access and browser compatibility

Make Management Processes accessible through a web browser or a Windows-compatible client. If browser-based, support Microsoft Internet Explorer 6.0 and later and Mozilla Firefox 2.0 and later. The sources present browser and Windows-client access as alternatives.

**Priority:** High (Explicit)
**Priority reason:** The early draft explicitly marks access through a browser or Windows-compatible client High Priority.
**Sources:** `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### REQ-026 — Accessibility and standards-compliant HTML

Provide accessibility for screen-reading software, screen magnification, and other assistive technologies, including the named examples JAWS, NVDA, and ZoomText. Section 508 compliance is stated as mandatory. Web components, reports, and help output must be properly structured and standards-compliant HTML, including the cited semantic structure, alt tags, and ARIA labels.

**Priority:** High (Explicit)
**Priority reason:** The early draft marks assistive-technology accessibility and standards-compliant HTML High Priority; a later source calls Section 508 compliance mandatory.
**Sources:** `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### REQ-027 — Relational database support

Use and support a fully relational database backend, including complex joins. Technical sources identify PostgreSQL as the existing PINES environment and favor keeping reporting data in the main relational database rather than requiring a denormalized reporting schema.

**Priority:** High (Explicit)
**Priority reason:** The early draft explicitly marks the relational database constraint High Priority.
**Sources:** `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### REQ-028 — Reporting architecture and production impact

Allow searches and reports to run during open hours without disrupting circulation, the OPAC, or other system functions. Background processing, queuing, read-only replicas, and a separate reporting database are proposed approaches. Other technical notes oppose a separately synchronized or denormalized reporting warehouse, so the non-disruptive behavior is clear but the architecture is unresolved. Long-running reports should be processed in the background rather than blocking normal interface operation.

**Priority:** High (Explicit)
**Priority reason:** The early draft marks the relevant operating environment High Priority, and multiple sources identify production and OPAC performance as a major concern.
**Sources:** `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`

### REQ-029 — Development, training, and production environments

Provide separate development and training environments apart from production. Training must permit experimentation without risking production data, and development must permit testing reports without affecting production.

**Priority:** Medium (Explicit)
**Priority reason:** The early draft explicitly marks development and training environments Medium Priority.
**Sources:** `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### REQ-030 — Configuration migration

Support migration of configurations between development, training, and production through export and import. Configurations include report templates, permission settings, and saved queries.

**Priority:** Medium (Explicit)
**Priority reason:** Configuration migration is included with the early draft's Medium Priority environment requirement.
**Sources:** `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### REQ-031 — Role-based access control

Control rights and privileges through security groups and/or roles, with access for individuals, workgroups, and arbitrary staff groups. Support role assignment and easy administration so permission changes can follow role changes. The sources identify roles including Patron, Staff, Local Admin, Global Admin, and Library Manager, with the corresponding indirect OPAC, staff, local, and system access described in the source material.

**Priority:** High (Explicit)
**Priority reason:** The early draft explicitly marks access control through groups or roles High Priority.
**Sources:** `early_draft_srs_galecia.txt`, `email_staff_login.eml`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### REQ-032 — OPAC separation and integration

Management Processes must not constrain or negatively affect OPAC functionality or responsiveness. They may query OPAC-related patron data, including holds and circulation, without modifying that data. Patrons' management-reporting access is indirect through OPAC displays rather than direct access to the management reporting system.

**Priority:** High (Explicit)
**Priority reason:** The early draft explicitly marks the prohibition on constraining OPAC functionality High Priority.
**Sources:** `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### REQ-033 — Enterprise ILS and vendor integration

Operate as part of a centralized, multi-location enterprise Library Automation System and rely on its data structures and functionality, including Acquisitions and Cataloging. Interface with vendor websites through published APIs and/or automated standard-format files such as USMARC21 and EDIFACT. Vendor integration data may be available but must not be assumed to exist at every library. The management reporting system reads rather than manages acquisitions and cataloging data.

**Priority:** Medium (Inferred)
**Priority reason:** The sources establish system dependencies and integration requirements but do not assign a priority level.
**Sources:** `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### REQ-034 — Data specifications and process documentation

Provide complete data specifications for authority, bibliographic, order, item, hold/request, and other records used or maintained by Management Processes. Documentation should include data dictionaries with field names, data types, and relationships. Provide high-level descriptions of major processes, including bibliographic import and export, authority validation, and standard reports.

**Priority:** High (Explicit)
**Priority reason:** The early draft marks complete data specifications High Priority and process documentation Medium Priority; both are preserved in this combined requirement.
**Sources:** `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### REQ-035 — Online help

Provide online HTML help that is hierarchical and cross-linked, describes and illustrates system functions, and is searchable and easy to navigate. The help should be accessible with screen readers; context-sensitive help is identified as important.

**Priority:** High (Explicit)
**Priority reason:** The early draft explicitly marks online help High Priority.
**Sources:** `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### REQ-036 — Error reporting and query diagnostics

Provide high-level error reporting and feedback when operations such as report execution fail. Local and Global System Administrators should be able to receive low-level, query-specific diagnostics through the front end, including affected table, field, and error type.

**Priority:** Medium (Explicit)
**Priority reason:** The early draft explicitly marks error reporting and query feedback Medium Priority.
**Sources:** `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### REQ-037 — Optional streamlined staff login

Support optional streamlined individual staff login, such as an employee badge or card swipe, while retaining individual username-and-password login as a fallback. Either method must authenticate and identify the individual staff member and maintain identity for auditing; card-based login must not be required or bypass individual authentication.

**Priority:** Low (Inferred)
**Priority reason:** The source expressly says streamlined login is available but not required.
**Sources:** `early_draft_srs_galecia.txt`, `email_staff_login.eml`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### REQ-038 — Report templates and controlled modification

Allow administrators to create templates available to staff. Authorized users should be able to run a template as-is or modify permitted selections without compromising result accuracy or consistency. Administrators should control which filters and display fields can be changed; cloning should create a distinct variant rather than modifying the original. Support template management and reuse.

**Priority:** Medium (Inferred)
**Priority reason:** Templates support consistent reporting; the sources do not state a formal priority level.
**Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `survey_results_2009.txt`

### REQ-039 — Report permissions and sharing

Provide distinct, fine-grained permissions for report creation, cloning, running, and access to filters, fields, tables, and data sets. Administrators should be able to create shared folders that allow or restrict staff from running reports or performing ad hoc reporting on specified data. Permission changes should be manageable through roles, and authorized users may be allowed to add canned reports.

**Priority:** Medium (Inferred)
**Priority reason:** Sources and survey results identify permissions as important, but do not state a formal priority level.
**Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `survey_results_2009.txt`

### REQ-040 — Open query tool

Provide a user-friendly query interface for bibliographic, item, patron, transaction, financial, and other record types. Users should be able to select query fields, choose values from picklists, use regular expressions, and apply Boolean operators, subject to administrator-controlled access to tables and fields. Make relevant reportable fields available and support complex query construction and field filtering. Allow users to save and reuse query definitions, including for custom or local reporting.

**Priority:** Medium (Inferred)
**Priority reason:** The query tool and reusable queries are core reporting capabilities, but no formal priority level is supplied.
**Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `survey_results_2009.txt`

### REQ-041 — Board and executive reports

Provide predefined reports for library boards, executives, and external consumers, including basic statistics needed for the Georgia Annual Report and Application for State Aid. Activity statistics should cover checkouts, check-ins, holds placed, and holds filled, with cross-tabulation by terminal, branch, library system, hour, patron age range, patron type, and patron location.

**Priority:** Medium (Inferred)
**Priority reason:** These reports support board and executive reporting; sources do not assign a formal priority level.
**Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### REQ-042 — Privacy-preserving transaction archives

Archive transaction data for the period required by applicable law while protecting patron privacy and removing personally identifying information. Retain useful anonymized demographic statistics. The required retention period is described as State Law-dependent or X years, not as one fixed duration.

**Priority:** High (Inferred)
**Priority reason:** The sources connect privacy protection and retention to state-law and compliance obligations.
**Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `survey_results_2009.txt`

### REQ-043 — Periodic and specialized reports

Support periodic and operational reports including bibliographic records with holds; items not checked out for a configurable period; item-level holds; invalid item types; in-transit items with outstanding holds; long in-transit items; last copies; long call numbers; missing items; bibliographic records without item records; patrons with invalid home libraries; notices sent; transactions by date, time, workstation, or staff member; item use by fiscal-year or monthly period; and total circulation with checkouts, renewals, and noncataloged circulation distinguished. Also support the supplied catalog of circulation, item, bibliographic, patron, hold, in-house-use, transit, and bills reports.

**Priority:** Medium (Inferred)
**Priority reason:** The sources specify a broad report catalog but do not assign an overall formal priority level.
**Sources:** `early_draft_srs_galecia.txt`

### REQ-044 — Report criteria display

Display the query selections and criteria used to generate report results. Clearly show the report name and selected date range with the results.

**Priority:** Medium (Inferred)
**Priority reason:** Showing criteria supports interpreting and reproducing results; no explicit priority level is supplied.
**Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`

### REQ-045 — Report queue status and priority

Let staff see whether a report is queued, its queue position and the number of reports ahead, its submission time, and its status, including waiting, running, completed, or failed. Support prioritizing selected reports so they can move ahead of other queued work.

**Priority:** Medium (Inferred)
**Priority reason:** Queue visibility is identified as important and helps staff understand report processing.
**Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `survey_results_2009.txt`

### REQ-046 — Reporting interface types

Provide canned reports that run immediately or recur, on-demand reports with preset criteria and editable selection or display options, and open-template reporting that exposes attributes for filtering and display across circulation, items, patrons, bills, and bibliographic records.

**Priority:** Medium (Inferred)
**Priority reason:** The sources identify these as required reporting interfaces without specifying a formal priority level.
**Sources:** `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`

### REQ-047 — Report scheduling and cancellation

Support running reports ASAP and scheduling them hourly, daily, weekly, monthly, or yearly. Users should be able to edit recurring report selections and delivery addresses, select multiple reports to run concurrently and view them in one document, and cancel reports that are scheduled or currently running.

**Priority:** Medium (Inferred)
**Priority reason:** Scheduling, concurrent runs, and cancellation support recurring and managed reporting; no formal priority level is provided.
**Sources:** `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`

### REQ-048 — Report discovery and descriptions

Provide quick access that helps users find reports. Show pop-up descriptions or hover tooltips for report titles and templates, and allow selection of desired portions of available data.

**Priority:** Low (Inferred)
**Priority reason:** The sources describe these as usability enhancements rather than essential reporting behavior.
**Sources:** `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `survey_results_2009.txt`

### REQ-049 — Report delivery and output formats

Provide report output in Excel, HTML, and CSV formats. Allow report results to be delivered by email as well as downloaded through the web interface, with an address book of frequently used recipients. Support configuring comparative columns for current and prior periods, percentage differences, and pivot-table output.

**Priority:** Medium (Inferred)
**Priority reason:** Multiple output and delivery options support reporting use cases; no formal priority level is specified.
**Sources:** `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`

### REQ-050 — Report output integrity

Test and demonstrate report output. Include null and blank fields rather than silently excluding them. Exported data, particularly Excel output, should not contain excessive duplicate rows.

**Priority:** Medium (Inferred)
**Priority reason:** Reliable output is necessary for accurate reporting and use of exported data.
**Sources:** `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`

### REQ-051 — Real-time and historical reporting

Support real-time reports against current data and historical reports that retrieve values as of a specified past date or date range, including cases where a location has since changed and historical bills snapshots. A reporting warehouse is one proposed approach in some sources, but other sources say it is not mandatory and caution against a separately synchronized or denormalized warehouse.

**Priority:** Medium (Inferred)
**Priority reason:** Both current and historical reporting are requested; the historical-data implementation is not settled.
**Sources:** `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`

### REQ-052 — Batch report filtering and MARC fields

Allow users to upload text files, such as barcodes or TCNs, as report filters. Allow reports to retrieve specified MARC fields and present them on a single row, including when fields are stored across multiple rows.

**Priority:** Medium (Inferred)
**Priority reason:** These capabilities address specified reporting and filtering needs; no formal priority level is supplied.
**Sources:** `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `survey_results_2009.txt`

### REQ-053 — Specialized item reports

Provide item-level reporting for edited-item counts; items grouped or filtered by fines-stopped reason; overdue items beyond a configurable number of days with patron contact information; items matching a specified total-use count; items created within a date range; claims-returned items or transactions; weeding results including last-circulation date; a separate last-circulation-date field; collection age and value by call number; a separate item edit date that does not change with circulation; and distinct check-in and renewal timestamps.

**Priority:** Medium (Inferred)
**Priority reason:** These are specified report capabilities, but their sources do not assign a common formal priority level.
**Sources:** `evergreen_reference_2009.txt`, `interview_cataloging_2009-05-08.txt`, `survey_results_2009.txt`

### REQ-054 — Specialized bibliographic and patron reports

Provide reports for edited bibliographic record counts, records added by user and library, and records missing specified MARC fields. Support patron counts by age demographic, county, city, and ZIP or postal code; voter survey responses; and staff account last-password-change dates. Allow filtering by survey name, resolving the name to its ID internally. Patron contact reporting may use available fields including name, address, email, city, state, and ZIP or postal code.

**Priority:** Medium (Inferred)
**Priority reason:** The sources specify these reporting capabilities without assigning a formal priority level.
**Sources:** `evergreen_reference_2009.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### REQ-055 — Specialized hold and debt reports

Provide reports or alerts for holds that should generate purchase alerts, unfilled holds, stale holds, and detailed aged debt.

**Priority:** Medium (Inferred)
**Priority reason:** The sources identify these as reporting gaps without assigning a formal priority level.
**Sources:** `evergreen_reference_2009.txt`

### REQ-056 — Reportable data coverage

Support reporting across bibliographic records, items, patrons, circulation actions, holds, money records, and staff accounts and permissions, including their documented relationships. Make relevant report fields available for those record types.

**Priority:** Medium (Inferred)
**Priority reason:** Broad record coverage supports the requested reporting functionality.
**Sources:** `evergreen_reference_2009.txt`

### REQ-057 — Uncataloged material inventory and use

Track shipments of uncataloged materials, such as paperback books and children's board books, as inventory without requiring individual fully cataloged records. Support quick distribution with minimal branch labor, identify how the material is used, and count its transactions in circulation statistics and reports.

**Priority:** Medium (Inferred)
**Priority reason:** The sources identify this as an operational inventory and reporting need.
**Sources:** `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`

### REQ-058 — Transaction history retention

Maintain transaction history for a configurable number of days, while retaining monthly and annual aggregate information indefinitely.

**Priority:** Medium (Inferred)
**Priority reason:** The source specifies configurable detailed-history retention and indefinite aggregate retention but gives no formal priority level.
**Sources:** `early_draft_srs_galecia.txt`, `survey_results_2009.txt`

### REQ-059 — Transaction grouping and reporting

Group transactions by hour, terminal, branch, and system and report transaction types including check-ins, checkouts, fines collected, patron registrations, and other types. Allow querying all transactions or a selected type. Report holds placed, holds filled, and checkouts by patron, library, selected group of libraries, system, or county, including per-patron counts and hold subtotals by status such as active, frozen, and frozen-until.

**Priority:** Medium (Inferred)
**Priority reason:** The sources specify detailed operational reporting dimensions and scopes without a formal priority level.
**Sources:** `early_draft_srs_galecia.txt`, `survey_results_2009.txt`

### REQ-060 — Check-in, checkout, renewal, and hold statistics

Count check-ins individually and cumulatively by method, including book drop, terminal, staff or user, and self-service. Count checkouts and renewals individually and cumulatively by staff, self-checkout, staff renewal, self-checkout renewal, online renewal, and OPAC renewal. Count holds and identify whether they were placed at a staff desk, public computer, or remotely.

**Priority:** Medium (Inferred)
**Priority reason:** These are explicit statistical reporting needs, but no formal priority level is supplied.
**Sources:** `early_draft_srs_galecia.txt`, `survey_results_2009.txt`

### REQ-061 — Item value reporting

Report item value using item-record data, including purchase price where specified. Allow reports for the entire collection or a selected portion, with filtering and aggregation examples such as long-overdue items, children's DVDs, or the complete collection.

**Priority:** Medium (Inferred)
**Priority reason:** The sources specify this financial and collection-management report without assigning a formal priority level.
**Sources:** `early_draft_srs_galecia.txt`, `email_financial_reports.eml`

### REQ-062 — Financial record relationships and updates

Associate fines, charges, waivers, payments, and ecommerce transactions with patron and item records and allow financial reporting to join those data. Make financial information easy to update and reflect a front-desk payment immediately.

**Priority:** Medium (Inferred)
**Priority reason:** These are supporting requirements for accurate financial reporting and reconciliation.
**Sources:** `early_draft_srs_galecia.txt`, `email_financial_reports.eml`

### REQ-063 — Financial reports and queries

Report patron account balances by patron, home library, and system; fines and charges by selectable time period and charge type; fines waived by time period and branch; and payments by time period, collection location, payment method or channel, and payment type. Allow staff to query accounts above a configurable balance threshold. Support financial reporting needs understood at the library director level.

**Priority:** Medium (Inferred)
**Priority reason:** These are specified director- and finance-level reporting needs without a formal priority level.
**Sources:** `early_draft_srs_galecia.txt`, `email_financial_reports.eml`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### REQ-064 — Payment audit ledger

Maintain a ledger of patron payments that identifies the specific charge or charges to which each payment was applied, so every payment can be traced to its charges for reconciliation.

**Priority:** High (Inferred)
**Priority reason:** A source calls the audit trail critical and says it is needed for account reconciliation.
**Sources:** `early_draft_srs_galecia.txt`, `email_financial_reports.eml`

### REQ-065 — Accounting and retention compliance

Ensure reports and data archiving comply with standard accounting practices and applicable state, county, and municipal auditing requirements. Enforce retention policies that follow state and local requirements; one source states some data must be retained for seven years, while the general retention obligation remains jurisdiction-dependent.

**Priority:** High (Inferred)
**Priority reason:** The source ties this requirement to applicable audit and retention obligations.
**Sources:** `early_draft_srs_galecia.txt`, `email_financial_reports.eml`

### REQ-066 — Expanded report catalog

Expand reporting beyond the existing Evergreen 1.4.0.4 capabilities to cover identified gaps, including circulation by modifier, Dewey classification, MARC fields, circulation location and patron county, and age demographic. Support the specified circulation, item, bibliographic, patron, hold, bills, transit, and in-house-use report categories, including individual report types captured in related specialized-report requirements.

**Priority:** Medium (Inferred)
**Priority reason:** The reference document identifies these as reporting gaps without assigning a formal priority level.
**Sources:** `evergreen_reference_2009.txt`

### REQ-067 — Custom and local reports

Support custom or local reports, including collection development, program attendance tracking, and staff productivity reporting such as time spent per transaction.

**Priority:** Medium (Inferred)
**Priority reason:** Survey respondents report using such reports, but no formal priority level is stated.
**Sources:** `survey_results_2009.txt`

### REQ-068 — Demographic and behavior analysis

Provide anonymized demographic statistics, including transactions by geographic region and age range, and support analysis of patron behavior and material use. Examples include average return speed, likelihood of renewal, renewal rates, and the percentage of branch checkouts that are renewals. Demographic results must not expose personally identifying information.

**Priority:** Medium (Inferred)
**Priority reason:** These analyses support program planning and collection-use analysis; no formal priority level is supplied.
**Sources:** `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `survey_results_2009.txt`

### REQ-069 — Management reporting scope and administration

Focus Management Processes on management-related planning, evaluation, oversight, collection and patron-use analysis, branch capacity and collection distribution, demographics, staff productivity and workflow, and financial transaction tracking and verification. Support local configuration and consortium-level administration and statistical reporting. Staff are identified as primary report content creators; patrons may encounter reports indirectly through library displays, while direct patron-facing interaction is primarily through the OPAC.

**Priority:** Medium (Inferred)
**Priority reason:** The sources define the intended scope and administrative users but do not assign a formal priority level.
**Sources:** `meeting_minutes/meeting_2009-03-15_minutes.txt`

### REQ-070 — Requirements and development approach

Focus initial requirements work on functional requirements, with detailed interface and data-structure decisions to be developed through iterative prototyping. Development is expected to be collaborative, with multiple opportunities for end-user review. Requirements documentation should be readable to non-technical audiences while remaining sufficiently specific for project managers and developers.

**Priority:** Medium (Inferred)
**Priority reason:** These are documented planning and documentation expectations; no formal priority level is provided.
**Sources:** `meeting_minutes/meeting_2009-03-15_minutes.txt`

### REQ-071 — Reports working-group testing

The Reports Working Group is intended to serve as the Reports testing group through which new Reports development is filtered. The group is also tasked with documenting desired functionality, identifying Executive Reports Interface needs, and determining templates for PINES libraries.

**Priority:** Medium (Inferred)
**Priority reason:** The sources record the group's agreed mission and testing role.
**Sources:** `meeting_minutes/meeting_2009-03-15_minutes.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### REQ-072 — Cross-branch comparison reports

Provide reports that compare information across library branches.

**Priority:** Medium (Inferred)
**Priority reason:** Interview findings identify cross-branch comparison as a reporting need.
**Sources:** `meeting_minutes/meeting_2009-07-20_minutes.txt`

### REQ-073 — Data-quality reports

Provide data-quality reports for invalid item types, long call numbers, and bibliographic records without item records.

**Priority:** Medium (Inferred)
**Priority reason:** The sources identify these reports as useful for maintaining data integrity.
**Sources:** `interview_cataloging_2009-05-08.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### REQ-074 — Editable canned report options

Allow users to edit the display options of canned reports.

**Priority:** Medium (Inferred)
**Priority reason:** Provisional priority: unmapped candidate CAND-0246 retained to prevent omission; review required.
**Sources:** `evergreen_reference_2009.txt`

## Blacklist

No requirements were discarded.

## Input documents

- `conversations/conv_pines014_material_volume.eml`
- `conversations/conv_pines015_capacity_interface.eml`
- `conversations/conv_pines016_shelf_space.eml`
- `conversations/conv_pines018_item_transfer.eml`
- `conversations/conv_pines019_020_missing_intransit.eml`
- `conversations/conv_pines021_item_purging.eml`
- `conversations/conv_pines022_deletions.eml`
- `conversations/conv_pines023_patron_characteristics.eml`
- `conversations/conv_pines024_inactive_patrons.eml`
- `early_draft_srs_galecia.txt`
- `email_financial_reports.eml`
- `email_report_features.eml`
- `email_staff_login.eml`
- `evergreen_reference_2009.txt`
- `interview_cataloging_2009-05-08.txt`
- `interview_sysadmin_2009-05-10.txt`
- `meeting_minutes/meeting_2009-03-15_minutes.txt`
- `meeting_minutes/meeting_2009-07-20_minutes.txt`
- `meeting_tech_subcommittee_2009-06-30.txt`
- `survey_results_2009.txt`
