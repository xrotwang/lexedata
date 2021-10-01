"""Generate a report of homophones.

List all groups of homophones in the dataset, together with (if available) the
minimal spanning tree according to clics, in order to identify polysemies vs.
accidental homophones

"""
import typing as t
from pathlib import Path
from csv import writer

import networkx as nx
import pycldf

import lexedata.cli as cli
from lexedata.util import load_clics


def list_homophones(
    dataset: pycldf.Dataset, output: Path, logger: cli.logging.Logger = cli.logger
) -> None:
    clics = load_clics()
    # warn if clics cannot be loaded
    if not clics:
        logger.warning("Clics could not be loaded. Using an empty graph instead")
        clics = nx.Graph()

    c_id = dataset["ParameterTable", "id"].name
    try:
        c_concepticon = dataset["ParameterTable", "concepticonReference"].name
    except KeyError:
        cli.Exit.INVALID_DATASET(
            "This script requires a column concepticonReference in ParamterTable. "
            "Please run add_concepticon.py"
        )
    concepticon = {}
    for concept in dataset["ParameterTable"]:
        concepticon[concept[c_id]] = concept[c_concepticon]

    f_id = dataset["FormTable", "id"].name
    f_lang = dataset["FormTable", "languageReference"].name
    f_concept = dataset["FormTable", "parameterReference"].name
    f_form = dataset["FormTable", "form"].name

    homophones: t.DefaultDict[str, t.List] = t.DefaultDict(list)

    for form in dataset["FormTable"]:
        if form[f_form] == "-" or form[f_form] is None:
            continue
        homophones[form[f_lang]].append(form)
    output = output.open("w", encoding="utf8", newline="")
    output = writer(output, delimiter=",")
    output.writerow(["Comment", "Concepticon Status", "Form_ID", "Form", "Concepts"])
    for lang, forms in homophones.items():
        print(forms)
        for form in forms:
            meanings = tuple(form[f_concept])
            if len(meanings) == 1:
                continue
            clics_nodes = [concepticon.get(concept) for concept in meanings]
            if None in clics_nodes:
                clics_nodes = [c for c in clics_nodes if c]
                x = "(but at least one concept not found)"
            else:
                x = ""
            if len(clics_nodes) <= 1:
                output.writerow(["Unknown", x, lang, form[f_id], form[f_form], meanings])
                print("Unknown:", lang, form[f_id], form[f_form], meanings)
            elif nx.is_connected(clics.subgraph(clics_nodes)):
                output.writerow(["Connected", x, lang, form[f_id], form[f_form], meanings])
                print("Connected:", x, lang, form[f_id], form[f_form], meanings)
            else:
                output.writerow(["Unconnected", x, lang, form[f_id], form[f_form], meanings])
                print("Unconnected:", x, lang, form[f_id], form[f_form], meanings)


if __name__ == "__main__":

    parser = cli.parser(description=__doc__)
    parser.add_argument(
        "--output-file",
        help="Path to output file",
        type=Path,
        default="homophones.csv"
    )
    args = parser.parse_args()
    logger = cli.setup_logging(args)
    list_homophones(dataset=pycldf.Dataset.from_metadata(args.metadata), output=args.output_file, logger=logger)
