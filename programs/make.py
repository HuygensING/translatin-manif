import sys
import collections
import re
from csv import reader

from openpyxl import load_workbook
from zipfile import ZipFile

from tf.core.helpers import console
from tf.core.files import (
    baseNm,
    dirNm,
    splitExt,
    replaceExt,
    abspath,
    isFile,
    dirContents,
    readYaml,
    writeYaml,
    expanduser as ex,
    unexpanduser as ux,
    initTree,
    getCwd,
    chDir,
    dirRemove,
    getLocation,
)

# from tf.app import use
from tf.convert.pagexml import PageXML

# from tf.advanced.helpers import dm

from watm import WATMS


HELP = """Transport and transform the translatin data.

USAGE

python make.py tasks

Transports data and metadata from the source location and produces
the next stages of processed data: TF and WATM.

The source data is supposed to be in ~/local/translatin.
It should contain delivery directories with zipfiles in it and a directory metadata.

All manifestations that are both present in a delivery and have an entry in the metadata
will be transported.

The metadata in the files will be merged/overridden by the metadata in the database.

The zip files will be unpacked and their contents sorted and stored in this the
directory "organized" in this repo (which is not synchronized with GitLab) and then
under source and then the source version and then in a subfolder named by the
manifestation acronym, lowercased.

After the sync, you might want to store this "organized" folder on a
file server of the HuC, over VPN with the command:

rsync -va . user@subdomain.diginfra.net:/data/translatin/scan/

For details, see the internal repositorys
https://code.huc.knaw.nl/tt/translatin/-/blob/main/source.yaml .

FLAGS

--help
    Print this help text

TASKS

meta
    Get all metadata organized
data
    Get all data organized
tf
    Produce text-fabric data
watm
    Produce text/anno repo data
organize
    Shorthand for: meta data
produce
    Shorthand for: tf watm
all
    Shorthand for: organize produce

--metaskip
    Skip the compilation of the metadata, assume there is a file manifestations.yaml

--metaonly
    Only compile the metadata
"""

TASKS = set(
    """
    meta
    data
    tf
    watm
""".strip().split()
)

CONFIG_FILE = "config.yaml"

META_FILES = {"metadata.xml", "mets.xml"}

TXT_EXTENSIONS = {
    f".{x}"
    for x in """
    xml
""".strip().split()
}

IMG_EXTENSIONS = {
    f".{x}"
    for x in """
    jpg
    jpeg
    png
    tif
    tiff
    eps
""".strip().split()
}

NONE = "unspecified"

ALFA_NUM = re.compile(r"""^(.*?)([0-9]+)$""")

MAN_RE = re.compile(r"""^(M[0-9]+)""", re.I)
EMAIL_RE = re.compile(r"""@\w[\w_+-]*\.[\w_+-.]*""")
METADATA_RE = re.compile(r"""<Metadata>.*?</Metadata>""", re.S)
EMAIL_OBFUSCATED = "@undisclosed"


def emailRepl(match):
    return EMAIL_RE.sub(EMAIL_OBFUSCATED, match.group(0))


def emailObfuscate(path, metaOnly=False):
    with open(path) as fh:
        text = fh.read()
    with open(path, "w") as fh:
        fh.write(
            METADATA_RE.sub(emailRepl, text)
            if metaOnly
            else EMAIL_RE.sub(EMAIL_OBFUSCATED, text)
        )


def parseFileName(path, metaFiles):
    file = baseNm(path).lower()

    if file in META_FILES:
        return ("meta", file)

    (bare, ext) = splitExt(file)

    num = bare.split("_", 1)[0]

    if num.isascii() and num.isdecimal():
        file = f"{num}{ext}"
        kind = (
            "scan"
            if ext in IMG_EXTENSIONS
            else "page"
            if ext in TXT_EXTENSIONS
            else "supplementary"
        )
    else:
        kind = "supplementary"

    return (kind, file)


def getContent(xml, elem):
    pattern = re.compile(rf"""<\s*{elem}\b[^>]*>(.*?)<\s*/\s*{elem}\s*>""", re.S)
    match = pattern.search(xml)

    if match:
        return match.group(1)

    return None


def readTsv(table, file, tables):
    with open(file, newline="") as fh:
        dataReader = reader(fh, delimiter="\t", quotechar='"')
        headers = next(dataReader)

        if headers[0] == "id":
            kind = "main"
            data = {}
        elif headers[1].endswith("_id"):
            kind = "cross"
            table1 = headers[0].removesuffix("_id").rstrip("s") + "s"
            table2 = headers[1].removesuffix("_id").rstrip("s") + "s"
            data1 = {}
            data2 = {}
            data3 = {}
        else:
            kind = "extra"
            data = {}

        for fieldData in dataReader:
            if kind in {"main", "extra"}:
                row = {k: v for (k, v) in zip(headers[1:], fieldData[1:])}
                eId = fieldData[0]
                data[eId] = row
            elif kind == "cross":
                id1 = fieldData[0]
                id2 = fieldData[1]
                row = {k: v for (k, v) in zip(headers[2:], fieldData[2:])}
                data1.setdefault(id1, set()).add(id2)
                data2.setdefault(id2, set()).add(id1)
                data3[(id1, id2)] = row

        if kind == "main":
            tables[kind][table] = data
        elif kind == "extra":
            (mainTable, field) = table.split("_", 1)
            mainTable = mainTable.rstrip("s") + "s"
            tables[kind][(mainTable, field)] = data
        elif kind == "cross":
            tables[kind][(table1, table2)] = data1
            tables[kind][(table2, table1)] = data2
            tables[kind][(table1, table2, "rest")] = data3


def readSheet(table, fileName):
    wb = load_workbook(fileName, data_only=True)
    ws = wb.active

    (headRow, *rows) = list(ws.rows)
    rows = [row for row in rows if any(c.value for c in row)]
    seen = set()
    header = {}

    good = True

    for i, cell in enumerate(headRow):
        field = cell.value
        if field in seen:
            console(f"""\tduplicate column name "{field}" """)
            good = False
        else:
            seen.add(field)
            header[i] = field

    if not good:
        return (None, None, None)

    data = {}

    ids = set()

    idField = header[0]
    nFields = len(header)

    for r, row in enumerate(rows):
        thisId = row[0].value
        if thisId in ids:
            console(f"Repeated value for {table}:{idField} '{thisId}' at row {r + 1}")
            good = False
            continue
        ids.add(thisId)

        values = {}

        for i in range(1, nFields):
            value = row[i].value
            if value is not None and value != "":
                values[header[i].lower().replace(" ", "_")] = value

        data[thisId] = values

    if not good:
        return (None, None, None)

    return (data, len(header), len(data))


class Make:
    def __init__(self):
        programsDir = dirNm(abspath(__file__))

        self.programsDir = programsDir

        self.good = True

        configFile = f"{programsDir}/{CONFIG_FILE}"
        cfg = readYaml(asFile=configFile)
        self.cfg = cfg

        locations = cfg.locations
        sourceVersion = cfg.sourceVersion
        repoBase = locations.repoBase
        localBase = f"{repoBase}/local"
        locations.localBase = localBase

        for k, v in locations.items():
            locations[k] = ex(v)

        repoBase = locations.repoBase
        localBase = locations.localBase

        (backend, org, repo, relative) = getLocation(targetDir=repoBase)
        self.backend = backend
        self.org = org
        self.repo = repo

        if not len(cfg):
            console(f"Missing config: {ux(configFile)}", error=True)
            self.good = False
            return

        metadataSpecs = cfg.metadata

        if not len(metadataSpecs):
            console(f"Missing metadata specs in {ux(configFile)}", error=True)
            self.good = False
            return

        mFile = metadataSpecs.file

        if not mFile:
            console(f"Missing metadata spec 'file' in {ux(configFile)}", error=True)
            self.good = False
            return

        metadataFiles = {mFile}
        self.metadataFile = mFile

        for mFile in metadataSpecs.otherFiles or []:
            metadataFiles.add(mFile)

        self.metadataFiles = metadataFiles

        metadataFields = set(metadataSpecs.elems or [])

        if not len(metadataFields):
            console(
                f"Metadata spec 'elems' is missing or empty in {ux(configFile)}",
                error=True,
            )
            self.good = False
            return

        self.metadataFields = metadataFields

        metadataDbFields = set(metadataSpecs.dbElems or [])

        if not len(metadataDbFields):
            console(
                f"Metadata spec 'dbElems' is missing or empty in {ux(configFile)}",
                error=True,
            )
            self.good = False
            return

        self.metadataDbFields = metadataDbFields

        if not sourceVersion:
            console("No valid source version given", error=True)
            self.good = False
            return

        self.localMetaTableDir = f"{localBase}/metadata/tables"
        self.localMetaSheetDir = f"{localBase}/metadata/sheets"
        repoMetaDir = f"{repoBase}/meta/{sourceVersion}"
        self.repoMetaDir = repoMetaDir
        self.repoMetaTableDir = f"{repoMetaDir}/tables"
        self.repoMetaSheetDir = f"{repoMetaDir}/sheets"

    def compileMetaSheets(self):
        console("Convert Excel sheets to yaml files ...")

        inDir = self.localMetaSheetDir
        outDir = self.repoMetaSheetDir
        initTree(outDir, fresh=False)
        console("Reading spreadsheets ...")

        EXCEL_RE = re.compile(r"""^transLatin_([a-z0-9_]+)\.xlsx$""", re.I)

        for f in dirContents(inDir)[0]:
            m = EXCEL_RE.match(f)
            if not m:
                continue
            name = m.group(1).lower()[0:-1]
            console(f"reading {name} ...", newline=False)
            (data, columns, rows) = readSheet(name, f"{inDir}/{f}")
            writeYaml(data, asFile=f"{outDir}/{name}.yaml")
            console(f"{columns} columns, {rows} rows")

    def compileMetaTables(self):
        inDir = self.localMetaTableDir
        outDir = self.repoMetaTableDir
        initTree(outDir, fresh=False)

        idMap = {}
        lastId = 0

        console("Sanitize postgres tsv files ...")

        for file in sorted(dirContents(inDir)[0]):
            if not file.endswith(".tsv"):
                continue

            console(f"{file} ...", newline=False)

            outRows = []

            with open(f"{inDir}/{file}", newline="") as fh:
                dataReader = reader(fh, delimiter="\t", quotechar='"')
                headers = next(dataReader)
                outRows.append(headers)

                idCols = set()

                for i, header in enumerate(headers):
                    if header.endswith("id"):
                        idCols.add(i)

                for row in dataReader:
                    values = []

                    for i, value in enumerate(row):
                        newValue = str(value)

                        if i in idCols:
                            if len(newValue) > 5:
                                newValue = idMap.get(newValue, None)
                                if newValue is None:
                                    lastId += 1
                                    idMap[value] = str(lastId)
                                    newValue = idMap[value]
                        else:
                            newValue = newValue.replace("\n", " ").replace("\t", " ")

                        values.append(newValue)

                    outRows.append(values)

            with open(f"{outDir}/{file}", "w") as fh:
                for row in outRows:
                    fh.write(("\t".join(row)) + "\n")

            console(f" {len(outRows):>5} rows")

    def compileMetaUsable(self, metaSkip=False):
        cfg = self.cfg
        langMap = cfg.langMap
        sourceTables = cfg.metadata.sourceTables
        unknownLangs = set()

        inDir = self.repoMetaTableDir
        outFileBase = self.repoMetaDir

        if metaSkip:
            inFile = f"{outFileBase}/manifestations.yaml"
            self.manifestations = readYaml(asFile=inFile)
            return

        console("Distil usable manifestation metadata into yaml files ...")

        tables = dict(main={}, cross={}, extra={})

        for table in sourceTables:
            readTsv(table, f"{inDir}/{table}.tsv", tables)

        for kind, tbs in tables.items():
            for tb in tbs:
                console(f"{kind:<10} {tb}")

        for (table, field), data in tables["extra"].items():
            mainData = tables["main"][table]

            for mId, fields in data.items():
                lang = fields.get("language", None)
                lan = langMap.get(lang, None)

                if lan is None:
                    unknownLangs.add(lang)

                for k, v in fields.items():
                    if k == "language":
                        continue
                    mainData.setdefault(mId, {})[f"{k}@{lan}"] = v

        if len(unknownLangs):
            self.good = False
            console(
                "Unknown languages:\n"
                + "".join(f"\t{lan}\n" for lan in sorted(unknownLangs))
            )
            return

        works = {}
        manifestations = {}

        for wId, wData in tables["main"]["works"].items():
            wLabel = wData["label"]
            wData = {k: v for (k, v) in wData.items() if v and k != "label"}

            eIds = tables["cross"][("works", "expressions")][wId]
            eItems = {}

            for eId in eIds:
                eData = tables["main"]["expressions"][eId]
                eLabel = eData["label"]
                eData = {k: v for (k, v) in eData.items() if v and k != "label"}

                mIds = tables["cross"][("expressions", "manifestations")][eId]
                mItems = {}

                for mId in mIds:
                    mData = tables["main"]["manifestations"][mId]
                    mLabel = mData["origin"]
                    mData = {
                        k: NONE if v is None or v == "" else v
                        for (k, v) in mData.items()
                        if k != "origin"
                    }

                    aIds = tables["cross"][("manifestations", "authors")].get(mId, None)
                    authors = (
                        NONE
                        if aIds is None
                        else [tables["main"]["authors"][aId]["name"] for aId in aIds]
                    )
                    mData["author"] = (
                        authors if type(authors) is str else ", ".join(authors)
                    )
                    pbIds = tables["cross"][("manifestations", "publishers")].get(
                        mId, None
                    )
                    publishers = (
                        NONE
                        if pbIds is None
                        else [
                            tables["main"]["publishers"][pbId]["name"] for pbId in pbIds
                        ]
                    )

                    places = []

                    if pbIds:
                        for pbId in pbIds:
                            plRow = tables["cross"][
                                ("manifestations", "publishers", "rest")
                            ][(mId, pbId)]
                            plId = plRow.get("place_id", None)
                            places.append(
                                tables["main"]["places"][plId]["name"] if plId else NONE
                            )

                    if len(places) == 0:
                        places = NONE

                    mData["publisher"] = (
                        publishers if type(publishers) is str else ", ".join(publishers)
                    )
                    mData["place"] = (
                        places if type(places) is str else ", ".join(places)
                    )
                    mItems[mLabel] = mData

                eData["manifestations"] = mItems
                eItems[eLabel] = eData

            wData["expressions"] = eItems
            works[wLabel] = wData

        for wLabel, wData in works.items():
            eItems = wData["expressions"]

            for eLabel, eData in eItems.items():
                mItems = eData["manifestations"]

                for mLabel, mData in mItems.items():
                    mData["expression"] = eLabel
                    mData["work"] = wLabel
                    manifestations[mLabel] = mData

                eData["manifestations"] = sorted(
                    mItems.keys(), key=lambda x: int(x[1:])
                )

        initTree(outFileBase, fresh=False, gentle=True)
        orderedW = {k: works[k] for k in sorted(works, key=lambda x: int(x[1:]))}
        orderedM = {
            k: manifestations[k]
            for k in sorted(manifestations, key=lambda x: int(x[1:]))
        }
        for data, name in ((orderedW, "works"), (orderedM, "manifestations")):
            outFile = f"{outFileBase}/{name}.yaml"
            writeYaml(data, asFile=outFile)
            console(f"Data written to {ux(outFile)}")

        self.manifestations = manifestations

    def organizeData(self, tasks):
        good = self.good
        if not good:
            console("Skipping 'organize data' because of an error condition")
            return

        console("Making data")

        cfg = self.cfg
        skipDocs = set(cfg.skipDocs or [])
        locations = cfg.locations
        repoBase = locations.repoBase
        srcPath = locations.localBase
        sourceVersion = cfg.sourceVersion
        manifestations = self.manifestations

        if not sourceVersion:
            console("No valid source version given", error=True)
            self.good = False
            return

        dstPath = f"{repoBase}/organized"

        initTree(dstPath, fresh=False)

        deliveryDirs = sorted(
            x for x in dirContents(srcPath)[1] if x.startswith("levering")
        )

        mans = {}
        noMeta = 0
        other = 0
        skipped = 0

        for deliveryDir in deliveryDirs:
            deliveryPath = f"{srcPath}/{deliveryDir}"
            deliveryFiles = [
                x for x in dirContents(deliveryPath)[0] if x.lower().endswith(".zip")
            ]

            for deliveryFile in deliveryFiles:
                m = MAN_RE.match(deliveryFile)

                if m:
                    man = m.group(1)
                    file = f"{deliveryPath}/{deliveryFile}"

                    if man in skipDocs:
                        skipped += 1
                        continue

                    if man in mans:
                        mans[man]["files"].append(file)
                    else:
                        meta = manifestations.get(man, None)
                        if meta is None:
                            noMeta += 1
                        else:
                            mans[man] = dict(meta=meta, files=[file])
                else:
                    other += 1

        console(f"{len(mans):>4} manifestations with metadata")
        console(f"{noMeta:>4} manifestations without metadata")
        console(f"{skipped:>4} skipped as specified in config.yaml")
        console(f"{other:>4} other zip files")

        done = 0
        failed = 0

        for man in sorted(mans, key=lambda x: int(x[1:])):
            manInfo = mans[man]
            meta = manInfo["meta"]
            title = meta.get(
                "title@la", meta.get("title@nl", meta.get("title", "no title"))
            )
            console(f"{man:<20} {title[0:40]:<40} ... ", newline=False)
            if self.organizeManifestation(sourceVersion, man, manInfo):
                done += 1
            else:
                failed += 1

        console(f"Manifestations transported: {done:>4}")
        console(f"               failed     : {failed:>4}")

    def organizeManifestation(self, version, man, manInfo):
        good = self.good
        if not good:
            console("Skipping 'organize data' because of an error condition")
            return False

        dbMeta = manInfo["meta"]
        zipPaths = manInfo["files"]

        metadataFile = self.metadataFile
        metadataFiles = self.metadataFiles
        metadataFields = self.metadataFields
        metadataDbFields = self.metadataDbFields
        cfg = self.cfg
        locations = cfg.locations
        repoBase = locations.repoBase
        dstPath = f"{repoBase}/organized"

        dstTxPath = f"{dstPath}/source"
        dstImPath = f"{dstPath}/scan"
        dstSpPath = f"{dstPath}/supplementary"
        dstRela = f"{man}/{version}"

        dstTxDir = f"{dstTxPath}/{dstRela}"
        dstImDir = f"{dstImPath}/{dstRela}"
        dstSpDir = f"{dstSpPath}/{dstRela}"

        curDir = getCwd()
        chDir(dstPath)

        kindBase = dict(page="source", meta="source")
        kindInter = dict(page="/page", meta="/meta")

        kinds = collections.Counter()

        for zipPath in zipPaths:
            z = ZipFile(zipPath)

            for zInfo in z.infolist():
                origPath = zInfo.filename
                if origPath.endswith("/"):
                    continue

                (kind, newPath) = parseFileName(origPath, metadataFiles)

                kinds[kind] += 1
                kBase = kindBase.get(kind, kind)
                kInter = kindInter.get(kind, "")
                path = f"{kBase}/{dstRela}{kInter}/{newPath}"
                zInfo.filename = path
                z.extract(zInfo)
                if kind in {"meta", "page"}:
                    emailObfuscate(path, metaOnly=kind == "page")

        if kinds["page"] == 0:
            dirRemove(dstTxDir)
            dirRemove(dstImDir)
            dirRemove(dstSpDir)
            console("--   no pages")
            return False

        chDir(curDir)

        metaPath = f"{dstTxDir}/meta/{metadataFile}"

        meta = {}

        if not isFile(metaPath):
            console("?? no filemeta ... ", newline=False)
        else:
            with open(metaPath) as fh:
                metaText = fh.read()

            good = True

            for fld in metadataFields:
                value = getContent(metaText, fld)
                if value is None:
                    console(f" (no {fld}) ", newline=False)
                    good = False
                    continue

                meta[fld] = value

            if not good:
                self.good = False

        for k in metadataDbFields:
            v = dbMeta.get(k, None)
            meta[k] = v or NONE

        writeYaml(meta, asFile=replaceExt(metaPath, "yaml"), sorted=True)
        console(f"{kinds['page']:>4} pages")
        return True

    def produceTf(self):
        good = self.good
        if not good:
            console("Skipping 'produce TF' because of an error condition")
            return

        cfg = self.cfg
        locations = cfg.locations
        repoBase = locations.repoBase
        sourceDir = f"{repoBase}/organized/source"
        console("Producing TF")

        P = PageXML(sourceDir, repoBase, verbose=1, source=0, tf="0.1")

        console("Converting PageXML to TF ...")

        if not P.task(convert=True, verbose=-1):
            self.good = False

        console("Precomputing and loading TF ...")

        if not P.task(load=True, verbose=-1):
            self.good = False

        console("Set up TF-app ...")

        if not P.task(app=True, verbose=1):
            self.good = False

        if not P.good:
            self.good = False

    def produceWatm(self):
        good = self.good
        if not good:
            console("Skipping 'produce WATM' because of an error condition")
            return

        backend = self.backend
        org = self.org
        repo = self.repo

        console("Producing WATM")
        W = WATMS(org, repo, backend)
        W.produce()

    def run(self, tasks):
        if "meta" in tasks:
            console("Making metadata")
            self.compileMetaSheets()
            self.compileMetaTables()

        self.compileMetaUsable(metaSkip="meta" not in tasks)

        if "data" in tasks:
            self.organizeData(tasks)

        if "tf" in tasks:
            self.produceTf()

        if "watm" in tasks:
            self.produceWatm()

        return 0 if self.good else 1


def main(cargs=sys.argv[1:]):
    if "--help" in cargs:
        console(HELP)
        return 0

    unrecognized = set()
    tasks = set()

    for carg in cargs:
        if carg == "all":
            for task in TASKS:
                tasks.add(task)
        elif carg == "organize":
            for task in ["meta", "data"]:
                tasks.add(task)
        elif carg == "produce":
            for task in ["tf", "watm"]:
                tasks.add(task)
        elif carg in TASKS:
            tasks.add(carg)
        else:
            unrecognized.add(carg)

    if len(unrecognized):
        console(HELP)
        console(f"Unrecognized arguments: {', '.join(sorted(unrecognized))}")
        return -1

    if len(tasks) == 0:
        console("Nothing to do")
        return 0

    Mk = Make()
    return Mk.run(tasks)


if __name__ == "__main__":
    sys.exit(main())
