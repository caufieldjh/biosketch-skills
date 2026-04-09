---
name: biosketch-review
description: >
  Review an NIH or DOE Biographical Sketch for format compliance, completeness,
  and clarity. Use this skill whenever the user wants feedback on a biosketch,
  asks to review or check a biosketch, wants to evaluate whether a biosketch
  meets requirements, or mentions "biosketch" together with "review", "check",
  "evaluate", "feedback", "critique", or "improve". Also trigger when the user
  asks whether their biosketch is ready for submission, or wants to know if their
  publications support their proposed research.
---

# Biosketch Review

Review an NIH or DOE Biographical Sketch PDF for format compliance, completeness,
clarity, and alignment between listed research products and described efforts.

## When this skill applies

The user has a biosketch PDF (NIH or DOE format) and wants feedback before
submission. The review covers three dimensions:

1. **Format compliance** — Does the biosketch follow official requirements?
2. **Completeness** — Are all required sections present with appropriate content?
3. **Quality** — Is the narrative clear, well-structured, and do the listed
   research products actually support the described planned efforts?

## Workflow

### Step 1: Read the biosketch

Read all pages of the provided PDF. If no PDF is specified, look in the current
working directory for biosketch files.

### Step 2: Identify the format

Determine whether this is an **NIH** or **DOE** biosketch based on:

- **NIH indicators**: Sections labeled A through D, "eRA COMMONS USER NAME",
  "Personal Statement", "Contributions to Science", OMB No. 0925-0001/0925-0002
- **DOE indicators**: "DOE Biosketch" header, "Synergistic Activities",
  "Publications" in two groups (closely related / other significant),
  OMB-3145-0279 and 1910-0400

If the format is ambiguous, ask the user.

### Step 3: Check format compliance

Read the appropriate reference file for detailed requirements:
- NIH: `references/nih-requirements.md`
- DOE: `references/doe-requirements.md`

Run through each requirement in the reference file and note any violations.

### Step 4: Check completeness

Verify all required sections are present and populated. Count entries in each
section and check against limits (e.g., NIH allows up to 5 contributions, DOE
allows up to 10 publications per group).

### Step 5: Evaluate clarity and narrative quality

Assess the writing quality of narrative sections. For NIH biosketches:

- **Personal Statement**: Does it explain why the individual is suited for the
  specific role? Is it written in first person? Does it connect training and
  experience to the proposed work?
- **Contributions to Science**: Does each contribution tell a coherent story?
  A strong contribution narrative follows an arc: introduce a problem or gap in
  the field, describe what the individual did, present the results and
  significance, and explain how this work moved the field forward. Narratives
  that merely list accomplishments without this arc are weaker.

For DOE biosketches:
- **Synergistic Activities**: Are they specific and clearly described?

### Step 6: Evaluate research product alignment

This is the most important qualitative check. The biosketch should demonstrate
that the individual's prior work equips them for the described planned efforts.

**How to assess alignment:**

1. Identify the planned efforts described in the biosketch (from the personal
   statement, contribution narratives, or research support descriptions). If
   the user has also provided a project description or aims page, use that too.

2. For each listed publication or research product, assess whether it provides
   evidence of relevant expertise. Look for:
   - **Topic alignment**: Do the publications cover topics relevant to the
     planned work? (e.g., if the biosketch describes planned microscopy
     research on snails, look for publications involving snails and/or
     microscopy)
   - **Methodology alignment**: Do the publications demonstrate the methods
     that will be used in the planned work?
   - **Role evidence**: Does the author's position in the author list
     (first author, last/senior author, middle author) suggest a meaningful
     contribution?

3. Identify gaps: Are there aspects of the planned work that have no supporting
   publications? These are areas where the individual may need collaborators or
   where reviewers may question their qualifications.

4. Identify irrelevant products: Are any listed publications unrelated to the
   proposed work? Space is limited and every product should earn its place.

### Step 7: Produce the review report

Structure the report as follows:

```
## Biosketch Review

**Format**: [NIH / DOE]
**Pages**: [count]
**Overall Assessment**: [Brief 1-2 sentence summary]

### Format Compliance

[List any violations of official requirements. Reference specific rules.
If no violations, say "No format compliance issues found."]

### Completeness

[Checklist of required sections with status. Note missing or underpopulated
sections. Note if entry counts are at or near limits.]

### Clarity and Narrative Quality

[Section-by-section assessment of writing quality. Note strengths and areas
for improvement. Be specific — quote passages that are strong or weak and
explain why.]

### Research Product Alignment

[Analysis of how well the listed publications support the described planned
efforts. Identify:
- Strong alignments (publications that directly support the planned work)
- Gaps (planned work areas with no publication support)
- Potentially irrelevant products (publications that don't connect to the
  planned work and could be replaced with more relevant ones)]

### Recommendations

[Prioritized list of specific, actionable improvements. Most critical items
first. Group into:
1. **Must fix** — format violations or missing required content
2. **Should fix** — completeness or alignment issues
3. **Consider** — quality improvements and strategic suggestions]

### Sources

This review was informed by the following official resources and guides:
- NIH Biosketch Format Page: https://grants.nih.gov/grants-process/write-application/forms-directory/biosketch
- NIH Biosketch FAQs: https://grants.nih.gov/faqs#/biosketches.htm
- "How to Prepare a Stellar NIH Biosketch" (Better at the Bench): https://www.betteratthebench.com/week-4-how-to-prepare-a-stellar-nih-biosketch
- UNC Library NIH Biosketch Guide: https://guides.lib.unc.edu/NIH-biosketch/biosketch
- Stanford ORA DOE Biosketch Resources: https://ora.stanford.edu/resources/disclosure-resources/department-energy-doe/doe-biosketch-resources
- "How to Update Your NIH Biosketch Using SciENcv" (McAllister & Quinn): https://jm-aq.com/how-to-update-your-nih-biosketch-using-sciencv-what-you-need-to-know-for-2026/
- Northwestern Galter Library SciENcv Guide: https://libguides.galter.northwestern.edu/SciENcv
- UW Health Sciences Library SciENcv/NIH Guide: https://guides.lib.uw.edu/hsl/sciencv/nih
```

## Important considerations

- **Be constructive, not discouraging.** The goal is to help the user improve
  their biosketch, not to find fault. Frame issues as opportunities.
- **Be specific.** Don't say "the personal statement could be stronger" —
  explain what's missing and suggest concrete improvements.
- **Distinguish requirements from best practices.** Format violations are
  objective problems; narrative quality is subjective. Make clear which feedback
  is based on official rules and which is based on best practice guidance.
- **Ask for context if needed.** If the user hasn't described the proposed
  project, ask — the alignment analysis is much more useful with that context.
- **Note format version.** For NIH biosketches, the new format (effective
  01/25/2026) has significant changes from the previous version. If the
  biosketch appears to use the old format, note specific items that need
  updating (e.g., citations in personal statement are no longer permitted,
  character limits now apply, ORCID is now required).
