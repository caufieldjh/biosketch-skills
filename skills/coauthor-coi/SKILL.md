---
name: coauthor-coi
description: >
  Generate a conflict-of-interest co-author list for grant applications. Use this
  skill whenever the user wants to build a COI list, generate a co-author list,
  find collaborators for a grant application, list people they've published with,
  or mentions "conflict of interest" together with "co-author", "collaborator",
  "TSV", or "spreadsheet". Also trigger when the user asks about COI requirements
  for NSF, DOE, or NIH proposals and needs to enumerate their co-authors.
---

# Co-author Conflict of Interest List Generator

Generate a deduplicated list of all co-authors for a researcher, with full names,
institutional affiliations, and last active year, formatted as a TSV suitable for
DOE/NSF conflict-of-interest disclosure.

## When this skill applies

The user needs a list of everyone they have co-authored papers with for a grant
application COI disclosure. This typically involves:

- Extracting co-authors from all of their publications
- Resolving full given names (not just initials)
- Finding institutional affiliations for each co-author
- Producing a formatted TSV for upload or inclusion in a proposal

## Background

Federal grant applications (NSF, DOE, NIH) require disclosure of potential conflicts
of interest, including a list of all individuals the applicant has co-authored
publications with in a defined look-back period. Building this list manually is
tedious for prolific researchers. This skill automates the process by querying
publication databases and extracting structured author metadata.

The output TSV uses the standard DOE/NSF COI format with 8 columns:

| Column | Content |
|--------|---------|
| 1 | PI Last (Family) Name |
| 2 | PI First (Given) Name |
| 3 | Co-author Last (Family) Name |
| 4 | Co-author First (Given) Name |
| 5 | ORCiD ID (optional) |
| 6 | Institution (Full Name) |
| 7 | Nature of Relationship |
| 8 | Last Active (4-digit Year) |

Columns 1-2 are the PI's name (repeated on every row). Column 7 is "Co-author"
for all entries. Column 5 is left blank unless ORCID data is available.

## Workflow

### Step 1: Identify the researcher

Ask the user for:

1. **Their full name** (Last, First) — this populates columns 1-2 of every row
2. **Publication sources** — any of the following:
   - NCBI My Bibliography URL (e.g., `https://www.ncbi.nlm.nih.gov/myncbi/name/bibliography/public/`)
   - ORCID iD (e.g., `0000-0001-2345-6789`)
   - Google Scholar profile URL
   - Or just confirm their name for a PubMed author search

The more sources provided, the more complete the result. If only a name is given,
use PubMed author search as the sole source.

### Step 2: Gather publications from the bibliography source

Try each source the user provides, in this order:

**NCBI My Bibliography** (best source for initial paper list):
- Fetch the public bibliography URL with WebFetch
- Extract every publication's title, complete author list, year, and journal
- This captures the user's curated publication list including preprints

**ORCID** (good for completeness):
- Fetch `https://pub.orcid.org/v3.0/{orcid}/works` with `Accept: application/json`
- Extract work titles and external identifiers (DOIs, PMIDs)
- Use any PMIDs found to supplement the PubMed search

**Google Scholar** (often blocked):
- Attempt to fetch the profile URL with WebFetch
- Google Scholar frequently blocks automated access with CAPTCHAs
- If blocked, inform the user and move on — do not retry

### Step 3: Search PubMed for structured author data

Regardless of which bibliography sources were used, always query PubMed to get
structured author metadata (full ForeName and AffiliationInfo):

1. Search for the researcher's papers:
   ```
   https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=LastName+Initials[Author]&retmax=100&retmode=json
   ```

2. If the bibliography source provided paper titles not found by author search,
   search for those individually:
   ```
   https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term="Paper+Title"&retmode=json
   ```

3. Fetch full XML for all PMIDs found:
   ```
   https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=PMID1,PMID2,...&rettype=xml&retmode=xml
   ```
   For large PMID lists (>50), batch into groups of 50.

4. Save the XML to a file (e.g., `pubmed_authors.xml`) in the working directory.

### Step 4: Parse PubMed XML for author details

Write a Python script to parse the PubMed XML and extract, for every author on
every paper:

- `LastName`
- `ForeName` (full given name, not just initials)
- `Initials`
- `AffiliationInfo/Affiliation` (full affiliation string)
- Publication year

Build a deduplicated map keyed by `lowercase(lastname)_lowercase(initials)`. For
each unique author, keep:
- The longest/most complete ForeName seen across papers
- All affiliations (use the most recent one later)
- All publication years (to determine last active year)

Exclude the PI themselves from the co-author list.

### Step 5: Merge bibliography and PubMed data

If the bibliography source (Step 2) included papers not found in PubMed (preprints,
conference papers, etc.), those papers may have co-authors not in the PubMed data.
Add them to the co-author map using their initials as a placeholder first name.

Handle common name variants during merging:
- Same last name with shorter vs. longer initials (e.g., "Reese J" and "Reese JT"
  are likely the same person — merge under the longer form)
- Names with and without diacritics (e.g., "Köhler" vs "Kohler")

### Step 6: Enrich with research group data (optional)

Many co-authors who lack full names or affiliations in PubMed may be members of the
researcher's own group or close collaborators. To fill gaps:

1. Ask the user: "Do you have a lab/group web page or GitHub organization URL that
   lists your team members? This helps fill in full names and affiliations for
   co-authors."

2. If the user provides a URL:
   - Fetch it with WebFetch (or curl if WebFetch is blocked)
   - If it's a GitHub organization, try fetching the repo tree for files like
     `team.json`, `people.yml`, or `CONTRIBUTORS.md` that list members
   - Extract each member's full name and institutional affiliation
   - Match members to co-authors by last name to fill in ForeName and Institution

3. If the user does not have a group page, skip this step. The remaining gaps will
   be flagged in the output for manual review.

### Step 7: Normalize institution names

PubMed affiliation strings are verbose (full address with department, building,
city, state, zip, country). Clean each to just the core institution name:

1. Remove email addresses and "Electronic address:" prefixes
2. Remove leading special characters (footnote markers like `‡‡` from PubMed XML)
3. Split on commas and identify the part containing an institution keyword:
   `university`, `institute`, `laboratory`, `hospital`, `college`, etc.
4. Prefer the part that starts with the keyword (e.g., "University of X") over a
   part that merely contains it (e.g., "Department of Y, University of X")
5. Strip trailing periods, city/state/country/zip suffixes
6. Consolidate variants of the same institution (e.g., "UCLA School of Medicine"
   and "University of California at Los Angeles" should both become
   "University of California, Los Angeles")

The goal is short, recognizable institution names: "University of Pittsburgh",
not "Center for Craniofacial and Dental Genetics, Department of Oral and
Craniofacial Sciences, School of Dental Medicine, University of Pittsburgh,
Pittsburgh, PA, USA".

### Step 8: Generate the TSV

Write the output TSV file (default name: `coauthors_coi.tsv`) with:

- Header row with the 8 column names
- One row per unique co-author, sorted alphabetically by last name then first name
- Columns 1-2: PI's last and first name (same on every row)
- Columns 3-4: co-author's last and first name
- Column 5: blank (ORCiD not typically available from PubMed)
- Column 6: normalized institution name
- Column 7: "Co-author"
- Column 8: the most recent year the PI and co-author appeared on a paper together

Use tab separators. Ensure no extra whitespace or trailing tabs.

### Step 9: Report summary

Tell the user:

- Total number of unique co-authors in the TSV
- Number of papers processed
- How many co-authors have full given names (vs. initials only)
- How many co-authors have institutional affiliations
- If there are gaps, list the co-authors missing names or institutions so the user
  can fill them in manually
- Remind the user to review the output for accuracy, especially:
  - Name disambiguation (common last names like "Wang" or "Li" may incorrectly
    merge different people, or fail to merge the same person)
  - Institution currency (affiliations reflect what PubMed recorded at time of
    publication and may be outdated)

## Important considerations

- **PubMed rate limits**: NCBI E-utilities allow 3 requests/second without an API
  key, 10/second with one. Add a brief delay between batch requests if needed.
  Do not hammer the API.

- **Consortium papers**: Large consortium papers (50+ authors) are common in
  genomics and bioinformatics. Every listed author is technically a co-author.
  Include them all — the user can prune later if their agency only requires a
  look-back window (e.g., NSF requires 48 months).

- **Name disambiguation is imperfect**: Two authors with the same last name and
  overlapping initials may be different people (e.g., "Wang W" on a 2018 UCLA
  paper vs. "Wang W" on a 2024 genomics paper). Flag this risk but err on the
  side of inclusion — it's safer to list a false positive than to miss a real
  co-author.

- **Google Scholar is unreliable for automation**: It blocks most automated
  fetches. Don't spend time retrying or working around CAPTCHAs. PubMed is
  the authoritative source.

- **Preprints may not be in PubMed**: Papers on bioRxiv, medRxiv, or arXiv may
  appear in the user's bibliography but lack PubMed records. The bibliography
  source (NCBI My Bibliography) typically includes these, so they'll contribute
  co-author names (with initials only). The user may need to manually add full
  names for co-authors who only appear on preprints.

## Common pitfalls

- **Fetching too few PubMed records**: The default `retmax` for esearch is 20.
  Always set `retmax=100` or higher. If the researcher has more than 100 papers,
  paginate with `retstart`.

- **Missing the PI's own name variants**: The PI may appear as "Smith JH" on
  some papers and "Smith J" on others. Exclude all variants from the co-author
  list. Ask the user for their initials as they appear on papers.

- **Splitting efetch into batches**: PubMed efetch can handle ~200 IDs per
  request. For very prolific authors, split into batches to avoid timeouts.

- **Affiliation assigned to wrong author**: In PubMed XML, `<AffiliationInfo>`
  is a child of `<Author>`, so it's correctly associated. But some older records
  have a single affiliation at the article level. In that case, the affiliation
  applies to all authors — use it as a fallback.

- **Unicode in names**: Author names may contain diacritics (ü, é, ö, etc.).
  Preserve them in the output. When building lookup keys, normalize to ASCII
  for matching but keep the original form for display.
