"""Query the Cupping Room release catalog with Python's standard library."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import unicodedata

DATA = Path(__file__).resolve().parent.parent / "references"
AXES = ("brightness", "sweetness", "body", "fruit", "floral")
TARGETS = {"balanced": (2.5, 4, 3.5, 2.5, 1), "chocolate": (1, 4, 4, 1, 0),
           "fruity": (4, 4, 3, 5, 1), "floral": (4, 3, 2, 3, 5)}
FIELDS = {"brand": "brand", "roast": "roast", "format": "format", "origin": "origins",
          "market": "markets", "species": "species", "label": "labels", "note": "notes",
          "method": "methods", "source": "sourceType"}


def folded(value):
    return "".join(ch for ch in unicodedata.normalize("NFKD", str(value).casefold())
                   if not unicodedata.combining(ch))


def values(row, field):
    value = row.get(field, [])
    return value if isinstance(value, list) else [value]


def per12(row):
    if row.get("price") is not None and row.get("ounces", 0) > 0:
        return row["price"] * 12 / row["ounces"]
    return None


def positive_amount(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("Enter a positive finite USD amount.")
    return number


def matches(row, args):
    for option, field in FIELDS.items():
        requested = getattr(args, option)
        if requested and not {folded(v) for v in requested}.intersection(folded(v) for v in values(row, field)):
            return False
    if args.caffeine and row.get("decaf") is not (args.caffeine == "decaf"):
        return False
    amount = per12(row)
    if args.budget is not None and (amount is None or amount > args.budget):
        return False
    searchable = " ".join(folded(v) for field in ("id", "name", *FIELDS.values()) for v in values(row, field))
    return all(word in searchable for word in folded(args.query).split())


def product(row):
    item = dict(row)
    amount = per12(row)
    if amount is not None:
        item["usdPer12oz"] = round(amount, 2)
        item["usdPer18gDose"] = round(amount / 12 / 28.349523125 * 18, 2)
    if "taste" in item:
        item["editorialProfile"] = dict(zip(AXES, item.pop("taste")))
    return item


def taste_match(row, flavor, method, milk):
    distance = sum(abs(a - b) for a, b in zip(row["taste"], TARGETS[flavor]))
    method_fit = method is not None and any(folded(m) == folded(method) for m in row.get("methods", []))
    return round(max(0, 100 - 4 * distance + 6 * method_fit + (row["taste"][2] - 3 if milk else 0)), 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    filters = argparse.ArgumentParser(add_help=False)
    filters.add_argument("--query", default="", help="All words must appear in catalog fields")
    for option in FIELDS:
        filters.add_argument("--" + option, action="append", help="Exact catalog value; repeat for alternatives")
    filters.add_argument("--caffeine", choices=["regular", "decaf"])
    filters.add_argument("--budget", type=positive_amount, help="Maximum recorded USD per 12 oz")
    filters.add_argument("--limit", type=int, choices=range(1, 31), default=6, metavar="1..30")
    search = actions.add_parser("search", parents=[filters])
    search.add_argument("--sort", choices=["default", "name", "price"], default="default")
    search.add_argument("--offset", type=int, default=0)
    facets = actions.add_parser("facets", parents=[filters])
    facets.add_argument("field", choices=sorted(FIELDS))
    compare = actions.add_parser("compare")
    compare.add_argument("ids", nargs="+")
    match = actions.add_parser("recommend", parents=[filters])
    match.add_argument("--flavor", choices=sorted(TARGETS), default="balanced")
    match.add_argument("--brew", help="Preferred method, used as a ranking signal")
    match.add_argument("--milk", action="store_true")
    args = parser.parse_args()
    rows = [json.loads(line) for path in sorted(DATA.glob("*.jsonl"))
            for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        parser.error("Bundled catalog missing. Reinstall this release.")
    if args.action == "compare":
        if not 2 <= len(args.ids) <= 4 or len(set(args.ids)) != len(args.ids):
            parser.error("Compare two to four distinct catalog IDs.")
        by_id = {r["id"]: r for r in rows}
        missing = [i for i in args.ids if i not in by_id]
        if missing:
            parser.error("Search for a valid coffee ID. Unknown: " + ", ".join(missing))
        output = {"coffees": [product(by_id[i]) for i in args.ids]}
    else:
        found = [r for r in rows if matches(r, args)]
        if args.action == "facets":
            counts = Counter(v for r in found for v in set(values(r, FIELDS[args.field])))
            output = {"matchedRecords": len(found), "distinctValues": len(counts),
                      "values": sorted(counts.items(), key=lambda t: (-t[1], folded(t[0])))[:args.limit]}
        elif args.action == "recommend":
            eligible = [r for r in found if r.get("taste") and per12(r) is not None]
            scored = [(taste_match(r, args.flavor, args.brew, args.milk), r) for r in eligible]
            scored.sort(key=lambda pair: (-pair[0], per12(pair[1]), pair[1]["id"]))
            output = {"eligibleProfiles": len(scored), "coffees": [
                {**product(r), "matchScore": score} for score, r in scored[:args.limit]]}
        else:
            if args.offset < 0:
                parser.error("Offset must be zero or greater.")
            def order(r):
                title = (folded(r["name"]), r["id"])
                if args.sort == "name":
                    return title
                if args.sort == "price":
                    price = per12(r)
                    return (price is None, price or 0, *title)
                return (r["sourceType"] != "official", *title)
            found.sort(key=order)
            output = {"total": len(found), "offset": args.offset,
                      "coffees": [product(r) for r in found[args.offset:args.offset + args.limit]]}
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
