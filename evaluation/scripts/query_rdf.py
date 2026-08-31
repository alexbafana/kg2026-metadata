#!/usr/bin/env python3
"""Execute a local SPARQL query against one Turtle file and print CSV results."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from rdflib import Graph


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, type=Path, help="Turtle input")
    parser.add_argument("--query", required=True, type=Path, help="SPARQL query file")
    args = parser.parse_args()

    graph = Graph()
    graph.parse(args.data, format="turtle")
    result = graph.query(args.query.read_text(encoding="utf-8"))
    writer = csv.writer(sys.stdout)
    writer.writerow([str(variable) for variable in result.vars])
    writer.writerows(
        ["" if value is None else str(value) for value in row] for row in result
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
