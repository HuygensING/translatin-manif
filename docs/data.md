# Data

## The `organized` data

### Directory `source`

Folder with the PageXML data.
Organized by manifestation.
Page files named as `0`*iii*`.xml` (4-digit numbers with leading zeroes).

### Directory `scan`

Folder with all the scans.
Organized by manifestation.
Page files named as `0`*iii*`.jog` (4-digit numbers with leading zeroes).

### Directory `supplementary`

Folder with supplementary files, found in the leveringen, not being scans or PageXMLs.
Organized by manifestation.
Will be ignored in further processing.

## The [meta](meta) data

Folder with metadata from various sources.

### Directory [sheets](meta/0.1/sheets)

The information contained in the spreadsheets made by Jirsi Reinders, transformed
into YAML format. 
The keys correspond to the column names; excessively long column names have
been abbreviated, and the original long names are stored in the
file
[fields.yaml](meta/0.1/sheets/fields.yaml).

No data transformation is directly based on these sheets, we keep them for reference.

### Directory [tables](meta/0.1/tables)

The information contained in the postgres database of Hayco de Jong, which is
the result of extracting sanitized information from the Excel sheets of Jirsi.
The  database has been exported to TSV, and after that the long record identifiers have
been mapped to short integers.

### File [manifestations.yaml](meta/0.1/manifestations.yaml)

Contains the collected metadata of the manifestations. Most of it comes from the
[tables](meta/0.1/tables), a few fields come from the metadata in the
accompanying metadata files in the `source`. There are references to the
*expression* and *work* that the manifestation is part of.

We collect a lot of this metadata and include it in the Text-Fabric representation
(as features of document nodes), and from there in the Text/AnnoRepo json files.

### File [works.yaml](meta/0.1/works.yaml)
Contains the container structure of *works*, *expressions*, and *manifestations*.
It is derived, together with the `manifestations.yaml` file, from the 
[tables](meta/0.1/tables).

At the moment, this file is not input for any data transformation.

## The text-fabric data

### Directory [tf](tf)

The Text-Fabric representation of the texts, organized by manifestation.

For each manifestation we have generated a separate TF data set.
The files in the dataset are *features*. The provide values for nodes.
Nodes are numbers that stand for the tokens, lines, text-regions and pages in the
document, and there is a node for the document itself.

An overview of the nodes is in the file `otype.tf`. For example, manifestion `M6` has:

```
@node
@conversion=KNAW/HuC TeamText
@conversionTF=Dirk Roorda
@project=TransLatin
@valueType=str
@writtenBy=Text-Fabric
@dateWritten=2023-12-13T13:02:40Z

1-37464	token
37465	doc
37466-43099	line
43100-43256	page
43257-43650	region
```

And the feature `author.tf` has this content:

```
@node
@conversion=KNAW/HuC TeamText
@conversionTF=Dirk Roorda
@description=author of document; if multiple they are given separated by commas
@project=TransLatin
@valueType=str
@writtenBy=Text-Fabric
@dateWritten=2023-12-13T13:02:40Z

37465	Eligius Eucharius
```

It assigns value `Eligius Eucharius` to node `37465`, which is the document node.

In the translatin datasets, most features are like this: they contain metadata of the
document. But there are also features that contain the raw text and logical text
of all tokens, and the coordinates of the bounding boxes of lines.

Here is the beginning of feature `h.tf` (height):

```
@node
@conversion=KNAW/HuC TeamText
@conversionTF=Dirk Roorda
@description=the height of the pagexml object
@project=TransLatin
@valueType=int
@writtenBy=Text-Fabric
@dateWritten=2023-12-13T13:02:40Z

37466	48
46
47
48
67
85
90
73
128
57
```

It assigns height `48` to node `37466`, which is indeed the first line.
And then it assigns height `46` to the next node, `37467`, which is indeed the
next line, and so on.

Likewise, there are features `w.tf` for width, and `x.tf` for the left-most coordinate
of the box and `y.tf` for the top coordinate of the box.

### Directory [app](app)

*   `app`: the definition of the TF-app with which you can access the TF data.

The TF data above is put to work by a TF app, which is just a configuration document
that specifies several characteristics of the data set and options how nodes
must be displayed.

This is what enables you to say in a Jupyter Notebook:

```
A = use(
    f"translatin/data:clone",
    relative="tf/M6",
    checkout="clone",
    backend="gitlab.huc.knaw.nl,
)
```

and get programmatic acces to all ins and outs of manifestation `M6`.

You can also get a local browser interface on `M6`.

```
cd ~/gitlab.knaw.nl/translatin/corpus
tf --relative=tf/M95
```

All in all, TF is a fully decomposed representation of the textual building blocks
of the corpus. As such, it is the starting position to build new representations
of the corpus, most importantly a Text+Annotation representation that can be fed into
the tech stack of Team-Text.

## The text+annotations data

#### Directory [watm](watm)

Folder with the generated JSON files for *TextRepo* and *AnnoRepo*.
Organized by manifestation.

Two json files per manifestation, e.g.
[M6](watm/0.1/M6):

*   `text.json`: the list of all tokens in the text:

    ```
    ...
    "\n",
    "ree ",
    "cotexta ",
    "secip ",
    "ingenioli ",
    "nen ",
    "opibus ",
    "alia ",
    "moenia",
    ". ",
    "gbus ",
    "im",
    "-",
    "\n",
    "mensam ",
    "tante ",
    "matrone ",
    "gloria ",
    "intercipere ",
    "possemrque ",
    "si ",
    "cuipia",
    "-",
    "\n",
    ...
    ```

*   `anno.json`: all annotations on those tokens, which represents
    the information of the PageXML file.

    ```
    "a049834": [
    "node",
    "tf",
    37463,
    "37462-37463"
    ],
    "a049835": [
    "node",
    "tf",
    37464,
    "37463-37464"
    ],
    "a049836": [
    "attribute",
    "pagexml",
    "author=Eligius Eucharius",
    "a000000"
    ],
    "a049837": [
    "attribute",
    "pagexml",
    "ceneton_scan=unspecified",
    "a000000"
    ],
    ```

For more details, see the [watm.ipynb](programs/watm.ipynb) notebook.


