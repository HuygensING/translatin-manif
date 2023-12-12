import json

from tf.core.files import initTree, dirContents, expanduser as ex
from tf.core.helpers import console
from tf.core.timestamp import DEEP
from tf.parameters import OTYPE, OSLOTS
from tf.app import use


TT_NAME = "watm"

NS_TF = "tf"
NS_PAGEXML = "pagexml"
NS_NLP = "nlp"

NS_FROM_OTYPE = dict(
    doc=NS_TF,
    token=NS_NLP,
)
NS_FROM_FEAT = dict(
    otype=NS_TF,
    doc=NS_TF,
    page=NS_TF,
    line=NS_TF,
    after=NS_TF,
    rafter=NS_TF,
    str=NS_TF,
    rstr=NS_TF,
)

KIND_NODE = "node"
KIND_EDGE = "edge"
KIND_ELEM = "element"
KIND_ATTR = "attribute"


class WATM:
    def __init__(self, app):
        self.app = app
        api = app.api
        self.L = api.L
        self.E = api.E
        self.Es = api.Es
        self.F = api.F
        self.Fs = api.Fs
        self.slotType = self.F.otype.slotType
        self.otypes = self.F.otype.all
        self.info = app.info

        Fall = api.Fall
        Eall = api.Eall
        excludedFeatures = {OTYPE, OSLOTS, "after", "str"}
        self.nodeFeatures = [f for f in Fall() if f not in excludedFeatures]
        self.edgeFeatures = [f for f in Eall() if f not in excludedFeatures]

    def makeText(self):
        F = self.F
        slotType = self.slotType

        text = []
        tlFromTf = {}

        self.text = text
        self.tlFromTf = tlFromTf

        for s in F.otype.s(slotType):
            value = F.rstr.v(s)
            if value is None:
                value = F.str.v(s) or ''
            after = F.rafter.v(s)
            if after is None:
                after = F.after.v(s) or ''
            value = f"{value}{after}"  # raw text
            # value = f"{F.str.v(s) or ''}{F.after.v(s) or ''}"  # logical text

            text.append(value)
            t = len(text) - 1
            tlFromTf[s] = t

    def mkAnno(self, kind, ns, body, target):
        """Make an annotation and return its id.

        Parameters
        ----------
        kind: string
            The kind of annotation.
        ns: string
            The namespace of the annotation.
        body: string
            The body of the annotation.
        target: string  or tuple of strings
            The target of the annotation.
        """
        annos = self.annos
        aId = f"a{len(annos):>06}"
        annos.append((kind, aId, ns, body, target))
        return aId

    def makeAnno(self):
        E = self.E
        Es = self.Es
        F = self.F
        Fs = self.Fs
        nodeFeatures = self.nodeFeatures
        edgeFeatures = self.edgeFeatures
        slotType = self.slotType
        otypes = self.otypes

        tlFromTf = self.tlFromTf

        annos = []
        text = self.text
        self.annos = annos

        wrongTargets = []

        for otype in otypes:
            isSlot = otype == slotType

            for n in F.otype.s(otype):
                if isSlot:
                    t = tlFromTf[n]
                    target = f"{t}-{t + 1}"
                    self.mkAnno(KIND_NODE, NS_TF, n, target)
                else:
                    ws = E.oslots.s(n)
                    start = tlFromTf[ws[0]]
                    end = tlFromTf[ws[-1]]
                    if end < start:
                        wrongTargets.append((otype, start, end))

                    target = f"{start}-{end + 1}"
                    aId = self.mkAnno(
                        KIND_ELEM, NS_FROM_OTYPE.get(otype, NS_PAGEXML), otype, target
                    )
                    tlFromTf[n] = aId
                    self.mkAnno(KIND_NODE, NS_TF, n, aId)

        for feat in nodeFeatures:
            ns = NS_FROM_FEAT.get(feat, NS_PAGEXML)

            for n, val in Fs(feat).items():
                t = tlFromTf.get(n, None)
                if t is None:
                    continue
                target = f"{t}-{t + 1}" if F.otype.v(n) == slotType else t
                aId = self.mkAnno(KIND_ATTR, ns, f"{feat}={val}", target)

        for feat in edgeFeatures:
            ns = NS_FROM_FEAT.get(feat, NS_PAGEXML)

            for fromNode, toNodes in Es(feat).items():
                fromT = tlFromTf.get(fromNode, None)
                if fromT is None:
                    continue
                targetFrom = (
                    f"{fromT}-{fromT + 1}" if F.otype.v(fromNode) == slotType else fromT
                )

                if type(toNodes) is dict:
                    for toNode, val in toNodes.items():
                        toT = tlFromTf.get(toNode, None)
                        if toT is None:
                            continue

                        targetTo = (
                            f"{toT}-{toT + 1}" if F.otype.v(toNode) == slotType else toT
                        )
                        target = f"{targetFrom}->{targetTo}"
                        aId = self.mkAnno(KIND_EDGE, ns, f"{feat}={val}", target)
                else:
                    for toNode in toNodes:
                        toT = tlFromTf.get(toNode, None)
                        if toT is None:
                            continue
                        target = f"{fromT}->{toT}"
                        aId = self.mkAnno(KIND_EDGE, ns, feat, target)

        if len(wrongTargets):
            print(f"WARNING: wrong targets, {len(wrongTargets)}x")
            for otype, start, end in wrongTargets:
                sega = text[start]
                segb = text[end - 1]
                print(f"{otype:>20} {start:>6} `{sega}` > {end - 1} `{segb}`")

    def writeAll(self):
        app = self.app
        text = self.text
        annos = self.annos

        repoLocation = app.repoLocation
        relative = app.context.relative
        version = app.version
        wRelative = relative.replace("/tf/", f"/{TT_NAME}/{version}/")
        resultDir = f"{repoLocation}{wRelative}"
        textFile = f"{resultDir}/text.json"
        annoFile = f"{resultDir}/anno.json"

        self.textFile = textFile
        self.annoFile = annoFile

        initTree(resultDir, fresh=True)

        with open(textFile, "w") as fh:
            json.dump(dict(_ordered_segments=text), fh, ensure_ascii=False, indent=1)

        with open(annoFile, "w") as fh:
            annoStore = {}
            for kind, aId, ns, body, target in annos:
                annoStore[aId] = (kind, ns, body, target)
            json.dump(annoStore, fh, ensure_ascii=False, indent=1)
        console(f"{len(text):>7} tokens {len(annos):>8} annos")


class WATMS:
    def __init__(self, org, repo, backend):
        self.org = org
        self.repo = repo
        self.backend = backend

        repoDir = ex(f"~/{backend}/{org}/{repo}")
        tfDir = f"{repoDir}/tf"
        docs = dirContents(tfDir)[1]
        console(f"Found {len(docs)} docs in {tfDir}")
        self.docs = docs

    def produce(self, doc=None):
        org = self.org
        repo = self.repo
        backend = self.backend
        docs = self.docs

        chosenDoc = doc

        for doc in sorted(docs, key=lambda x: (x[0], int(x[1:]))):
            if chosenDoc is not None and chosenDoc != doc:
                continue

            console(f"{doc:>5} ... ", newline=False)
            A = use(
                f"{org}/{repo}:clone",
                relative=f"tf/{doc}",
                checkout="clone",
                backend=backend,
                silent=DEEP,
            )
            WA = WATM(A)
            WA.makeText()
            WA.makeAnno()
            WA.writeAll()
