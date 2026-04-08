#!/usr/bin/env python3
"""Generate a DOE C&P(O)S PDF from SciENcv C&P(O)S XML."""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, KeepTogether
    )
    from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Frame
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
except ImportError:
    print("Error: reportlab is required. Install with: pip install reportlab")
    sys.exit(1)


def get_text(element, tag, default=""):
    """Get text content of a child element."""
    if element is None:
        return default
    child = element.find(tag)
    if child is not None and child.text:
        return child.text.strip()
    return default


def parse_date_to_mmyyyy(date_str):
    """Convert YYYY-MM-DD or YYYY-MM-01 to MM/YYYY."""
    if not date_str:
        return ""
    parts = date_str.split("-")
    if len(parts) >= 2:
        return f"{parts[1]}/{parts[0]}"
    return date_str


def format_amount(amount_str):
    """Format a plain number as $N,NNN,NNN."""
    if not amount_str:
        return ""
    try:
        num = int(amount_str)
        return f"${num:,}"
    except ValueError:
        try:
            num = float(amount_str)
            return f"${num:,.0f}"
        except ValueError:
            return amount_str


def parse_xml(xml_path):
    """Parse the C&P(O)S XML and return structured data."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    data = {
        "name": "",
        "position": "",
        "organization": "",
        "location": "",
        "supports": []
    }

    # Identification
    ident = root.find("identification")
    if ident is not None:
        name_el = ident.find("name")
        if name_el is not None:
            first = get_text(name_el, "firstname", "")
            middle = get_text(name_el, "middlename", "")
            last = get_text(name_el, "lastname", "")
            parts = [p for p in [last, ", ".join(filter(None, [first, middle]))] if p]
            if last and (first or middle):
                data["name"] = f"{last}, {' '.join(filter(None, [first, middle]))}"
            else:
                data["name"] = last or first or ""

    # Employment
    emp = root.find("employment")
    if emp is not None:
        pos = emp.find("position")
        if pos is not None:
            data["position"] = get_text(pos, "positiontitle")
            org = pos.find("organization")
            if org is not None:
                orgname = get_text(org, "orgname", "")
                city = get_text(org, "city", "")
                state = get_text(org, "stateorprovince", "")
                country = get_text(org, "country", "")
                data["organization"] = orgname
                loc_parts = [p for p in [orgname, city, state, country] if p]
                data["location"] = ", ".join(loc_parts)

    # Funding / Support entries
    funding = root.find("funding")
    if funding is not None:
        for support in funding.findall("support"):
            entry = {
                "projecttitle": get_text(support, "projecttitle"),
                "awardnumber": get_text(support, "awardnumber"),
                "supportsource": get_text(support, "supportsource"),
                "location": get_text(support, "location"),
                "contributiontype": get_text(support, "contributiontype", "award"),
                "awardamount": get_text(support, "awardamount"),
                "inkinddescription": get_text(support, "inkinddescription"),
                "overallobjectives": get_text(support, "overallobjectives"),
                "potentialoverlap": get_text(support, "potentialoverlap"),
                "startdate": get_text(support, "startdate"),
                "enddate": get_text(support, "enddate"),
                "supporttype": get_text(support, "supporttype"),
                "personmonths": []
            }
            commitment = support.find("commitment")
            if commitment is not None:
                for pm in commitment.findall("personmonth"):
                    year = pm.get("year", "")
                    value = pm.text.strip() if pm.text else ""
                    entry["personmonths"].append((year, value))
            data["supports"].append(entry)

    return data


class CPOSDocTemplate(BaseDocTemplate):
    """Custom document template with header and footer."""

    def __init__(self, filename, total_pages_holder, **kwargs):
        self.total_pages_holder = total_pages_holder
        super().__init__(filename, **kwargs)
        frame = Frame(
            0.75 * inch, 0.75 * inch,
            kwargs.get("pagesize", letter)[0] - 1.5 * inch,
            kwargs.get("pagesize", letter)[1] - 1.75 * inch,
            id="main"
        )
        self.addPageTemplates([PageTemplate(id="main", frames=[frame],
                                           onPage=self._draw_header_footer)])

    def _draw_header_footer(self, canvas, doc):
        canvas.saveState()
        width = doc.pagesize[0]

        # Header
        canvas.setFont("Times-Roman", 9)
        canvas.drawString(0.75 * inch, doc.pagesize[1] - 0.5 * inch,
                          "Effective 05/01/2025")
        canvas.drawCentredString(width / 2, doc.pagesize[1] - 0.5 * inch,
                                 "DOE C&P(O)S")
        canvas.drawRightString(width - 0.75 * inch, doc.pagesize[1] - 0.5 * inch,
                               "OMB-3145-0279 and 1910-0400")

        # Footer
        canvas.setFont("Times-Roman", 9)
        canvas.drawString(0.75 * inch, 0.4 * inch, "SCV C&P(O)S v.2025-1")
        page_num = canvas.getPageNumber()
        canvas.drawRightString(width - 0.75 * inch, 0.4 * inch,
                               f"Page {page_num} of %(total)s" %
                               {"total": self.total_pages_holder[0]})
        canvas.restoreState()


def make_styles():
    """Create paragraph styles (fresh each call for two-pass builds)."""
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "CPOSTitle", parent=styles["Normal"],
            fontName="Times-Bold", fontSize=11,
            alignment=TA_CENTER, spaceAfter=2),
        "subtitle": ParagraphStyle(
            "CPOSSubtitle", parent=styles["Normal"],
            fontName="Times-Roman", fontSize=9,
            alignment=TA_CENTER, spaceAfter=6),
        "field_label": ParagraphStyle(
            "FieldLabel", parent=styles["Normal"],
            fontName="Times-Bold", fontSize=10,
            alignment=TA_RIGHT, leading=12),
        "field_value": ParagraphStyle(
            "FieldValue", parent=styles["Normal"],
            fontName="Times-Roman", fontSize=10,
            leading=12),
        "section_header": ParagraphStyle(
            "SectionHeader", parent=styles["Normal"],
            fontName="Times-Bold", fontSize=10,
            spaceAfter=6, spaceBefore=12),
        "body": ParagraphStyle(
            "Body", parent=styles["Normal"],
            fontName="Times-Roman", fontSize=10,
            leading=13, spaceAfter=6),
        "bold_label": ParagraphStyle(
            "BoldLabel", parent=styles["Normal"],
            fontName="Times-Bold", fontSize=10,
            leading=12),
        "ident": ParagraphStyle(
            "Ident", parent=styles["Normal"],
            fontName="Times-Roman", fontSize=10,
            leading=13, spaceBefore=2, spaceAfter=2),
    }


def build_elements(data):
    """Build fresh flowable elements from data (must be called fresh each pass)."""
    st = make_styles()
    page_width = letter[0] - 1.5 * inch
    label_width = 3.2 * inch
    value_width = page_width - label_width
    elements = []

    def rule():
        t = Table([[""]], colWidths=[page_width], rowHeights=[1])
        t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 1, colors.black)]))
        return t

    def field_row(label, value):
        return [Paragraph(label, st["field_label"]),
                Paragraph(value, st["field_value"])]

    def field_table(rows):
        t = Table(rows, colWidths=[label_width, value_width])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (0, -1), 6),
        ]))
        return t

    # Title block
    elements.append(Paragraph(
        "<b>CURRENT AND PENDING (OTHER) SUPPORT INFORMATION</b>", st["title"]))
    elements.append(Paragraph(
        "Provide the following information for the Senior/key personnel and other "
        "significant contributors.<br/>Follow this format for each person.",
        st["subtitle"]))

    # Identification
    elements.append(rule())
    elements.append(Paragraph(f"*NAME: {data['name']}", st["ident"]))
    elements.append(rule())
    elements.append(Paragraph(f"*POSITION TITLE: {data['position']}", st["ident"]))
    elements.append(rule())
    elements.append(Paragraph(
        f"*ORGANIZATION AND LOCATION: {data['location']}", st["ident"]))
    elements.append(rule())
    elements.append(Spacer(1, 6))

    awards = [e for e in data["supports"] if e["contributiontype"] == "award"]
    inkinds = [e for e in data["supports"] if e["contributiontype"] == "inkind"]

    if awards:
        elements.append(Paragraph(
            "<b><u>Proposals and Active Projects</u></b>", st["section_header"]))

        for entry in awards:
            rows = []
            if entry["projecttitle"]:
                rows.append(field_row("*Proposal/Active Project Title:",
                                      entry["projecttitle"]))
            status = entry["supporttype"].capitalize() if entry["supporttype"] else ""
            rows.append(field_row("*Status of Support:", status))
            if entry["awardnumber"]:
                rows.append(field_row("Proposal/Award Number:", entry["awardnumber"]))
            if entry["supportsource"]:
                rows.append(field_row("*Source of Support:", entry["supportsource"]))
            if entry["location"]:
                rows.append(field_row("*Primary Place of Performance:",
                                      entry["location"]))
            start = parse_date_to_mmyyyy(entry["startdate"])
            if start:
                rows.append(field_row(
                    "*Proposal/Active Project Start Date: (MM/YYYY):", start))
            end = parse_date_to_mmyyyy(entry["enddate"])
            if end:
                rows.append(field_row(
                    "*Proposal/Active Project End Date: (MM/YYYY):", end))
            amount = format_amount(entry["awardamount"])
            if amount:
                rows.append(field_row(
                    "*Total Anticipated Proposal/Project Amount:", amount))
            if rows:
                elements.append(field_table(rows))

            # Person months
            if entry["personmonths"]:
                elements.append(Spacer(1, 4))
                elements.append(Paragraph(
                    "* Person Months per budget period Devoted to the "
                    "Proposal/Active Project:", st["bold_label"]))
                elements.append(Spacer(1, 4))
                centered = ParagraphStyle("pmc", fontName="Times-Roman",
                                          fontSize=10, alignment=TA_CENTER)
                centered_b = ParagraphStyle("pmcb", fontName="Times-Bold",
                                            fontSize=10, alignment=TA_CENTER)
                pm_rows = [[Paragraph("<b>Year</b>", centered_b),
                            Paragraph("<b>Person Months</b>", centered_b)]]
                for year, months in entry["personmonths"]:
                    pm_rows.append([Paragraph(year, centered),
                                    Paragraph(months, centered)])
                pm = Table(pm_rows, colWidths=[1.5 * inch, 1.5 * inch])
                pm.setStyle(TableStyle([
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]))
                wrapper = Table([[pm]], colWidths=[page_width])
                wrapper.setStyle(TableStyle([
                    ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ]))
                elements.append(wrapper)

            # Objectives
            if entry["overallobjectives"]:
                elements.append(Spacer(1, 6))
                elements.append(Paragraph("*Overall Objectives:", st["bold_label"]))
                elements.append(Spacer(1, 4))
                elements.append(Paragraph(entry["overallobjectives"], st["body"]))

            # Overlap
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(
                "*Statement of Potential Overlap:", st["bold_label"]))
            elements.append(Spacer(1, 4))
            elements.append(Paragraph(
                entry["potentialoverlap"] or "None", st["body"]))
            elements.append(Spacer(1, 18))

    if inkinds:
        elements.append(Paragraph(
            "<b><u>In-Kind Contributions</u></b>", st["section_header"]))
        for entry in inkinds:
            rows = []
            if entry["inkinddescription"]:
                rows.append(field_row("*In-Kind Contribution Description:",
                                      entry["inkinddescription"]))
            status = entry["supporttype"].capitalize() if entry["supporttype"] else ""
            rows.append(field_row("*Status of Support:", status))
            if entry["supportsource"]:
                rows.append(field_row("*Source of Support:", entry["supportsource"]))
            if entry["location"]:
                rows.append(field_row("*Primary Place of Performance:",
                                      entry["location"]))
            start = parse_date_to_mmyyyy(entry["startdate"])
            if start:
                rows.append(field_row("*Start Date: (MM/YYYY):", start))
            end = parse_date_to_mmyyyy(entry["enddate"])
            if end:
                rows.append(field_row("*End Date: (MM/YYYY):", end))
            amount = format_amount(entry["awardamount"])
            if amount:
                rows.append(field_row("*Estimated Value:", amount))
            if rows:
                elements.append(field_table(rows))
            if entry["overallobjectives"]:
                elements.append(Spacer(1, 6))
                elements.append(Paragraph("*Overall Objectives:", st["bold_label"]))
                elements.append(Spacer(1, 4))
                elements.append(Paragraph(entry["overallobjectives"], st["body"]))
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(
                "*Statement of Potential Overlap:", st["bold_label"]))
            elements.append(Spacer(1, 4))
            elements.append(Paragraph(
                entry["potentialoverlap"] or "None", st["body"]))
            elements.append(Spacer(1, 18))

    return elements


def build_pdf(data, output_path):
    """Build the PDF with two passes for correct page count."""
    total_pages = [1]

    # First pass to count pages
    doc1 = CPOSDocTemplate(output_path, total_pages, pagesize=letter,
                           title="DOE Current and Pending (Other) Support")
    doc1.build(build_elements(data))
    total_pages[0] = doc1.page

    # Second pass with correct total
    doc2 = CPOSDocTemplate(output_path, total_pages, pagesize=letter,
                           title="DOE Current and Pending (Other) Support")
    doc2.build(build_elements(data))

    return len(data["supports"]), doc2.page


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input.xml> [output.pdf]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) >= 3 else str(
        Path(input_path).with_suffix(".pdf"))

    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    data = parse_xml(input_path)
    num_entries, num_pages = build_pdf(data, output_path)

    current = sum(1 for s in data["supports"] if s["supporttype"] == "current")
    pending = sum(1 for s in data["supports"] if s["supporttype"] == "pending")

    print(f"Generated {output_path}")
    print(f"  {num_entries} support entries ({current} current, {pending} pending)")
    print(f"  {num_pages} pages")


if __name__ == "__main__":
    main()
