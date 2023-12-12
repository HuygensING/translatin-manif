# TransLatin data

## About

This repo contains texts and metadata of documents produced by the

[Translatin](https://www.huygens.knaw.nl/en/projecten/translatin-2/)
project, the purpose of which is to study

> the transnational impact of Latin drama from the early modern Netherlands, a
qualitative and computational analysis.

The following employees are involved preparing the data for the project:

* [Jan Bloemendal](https://www.huygens.knaw.nl/en/medewerkers/jan-bloemendal-2/)
* [Jirsi Reinders](https://www.huygens.knaw.nl/en/medewerkers/jirsi-reinders-2/)

[Team-Text](https://di.huc.knaw.nl/tekstanalyse-nl.html)
is involved in preparing the resulting data for the use by researchers and the
general public.

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
[internal fileshare](https://code.huc.knaw.nl/tt/translatin/-/blob/main/source.yaml).

There we find many zip files with page scans and corresponding PageXML data.
Besides that, there is various crucial metadata in the form of excel sheets and
postgres SQL data.

Hayco de Jong (Team-Text) has done work on the metadata with Jirsi Reinders.

*   postgres database has been set up to store the Excel sheets with metadata;
*   this database has been used to get evidence for which manifestations belong
    to which expressions, and which expressions belong to which works;
*   the outcome of this analysis has been stored in this same postgres database.

## Process

The Translatin documents must be published on a website, and they should also be made
available in ways that are convenient for researchers and data scientists.

Team-Text is developing a pipeline that can publish small and large corpora with
efficient logistics. Here is an overview how that works, and which person is
primarily dealing with which part of the project.

*   **Dirk Roorda**

    *   has defined an
        [ingest procedure](https://gitlab.huc.knaw.nl/translatin/logic/-/blob/main/tools/ingest.py?ref_type=heads)
        which collects all metadata and a subset of the data into this Gitlab repo;
    *   uses his
        [Text-Fabric](https://github.com/annotation/text-fabric/tree/master)
        and Marijn Koolen's
        [pagexml tools](https://github.com/knaw-huc/pagexml) to produce various
        untangled versions of the texts:

        *   a text-fabric version, which can be used directly by researchers, but also
            acts as a starting format for further processing;
        *   two json files per manifestation, e.g.
            [M95](https://gitlab.huc.knaw.nl/translatin/data/-/tree/main/watm/0.1/M95?ref_type=heads):

            *   `text.json`: the list of all tokens in the text;
            *   `anno.json`: all annotations on those tokens, which represents
                the information of the PageXML file.

*   **Bram Buitendijk**

    *   picks up the `text.json` and `anno.json` files, processes them further and
        stores them in the infrastructure of Team-Text: *TextRepo* and *AnnoRepo*.

*   **Hayco de Jong**

    *   defines a pipeline from Text/Anno Repo to a web front-end called *TextAnnoViz*
        using a broker system *Broccoli*.

*   **Sebastiaan van Daalen**

    *   develops and manages *TextAnnoviz* and takes care that the website fulfills
        the end-user requirements.

*   **Henny Brugman**
    
    *   oversees the pipeline, manages requirements and resources, helps to ensure
        that individual projects can fit in the generic pipeline.

## Ingest procedure

I have defined an ingest procedure by which we get all data within reach before
processing it. It takes source data from the leveringen, and produces various
folders with data in this repo.

There is 14 GB of data there.

Do this only if you need to create a new version of the data from the
sources.

If you only want to process data, you can just use the this repo
plus the reorganized scans in the
[internal fileshare](https://code.huc.knaw.nl/tt/translatin/-/blob/main/source.yaml).

This repo has only 0.5 GB of data, and those scans are 4GB.

1.  Copy the `levering-`*i* and `metadata` directories from the internal fileshare
    to your own computer, and put them under `~/local/translatin`;

    ```
    mkdir ~/local
    cd ~/local
    scp -r you@internal.fileshare:/data/translatin .
    ```

1.  Clone this data repo to your own computer:
    
    ```
    mkdir -p ~/gitlab.huc.knaw.nl/translatin
    cd ~/gitlab.huc.knaw.nl/translatin
    git clone http://gitlab.huc.knaw.nl/translatin/data.git
    ```

1.  Clone the logic repo to your own computer:

    ```
    cd ~/gitlab.huc.knaw.nl/translatin
    git clone http://gitlab.huc.knaw.nl/translatin/logic.git
    ```

1.  Run the ingest script:

    ```
    cd ~/gitlab.huc.knaw.nl/translatin/logic/tools
    python ingest.py
    ```

    This creates the folders **source**, **supplementary**, **meta**, and **scan**
    in this repo.

    N.B. The directory **scan** will not be synced to GitLab, it is in the
    `.gitignore` file.

## Data description

### After ingest

After doing the ingest, this repo has the following folders.

#### [source](source)

Folder with the PageXML data.
Organized by manifestation.

#### **scan**

Folder with all the scans, organized as [source](source).
This folder is not online, you do not get it when you clone this repo, but you
can get it from the
[internal fileshare](https://code.huc.knaw.nl/tt/translatin/-/blob/main/source.yaml),
indicated under **Sources** above.

#### [supplementary](supplementary)

Folder with supplementary files, found in the leveringen, not being scans or PageXMLs.
Organized by manifestation.

#### [meta](meta)

Folder with subfolders `sheets` and `tables` which contain the information of
the metadata as found in the Excel sheets of Jirsi and the postgres database of Hayco.
But the representation is different:

*   the sheets are in YAML; the keys correspond to the column names; excessively long
    column names have been abbreviated, and the original long names are saved in the
    file
    [fields.yaml](https://gitlab.huc.knaw.nl/translatin/data/-/blob/main/meta/0.1/sheets/fields.yaml?ref_type=heads);
*   the postgres tables are in TSV, and have their long identifiers replaced by 
    short numbers.

### After TF conversion

#### [tf](tf) and [app](app)

*   `tf`: the Text-Fabric representation of the texts, organized by manifestation.
*   `app`: the definition of the TF-app with which you can access the TF data.

This is what enables you to say in a Jupyter Notebook:

```
A = use(
    f"translatin/data:clone",
    relative="tf/M95",
    checkout="clone",
    backend="gitlab.huc.knaw.nl,
)
```

and get programmatic acces to all ins and outs of manifestation `M95`.

You can also navigate on the commandline to the repository and say

```
tf --relative=tf/M95
```

and get a local browser interface on `M95`.

### After text/anno generation

#### [watm](watm)

Folder with the generated JSON files for *TextRepo* and *AnnoRepo*.
Organized by manifestation.

## Tool description

The tools used to ingest and process the data of the Translatin project are in the
directory
[programs](https://gitlab.huc.knaw.nl/translatin/corpus/-/tree/main/programs?ref_type=heads).

*   [tsvFromPg.sh](tools/tsvFromPg.sh?ref_type=heads)
    Shell script to read the postgres SQL export and deliver all tables as TSV.
*   [ingest.py](tools/ingest.py?ref_type=heads)
    Python script to carry out the ingest: data and metadata.
*   [convertPlain.ipynb](tools/convertPlain.ipynb?ref_type=heads)
    Jupyter notebook that converts the manifestations from PageXML files to Text-Fabric.
    The actual conversion code is in Text-Fabric itself:
    [pagexml.py](https://github.com/annotation/text-fabric/blob/master/tf/convert/pagexml.py).
*   [watm.py](tools/watm.py?ref_type=heads)
    Python script to converst the TF data to JSON files to be ingested in
    *TextRepo* and *AnnoRepo*.
*   [watmFromTf.ipynb](tools/watmFromTf.ipynb?ref_type=heads)
    Jupyter Notebook to run the `watm.py` script. It will also test the result for
    M95 exhaustively.

## Status

The project has delivered many Latin documents, consisting of thousands of
pages of text, in the form of scans and their OCRed PageXML results, as well as
extensive metadata of those texts.

### 2023-12-09

So far, we have found 73 workable manifestations with scans, PageXML and metadata. 

