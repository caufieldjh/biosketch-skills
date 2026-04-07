# SciENcv C&P(O)S XML Structure Reference

## Complete XML skeleton

```xml
<profile>
<identification>
<name>
<firstname>First</firstname>
<middlename>M.</middlename>
<lastname>Last</lastname>
</name>
</identification>
<employment>
<position>
<positiontitle>Job Title</positiontitle>
<organization>
<orgname>Organization Name</orgname>
<city>City</city>
<stateorprovince>State</stateorprovince>
<country>Country</country>
</organization>
<startdate>
<year>2015</year>
</startdate>
<enddate>
<year>2025</year>
</enddate>
</position>
</employment>
<funding>
<support>
<!-- Repeat this block for each project entry -->
<projecttitle>Full project title including PI info</projecttitle>
<awardnumber>Award/proposal number</awardnumber>
<supportsource>Funding source</supportsource>
<location>Primary place of performance</location>
<contributiontype>award</contributiontype>
<awardamount>500000</awardamount>
<inkinddescription/>
<overallobjectives>Full text of overall objectives paragraph.</overallobjectives>
<potentialoverlap>None</potentialoverlap>
<startdate>2025-10-01</startdate>
<enddate>2027-09-01</enddate>
<supporttype>current</supporttype>
<commitment>
<personmonth year="2026">0.36</personmonth>
<personmonth year="2027">0.36</personmonth>
</commitment>
</support>
</funding>
</profile>
```

## Element details

### `<identification>`

Contains `<name>` with child elements:
- `<firstname>` - Required. May include middle name as part of first name if no separate middle name field in PDF.
- `<middlename>` - Optional. Include only if the PDF explicitly provides a middle name or initial.
- `<lastname>` - Required.

### `<employment>`

Contains `<position>` with:
- `<positiontitle>` - The position/job title from the PDF header
- `<organization>` - Contains `<orgname>`, `<city>`, `<stateorprovince>`, `<country>`
- `<startdate>` and `<enddate>` - Optional. Contains `<year>` child element. These typically aren't shown in the DOE C&P(O)S PDF, so omit them unless the user provides this information.

### `<funding>`

Contains one or more `<support>` blocks. Each project entry in the PDF becomes one `<support>` block.

### `<support>` element children (in order)

| Element | Description | Format |
|---------|-------------|--------|
| `<projecttitle>` | Full title from PDF, including PI names in parentheses | Text |
| `<awardnumber>` | Proposal/Award Number from PDF | Text |
| `<supportsource>` | Source of Support from PDF | Text |
| `<location>` | Primary Place of Performance from PDF | Text |
| `<contributiontype>` | `award` or `inkind` | Enum, required |
| `<awardamount>` | Total amount, plain integer | Number |
| `<inkinddescription>` | Empty (`/>`) for awards, description text for in-kind | Text |
| `<overallobjectives>` | Full objectives paragraph | Text |
| `<potentialoverlap>` | Overlap statement, often "None" | Text |
| `<startdate>` | Project start, `YYYY-MM-01` format | Date |
| `<enddate>` | Project end, `YYYY-MM-01` format | Date |
| `<supporttype>` | `current` or `pending` (lowercase) | Enum |
| `<commitment>` | Container for person-month entries | Container |

### `<commitment>` children

Each row in the "Person Months per budget period" table becomes:
```xml
<personmonth year="YYYY">value</personmonth>
```

The `year` is an XML attribute. The value is the person-months number (can be decimal, e.g., `0.36`).

## Field mapping from PDF to XML

| PDF Field | XML Element |
|-----------|-------------|
| *NAME | `<identification><name>` |
| *POSITION TITLE | `<positiontitle>` |
| *ORGANIZATION AND LOCATION | `<organization>` children |
| *Proposal/Active Project Title | `<projecttitle>` |
| *Status of Support | `<supporttype>` |
| Proposal/Award Number | `<awardnumber>` |
| *Source of Support | `<supportsource>` |
| *Primary Place of Performance | `<location>` |
| *Start Date (MM/YYYY) | `<startdate>` as YYYY-MM-01 |
| *End Date (MM/YYYY) | `<enddate>` as YYYY-MM-01 |
| *Total Anticipated Amount | `<awardamount>` as plain integer |
| Person Months table | `<commitment>` with `<personmonth>` children |
| *Overall Objectives | `<overallobjectives>` |
| *Statement of Potential Overlap | `<potentialoverlap>` |

## Validation rules

1. `<contributiontype>` is the only **required** field for a valid upload. All other elements can be empty, but must be present.
2. If person-months are omitted, the `<commitment>` element can be empty, but the year must still be provided if any commitment data exists.
3. Element order within `<support>` matters - follow the order shown in the skeleton above.
