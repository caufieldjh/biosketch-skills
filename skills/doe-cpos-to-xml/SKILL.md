---
name: doe-cpos-to-xml
description: >
  Transform a DOE Current and Pending (Other) Support PDF into SciENcv-compatible XML.
  Use this skill whenever the user wants to convert a DOE C&P(O)S PDF to XML, mentions
  SciENcv XML upload, asks about converting current and pending support documents,
  or has a DOE CPOS PDF they need in XML format. Also trigger when the user mentions
  "current and pending" together with "XML", "SciENcv", or "DOE".
---

# DOE C&P(O)S PDF to SciENcv XML Converter

Convert a DOE Current and Pending (Other) Support PDF document into the XML format
accepted by the NIH SciENcv system for upload.

## When this skill applies

The user has a DOE C&P(O)S PDF (typically generated from SciENcv or filled out manually)
and needs an XML version for upload to SciENcv. The PDF follows the standard DOE
C&P(O)S form layout with sections for identification, proposals/active projects,
and in-kind contributions.

## Background

The SciENcv (Science Experts Network Curriculum Vitae) system accepts XML uploads
of Current and Pending (Other) Support documents. The XML format has a specific
structure defined by NIH/NLM. The official reference files are:

- Blank template: https://ftp.ncbi.nlm.nih.gov/pub/sciencv/cposXML/sample-blank.xml
- Populated sample: https://ftp.ncbi.nlm.nih.gov/pub/sciencv/cposXML/SampleXML.xml
- Instructions: https://support.nlm.nih.gov/kbArticle/?pn=KA-05499

If you need to verify the exact XML structure, fetch the populated sample URL above.
The reference file `xml-structure.md` in this skill has the complete schema documented
so you usually won't need to.

## Workflow

### Step 1: Find the PDF

Look in the current working directory for a PDF file. If there are multiple PDFs,
ask the user which one is the DOE C&P(O)S document. The filename often contains
"cpos" or similar, but not always.

### Step 2: Read all pages

DOE C&P(O)S documents can be long (10-20+ pages). Read the PDF in chunks
(pages 1-10, then 11-20, etc.) to capture every project entry. The last page
is typically the certification/addendum page, which you can note but don't need
to convert to XML.

### Step 3: Extract the data

From the PDF, extract these sections:

**Identification (page 1 header):**
- NAME (first name, last name; middle name if present)
- POSITION TITLE
- ORGANIZATION AND LOCATION (org name, city, state, country)

**Each project entry contains:**
- Proposal/Active Project Title
- Status of Support (Current or Pending)
- Proposal/Award Number
- Source of Support
- Primary Place of Performance
- Start Date (MM/YYYY)
- End Date (MM/YYYY)
- Total Anticipated Proposal/Project Amount
- Person Months table (Year + Person Months per row)
- Overall Objectives (paragraph text)
- Statement of Potential Overlap

**Distinguishing award vs. in-kind:**
- Entries under "Proposals and Active Projects" use `contributiontype` = `award`
- Entries under "In-Kind Contributions" use `contributiontype` = `inkind`
- In-kind entries have a description field instead of a project title

### Step 4: Build the XML

Use the structure documented in `references/xml-structure.md`. Key formatting rules:

**Dates:** Convert `MM/YYYY` from the PDF to `YYYY-MM-01` in XML.
  - Example: `10/2025` becomes `2025-10-01`

**Award amounts:** Plain integers, no dollar sign, no commas.
  - Example: `$4,000,000` becomes `4000000`

**Support type:** Lowercase `current` or `pending` (the PDF may say "Current" or "Pending").

**Contribution type:** `award` for proposals/active projects, `inkind` for in-kind contributions.

**Person months commitment:** Each year-value pair becomes a `<personmonth>` element
with the year as an attribute:
```xml
<commitment>
<personmonth year="2026">0.36</personmonth>
<personmonth year="2027">0.36</personmonth>
</commitment>
```

**In-kind description:** For award entries, use `<inkinddescription/>` (self-closing empty).
For in-kind entries, populate with the description text.

**Potential overlap:** Use the exact text from the PDF. If the PDF says "None", use `None`.
If there's additional context (e.g., "None -- Subaward for this award is currently under negotiation."),
preserve the full text.

**Overall objectives:** Preserve the full paragraph text from the PDF. Do not summarize or truncate.

### Step 5: Write the output

Save the XML file with the same base name as the input PDF but with `.xml` extension.
For example, `cpos-2359756.pdf` becomes `cpos-2359756.xml`.

Tell the user how many project entries were converted (broken down by current vs. pending)
and remind them to review the output for accuracy, especially award numbers and amounts.

## Common pitfalls

- **Missing pages:** Always read ALL pages of the PDF. Projects span multiple pages and
  it's easy to miss entries on later pages if you stop reading too early.
- **Split entries:** A single project entry often spans a page break. The project title
  may be on one page and the person-months table on the next. Make sure to associate
  all fields with the correct project.
- **Colon in award number:** Some award numbers in the PDF have a leading colon
  (e.g., `: DE-AC02-05CH11231`). Strip the colon.
- **End date for in-kind entries:** In-kind contributions may not have an end date.
  Omit the `<enddate>` element entirely if there is no end date (don't include an
  empty element).
- **The certification page:** The last page contains certification language and a
  signature. This is not converted to XML.
