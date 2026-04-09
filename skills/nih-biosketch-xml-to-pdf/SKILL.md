---
name: nih-biosketch-xml-to-pdf
description: >
  Generate an NIH Biographical Sketch PDF from SciENcv 1.3 XML. Use this skill
  whenever the user wants to convert NIH biosketch XML to PDF, generate a PDF from
  NIH biographical sketch XML, or produce a printable NIH biosketch from XML data.
  Also trigger when the user mentions "NIH biosketch" or "NIH biographical sketch"
  together with "PDF" and "XML", or wants to render/print an NIH biosketch XML file.
  Produces the new Common Form layout (effective 01/25/2026) and can also accept
  old-format XML with embedded citations.
---

# NIH Biosketch XML to PDF Converter

Generate an NIH Biographical Sketch PDF from a SciENcv 1.3 schema XML file,
producing the new Common Form layout (effective 01/25/2026).

## When this skill applies

The user has a SciENcv 1.3 XML file (with `<profile>` root containing
`<identification>`, `<education>`, `<employment>`, and optionally `<funding>`,
`<distinctions>`, `<contributions>`, and `<statements>` sections) and wants a
formatted PDF matching the current NIH biographical sketch form.

**Backward compatibility**: The script accepts XML from both the new and old
format. If the XML has citations embedded under contributions or the personal
statement (old format), those citations are collected into the Products section
in the PDF output. This enables converting old-format documents to the new
layout.

## Dependencies

This skill requires Python with the `reportlab` library for PDF generation.

**Preferred:** `pip install reportlab`

**Alternatives** (if reportlab is unavailable):
- `fpdf2` -- lighter weight, simpler API: `pip install fpdf2`
- `weasyprint` -- HTML/CSS to PDF, more flexible styling but heavier install:
  `pip install weasyprint`

If using an alternative library, you'll need to adapt the bundled script or write
equivalent PDF generation code following the layout described below.

## Workflow

### Step 1: Install dependencies

Check if reportlab is available. If not, install it:

```bash
pip install reportlab
```

### Step 2: Find the XML file

Look in the current working directory for an XML file containing biosketch data.
The file should have a `<profile>` root element with `<identification>`,
`<education>`, `<employment>`, and optionally `<contributions>` and `<statements>`.

Note: The SciENcv 1.3 schema uses a namespace
(`http://www.ncbi.nlm.nih.gov/sciencv`). The bundled script handles both
namespaced and non-namespaced XML.

### Step 3: Run the bundled script

This skill includes a Python script at `scripts/generate_pdf.py` that handles
the full conversion. Run it with:

```bash
python <skill-path>/scripts/generate_pdf.py <input.xml> [output.pdf]
```

If `output.pdf` is omitted, the script will use the same base name as the input
with a `.pdf` extension.

### Step 4: Report results

Tell the user the output PDF path and summarize what was rendered (education
entries, positions, honors, products, contributions, research support entries,
page count).

## PDF layout reference

The generated PDF follows the new NIH Common Form layout (effective 01/25/2026):

- **Page header**: "OMB No. 0925-0001 and 0925-0002" (left),
  "Biographical Sketch Format Page" (right)
- **Title**: "BIOGRAPHICAL SKETCH" (centered, bold)
- **Subtitle**: Instructions text about providing information for Senior/key
  personnel

**Common Form sections:**
- **Identifying Information**: NAME, ORCID iD, eRA COMMONS USER NAME,
  POSITION TITLE (each as a labeled line with horizontal rules)
- **Professional Preparation**: Table with columns for INSTITUTION AND
  LOCATION, DEGREE, Completion Date (MM/YYYY), FIELD OF STUDY
- **Appointments & Positions**: Positions from the past 3 years, reverse
  chronological order
- **Products**: Two subsections:
  - "Most closely related to the proposed project" (up to 5)
  - "Other significant products" (up to 5)

**NIH Supplement sections:**
- **Personal Statement**: Narrative text only (no citations)
- **Honors**: List of honors and awards (up to 15)
- **Contributions to Science**: Up to 5 numbered contributions, each with a
  narrative description only (no embedded citations)
- **Research Support**: Ongoing and completed support (optional)

- **Page footer**: "Page X of Y" (right-aligned)
