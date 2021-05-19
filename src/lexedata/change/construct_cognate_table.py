""" Add a CognateTable to the dataset.

If the dataset has a CognateTable, do nothing.
If the dataset has no cognatesetReference column anywhere, add an empty CognateTable.
If the dataset has a cognatesetReference in the FormTable, extract that to a separate cognateTable, also transferring alignments if they exist.
If the dataset has a cognatesetReference anywhere else, admit you don't know what is going on and die.
"""

import pycldf
from lexedata.util import cache_table
from lexedata import cli


def add_explicit_cognateset_table(dataset: pycldf.Wordlist) -> None:
    if "CognatesetTable" in dataset:
        return
    dataset.add_component("CognatesetTable")

    c_cognateset = dataset["CognateTable", "cognatesetReference"].name

    cognatesets = set()
    for judgement in dataset["CognateTable"]:
        cognatesets.add(c_cognateset)

    dataset.write(CognatesetTable=[{"ID": id for id in sorted(cognatesets)}])


def add_cognate_table(
    dataset: pycldf.Wordlist, logger: cli.logging.Logger = cli.logger
) -> None:
    if "CognateTable" in dataset:
        return
    dataset.add_component("CognateTable")

    # TODO: Check if that cognatesetReference is already a foreign key
    # elsewhere, because then we need to transfer that knowledge.

    # Load anything that's useful for a cognate set table: Form IDs, segments,
    # segment slices, cognateset references, alignments
    columns = {
        "id": dataset["FormTable", "id"].name,
        "form": dataset["FormTable", "form"].name,
    }
    for property in ["segments", "segmentSlice", "cognatesetReference", "alignment"]:
        try:
            columns[property] = dataset["FormTable", property].name
        except KeyError:
            pass
    cognate_judgements = []
    forms = cache_table(dataset, columns=columns)
    for f, form in forms.items():
        if form.get("cognatesetReference"):
            # TODO: Accept a parameter which describes that cognatesets are per-concept, and need to be split here by adding the concept to the cognatesetReference.
            judgement = {
                "ID": f,
                "Form_ID": f,
                "Cognateset_ID": form["cognatesetReference"],
            }
            try:
                judgement["Segment_Slice"] = form["segmentSlice"]
            except KeyError:
                try:
                    if (
                        "+" in form["segments"]
                        and dataset["FormTable", "cognatesetReference"].separator
                    ):
                        logger.warning(
                            "You seem to have morpheme annotations in your cognates. I will probably mess them up a bit, because I have not been taught properly how to deal with them. Sorry!"
                        )
                    judgement["Segment_Slice"] = "1:{:d}".format(len(form["segments"]))
                except (KeyError, TypeError):
                    logger.warning(
                        f"No segments found for form {f} ({form['form']}). You can generate segments using `lexedata.enrich.segment_using_clts`."
                    )
            # What does an alignment mean without segments or their slices?
            # Doesn't matter, if we were given one, we take it.
            judgement["Alignment"] = form.get("alignment")
            cognate_judgements.append(judgement)

    # TODO: Delete those moved columns
    dataset.write(CognateTable=cognate_judgements)

    add_explicit_cognateset_table(dataset)


if __name__ == "__main__":
    parser = cli.parser(__doc__)
    args = parser.parse_args()
    logger = cli.setup_logging(args)

    dataset = pycldf.Wordlist.from_metadata(args.metadata)
    add_cognate_table(dataset)
