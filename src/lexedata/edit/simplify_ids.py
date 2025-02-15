"""Clean up all ID columns in the dataset.

Take every ID column and convert it to either an integer-valued or a restricted-string-valued (only containing a-z, 0-9, or _) column, maintaining uniqueness of IDs, and keeping IDs as they are where they fit the format.

Optionally, create ‘transparent’ IDs, that is alphanumerical IDs which are derived from the characteristic columns of the corresponding table. For example, the ID of a FormTable would be derived from language and concept; for a CognatesetTable from the central concept if there is one.

"""
import pycldf

from lexedata.util import cache_table
import lexedata.cli as cli
from lexedata.util.simplify_ids import (
    clean_mapping,
    update_integer_ids,
    update_ids,
    ID_COMPONENTS,
)

if __name__ == "__main__":
    parser = cli.parser(__doc__)
    parser.add_argument(
        "--transparent",
        action="store_true",
        default=False,
        help="Generate transparent IDs.",
    )
    parser.add_argument(
        "--uppercase",
        action="store_true",
        default=False,
        help="Normalize to uppercase letters, instead of the default lowercase.",
    )
    parser.add_argument(
        "--tables",
        nargs="+",
        help="Only fix the IDs of these tables.",
    )
    args = parser.parse_args()
    logger = cli.setup_logging(args)

    if args.uppercase:
        # TODO: implement this
        raise NotImplementedError

    ds = pycldf.Wordlist.from_metadata(args.metadata)

    if args.tables:
        tables = []
        for table in args.tables:
            try:
                tables.append(ds[table])
            except KeyError:
                cli.Exit.INVALID_TABLE_NAME(f"No table {table} in dataset.")
    else:
        tables = ds.tables

    for table in tables:
        logger.info(f"Handling table {table.url.string}…")
        ttype = ds.get_tabletype(table)
        c_id = table.get_column("http://cldf.clld.org/v1.0/terms.rdf#id")
        if c_id.datatype.base == "string":
            # Temporarily open up the datatype format, otherwise we may be unable to read
            c_id.datatype.format = None
        elif c_id.datatype.base == "integer":
            # Temporarily open up the datatype format, otherwise we may be unable to read
            c_id.datatype = "string"
            update_integer_ids(ds, table)
            c_id.datatype = "integer"
            continue
        else:
            logger.warning(
                f"Table {table.uri} had an id column ({c_id.name}) that is neither integer nor string. I did not touch it."
            )
            continue

        if args.transparent and ttype in ID_COMPONENTS:
            cols = {prop: ds[ttype, prop].name for prop in ID_COMPONENTS[ttype]}
            mapping = clean_mapping(cache_table(ds, ttype, cols))
        else:
            ids = {row[c_id.name] for row in ds[table]}
            mapping = clean_mapping(cache_table(ds, table.url.string, {}))

        update_ids(ds, table, mapping)

    ds.write_metadata()
