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
