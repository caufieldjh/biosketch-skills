#!/usr/bin/env python3
"""Generate an NIH Biographical Sketch PDF from SciENcv 1.3 XML.

Produces the new Common Form layout (effective 01/25/2026). Accepts XML from
both the new and old format — if citations are embedded under contributions
or the personal statement, they are collected into the Products section.
"""

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
    """Parse the SciENcv 1.3 XML and return structured data for NIH biosketch."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    data = {
        "name": "",
        "orcid": "",
        "era_commons": "",
        "position": "",
        "organization": "",
        "location": "",
        "degrees": [],
        "positions": [],
        "distinctions": [],
        "contributions": [],
        "personal_statement": None,
        "awards": [],
    }

    # Identification
    ident = find_el(root, "identification")
    if ident is not None:
        # ORCID
        for id_el in find_all_el(ident, "id"):
            id_type = id_el.get("idtype", "")
            if id_type == "orcid" and id_el.text:
                data["orcid"] = id_el.text.strip()

        # eRA Commons
        for acct in find_all_el(ident, "account"):
            acct_type = acct.get("accounttype", "")
            if acct_type == "era" and acct.text:
                data["era_commons"] = acct.text.strip()

        name_el = find_el(ident, "name")
        if name_el is not None:
            given = get_text(name_el, "givennames")
            surname = get_text(name_el, "surname")
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
            orgname = get_text(org_el, "orgname") if org_el is not None else ""
            city = get_text(org_el, "city") if org_el is not None else ""
            state = get_text(org_el, "stateorprovince") if org_el is not None else ""
            country = get_text(org_el, "country") if org_el is not None else ""

            start_el = find_el(pos, "startdate")
            start_year = get_text(start_el, "year") if start_el is not None else ""

            end_el = find_el(pos, "enddate")
            end_year = get_text(end_el, "year") if end_el is not None else ""

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
                data["organization"] = orgname
                org_loc_parts = [p for p in [orgname, city, state, country] if p]
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
            orgname = get_text(org_el, "orgname") if org_el is not None else ""
            city = get_text(org_el, "city") if org_el is not None else ""
            state = get_text(org_el, "stateorprovince") if org_el is not None else ""
            country = get_text(org_el, "country") if org_el is not None else ""

            degreetype = degree.get("degreetype", "")
            degreename = degree.get("degreename", "")

            end_el = find_el(degree, "enddate")
            end_year = get_text(end_el, "year") if end_el is not None else ""
            end_month = get_text(end_el, "month") if end_el is not None else ""

            major = get_text(degree, "major")

            loc_parts = [p for p in [city, state, country] if p]

            completion = ""
            if end_month and end_year:
                completion = f"{end_month}/{end_year}"
            elif end_year:
                completion = end_year

            data["degrees"].append({
                "institution": orgname,
                "location": ", ".join(loc_parts),
                "degree": degreename or degreetype,
                "completion": completion,
                "field": major,
            })

    # Distinctions (honors)
    dist = find_el(root, "distinctions")
    if dist is not None:
        for d in find_all_el(dist, "distinction"):
            desc = get_text(d, "description")
            org_el = find_el(d, "organization")
            orgname = get_text(org_el, "orgname") if org_el is not None else ""
            date_el = find_el(d, "date")
            year = get_text(date_el, "year") if date_el is not None else ""
            if desc:
                data["distinctions"].append({
                    "description": desc,
                    "organization": orgname,
                    "year": year,
                })

    # Contributions (narratives + citations)
    contrib = find_el(root, "contributions")
    if contrib is not None:
        for citations_group in find_all_el(contrib, "citations"):
            group_name = citations_group.get("group", "")
            annotation = get_text(citations_group, "annotation")
            pubs = []
            for citation in find_all_el(citations_group, "citation"):
                pubs.append(_parse_citation(citation))

            data["contributions"].append({
                "name": group_name,
                "narrative": annotation,
                "citations": pubs,
            })

    # Statements (Personal Statement)
    stmts = find_el(root, "statements")
    if stmts is not None:
        for stmt in find_all_el(stmts, "statement"):
            stmt_type = stmt.get("statementtype", "")
            if stmt_type == "personalstatement":
                annotation = get_text(stmt, "annotation")
                pubs = []
                for citation in find_all_el(stmt, "citation"):
                    pubs.append(_parse_citation(citation))
                data["personal_statement"] = {
                    "text": annotation,
                    "citations": pubs,
                }
                break

    # Funding (Research Support)
    funding = find_el(root, "funding")
    if funding is not None:
        for award in find_all_el(funding, "award"):
            source = get_text(award, "fundingsource")
            award_id_el = find_el(award, "awardid")
            award_id = award_id_el.text.strip() if award_id_el is not None and award_id_el.text else ""
            project_title = get_text(award, "projecttitle")
            role = get_text(award, "role")
            description = get_text(award, "description")

            pi_el = find_el(award, "principalinvestigator")
            pi_name = get_text(pi_el, "stringname") if pi_el is not None else ""

            start = get_text(award, "startdate")
            end = get_text(award, "enddate")

            data["awards"].append({
                "source": source,
                "award_id": award_id,
                "title": project_title,
                "role": role,
                "pi": pi_name,
                "start": start,
                "end": end,
                "description": description,
            })

    return data


def _parse_citation(citation):
    """Parse a single <citation> element into a formatted string."""
    title = get_text(citation, "title")
    date = get_text(citation, "displaydate")

    authors = []
    contribs_el = find_el(citation, "contributors")
    if contribs_el is not None:
        for c in find_all_el(contribs_el, "contributor"):
            if c.text:
                authors.append(c.text.strip())

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

    parts = []
    if authors:
        parts.append(", ".join(authors) + ".")
    if title:
        parts.append(f"{title}.")
    if journal_name:
        jstr = journal_name + "."
        if date:
            jstr += f" {date}"
        if volume:
            jstr += f";{volume}"
            if issue:
                jstr += f"({issue})"
        if page:
            jstr += f":{page}"
        jstr += "."
        parts.append(jstr)
    elif date:
        parts.append(f"{date}.")
    if doi:
        parts.append(f"doi:{doi}")
    if pmid:
        parts.append(f"PMID: {pmid}")

    return " ".join(parts) if parts else title


def _collect_products(data):
    """Collect all citations into two product groups for the new Common Form.

    Returns (closely_related, other_significant) lists of formatted citation
    strings. Citations from contribution groups whose name contains "related"
    or "Contribution 1" go into closely_related; the rest go into
    other_significant. Citations from the personal statement (old format XML)
    are added to other_significant.
    """
    closely_related = []
    other_significant = []

    for contrib in data["contributions"]:
        name_lower = contrib["name"].lower()
        if ("related" in name_lower or "closely" in name_lower
                or contrib["name"] in ("Contribution 1", "Contribution 2")):
            closely_related.extend(contrib["citations"])
        else:
            other_significant.extend(contrib["citations"])

    # If all citations ended up in one bucket with none in the other,
    # split them evenly (up to 5 each)
    if closely_related and not other_significant and len(closely_related) > 5:
        other_significant = closely_related[5:]
        closely_related = closely_related[:5]
    elif other_significant and not closely_related and len(other_significant) > 5:
        closely_related = other_significant[:5]
        other_significant = other_significant[5:]

    # Personal statement citations (from old format) go to other_significant
    if data["personal_statement"] and data["personal_statement"]["citations"]:
        other_significant.extend(data["personal_statement"]["citations"])

    # Cap at 5 each per new format rules
    closely_related = closely_related[:5]
    other_significant = other_significant[:5]

    return closely_related, other_significant


class NIHBiosketchDocTemplate(BaseDocTemplate):
    """Custom document template with NIH biosketch header and footer."""

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
        canvas.setFont("Times-Roman", 8)
        canvas.drawString(0.75 * inch, doc.pagesize[1] - 0.5 * inch,
                          "OMB No. 0925-0001 and 0925-0002")
        canvas.drawRightString(width - 0.75 * inch, doc.pagesize[1] - 0.5 * inch,
                               "Biographical Sketch Format Page")

        # Footer
        canvas.setFont("Times-Roman", 9)
        page_num = canvas.getPageNumber()
        canvas.drawRightString(width - 0.75 * inch, 0.4 * inch,
                               f"Page {page_num} of %(total)s" %
                               {"total": self.total_pages_holder[0]})
        canvas.restoreState()


def build_elements(data):
    """Build fresh flowable elements in the new Common Form layout."""
    styles = getSampleStyleSheet()
    st = {
        "title": ParagraphStyle("BioTitle", parent=styles["Normal"],
                                fontName="Times-Bold", fontSize=12,
                                alignment=TA_CENTER, spaceAfter=2),
        "subtitle": ParagraphStyle("BioSubtitle", parent=styles["Normal"],
                                   fontName="Times-Roman", fontSize=8,
                                   alignment=TA_CENTER, spaceAfter=6),
        "section": ParagraphStyle("Section", parent=styles["Normal"],
                                  fontName="Times-Bold", fontSize=10,
                                  spaceBefore=10, spaceAfter=6),
        "subsection": ParagraphStyle("Subsection", parent=styles["Normal"],
                                     fontName="Times-Bold", fontSize=10,
                                     spaceBefore=6, spaceAfter=4),
        "body": ParagraphStyle("Body", parent=styles["Normal"],
                               fontName="Times-Roman", fontSize=10,
                               leading=13, spaceAfter=4),
        "ident": ParagraphStyle("Ident", parent=styles["Normal"],
                                fontName="Times-Roman", fontSize=10,
                                leading=13, spaceBefore=2, spaceAfter=2),
        "citation": ParagraphStyle("Citation", parent=styles["Normal"],
                                   fontName="Times-Roman", fontSize=10,
                                   leading=13, spaceAfter=3,
                                   leftIndent=18),
    }
    page_width = letter[0] - 1.5 * inch
    elements = []

    def rule():
        t = Table([[""]], colWidths=[page_width], rowHeights=[1])
        t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 1, colors.black)]))
        return t

    # Title
    elements.append(Paragraph("<b>BIOGRAPHICAL SKETCH</b>", st["title"]))
    elements.append(Paragraph(
        "Provide the following information for the Senior/key personnel and "
        "other significant contributors.<br/>"
        "Follow this format for each person. <b>DO NOT EXCEED FIVE PAGES.</b>",
        st["subtitle"]))

    # --- Common Form: Identifying Information ---
    elements.append(rule())
    elements.append(Paragraph(f"NAME: {data['name']}", st["ident"]))
    elements.append(rule())
    if data["orcid"]:
        elements.append(Paragraph(
            f"ORCID iD: {data['orcid']}", st["ident"]))
        elements.append(rule())
    elements.append(Paragraph(
        f"eRA COMMONS USER NAME (credential, e.g., agency login): "
        f"{data['era_commons']}", st["ident"]))
    elements.append(rule())
    elements.append(Paragraph(
        f"POSITION TITLE: {data['position']}", st["ident"]))
    elements.append(rule())

    # --- Common Form: Professional Preparation ---
    if data["degrees"]:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "<b><u>Professional Preparation</u></b>", st["section"]))
        hdr = ParagraphStyle("eh", fontName="Times-Bold", fontSize=9,
                             alignment=TA_CENTER)
        cell = ParagraphStyle("ec", fontName="Times-Roman", fontSize=9,
                              alignment=TA_CENTER)
        edu_rows = [[
            Paragraph("<b>INSTITUTION AND LOCATION</b>", hdr),
            Paragraph("<b>DEGREE<br/>(if applicable)</b>", hdr),
            Paragraph("<b>Completion<br/>Date<br/>MM/YYYY</b>", hdr),
            Paragraph("<b>FIELD OF STUDY</b>", hdr),
        ]]
        for deg in data["degrees"]:
            inst_loc = deg["institution"]
            if deg["location"]:
                inst_loc += f", {deg['location']}"
            edu_rows.append([
                Paragraph(inst_loc, cell),
                Paragraph(deg["degree"], cell),
                Paragraph(deg["completion"], cell),
                Paragraph(deg["field"], cell),
            ])
        edu_table = Table(edu_rows,
                          colWidths=[2.5 * inch, 1.0 * inch, 1.0 * inch,
                                     page_width - 4.5 * inch])
        edu_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        elements.append(edu_table)

    # --- Common Form: Appointments & Positions ---
    if data["positions"]:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "<b><u>Appointments &amp; Positions</u></b>", st["section"]))
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

    # --- Common Form: Products ---
    closely_related, other_significant = _collect_products(data)
    if closely_related or other_significant:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "<b><u>Products</u></b>", st["section"]))

        if closely_related:
            elements.append(Paragraph(
                "<b>Most closely related to the proposed project</b>",
                st["subsection"]))
            for i, pub in enumerate(closely_related, 1):
                elements.append(Paragraph(f"{i}. {pub}", st["citation"]))

        if other_significant:
            elements.append(Paragraph(
                "<b>Other significant products</b>", st["subsection"]))
            for i, pub in enumerate(other_significant, 1):
                elements.append(Paragraph(f"{i}. {pub}", st["citation"]))

    # --- NIH Supplement: Personal Statement ---
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "<b><u>Personal Statement</u></b>", st["section"]))
    if data["personal_statement"] and data["personal_statement"]["text"]:
        elements.append(Paragraph(
            data["personal_statement"]["text"], st["body"]))

    # --- NIH Supplement: Honors ---
    if data["distinctions"]:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "<b><u>Honors</u></b>", st["section"]))
        for d in data["distinctions"]:
            parts = []
            if d["year"]:
                parts.append(d["year"])
            parts.append(d["description"])
            if d["organization"]:
                parts.append(d["organization"])
            elements.append(Paragraph("  ".join(parts), st["body"]))

    # --- NIH Supplement: Contributions to Science ---
    contributions_with_narratives = [
        c for c in data["contributions"] if c["narrative"]]
    if contributions_with_narratives:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "<b><u>Contributions to Science</u></b>", st["section"]))
        for i, contrib in enumerate(contributions_with_narratives, 1):
            elements.append(Spacer(1, 4))
            elements.append(Paragraph(
                f"<b>{i}.</b> {contrib['narrative']}", st["body"]))

    # --- NIH Supplement: Research Support ---
    if data["awards"]:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "<b><u>Research Support</u></b>", st["section"]))

        ongoing = [a for a in data["awards"] if not a["end"] or
                   a["end"] >= "2024"]
        completed = [a for a in data["awards"] if a["end"] and
                     a["end"] < "2024"]

        if ongoing:
            elements.append(Paragraph(
                "<b>Ongoing Research Support</b>", st["subsection"]))
            for a in ongoing:
                _add_award_block(elements, a, st)

        if completed:
            elements.append(Paragraph(
                "<b>Completed Research Support</b>", st["subsection"]))
            for a in completed:
                _add_award_block(elements, a, st)

    return elements


def _add_award_block(elements, award, st):
    """Add a single research support entry."""
    header_parts = []
    if award["award_id"]:
        header_parts.append(award["award_id"])
    if award["source"]:
        header_parts.append(f"({award['source']})")
    header = " ".join(header_parts)

    date_range = ""
    if award["start"] or award["end"]:
        start = award["start"][:7] if award["start"] else ""
        end = award["end"][:7] if award["end"] else ""
        date_range = f"{start} - {end}"

    if header and date_range:
        elements.append(Paragraph(
            f"<b>{header}</b>    {date_range}", st["body"]))
    elif header:
        elements.append(Paragraph(f"<b>{header}</b>", st["body"]))

    if award["title"]:
        elements.append(Paragraph(award["title"], st["body"]))
    if award["role"] or award["pi"]:
        role_line = []
        if award["role"]:
            role_line.append(f"Role: {award['role']}")
        if award["pi"]:
            role_line.append(f"PI: {award['pi']}")
        elements.append(Paragraph("; ".join(role_line), st["body"]))
    if award["description"]:
        elements.append(Paragraph(award["description"], st["body"]))
    elements.append(Spacer(1, 6))


def build_pdf(data, output_path):
    """Build the PDF with two passes for correct page count."""
    total_pages = [1]

    doc1 = NIHBiosketchDocTemplate(output_path, total_pages, pagesize=letter,
                                   title="NIH Biographical Sketch")
    doc1.build(build_elements(data))
    total_pages[0] = doc1.page

    doc2 = NIHBiosketchDocTemplate(output_path, total_pages, pagesize=letter,
                                   title="NIH Biographical Sketch")
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

    closely_related, other_significant = _collect_products(data)

    print(f"Generated {output_path}")
    print(f"  {len(data['degrees'])} education entries")
    print(f"  {len(data['positions'])} positions")
    print(f"  {len(data['distinctions'])} honors/distinctions")
    print(f"  {len(closely_related)} closely related products")
    print(f"  {len(other_significant)} other significant products")
    contribs_with_narrative = sum(
        1 for c in data["contributions"] if c["narrative"])
    print(f"  {contribs_with_narrative} contribution narratives")
    print(f"  {len(data['awards'])} research support entries")
    has_ps = "yes" if data["personal_statement"] and data["personal_statement"]["text"] else "no"
    print(f"  Personal statement: {has_ps}")
    print(f"  ORCID: {data['orcid'] or 'not provided'}")
    print(f"  {num_pages} pages")


if __name__ == "__main__":
    main()
