# biosketch-skills

Agent Skills for working with scholarly biosketches and related documents. Includes Skills for working with SciENcv formats.

## Skills

### doe-biosketch-to-xml

Converts a DOE Biographical Sketch PDF into SciENcv-compatible XML (sciencv.1.3 schema). Extracts identification, education/training, professional appointments, publications, and synergistic activities from the standard DOE biosketch form.

### doe-biosketch-xml-to-pdf

Generates a DOE Biographical Sketch PDF from SciENcv 1.3 XML. Reproduces the standard DOE biosketch form layout with education table, professional appointments, publications, and synergistic activities. Requires `reportlab` (`pip install reportlab`).

### doe-cpos-to-xml

Converts a DOE Current and Pending (Other) Support PDF into SciENcv-compatible XML for upload. Extracts identification, employment, and all funding/support entries from the standard DOE C&P(O)S form and maps them to the official SciENcv XML schema.

### doe-cpos-xml-to-pdf

Generates a DOE Current and Pending (Other) Support PDF from SciENcv C&P(O)S XML. Reproduces the standard DOE C&P(O)S form layout with identification fields, project entries, person-months tables, and objectives. Requires `reportlab` (`pip install reportlab`).

### nih-biosketch-to-xml

Converts an NIH Biographical Sketch PDF into SciENcv-compatible XML (sciencv.1.3 schema). Extracts identification (including eRA Commons username), education/training, personal statement (Section A), positions/appointments/honors (Section B), contributions to science with grouped citations (Section C), and research support (Section D) from the standard NIH biosketch form.

### nih-biosketch-xml-to-pdf

Generates an NIH Biographical Sketch PDF from SciENcv 1.3 XML. Reproduces the standard NIH biosketch form layout with sections A through D: Personal Statement, Positions/Scientific Appointments/Honors, Contributions to Science (narrative descriptions with supporting citations), and Research Support. Requires `reportlab` (`pip install reportlab`).

### coauthor-coi

Generates a conflict-of-interest co-author list for grant applications. Queries NCBI My Bibliography, PubMed, ORCID, and optionally Google Scholar to find all of a researcher's publications, extracts every co-author with full names and institutional affiliations, and produces an 8-column DOE/NSF COI format TSV. Optionally enriches data from lab/group web pages to fill in missing names and affiliations.

### biosketch-review

Reviews an NIH or DOE Biographical Sketch for format compliance, completeness, and clarity. Checks against official requirements (including the new NIH format effective 01/25/2026), evaluates narrative quality, and assesses whether listed research products support the described planned efforts. Based on guidelines from [NIH](https://grants.nih.gov/grants-process/write-application/forms-directory/biosketch), [UNC Library](https://guides.lib.unc.edu/NIH-biosketch/biosketch), [Better at the Bench](https://www.betteratthebench.com/week-4-how-to-prepare-a-stellar-nih-biosketch), and [Stanford ORA](https://ora.stanford.edu/resources/disclosure-resources/department-energy-doe/doe-biosketch-resources).

## Installation

Add as a Claude Code plugin marketplace:

```
/plugin marketplace add caufieldjh/biosketch-skills
```

Then install:

```
/plugin
```

Select `biosketch-skills` from the list and follow the prompts.

## License

CC0 1.0 Universal - see [LICENSE](LICENSE) for details.
