#!/usr/bin/env python3
"""Generate a DOE Biographical Sketch PDF from SciENcv 1.3 XML."""

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
        PageBreak, KeepTogether, ListFlowable, ListItem
    )
    from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Frame
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
except ImportError:
    print("Error: reportlab is required. Install with: pip install reportlab")
    sys.exit(1)


# SciENcv 1.3 namespace
NS = {"scv": "http://www.ncbi.nlm.nih.gov/sciencv"}


def find_el(parent, tag):
    """Find element with or without namespace."""
    if parent is None:
        return None
    el = parent.find(f"scv:{tag}", NS)
    if el is None:
        el = parent.find(tag)
    return el


def find_all_el(parent, tag):
    """Find all elements with or without namespace."""
    if parent is None:
        return []
    els = parent.findall(f"scv:{tag}", NS)
    if not els:
        els = parent.findall(tag)
    return els


def get_text(parent, tag, default=""):
    """Get text of a child element."""
    el = find_el(parent, tag)
    if el is not None and el.text:
        return el.text.strip()
    return default


def parse_xml(xml_path):
    """Parse the SciENcv 1.3 XML and return structured data."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Strip namespace from root tag if present
    root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

    data = {
        "name": "",
        "position": "",
        "organization": "",
        "location": "",
        "degrees": [],
        "positions": [],
        "citation_groups": [],
        "activities": [],
    }

    # Identification
    ident = find_el(root, "identification")
    if ident is not None:
        name_el = find_el(ident, "name")
        if name_el is not None:
            given = get_text(name_el, "givennames")
            surname = get_text(name_el, "surname")
            # Also try firstname/lastname (C&P(O)S style, just in case)
            if not given:
                given = get_text(name_el, "firstname")
            if not surname:
                surname = get_text(name_el, "lastname")
            if surname and given:
                data["name"] = f"{surname}, {given}"
            else:
                data["name"] = surname or given or ""

    # Employment - extract all positions
    emp = find_el(root, "employment")
    if emp is not None:
        for pos in find_all_el(emp, "position"):
            title = get_text(pos, "positiontitle")
            org_el = find_el(pos, "organization")
            orgname = get_text(org_el, "orgname") if org_el else ""
            city = get_text(org_el, "city") if org_el else ""
            state = get_text(org_el, "stateorprovince") if org_el else ""
            country = get_text(org_el, "country") if org_el else ""

            start_el = find_el(pos, "startdate")
            start_year = get_text(start_el, "year") if start_el else ""

            end_el = find_el(pos, "enddate")
            end_year = get_text(end_el, "year") if end_el else ""

            is_current = pos.get("current", "no") == "yes"

            loc_parts = [p for p in [city, state, country] if p]
            location_str = ", ".join(loc_parts)

            position_data = {
                "title": title,
                "orgname": orgname,
                "location": location_str,
                "start_year": start_year,
                "end_year": end_year,
                "current": is_current,
            }
            data["positions"].append(position_data)

            # Use the current position for the header
            if is_current or (not data["position"] and not end_year):
                data["position"] = title
                org_loc_parts = [p for p in [orgname, city, state, country] if p]
                data["organization"] = orgname
                data["location"] = ", ".join(org_loc_parts)

    # If no current position found, use the first one
    if not data["position"] and data["positions"]:
        p = data["positions"][0]
        data["position"] = p["title"]
        data["organization"] = p["orgname"]
        data["location"] = ", ".join(
            [pp for pp in [p["orgname"], p["location"]] if pp])

    # Education
    edu = find_el(root, "education")
    if edu is not None:
        for degree in find_all_el(edu, "degree"):
            org_el = find_el(degree, "organization")
            orgname = get_text(org_el, "orgname") if org_el else ""
            city = get_text(org_el, "city") if org_el else ""
            state = get_text(org_el, "stateorprovince") if org_el else ""
            country = get_text(org_el, "country") if org_el else ""

            degreetype = degree.get("degreetype", "")
            degreename = degree.get("degreename", "")

            end_el = find_el(degree, "enddate")
            end_year = get_text(end_el, "year") if end_el else ""

            major = get_text(degree, "major")

            loc_parts = [p for p in [city, state, country] if p]

            data["degrees"].append({
                "institution": orgname,
                "location": ", ".join(loc_parts),
                "degree": degreename or degreetype,
                "year": end_year,
                "field": major,
            })

    # Contributions (publications)
    contrib = find_el(root, "contributions")
    if contrib is not None:
        for citations_group in find_all_el(contrib, "citations"):
            group_name = citations_group.get("group", "Publications")
            pubs = []
            for citation in find_all_el(citations_group, "citation"):
                title = get_text(citation, "title")
                date = get_text(citation, "displaydate")

                # Contributors
                authors = []
                contribs_el = find_el(citation, "contributors")
                if contribs_el is not None:
                    for c in find_all_el(contribs_el, "contributor"):
                        if c.text:
                            authors.append(c.text.strip())

                # External IDs
                doi = ""
                pmid = ""
                extids = find_el(citation, "externalids")
                if extids is not None:
                    for eid in find_all_el(extids, "externalid"):
                        eid_type = eid.get("type", "")
                        if eid.text:
                            if eid_type == "doi":
                                doi = eid.text.strip()
                            elif eid_type == "pmid":
                                pmid = eid.text.strip()

                # Journal info
                journal_name = ""
                volume = ""
                issue = ""
                page = ""
                journal_el = find_el(citation, "journal")
                if journal_el is not None:
                    journal_name = get_text(journal_el, "journalname")
                    volume = get_text(journal_el, "volume")
                    issue = get_text(journal_el, "issue")
                    page = get_text(journal_el, "page")

                # Build formatted citation string
                parts = []
                if authors:
                    parts.append(", ".join(authors) + ".")
                if title:
                    parts.append(f"({date}) {title}." if date else f"{title}.")
                if journal_name:
                    jstr = journal_name
                    if volume:
                        jstr += f" {volume}"
                        if issue:
                            jstr += f"({issue})"
                    if page:
                        jstr += f":{page}"
                    parts.append(jstr + ".")
                if doi:
                    parts.append(f"doi:{doi}")
                elif pmid:
                    parts.append(f"PMID:{pmid}")

                formatted = " ".join(parts) if parts else title
                pubs.append(formatted)

            if pubs:
                data["citation_groups"].append({
                    "name": group_name,
                    "publications": pubs,
                })

    # Statements (synergistic activities)
    stmts = find_el(root, "statements")
    if stmts is not None:
        for stmt in find_all_el(stmts, "statement"):
            annotation = get_text(stmt, "annotation")
            if annotation:
                data["activities"].append(annotation)

    return data


class BiosketchDocTemplate(BaseDocTemplate):
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
                                 "DOE Biosketch")
        canvas.drawRightString(width - 0.75 * inch, doc.pagesize[1] - 0.5 * inch,
                               "OMB-3145-0279 and 1910-0400")

        # Footer
        canvas.setFont("Times-Roman", 9)
        canvas.drawString(0.75 * inch, 0.4 * inch, "SCV DOE Biosketch v.2025-1")
        page_num = canvas.getPageNumber()
        canvas.drawRightString(width - 0.75 * inch, 0.4 * inch,
                               f"Page {page_num} of %(total)s" %
                               {"total": self.total_pages_holder[0]})
        canvas.restoreState()


def build_elements(data):
    """Build fresh flowable elements (must be called fresh each pass)."""
    styles = getSampleStyleSheet()
    st = {
        "title": ParagraphStyle("BioTitle", parent=styles["Normal"],
                                fontName="Times-Bold", fontSize=12,
                                alignment=TA_CENTER, spaceAfter=6),
        "section": ParagraphStyle("Section", parent=styles["Normal"],
                                  fontName="Times-Bold", fontSize=10,
                                  spaceBefore=12, spaceAfter=6),
        "body": ParagraphStyle("Body", parent=styles["Normal"],
                               fontName="Times-Roman", fontSize=10,
                               leading=13, spaceAfter=4),
        "ident": ParagraphStyle("Ident", parent=styles["Normal"],
                                fontName="Times-Roman", fontSize=10,
                                leading=13, spaceBefore=2, spaceAfter=2),
    }
    page_width = letter[0] - 1.5 * inch
    elements = []

    def rule():
        t = Table([[""]], colWidths=[page_width], rowHeights=[1])
        t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 1, colors.black)]))
        return t

    # Title
    elements.append(Paragraph("<b>BIOGRAPHICAL SKETCH</b>", st["title"]))

    # Identification
    elements.append(rule())
    elements.append(Paragraph(f"*NAME: {data['name']}", st["ident"]))
    elements.append(rule())
    elements.append(Paragraph(f"*POSITION TITLE: {data['position']}", st["ident"]))
    elements.append(rule())
    elements.append(Paragraph(
        f"*ORGANIZATION AND LOCATION: {data['location']}", st["ident"]))
    elements.append(rule())

    # Education/Training
    if data["degrees"]:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "<b><u>Education/Training</u></b>", st["section"]))
        hdr = ParagraphStyle("eh", fontName="Times-Bold", fontSize=9,
                             alignment=TA_CENTER)
        cell = ParagraphStyle("ec", fontName="Times-Roman", fontSize=9,
                              alignment=TA_CENTER)
        edu_rows = [[
            Paragraph("<b>Institution and Location</b>", hdr),
            Paragraph("<b>Degree<br/>(if applicable)</b>", hdr),
            Paragraph("<b>Completion<br/>Date</b>", hdr),
            Paragraph("<b>Field of Study</b>", hdr),
        ]]
        for deg in data["degrees"]:
            inst_loc = deg["institution"]
            if deg["location"]:
                inst_loc += f", {deg['location']}"
            edu_rows.append([
                Paragraph(inst_loc, cell),
                Paragraph(deg["degree"], cell),
                Paragraph(deg["year"], cell),
                Paragraph(deg["field"], cell),
            ])
        edu_table = Table(edu_rows,
                          colWidths=[2.5 * inch, 1.2 * inch, 1.0 * inch,
                                     page_width - 4.7 * inch])
        edu_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        elements.append(edu_table)

    # Professional Appointments
    if data["positions"]:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "<b><u>Professional Appointments</u></b>", st["section"]))
        for pos in data["positions"]:
            dr = pos["start_year"]
            if pos["current"] or not pos["end_year"]:
                dr += "-present"
            elif pos["end_year"]:
                dr += f"-{pos['end_year']}"
            org_parts = [pos["orgname"]]
            if pos["location"]:
                org_parts.append(pos["location"])
            elements.append(Paragraph(
                f"{dr}  {pos['title']}, {', '.join(org_parts)}", st["body"]))

    # Publications
    for group in data["citation_groups"]:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            f"<b><u>Publications: {group['name']}</u></b>", st["section"]))
        for i, pub in enumerate(group["publications"], 1):
            elements.append(Paragraph(f"{i}. {pub}", st["body"]))

    # Synergistic Activities
    if data["activities"]:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "<b><u>Synergistic Activities</u></b>", st["section"]))
        for i, activity in enumerate(data["activities"], 1):
            elements.append(Paragraph(f"{i}. {activity}", st["body"]))

    return elements


def build_pdf(data, output_path):
    """Build the PDF with two passes for correct page count."""
    total_pages = [1]

    doc1 = BiosketchDocTemplate(output_path, total_pages, pagesize=letter,
                                title="DOE Biographical Sketch")
    doc1.build(build_elements(data))
    total_pages[0] = doc1.page

    doc2 = BiosketchDocTemplate(output_path, total_pages, pagesize=letter,
                                title="DOE Biographical Sketch")
    doc2.build(build_elements(data))

    return doc2.page


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
    num_pages = build_pdf(data, output_path)

    print(f"Generated {output_path}")
    print(f"  {len(data['degrees'])} education entries")
    print(f"  {len(data['positions'])} positions")
    pubs = sum(len(g["publications"]) for g in data["citation_groups"])
    print(f"  {pubs} publications")
    print(f"  {len(data['activities'])} synergistic activities")
    print(f"  {num_pages} pages")


if __name__ == "__main__":
    main()
