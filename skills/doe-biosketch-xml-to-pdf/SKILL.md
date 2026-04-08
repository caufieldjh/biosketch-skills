---
name: doe-biosketch-xml-to-pdf
description: >
  Generate a DOE Biographical Sketch PDF from SciENcv 1.3 XML. Use this skill
  whenever the user wants to convert biosketch XML to PDF, generate a PDF from
  biographical sketch XML, or produce a printable DOE biosketch from XML data.
  Also trigger when the user mentions "biosketch" or "biographical sketch" together
  with "PDF" and "XML", or wants to render/print a biosketch XML file.
---

# DOE Biosketch XML to PDF Converter

Generate a DOE Biographical Sketch PDF from a SciENcv 1.3 schema XML file,
reproducing the standard DOE biosketch form layout.

## When this skill applies

The user has a SciENcv 1.3 XML file (with `<profile>` root containing
`<identification>`, `<education>`, `<employment>`, `<contributions>`, and
`<statements>` sections) and wants a formatted PDF matching the official DOE
biographical sketch form.

## Dependencies

This skill requires Python with the `reportlab` library for PDF generation.

**Preferred:** `pip install reportlab`

**Alternatives** (if reportlab is unavailable):
- `fpdf2` — lighter weight, simpler API: `pip install fpdf2`
- `weasyprint` — HTML/CSS to PDF, more flexible styling but heavier install:
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

Tell the user the output PDF path and summarize what was rendered (number of
degrees, positions, publications, synergistic activities).

## PDF layout reference

The generated PDF reproduces the standard DOE Biographical Sketch form:

- **Page header**: "Effective 05/01/2025 | DOE Biosketch | OMB-3145-0279 and 1910-0400"
- **Title**: "BIOGRAPHICAL SKETCH" (centered, bold)
- **Identification fields**: NAME, POSITION TITLE, ORGANIZATION AND LOCATION
  (each as a labeled line with horizontal rules)
- **Education/Training section**: Table with columns for Institution and Location,
  Degree (with year), Completion Date, and Field of Study
- **Professional Appointments section**: List of positions in reverse chronological
  order, each showing dates, title, and organization
- **Publications sections**:
  - "Most closely related to the proposed project" — numbered list
  - "Other significant publications" — numbered list
- **Synergistic Activities section**: Numbered list of activities
- **Page footer**: "SCV DOE Biosketch v.2025-1" (left) and "Page X of Y" (right)
