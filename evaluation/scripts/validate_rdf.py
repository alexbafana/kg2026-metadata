#!/usr/bin/env python3
"""Parse Turtle with RDFLib; this is a syntax check, not an acceptance decision."""

from __future__ import annotations

import argparse
from pathlib import Path

from rdflib import Graph


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Turtle parses with RDFLib.")
    parser.add_argument("turtle", type=Path)
    args = parser.parse_args()

    graph = Graph()
    graph.parse(args.turtle, format="turtle")
    print(f"PASS: {args.turtle} parsed as Turtle ({len(graph)} triples)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
