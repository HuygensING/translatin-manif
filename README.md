# TransLatin data

## About

This repo contains processed data of documents produced by the

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

    *   has written a few scripts that rsync the source data from an internal machine
        to a clone of this repo on your local machine. They are in the repo
        [tt/translatin](https://code.huc.knaw.nl/tt/translatin).
        One of the scripts can be used to put the organized data back to that share;
    *   has defined an
        [make procedure](https://gitlab.huc.knaw.nl/translatin/corpus/-/blob/main/programs/make.py?ref_type=heads)
        which collects all metadata and a subset of the data into this Gitlab repo;
        this material will not be tracked by git;
    *   uses his
        [Text-Fabric](https://github.com/annotation/text-fabric/tree/master)
        and Marijn Koolen's
        [pagexml tools](https://github.com/knaw-huc/pagexml) to produce various
        untangled versions of the texts:

        *   a text-fabric version, which can be used directly by researchers, but also
            acts as a starting format for further processing;
        *   two json files per manifestation, e.g.
            [M95](https://gitlab.huc.knaw.nl/translatin/corpus/-/tree/main/watm/0.1/M95?ref_type=heads):

            *   `text.json`: the list of all tokens in the text;
            *   `anno.json`: all annotations on those tokens, which represents
                the information of the PageXML file.

        The text-fabric data and json data will be tracked by git and published on
        the HuC GitLab.

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


## The internal file share

The source data is in an internal fileshare and is not public.
Employees of KNAW/HuC can access it.

The details are in an internal repo
[tt/translatin](https://code.huc.knaw.nl/tt/translatin).

Here are a few streamlined ways to work with that data.

If you just want to view data, you can use the script `getorganized.sh` from
[tt/translatin](https://code.huc.knaw.nl/tt/translatin)
to get the organized data from the internal fileshare into your local clone of this
repo.

Now you have access to all data, since the produced data is already in this public repo.

But, based on the organized data, you can reproduce Text-Fabric and Text/AnnoRepo
representations by means of the
[make.py script](programs/make.py).

If you want go a step further back, and redo the organizing of the data,
you can use the script `get.sh` from
[tt/translatin](https://code.huc.knaw.nl/tt/translatin)
to get the source data, and run the
[make.py script](programs/make.py)
to organize the data.

From this stage you can then reproduce Text-Fabric and Text/AnnoRepo
representations by means of the
[make.py script](programs/make.py).

**N.B.:**

The source data that we grab from the internal share is just a subset of the
available data. We have used the delivery files whose names start with `M`*iii*
where *iii* is a number.

Moreover, if the source does not have metadata for manifestation `M`*iii*, we 
do not fetch its zip-file.

Hence, the organized data also corresponds to a subset of the full data.

## Make

I have defined an *make* procedure to transport and transform all data.
It can doc the following tasks:

1.  Clone this repo to your own computer:
    
    ```
    mkdir -p ~/gitlab.huc.knaw.nl/translatin
    cd ~/gitlab.huc.knaw.nl/translatin
    git clone http://gitlab.huc.knaw.nl/translatin/corpus.git
    ```

1.  Run the make script:

    ```
    cd ~/gitlab.huc.knaw.nl/translatin/corpus/programs
    python ingest.py all
    ```

The make script can also accept parameters that limit its operation to a certain stage:

*   `meta`: compile the metadata
*   `data`: organize the data and combine it with the metadata
*   `tf`: produce the text-fabric data
*   `watm`: produce the Text/AnnoRepo json data

It also accepts:

*   `organize`: shorthand for `meta` and `data`
*   `produce`: shorthand for `tf` and `watm`

## Data description

### After `organize`

After doing `python make.py organize`, this repo has the folder `organized`.
This folder is not online. It has has the following subfolders.

#### [source](source)

Folder with the PageXML data.
Organized by manifestation.

#### **scan**

Folder with all the scans, organized as [source](source).

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

It also contains the files

*   `manifestations.yaml`
    Contains the collected metadata of the manifestations. Most of it comes from the
    postgres tables, a few fields come from the metadata in the accompanying metadata
    files in the source. There are references to the *expression* and *work* that the
    manifestation is part of.

*   `works.yaml`.
    Contains the container structure of *works*, *expressions*, and *manifestations*.

### After `produce`

After doing `python make.py produce`, this repo has the folders `app`, `tf`, and `watm`.

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

#### [watm](watm)

Folder with the generated JSON files for *TextRepo* and *AnnoRepo*.
Organized by manifestation.

## Tool description

The tools used to ingest and process the data of the Translatin project are in the
directory
[programs](https://gitlab.huc.knaw.nl/translatin/corpus/-/tree/main/programs?ref_type=heads).

*   [tsvFromPg.sh](programs/tsvFromPg.sh?ref_type=heads)
    Shell script to read the postgres SQL export and deliver all tables as TSV.
*   [make.py](programs/make.py?ref_type=heads)
    Python script to carry out the organizing and production of data and metadata.
*   [convertPlain.ipynb](tools/convertPlain.ipynb?ref_type=heads)
    Jupyter notebook that also converts the manifestations from PageXML files
    to Text-Fabric. The actual conversion code is in Text-Fabric itself:
    [pagexml.py](https://github.com/annotation/text-fabric/blob/master/tf/convert/pagexml.py).
    The notebook is for illustrative and debugging purposes.
*   [watm.py](tools/watm.py?ref_type=heads)
    Python library to converst the TF data to JSON files to be ingested in
    *TextRepo* and *AnnoRepo*.
*   [watmFromTf.ipynb](tools/watmFromTf.ipynb?ref_type=heads)
    Jupyter Notebook to run the `watm.py` script. It will also test the result for
    M95 exhaustively. 
    The notebook is for illustrative and debugging purposes.

## Data choices

The following noteworthy choices have been made when transforming the data.

### Logical versus physical text

The TF export contains both the raw text with line breaks and soft-hyphens as well as
a more logical text, without line breaks and with tokens around soft-hyphens being
joined together.

However, because of the nature of the pages, which often contain text where the line
breaks are meaningful, and because we have not seriously tried to detect meaningful
page layout regions, we stick to the raw text for display on the web.
The transformation from TF to WATM takes care of this.

That means that the TF data still contains both raw and logical text.

### Metadata richness

There is very rich metadata in the spreadsheets. It has been cleaned up and organized
in a postgress database, but the result is still very rich.
We do not expose all metadata. This is what we do expose:

*   all metadata in the `manifestations` table; in particular this includes:
    *   multilingual titles with corresponding certainties;
*   the author names of a manifestation in a single, comma-separated string; 
*   the publisher names of a manifestation in a single, comma-separated string; 
*   the publisher places of a manifestation in a single, comma-separated string; 

### Undefined values

Where metadata is missing for some fields, we do not leave out the field and neither
we leave it blank. Instead we put a `unspecified` literla value in.

## Status

The project has delivered many Latin documents, consisting of thousands of
pages of text, in the form of scans and their OCRed PageXML results, as well as
extensive metadata of those texts.

### 2023-12-12

We have added more metadata, changed the text-representation to physical text
instead of logical text.
The Team-Text production street has been used, from Text/AnnoRepo through Broccoli and
Brinta towards TextAnnoViz, and it works.

### 2023-12-09

So far, we have found 73 workable manifestations with scans, PageXML and metadata. 

