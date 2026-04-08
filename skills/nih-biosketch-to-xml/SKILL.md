---
name: nih-biosketch-to-xml
description: >
  Transform an NIH Biographical Sketch PDF into SciENcv-compatible XML (sciencv.1.3 schema).
  Use this skill whenever the user wants to convert an NIH biosketch PDF to XML, mentions
  SciENcv biosketch XML with NIH, asks about converting an NIH biographical sketch to XML,
  or has an NIH biosketch PDF they need in XML format. Also trigger when the user mentions
  "NIH biosketch" or "NIH biographical sketch" together with "XML" or "SciENcv", or when
  they have a biosketch with sections A through D (Personal Statement, Positions/Honors,
  Contributions to Science, Research Support).
---

# NIH Biosketch PDF to SciENcv XML Converter

Convert an NIH Biographical Sketch PDF into the XML format defined by the SciENcv
1.3 schema (`sciencv.1.3.xsd`) for import into the NIH SciENcv system.

## When this skill applies

The user has an NIH Biographical Sketch PDF (typically generated from SciENcv or
filled out manually) and needs an XML version. The PDF follows the standard NIH
biosketch format with sections A through D.

## Background

The SciENcv system uses the `sciencv.1.3.xsd` schema for CV/biosketch XML. This
is the same schema used for DOE biosketches, but the NIH biosketch PDF has a
different section layout with lettered sections (A-D) and different content
organization, especially around how publications are grouped with narrative
descriptions.

- Schema: https://api.ncbi.nlm.nih.gov/sciencv/schema/sciencv.1.3.xsd

The reference file `references/xml-structure.md` in this skill documents the
complete element hierarchy so you typically won't need to fetch the XSD.

## NIH Biosketch PDF layout

An NIH biosketch PDF has these sections (in order):

1. **Header**: NAME, eRA COMMONS USER NAME, POSITION TITLE, EDUCATION/TRAINING
   table (Institution/Location, Degree, Completion Date, Field of Study)
2. **Section A — Personal Statement**: A narrative paragraph describing the
   investigator's qualifications, followed by up to 4 citations supporting the
   statement
3. **Section B — Positions, Scientific Appointments, and Honors**: Three
   subsections listing positions held, other appointments, and honors/awards
4. **Section C — Contributions to Science**: Up to 5 numbered contributions, each
   consisting of a narrative description of the contribution followed by up to 4
   supporting citations
5. **Section D — Research Support and/or Scholastic Performance** (optional):
   Lists ongoing and recently completed research support (grants/awards)

The total biosketch is limited to 5 pages.

## Workflow

### Step 1: Find the PDF

Look in the current working directory for a PDF file. If there are multiple PDFs,
ask the user which one is the NIH biosketch. The filename may contain "biosketch",
"bio", "NIH", or the person's name.

### Step 2: Read all pages

NIH biosketches are limited to 5 pages. Read all pages to capture all sections,
especially Contributions to Science and Research Support which often extend across
page breaks.

### Step 3: Extract and map each section

Read `references/xml-structure.md` for the complete XML element hierarchy and
mapping details. Here is a summary of the key mappings:

**Header — Identification** maps to `<identification>`:
- Name -> `<name current="yes">` with `<givennames>` and `<surname>`
  - The schema uses `givennames`/`surname`, NOT firstname/lastname
  - The `current` attribute is required and should be `"yes"`
- eRA Commons User Name -> `<account accounttype="era">` with the username as text

**Header — Education/Training** maps to `<education>`:
- Each row becomes a `<degree>` element
- The `degreetype` attribute is required (e.g., "PhD", "BS", "MS", "BA", "MD")
- Dates use the `Date` complex type: `<year>YYYY</year>` (with optional
  `<month>` and `<day>` children), NOT date strings
- Field of study goes in `<major>`

**Section A — Personal Statement** maps to `<statements>`:
- The narrative text becomes a `<statement statementtype="personalstatement">`
  with the text in `<annotation>`
- Any citations listed after the narrative become `<citation>` elements within
  the same `<statement>` (the statement type extends Citations, so it can
  contain citations directly)

**Section B — Positions, Scientific Appointments, and Honors**:
- **Positions** and **Scientific Appointments** map to `<employment>`:
  - Each position becomes a `<position current="yes/no">` element
  - The `current` attribute is required — set to `"yes"` for the current
    position, `"no"` for past positions
  - Dates use the structured `Date` type with `<year>` children
- **Honors** map to `<distinctions>`:
  - Each honor/award becomes a `<distinction>` element with:
    - `<description>` for the honor name/description
    - `<organization>` for the granting organization (if mentioned)
    - `<date>` for the year received

**Section C — Contributions to Science** maps to `<contributions>`:
- Each numbered contribution becomes a `<citations group="Contribution N">`
  block (where N is the contribution number)
- The narrative description for each contribution goes in the `<annotation>`
  element within that `<citations>` group
- Each citation listed under the contribution becomes a `<citation type="journal">`
  (or appropriate type) within the same `<citations>` group
- Parse author lists, title, journal, volume, issue, pages, year, and DOI/PMID
  from each citation string

**Section D — Research Support** maps to `<funding>`:
- Each grant/award becomes an `<award>` element with:
  - `<fundingsource>` for the funding agency
  - `<awardid type="grant">` for the grant number
  - `<projecttitle>` for the project title
  - `<role>` for the investigator's role (PI, Co-PI, etc.)
  - `<principalinvestigator>` with `<stringname>` for the PI name
  - `<startdate>` and `<enddate>` as xs:date strings (YYYY-MM-DD)
  - `<description>` for the project description if provided
- If Section D is absent or empty, include `<funding/>` as a self-closing tag

### Step 4: Build the XML

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

The `xmlns` namespace attribute is important for schema validation.

### Step 5: Write the output

Save the XML file with the same base name as the input PDF but with `.xml` extension.
Tell the user how many entries were converted per section (education, positions,
honors, contributions with citation counts, research support) and remind them to
review, especially the parsed publication citations.

## Parsing publications

Publication parsing is the trickiest part of this conversion. NIH biosketch PDFs
list publications as formatted citation strings within each contribution. You need
to decompose each into structured XML elements.

**Common citation formats you'll encounter:**

```
Smith J, Jones A, Lee B. Title of the paper. Journal Name. 2024;15(3):123-145.
doi:10.1234/example. PMID: 12345678.
```

Map these parts to:
- Authors -> `<contributors>` with `<contributor type="author">` for each
- Title -> `<title>`
- Year -> `<displaydate>`
- Journal -> `<journal>` with `<journalname>`, `<volume>`, `<issue>`, `<page>`
- DOI -> `<externalids>` with `<externalid type="doi">`
- PMID -> `<externalids>` with `<externalid type="pmid">`

If you cannot confidently parse a citation into its components, preserve the full
citation text in the `<title>` element and note it for the user to review.

## Key differences from DOE biosketch conversion

- **Personal Statement**: NIH biosketches have a narrative personal statement
  (Section A) that DOE biosketches don't. This maps to
  `<statement statementtype="personalstatement">`.
- **Grouped publications**: NIH publications are grouped under narrative
  contribution descriptions (Section C), not in flat lists. Each group maps to
  a separate `<citations group="...">` block with an `<annotation>`.
- **Honors/Distinctions**: NIH biosketches have a dedicated honors subsection in
  Section B. These map to `<distinctions>`, which DOE biosketches don't use.
- **Research Support**: NIH biosketches optionally list grants (Section D), which
  maps to `<funding>` with `<award>` elements. DOE biosketches don't include
  funding (that's in the separate C&P(O)S document).
- **eRA Commons**: NIH biosketches include an eRA Commons username, which maps to
  `<account accounttype="era">`.
- **No Synergistic Activities**: NIH biosketches don't have a synergistic
  activities section (that's a DOE/NSF concept).

## Common pitfalls

- **Name elements**: The schema uses `<givennames>` and `<surname>`, not
  `<firstname>` and `<lastname>`.
- **Required attributes**: `<name>`, `<position>`, `<emailaddress>`, and `<phone>`
  all require a `current` attribute with value `"yes"` or `"no"`.
- **Date format**: Dates in education/employment are structured elements
  (`<year>2024</year>`), but dates in `<award>` (funding) use xs:date strings
  (`2024-01-01`). Don't mix these up.
- **Element order**: Elements within each complex type must appear in the order
  defined by the schema. See the reference file for the exact ordering.
- **Publications spanning pages**: A single citation often wraps across a page
  break. Make sure to reassemble the full citation before parsing.
- **Contribution narratives vs citations**: Each numbered contribution in
  Section C starts with a narrative paragraph, followed by citations. Make sure
  to separate the narrative (which goes in `<annotation>`) from the citations.
- **Degree type attribute**: `<degree>` requires a `degreetype` attribute.
- **Empty required sections**: `<education>`, `<employment>`, and `<funding>` are
  required by the schema even if empty. Include them as self-closing tags if needed.
