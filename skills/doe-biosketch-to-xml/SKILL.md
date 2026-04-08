---
name: doe-biosketch-to-xml
description: >
  Transform a DOE Biographical Sketch PDF into SciENcv-compatible XML (sciencv.1.3 schema).
  Use this skill whenever the user wants to convert a DOE biosketch PDF to XML, mentions
  SciENcv biosketch XML, asks about converting a biographical sketch to XML, or has a
  DOE biosketch PDF they need in XML format. Also trigger when the user mentions
  "biosketch" or "biographical sketch" together with "XML", "SciENcv", or "DOE".
---

# DOE Biosketch PDF to SciENcv XML Converter

Convert a DOE Biographical Sketch PDF into the XML format defined by the SciENcv
1.3 schema (`sciencv.1.3.xsd`) for import into the NIH SciENcv system.

## When this skill applies

The user has a DOE Biographical Sketch PDF (typically generated from SciENcv or
filled out manually) and needs an XML version. The PDF follows the standard DOE
biosketch form layout with sections for identification, education/training,
professional appointments, publications, and synergistic activities.

## Background

The SciENcv system uses the `sciencv.1.3.xsd` schema for CV/biosketch XML. This
schema is different from the C&P(O)S XML format — it uses different element names,
date structures, and has a richer data model for publications. The schema is at:

- Schema: https://api.ncbi.nlm.nih.gov/sciencv/schema/sciencv.1.3.xsd

The reference file `references/xml-structure.md` in this skill documents the
complete element hierarchy so you typically won't need to fetch the XSD.

## DOE Biosketch PDF layout

A DOE biosketch PDF has these sections (in order):

1. **Header**: "BIOGRAPHICAL SKETCH" title
2. **Identification**: NAME, POSITION TITLE, ORGANIZATION AND LOCATION
3. **Education/Training**: Table with columns for Institution/Location, Degree,
   Completion Date, and Field of Study
4. **Professional Appointments**: List of positions with dates and institutions
   (most recent first)
5. **Publications**: Two subsections:
   - "Most closely related to the proposed project" (up to 10)
   - "Other significant publications" (up to 10)
6. **Synergistic Activities**: Numbered list (up to 5)

## Workflow

### Step 1: Find the PDF

Look in the current working directory for a PDF file. If there are multiple PDFs,
ask the user which one is the DOE biosketch. The filename may contain "biosketch",
"bio", or the person's name.

### Step 2: Read all pages

DOE biosketches are typically 3-5 pages. Read all pages to capture the full
publications list and synergistic activities, which often extend across page breaks.

### Step 3: Extract and map each section

Read `references/xml-structure.md` for the complete XML element hierarchy and
mapping details. Here is a summary of the key mappings:

**Identification** maps to `<identification>`:
- Name → `<name current="yes">` with `<givennames>` and `<surname>`
  - Note: the schema uses `givennames`/`surname`, NOT firstname/lastname
  - The `current` attribute is required and should be `"yes"`

**Education/Training** maps to `<education>`:
- Each row becomes a `<degree>` element
- The `degreetype` attribute is required (e.g., "PhD", "BS", "MS", "BA", "MD")
- Dates use the `Date` complex type: `<year>YYYY</year>` (with optional
  `<month>` and `<day>` children), NOT date strings like "2025-01-01"
- Field of study goes in `<major>`

**Professional Appointments** maps to `<employment>`:
- Each position becomes a `<position current="yes/no">` element
- The `current` attribute is required — set to `"yes"` for the current position,
  `"no"` for all past positions. If the PDF shows "present" or has no end date
  for a position, that's the current one.
- Dates use the same `Date` complex type with `<year>` children

**Publications** maps to `<contributions>`:
- Each publication subsection becomes a `<citations group="...">` block
- Use group names like `"Most closely related to the proposed project"` and
  `"Other significant publications"`
- Each publication becomes a `<citation type="journal">` (or appropriate type)
- See `references/xml-structure.md` for the full citation element structure
- Parse author lists, title, journal, volume, issue, pages, year, and DOI/PMID
  from each citation string

**Synergistic Activities** maps to `<statements>`:
- Each activity becomes a `<statement statementtype="nsfactivity">` element
  (DOE biosketches use the same synergistic activities concept as NSF)
- The text goes in the `<annotation>` child element

**Funding** — DOE biosketches typically don't list funding (that's in the C&P(O)S
document). Include an empty `<funding/>` element since it's required by the schema.

### Step 4: Build the XML

Assemble the XML following the schema's required element order:

```xml
<profile xmlns="http://www.ncbi.nlm.nih.gov/sciencv">
  <identification>...</identification>
  <education>...</education>
  <employment>...</employment>
  <funding/>
  <contributions>...</contributions>
  <statements>...</statements>
</profile>
```

The `xmlns` namespace attribute is important for schema validation.

### Step 5: Write the output

Save the XML file with the same base name as the input PDF but with `.xml` extension.
Tell the user how many entries were converted per section (education, positions,
publications, synergistic activities) and remind them to review, especially the
parsed publication citations.

## Parsing publications

Publication parsing is the trickiest part of this conversion. DOE biosketch PDFs
list publications as formatted citation strings. You need to decompose each into
structured XML elements.

**Common citation formats you'll encounter:**

```
Smith J, Jones A, Lee B. (2024) Title of the paper. Journal Name. 15(3):123-145.
doi:10.1234/example
```

Map these parts to:
- Authors → `<contributors>` with `<contributor type="author">` for each
- Title → `<title>`
- Year → `<displaydate>`
- Journal → `<journal>` with `<journalname>`, `<volume>`, `<issue>`, `<page>`
- DOI → `<externalids>` with `<externalid type="doi">`
- PMID → `<externalids>` with `<externalid type="pmid">`

If you cannot confidently parse a citation into its components, preserve the full
citation text in the `<title>` element and note it for the user to review. It's
better to have a slightly imperfect but complete conversion than to lose data.

## Common pitfalls

- **Name elements**: The schema uses `<givennames>` and `<surname>`, not
  `<firstname>` and `<lastname>`. The C&P(O)S format uses the latter — don't mix
  them up.
- **Required attributes**: `<name>`, `<position>`, `<emailaddress>`, and `<phone>`
  all require a `current` attribute with value `"yes"` or `"no"`.
- **Date format**: Dates are structured elements (`<year>2024</year>`), not strings.
  This differs from the C&P(O)S format which uses `YYYY-MM-01` strings.
- **Element order**: Elements within each complex type must appear in the order
  defined by the schema. See the reference file for the exact ordering.
- **Publications spanning pages**: A single citation often wraps across a page break.
  Make sure to reassemble the full citation before parsing.
- **Degree type attribute**: `<degree>` requires a `degreetype` attribute. Parse it
  from the Degree column of the education table (e.g., "Ph.D.", "B.S.", "M.D.").
- **Empty required sections**: `<education>`, `<employment>`, and `<funding>` are
  required by the schema even if empty. Include them as self-closing tags if needed.
