# Tools

## [tsvFromPg.sh](programs/tsvFromPg.sh)

Shell script to read the postgres SQL export and deliver all tables as TSV.

## [make.py](programs/make.py)

Python script to carry out the organizing and production of data and metadata.

## [convertPlain.ipynb](programs/convertPlain.ipynb)

Jupyter notebook that also converts the manifestations from PageXML files
to Text-Fabric. The actual conversion code is in Text-Fabric itself:
[pagexml.py](https://github.com/annotation/text-fabric/blob/master/tf/convert/pagexml.py).
The notebook is for documentation and debugging purposes.

## [watm.py](programs/watm.py)

Python library to converst the TF data to JSON files to be ingested in
*TextRepo* and *AnnoRepo*.

## [watmFromTf.ipynb](programs/watmFromTf.ipynb)

Jupyter Notebook to run the `watm.py` script. It will also test the result for
M95 exhaustively. 
The notebook is for documentation and debugging purposes.
