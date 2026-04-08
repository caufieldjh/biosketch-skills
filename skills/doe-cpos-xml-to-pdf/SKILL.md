---
name: doe-cpos-xml-to-pdf
description: >
  Generate a DOE Current and Pending (Other) Support PDF from SciENcv C&P(O)S XML.
  Use this skill whenever the user wants to convert C&P(O)S XML to PDF, generate a
  PDF from current and pending support XML, or produce a printable DOE C&P(O)S form
  from XML data. Also trigger when the user mentions "current and pending" together
  with "PDF" and "XML", or wants to render/print a C&P(O)S XML file.
---

# DOE C&P(O)S XML to PDF Converter

Generate a DOE Current and Pending (Other) Support PDF from a SciENcv-compatible
C&P(O)S XML file, reproducing the standard DOE form layout.

## When this skill applies

The user has a SciENcv C&P(O)S XML file (with `<profile>` root containing
`<support>` entries) and wants a formatted PDF matching the official DOE
C&P(O)S form.

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

Look in the current working directory for an XML file containing C&P(O)S data.
The file should have a `<profile>` root element with `<funding>` > `<support>`
children.

### Step 3: Run the bundled script

This skill includes a Python script at `scripts/generate_pdf.py` that handles
the full conversion. Run it with:

```bash
python <skill-path>/scripts/generate_pdf.py <input.xml> [output.pdf]
```

If `output.pdf` is omitted, the script will use the same base name as the input
with a `.pdf` extension.

### Step 4: Report results

Tell the user the output PDF path and how many support entries were rendered.

## PDF layout reference

The generated PDF reproduces the standard DOE C&P(O)S form (SCV C&P(O)S v.2025-1):

- **Page header**: "Effective 05/01/2025 | DOE C&P(O)S | OMB-3145-0279 and 1910-0400"
- **Title block**: "CURRENT AND PENDING (OTHER) SUPPORT INFORMATION" (centered, bold)
  with subtitle about providing information for senior/key personnel
- **Identification fields**: NAME, POSITION TITLE, ORGANIZATION AND LOCATION
  (each as a labeled line with horizontal rules)
- **Section header**: "Proposals and Active Projects" (bold, underlined)
- **Each support entry**: Right-aligned bold labels with values, including:
  Project Title, Status of Support, Proposal/Award Number, Source of Support,
  Primary Place of Performance, Start Date, End Date, Total Amount
- **Person Months table**: Two-column table (Year | Person Months)
- **Overall Objectives**: Bold label followed by paragraph text
- **Statement of Potential Overlap**: Bold label followed by text
- **Page footer**: "SCV C&P(O)S v.2025-1" (left) and "Page X of Y" (right)
