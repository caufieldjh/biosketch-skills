# SciENcv 1.3 Biosketch XML Structure Reference

Schema: `sciencv.1.3.xsd` at https://api.ncbi.nlm.nih.gov/sciencv/schema/sciencv.1.3.xsd

## Complete XML skeleton

```xml
<?xml version="1.0" encoding="UTF-8"?>
<profile xmlns="http://www.ncbi.nlm.nih.gov/sciencv">
<identification>
  <name current="yes">
    <givennames>John</givennames>
    <surname>Smith</surname>
  </name>
</identification>
<education>
  <degree degreetype="PhD" degreestatus="complete">
    <organization>
      <orgname>University Name</orgname>
      <city>City</city>
      <stateorprovince>State</stateorprovince>
      <country>Country</country>
    </organization>
    <enddate>
      <year>2010</year>
    </enddate>
    <major>Field of Study</major>
  </degree>
</education>
<employment>
  <position current="yes">
    <positiontitle>Job Title</positiontitle>
    <organization>
      <orgname>Organization Name</orgname>
      <city>City</city>
      <stateorprovince>State</stateorprovince>
      <country>United States</country>
    </organization>
    <startdate>
      <year>2020</year>
    </startdate>
  </position>
  <position current="no">
    <positiontitle>Previous Title</positiontitle>
    <organization>
      <orgname>Previous Org</orgname>
      <city>City</city>
      <stateorprovince>State</stateorprovince>
      <country>United States</country>
    </organization>
    <startdate>
      <year>2015</year>
    </startdate>
    <enddate>
      <year>2020</year>
    </enddate>
  </position>
</employment>
<funding/>
<contributions>
  <citations group="Most closely related to the proposed project">
    <citation type="journal">
      <title>Title of the article</title>
      <displaydate>2024</displaydate>
      <contributors>
        <contributor type="author">Smith J</contributor>
        <contributor type="author">Jones A</contributor>
      </contributors>
      <externalids>
        <externalid type="doi">10.1234/example</externalid>
      </externalids>
      <journal>
        <journalname>Journal Name</journalname>
        <volume>15</volume>
        <issue>3</issue>
        <page>123-145</page>
      </journal>
    </citation>
  </citations>
  <citations group="Other significant publications">
    <!-- same citation structure -->
  </citations>
</contributions>
<statements>
  <statement statementtype="nsfactivity">
    <annotation>Description of synergistic activity</annotation>
  </statement>
</statements>
</profile>
```

## Element reference

### Root: `<profile>`

| Attribute | Required | Description |
|-----------|----------|-------------|
| `xmlns` | Recommended | `http://www.ncbi.nlm.nih.gov/sciencv` |
| `accession` | No | SciENcv ID, pattern `SCV[0-9]+(\.[0-9]+)?` |

Children (in order):

| Element | Required | Description |
|---------|----------|-------------|
| `<identification>` | Yes | Name and contact info |
| `<education>` | Yes | Degrees and training |
| `<employment>` | Yes | Positions held |
| `<funding>` | Yes | Awards (empty for biosketches) |
| `<distinctions>` | No | Honors and awards |
| `<contributions>` | No | Publications |
| `<statements>` | No | Synergistic activities |
| `<associates>` | No | Collaborators |

---

### `<identification>`

Children (in order):

| Element | Required | Description |
|---------|----------|-------------|
| `<id idtype="...">` | No | Identifiers (ORCID, etc.) |
| `<account accounttype="...">` | No | Account references |
| `<name current="yes/no">` | Yes (1+) | Name |
| `<gender>` | No | |
| `<birthdate>` | No | xs:date format |
| `<language>` | No | Spoken/written language |
| Contact elements | No | `<phone>`, `<mailingaddress>`, `<emailaddress>`, `<webaddress>` |

#### `<name>` children (in order):

| Element | Required | Description |
|---------|----------|-------------|
| `<salutation>` | No | e.g., "Dr." |
| `<prefix>` | No | |
| `<givennames>` | Yes | First and middle names |
| `<surname>` | Yes | Last name |
| `<suffix>` | No | e.g., "Jr.", "III" |
| `<presentedname>` | No | Display name |

**Important**: `current` attribute on `<name>` is required. Use `"yes"`.

---

### `<education>`

Contains `<degree>`, `<professionaltraining>`, and/or `<professionalaccreditation>` elements (choice, any order).

#### `<degree>` attributes:

| Attribute | Required | Values |
|-----------|----------|--------|
| `degreetype` | Yes | e.g., "PhD", "BS", "MS", "BA", "MD", "MPH" |
| `degreename` | No | Full degree name |
| `degreestatus` | No | `"complete"` or `"in process"` |
| `withhonors` | No | `"true"`, `"cum laude"`, `"summa cum laude"`, `"magna cum laude"` |

#### `<degree>` children (in order):

| Element | Required | Description |
|---------|----------|-------------|
| `<organization>` | Yes | Institution |
| `<startdate>` | No | Date type |
| `<enddate>` | No | Completion date |
| `<expecteddate>` | No | Expected completion |
| `<major>` | No (0+) | Field of study |
| `<minor>` | No (0+) | Minor field |
| `<thesistitle>` | No | |
| `<supervisors>` | No | |
| `<description>` | No | |

---

### `<employment>`

Contains `<position>` and/or `<leaveofabsence>` elements.

#### `<position>` attributes:

| Attribute | Required | Values |
|-----------|----------|--------|
| `current` | Yes | `"yes"` or `"no"` |
| `featured` | No | boolean |

#### `<position>` children (in order):

| Element | Required | Description |
|---------|----------|-------------|
| `<positiontitle>` | Yes | Job title |
| `<academicrank>` | No | |
| `<employmentstatus>` | No | |
| `<organization>` | Yes | Employer |
| `<startdate>` | No | Date type |
| `<enddate>` | No | Date type |
| `<effectivedate>` | No | |
| `<tenuredate>` | No | |
| `<description>` | No | |

---

### `<funding>`

Contains `<award>` elements. For biosketches this is typically empty (`<funding/>`).

#### `<award>` children (in order):

| Element | Required | Description |
|---------|----------|-------------|
| `<fundingsource>` | Yes | Source name (has optional `code` attribute) |
| `<awardid type="...">` | Yes | Award number (`type` attribute required) |
| `<projecttitle>` | Yes | |
| `<description>` | No | |
| `<role>` | Yes | Role on the award |
| `<principalinvestigator>` | Yes | PI info with `<stringname>` |
| `<startdate>` | No | xs:date (YYYY-MM-DD string, NOT Date type) |
| `<enddate>` | No | xs:date |
| `<amount currency="...">` | No | Award amount |
| `<renewable>` | No | |

---

### `<contributions>`

Children (in order):

| Element | Required | Description |
|---------|----------|-------------|
| `<citations group="...">` | No (0+) | Publication groups |
| `<memberships>` | No (0+) | Professional memberships |
| `<bibliographyurl>` | No | URL to full bibliography |

#### `<citations>` attributes:

| Attribute | Required | Description |
|-----------|----------|-------------|
| `group` | No | Group label, e.g., "Most closely related to the proposed project" |

#### `<citations>` children:

| Element | Required | Description |
|---------|----------|-------------|
| `<annotation>` | No | Group-level annotation text |
| `<citation type="...">` | No (0+) | Individual publications |

#### `<citation>` attributes:

| Attribute | Required | Values |
|-----------|----------|--------|
| `type` | Yes | `"journal"`, `"book"`, `"patent"`, `"presentation"`, `"meeting"`, `"dataset"`, `"software"`, `"other"` |
| `id` | No | Integer |
| `version` | No | Integer |

#### `<citation>` children (in order):

| Element | Required | Description |
|---------|----------|-------------|
| `<title>` | Yes | Article/paper title |
| `<subtitle>` | No | |
| `<displaydate>` | Yes | Publication year as string |
| `<contributors>` | Yes | Author list |
| `<externalids>` | Yes | DOI, PMID, etc. |
| `<summary>` | No | Abstract |
| `<url>` | No | Link to paper |
| `<info>` | No | Additional info |
| `<grantassociation>` | No (0+) | Associated grants |
| `<refsystem>` | No | Reference system |
| `<refuid>` | No | Reference UID |
| Type-specific element | Yes | One of: `<journal>`, `<book>`, `<patent>`, `<presentation>`, `<meeting>`, `<dataset>`, `<software>`, `<other>` |

#### `<journal>` children:

| Element | Required | Description |
|---------|----------|-------------|
| `<journalname>` | Yes | Full journal name |
| `<volume>` | No | |
| `<issue>` | No | |
| `<page>` | No | Page range, e.g., "123-145" |

#### `<contributor>` attributes:

| Attribute | Required | Values |
|-----------|----------|--------|
| `type` | Yes | `"author"`, `"editor"`, `"inventor"`, `"creator"`, `"curator"`, `"producer"`, `"cartographer"`, `"other"` |

Text content is the contributor name string (e.g., "Smith J").

#### `<externalid>` attributes:

| Attribute | Required | Description |
|-----------|----------|-------------|
| `type` | Yes | e.g., `"doi"`, `"pmid"`, `"pmc"`, `"arxiv"` |
| `authority` | No | Issuing authority |

Text content is the identifier value.

---

### `<statements>`

Contains `<statement>` elements.

#### `<statement>` attributes:

| Attribute | Required | Values |
|-----------|----------|--------|
| `statementtype` | No | `"personalstatement"`, `"bio"`, `"nsfactivity"`, `"other"` |
| `group` | No | Group label |

`<statement>` extends `Citations`, so it can contain:

| Element | Required | Description |
|---------|----------|-------------|
| `<annotation>` | No | The statement text |
| `<citation>` | No (0+) | Associated publications |

For synergistic activities, use `statementtype="nsfactivity"` and put the
activity text in `<annotation>`.

---

## Date type reference

Dates in this schema (for education, employment, distinctions) use a structured
`Date` complex type, NOT date strings:

```xml
<startdate>
  <year>2020</year>
  <month>9</month>   <!-- optional -->
  <day>1</day>        <!-- optional, requires month -->
</startdate>
```

**Exception**: `<startdate>` and `<enddate>` within `<award>` (funding section) use
`xs:date` format (YYYY-MM-DD string), not the structured Date type.

---

## Organization type reference

`<organization>` appears in many contexts (education, employment, distinctions).
The structure is always:

```xml
<organization>
  <orgname>Institution Name</orgname>
  <orgsection>Department</orgsection>    <!-- optional -->
  <city>City</city>                       <!-- optional -->
  <stateorprovince>State</stateorprovince> <!-- optional -->
  <country>Country</country>              <!-- optional -->
</organization>
```

---

## Field mapping: DOE Biosketch PDF to XML

| PDF Section | PDF Field | XML Path |
|-------------|-----------|----------|
| Header | NAME | `identification > name > givennames + surname` |
| Header | POSITION TITLE | `employment > position > positiontitle` (current) |
| Header | ORGANIZATION AND LOCATION | `employment > position > organization` (current) |
| Education/Training | Institution, Location | `education > degree > organization` |
| Education/Training | Degree | `education > degree[@degreetype]` |
| Education/Training | Completion Date | `education > degree > enddate > year` |
| Education/Training | Field of Study | `education > degree > major` |
| Professional Appointments | Position, Dates, Institution | `employment > position` |
| Publications (closely related) | Each citation | `contributions > citations[group="Most closely related..."] > citation` |
| Publications (other significant) | Each citation | `contributions > citations[group="Other significant..."] > citation` |
| Synergistic Activities | Each activity | `statements > statement[statementtype="nsfactivity"] > annotation` |
