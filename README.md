# TransLatin data

## About

This repo contains processed data of documents produced by the

[Translatin](https://www.huygens.knaw.nl/en/projecten/translatin-2/)
project, the purpose of which is to study

> the transnational impact of Latin drama from the early modern Netherlands, a
qualitative and computational analysis.

The following employees are involved preparing the data for the project:

*   [Jan Bloemendal](https://www.huygens.knaw.nl/en/medewerkers/jan-bloemendal-2/)
*   [Jirsi Reinders](https://www.huygens.knaw.nl/en/medewerkers/jirsi-reinders-2/)
*   [Team-Text](https://di.huc.knaw.nl/tekstanalyse-nl.html)
    is involved in preparing the resulting data for the use by researchers and
    the general public:

    *   Hennie Brugman (management of requirements and solutions)
    *   Hayco de Jong (source preparation and middleware)
    *   Sebastiaan van Daalen (front-end)
    *   Bram Buitendijk (text plus annotations preparation and middleware)
    *   Dirk Roorda (pre-processing with Text-fabric)

    The current status of the website can be followed
    [here](https://translatin-tav.tt.di.huc.knaw.nl/).

    For more details, see [team](docs/team.md).

The Translatin documents are printed pages and are considered to be *manifestations* of
*expressions* of *works*, in the
[FRBR](https://en.wikipedia.org/wiki/Functional_Requirements_for_Bibliographic_Records)
sense.

However, the grouping of these documents into expressions and works is a matter of
interpretation, where the metadata is of vital importance.
This classification is not yet finished.

## Author (of this repo documentation)

*   [Dirk Roorda](https://pure.knaw.nl/portal/en/persons/dirk-roorda)

## Sources

The sources of Translatin, seen from the perspective of Team-Text, consist of 
several directories on an
( 🆔
[internal fileshare](https://code.huc.knaw.nl/tt/translatin2023/-/blob/main/source.yaml)
🆔) (the link only works within the KNAW/HuC network). 

There we find many zip files with page scans and corresponding PageXML data.
Besides that, there is various crucial metadata in the form of excel sheets and
postgres SQL data.

Hayco de Jong (Team-Text) has done work on the metadata with Jirsi Reinders.

*   postgres database has been set up to store the Excel sheets with metadata;
*   this database has been used to get evidence for which manifestations belong
    to which expressions, and which expressions belong to which works;
*   the outcome of this analysis has been stored in this same postgres database.

## Data description

The translatin data is divided in an unpublished part and a published part.
The unpublished part consists of the scans and pagexmls and other files that
reside on an internal fileshare.
There is no legal reason not to publish them, only reasons of practicality:

*   we are currently preparing a publishable representation of that data, and the
    results of that are in this public repo and will be used for a public website;
*   it is a lot of material, and it does not fit neatly into a git system.
*   We do not process all the material, see the overview of material kinds and sizes
    below:

where | kind | size (MB)
--- | --- | ---:
source (everything) | zip | 15,000
source (what we use) | zip | 6,800
organized | all | 5,300
organized | scans | 4,960
organized | pagexml | 324
text-fabric | tf | 68
text+annotations | json | 323

In [trans](docs/trans.md) we describe how to get the full data and produce a
publishable subset of it.

In [data](docs/data.md) we describe exactly what data resides where in this repo.

## Tool description

The tools used to ingest and process the data of the Translatin project are in the
directory
[programs](https://gitlab.huc.knaw.nl/translatin/corpus/-/tree/main/programs?ref_type=heads).

A description is in [tools](docs/tools.md).

## Data design choices

The following noteworthy choices have been made when transforming the data.

### Logical versus physical text

We make a distinction between raw text with line breaks and soft-hyphens on the one hand
and logical text on the other hand, without line breaks, and where tokens
around soft-hyphens have been joined together.

However, because of the nature of the pages, which often contain text where the line
breaks are meaningful, and because we have not seriously tried to detect meaningful
page layout regions, we stick to the raw text for display on the web.

The Text-Fabric conversion has made a feeble attempt to include logical text next to
raw text, but we only export raw text to the Text+Annotations data, and hence to the
front-end.

### Metadata richness

There is very rich metadata in the spreadsheets. It has been cleaned up and organized
into a Postgress database, but the result is still very rich.
We do not expose all metadata. This is what we do expose:

*   all metadata in the `manifestations` table; in particular this includes:
    *   multilingual titles with corresponding certainties;
*   the author names of a manifestation in a single, comma-separated string; 
*   the publisher names of a manifestation in a single, comma-separated string; 
*   the publisher places of a manifestation in a single, comma-separated string; 

We do *not* include the other details about authors and publishers.

### Undefined values

Where metadata is missing for some fields, we do not leave out the field and neither
we leave it blank. Instead we put in the literal value `unspecified`.

## Status

The project has delivered many Latin documents, consisting of thousands of
pages of text, in the form of scans and their OCRed PageXML results, as well as
extensive metadata of those texts.

### 2023-12-13

A minor update having to do with line breaks.

### 2023-12-12

We have added more metadata, changed the text-representation to physical text
instead of logical text.
The Team-Text production street has been used, from Text/AnnoRepo through Broccoli and
Brinta towards TextAnnoViz, and it works.

### 2023-12-09

So far, we have found 73 workable manifestations with scans, PageXML and metadata. 

