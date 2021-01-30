# Input for edictor is a .tsv file containing the forms
# The first column needs to be 'ID', 1-based integers
# Cognatesets IDs need to be 1-based integers

from pathlib import Path
import csv
import typing as t

import pycldf

from lexedata.util import segment_slices_to_segment_list


def forms_to_tsv(
    dataset: pycldf.Dataset,
    languages: t.Iterable[str],
    concepts: t.Iterable[str],
    cognatesets: t.Iterable[str],
    output_file: Path,
):
    # required fields
    c_cognate_cognateset = dataset["CognateTable", "cognatesetReference"].name
    c_cognate_form = dataset["CognateTable", "formReference"].name
    c_form_language = dataset["FormTable", "languageReference"].name
    c_form_concept = dataset["FormTable", "parameterReference"].name
    c_form_id = dataset["FormTable", "id"].name
    c_form_segments = dataset["FormTable", "segments"].name

    # prepare the header for the tsv output
    # the first column must be named ID and contain 1-based integer IDs
    # set header for tsv
    tsv_header = list(dataset["FormTable"].tableSchema.columndict.keys())
    # replace ID column by Original_ID if already exists
    try:
        id_column = tsv_header.index("ID")
        tsv_header[id_column] = "Original_ID"
    except ValueError:
        pass
    # ID column at first place
    tsv_header.insert(0, "ID")
    # add Cognateset ID
    if "Cognateset_ID" not in tsv_header:
        tsv_header.append("Cognateset_ID")

    # select forms and cognates given restriction of languages and concepts, cognatesets respectively
    forms = {}
    for form in dataset["FormTable"]:
        if languages:
            if form[c_form_language] in languages:
                forms[form[c_form_id]] = form
        else:
            forms[form[c_form_id]] = form
    for id, form in forms.items():
        if concepts:
            if form[c_form_concept] not in concepts:
                del forms[id]

    # load all cognates corresponding to those forms
    form_ids = list(forms.keys())
    cognates = []
    for judgement in dataset["CognateTable"]:
        if judgement[c_cognate_form] in form_ids:
            if cognatesets:
                if judgement[c_cognate_cognateset] in cognatesets:
                    cognates.append(judgement)
            else:
                cognates.append(judgement)
    del form_ids
    # get cognateset integer IDs
    all_cognatesets = {
        cognateset["ID"]: c
        for c, cognateset in enumerate(dataset["CognatesetTable"], 1)
    }

    # match segements to cognatesets for given cognates
    which_segment_belongs_to_which_cognateset: t.Dict[str, t.List[t.Set[str]]] = {}
    for j in cognates:
        if j[c_form_id] not in which_segment_belongs_to_which_cognateset:
            form = forms[j[c_cognate_form]]
            which_segment_belongs_to_which_cognateset[j[c_cognate_form]] = [
                set() for _ in form[c_form_segments]
            ]
        segments_judged = segment_slices_to_segment_list(
            segments=form[c_form_segments], judgement=j
        )
        for s in segments_judged:
            try:
                which_segment_belongs_to_which_cognateset[j["Form_ID"]][s].add(
                    j["Cognateset_ID"]
                )
            except IndexError:
                continue
    # write output to tsv
    out = csv.DictWriter(
        output_file.open("w", encoding="utf8"),
        fieldnames=tsv_header,
        delimiter="\t",
    )
    out.writeheader()
    for c, values in enumerate(which_segment_belongs_to_which_cognateset.items(), 1):
        form, judgements = values
        for s, segment_cognatesets in enumerate(judgements):
            if s == 0:
                if not segment_cognatesets:
                    out_segments = [forms[form][c_form_segments][s]]
                    out_cognatesets = [0]
                elif len(segment_cognatesets) >= 1:
                    out_segments = [forms[form][c_form_segments][s]]
                    out_cognatesets = [all_cognatesets[segment_cognatesets.pop()]]
            else:
                if out_cognatesets[-1] in segment_cognatesets:
                    pass
                elif out_cognatesets[-1] == 0 and not segment_cognatesets:
                    pass
                elif not segment_cognatesets:
                    out_segments.append("+")
                    out_cognatesets.append(0)
                else:
                    out_segments.append("+")
                    out_cognatesets.append(all_cognatesets[segment_cognatesets.pop()])
                out_segments.append(forms[form][c_form_segments][s])
        # store original form id in other field and get cogset integer id
        this_form = forms[form]
        if "ID" in this_form:
            this_form["Original_ID"] = this_form.pop("ID")
        # if there is a cogset, add its integer id. otherwise set id to 0
        this_form["Cognateset_ID"] = " ".join(str(e) for e in out_cognatesets)
        this_form[c_form_segments] = " ".join(out_segments)

        # add integer form id
        this_form["ID"] = c
        out.writerow(this_form)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Export #FormTable to tsv format for import to edictor"
    )
    parser.add_argument(
        "--metadata",
        type=Path,
        default="Wordlist-metadata.json",
        help="Path to the JSON metadata file describing the dataset (default: ./Wordlist-metadata.json)",
    )
    # TODO: set these arguments correctly
    parser.add_argument(
        "--languages",
        type=str,
        nargs="*",
        default=[],
        help="Language references for form selection",
    )
    parser.add_argument(
        "--concepts",
        type=str,
        nargs="*",
        default=[],
        help="",
    )
    parser.add_argument(
        "--cognatesets",
        type=str,
        nargs="*",
        default=[],
        help="",
    )
    parser.add_argument(
        "--output-file",
        "-o",
        type=Path,
        default="cognate.tsv",
        help="Path to the output file",
    )
    args = parser.parse_args()
    forms_to_tsv(
        dataset=pycldf.Dataset.from_metadata(args.metadata),
        languages=args.languages,
        concepts=args.concepts,
        cognatesets=args.cognatesets,
        output_file=args.output_file,
    )

# NON-RUNNING EXAMPLE NOTES FOLLOW
"""
FormTable
himmelauge, h i m m e l a u g e
himmelsauge, h i m m e l s a u g e
tão, t ã o
kitab, k i t a b

CognateTable
himmelauge,1:6,HIMMEL
himmelauge,7:10,AUGE
himmelsauge,1:6,HIMMEL
himmelsauge,8:11,AUGE
tão,1:2,TA
tão,2:3,NO
kitab,"1,3,5",KTB
kitab,"2,4",IA

CognatesetTable
HIMMEL,1
AUGE,2
TA,3
NO,4

Edictor
1	himmelsauge	h i m m e l + a u g e	1 2
2	himmelsauge	h i m m e l + s + a u g e	1 0 2
3	tão	t ã + o	3 4
4	kitab	k + i + t + a + b	5 6 5 6 5


which_segment_belongs_to_which_cognateset: Dict[FormID, List[Set[CognatesetID]]] = {}
for j in ds["CognateTable"]:
    if j["Form_ID"] not in which_segment_belongs_to_which_cognateset:
        form = forms[j["Form_ID"]]
        which_segment_belongs_to_which_cognateset[j["Form_ID"]] = [set() for _ in form["Segments"]]

    segments_judged = lexedata.util.parse_segment_slice(j["Segment_Slice"])
    for s in segments_judged:
        which_segment_belongs_to_which_cognateset[j["Form_ID"]][s].add(j["Cognateset_ID"])



{"himmelsauge": [{"HIMMEL"}, {"HIMMEL"}, {"HIMMEL"}, {"HIMMEL"}, {"HIMMEL"}, {"HIMMEL"}, set(), {"AUGE"}, {"AUGE"}, {"AUGE"}, {"AUGE"}]}

all_cognatesets = {cognateset["ID"]: c for c, cognateset in enumerate(ds["CognatesetTable"], 1)}

for form, judgements in which_segment_belongs_to_which_cognateset.items():
    for s, segment_cognatesets in enumerate(judgements):
        if s = 0:
            if not segment_cognatesets:
                out_segments = [forms[form]["Segments"][s]]
                out_cognatesets = [0]
            elif len(segment_cognatesets) >= 1:
                out_segments = [forms[form]["Segments"][s]]
                out_cognatesets = [all_cognatesets[segment_cognatesets.pop()]]
        else:
            if out_cognatesets[-1] in segment_cognatesets:
                pass
            elif out_cognatesets[-1] == 0 and not segment_cognatesets:
                pass
            elif not segment_cognatesets:
                out_segments.append("+")
                out_cognatesets.append(0)
            else:
                out_segments.append("+")
                out_cognatesets.append(all_cognatesets[segment_cognatesets.pop()])
            out_segments.append(forms[form]["Segments"][s])


{"himmelsauge": [1, 1, 1, 1, 1, 1, +, 0, +, 2, 2, 2, 2]}
{"himmelsauge": [h, i, m, m, e, l, +, s, +, a, u, g, e], [1, 0, 2]}
himmelsauge	h i m m e l + s + a u g e	1 0 2
"""
