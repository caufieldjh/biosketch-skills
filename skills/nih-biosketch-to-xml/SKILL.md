---
name: nih-biosketch-to-xml
description: >
  Transform an NIH Biographical Sketch PDF into SciENcv-compatible XML (sciencv.1.3 schema).
  Use this skill whenever the user wants to convert an NIH biosketch PDF to XML, mentions
  SciENcv biosketch XML with NIH, asks about converting an NIH biographical sketch to XML,
  or has an NIH biosketch PDF they need in XML format. Also trigger when the user mentions
  "NIH biosketch" or "NIH biographical sketch" together with "XML" or "SciENcv", or when
  they have a biosketch with sections A through D or a Common Form biosketch with a
  Products section.
---

# NIH Biosketch PDF to SciENcv XML Converter

Convert an NIH Biographical Sketch PDF into the XML format defined by the SciENcv
1.3 schema (`sciencv.1.3.xsd`) for import into the NIH SciENcv system.

## When this skill applies

The user has an NIH Biographical Sketch PDF (generated from SciENcv or filled out
manually) and needs an XML version. The PDF may be in either the new Common Form
format (effective 01/25/2026) or the legacy A-D section format.

## Background

The SciENcv system uses the `sciencv.1.3.xsd` schema for CV/biosketch XML. This
is the same schema used for DOE biosketches, but the NIH biosketch PDF has a
different section layout.

- Schema: https://api.ncbi.nlm.nih.gov/sciencv/schema/sciencv.1.3.xsd

The reference file `references/xml-structure.md` in this skill documents the
complete element hierarchy so you typically won't need to fetch the XSD.

**Important**: The XML output is identical regardless of whether the input PDF
uses the new or old format — the same sciencv.1.3 schema applies in both cases.
The difference is only in where data appears in the PDF.

## Detecting the format version

Before parsing, determine which PDF format you're working with:

**New Common Form (2026+)** indicators:
- Has a separate "Products" section with a flat list of citations
- Personal Statement has NO embedded citations
- Contributions to Science have NO embedded citation lists
- ORCID iD present in identification
- Certification statement on the final page
- No section letters (A, B, C, D) as headings

**Legacy format (pre-2026)** indicators:
- Sections labeled A through D
- Personal Statement (Section A) followed by up to 4 citations
- Each Contribution to Science (Section C) followed by up to 4 lettered citations
- No separate Products section
- No ORCID iD
- eRA Commons username present

Both formats produce identical XML output — the mapping instructions below cover
both layouts.

## NIH Biosketch PDF layout — New Common Form (2026+)

The new format consists of two combined parts in a single PDF:

**Part 1 — Biosketch Common Form:**
1. **Identifying Information**: NAME, ORCID iD, POSITION TITLE, ORGANIZATION
   AND LOCATION
2. **Professional Preparation**: Education/training table (Institution/Location,
   Degree, Start/End Dates, Field of Study) — reverse chronological
3. **Appointments & Positions**: Academic/professional positions from the past
   3 years only, reverse chronological
4. **Products**: Two groups:
   - Up to 5 products most closely related to the proposed project
   - Up to 5 other significant products

**Part 2 — NIH Biographical Sketch Supplement:**
5. **Personal Statement**: Narrative text only (3,500 character limit), no citations
6. **Honors**: Up to 15 entries
7. **Contributions to Science**: Up to 5 narrative descriptions (2,000 characters
   each), no embedded citations
8. **Research Support**: Ongoing and completed (optional)

**Certification page**: Final page with certification statement

## NIH Biosketch PDF layout — Legacy format (pre-2026)

1. **Header**: NAME, eRA COMMONS USER NAME, POSITION TITLE, EDUCATION/TRAINING
   table
2. **Section A — Personal Statement**: Narrative paragraph followed by up to 4
   citations
3. **Section B — Positions, Scientific Appointments, and Honors**: Three
   subsections
4. **Section C — Contributions to Science**: Up to 5 numbered contributions,
   each with narrative + up to 4 citations
5. **Section D — Research Support** (optional)

## Workflow

### Step 1: Find the PDF

Look in the current working directory for a PDF file. If there are multiple PDFs,
ask the user which one is the NIH biosketch.

### Step 2: Read all pages

NIH biosketches are limited to 5 pages (plus certification page in new format).
Read all pages.

### Step 3: Detect the format version

Use the indicators above to determine if this is new or legacy format. This
affects where you look for citations and products, but not the XML output.

### Step 4: Extract and map each section

Read `references/xml-structure.md` for the complete XML element hierarchy.
Here are the key mappings:

**Identification** maps to `<identification>`:
- Name -> `<name current="yes">` with `<givennames>` and `<surname>`
  - The schema uses `givennames`/`surname`, NOT firstname/lastname
  - The `current` attribute is required and should be `"yes"`
- ORCID iD (new format) -> `<id idtype="orcid">` with the ORCID as text
- eRA Commons User Name -> `<account accounttype="era">` with the username as text

**Education / Professional Preparation** maps to `<education>`:
- Each row becomes a `<degree>` element
- The `degreetype` attribute is required (e.g., "PhD", "BS", "MS", "BA", "MD")
- Dates use the `Date` complex type: `<year>YYYY</year>` (with optional
  `<month>` and `<day>` children), NOT date strings
- Field of study goes in `<major>`

**Personal Statement** maps to `<statements>`:
- The narrative text becomes a `<statement statementtype="personalstatement">`
  with the text in `<annotation>`
- **New format**: No citations to extract — the statement has only narrative text
- **Legacy format**: Any citations listed after the narrative become `<citation>`
  elements within the same `<statement>`

**Positions / Appointments** maps to `<employment>`:
- Each position becomes a `<position current="yes/no">` element
- The `current` attribute is required
- Dates use the structured `Date` type with `<year>` children

**Honors** maps to `<distinctions>`:
- Each honor/award becomes a `<distinction>` element with `<description>`,
  optional `<organization>`, and optional `<date>`

**Products (new format) / Citations within contributions (legacy format)**
map to `<contributions>`:
- **New format**: The Products section has two flat lists. Map each list to a
  `<citations group="...">` block:
  - "Most closely related to the proposed project"
  - "Other significant products"
  - Parse each citation into a `<citation type="journal">` element
  - Contribution narratives (from the Contributions to Science section) map to
    separate `<citations group="Contribution N">` blocks with `<annotation>`
    but **no** `<citation>` children (since citations are in Products)
- **Legacy format**: Each numbered contribution becomes a
  `<citations group="Contribution N">` block with `<annotation>` for the
  narrative and `<citation>` elements for the embedded citations

**Research Support** maps to `<funding>`:
- Each grant/award becomes an `<award>` element
- If absent or empty, include `<funding/>` as a self-closing tag

### Step 5: Build the XML

Assemble the XML following the schema's required element order:

```xml
<profile xmlns="http://www.ncbi.nlm.nih.gov/sciencv">
  <identification>...</identification>
  <education>...</education>
  <employment>...</employment>
  <funding>...</funding>
  <distinctions>...</distinctions>
  <contributions>...</contributions>
  <statements>...</statements>
</profile>
```

### Step 6: Write the output

Save the XML file with the same base name as the input PDF but with `.xml`
extension. Tell the user:
- Which format was detected (new Common Form or legacy)
- How many entries were converted per section
- Remind them to review parsed publication citations

## Parsing publications

Publication parsing applies to both formats. In the new format, citations appear
in the Products section; in the legacy format, they appear under contributions
and the personal statement.

**Common citation formats:**

```
Smith J, Jones A, Lee B. Title of the paper. Journal Name. 2024;15(3):123-145.
doi:10.1234/example. PMID: 12345678.
```

Map to:
- Authors -> `<contributors>` with `<contributor type="author">` for each
- Title -> `<title>`
- Year -> `<displaydate>`
- Journal -> `<journal>` with `<journalname>`, `<volume>`, `<issue>`, `<page>`
- DOI -> `<externalids>` with `<externalid type="doi">`
- PMID -> `<externalids>` with `<externalid type="pmid">`

If you cannot confidently parse a citation, preserve the full text in `<title>`
and note it for the user to review.

## Common pitfalls

- **Name elements**: The schema uses `<givennames>` and `<surname>`, not
  `<firstname>` and `<lastname>`.
- **Required attributes**: `<name>`, `<position>` require a `current` attribute.
- **Date format**: Dates in education/employment are structured elements
  (`<year>2024</year>`), but dates in `<award>` (funding) use xs:date strings
  (`2024-01-01`). Don't mix these up.
- **Element order**: Elements must appear in schema-defined order.
- **Publications spanning pages**: Reassemble full citations before parsing.
- **New format Products mapping**: Even though citations are listed flat in the
  Products section, they should still be grouped into the appropriate
  `<citations group="...">` blocks in the XML.
- **Empty required sections**: `<education>`, `<employment>`, and `<funding>` are
  required by the schema even if empty.
