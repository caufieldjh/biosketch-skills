# biosketch-skills

Agent Skills for working with scholarly biosketches and related documents. Includes Skills for working with SciENcv formats.

## Skills

### doe-biosketch-to-xml

Converts a DOE Biographical Sketch PDF into SciENcv-compatible XML (sciencv.1.3 schema). Extracts identification, education/training, professional appointments, publications, and synergistic activities from the standard DOE biosketch form.

### doe-cpos-to-xml

Converts a DOE Current and Pending (Other) Support PDF into SciENcv-compatible XML for upload. Extracts identification, employment, and all funding/support entries from the standard DOE C&P(O)S form and maps them to the official SciENcv XML schema.

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
