#!/usr/bin/env python3
"""Nearest neighbors for precomputed 256-component interaction count vectors.

This does not generate fingerprints or establish their equivalence to the paper.
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

FEATURES = [f"f{i:03d}" for i in range(256)]


def read_vectors(path):
    ids, rows, failed = [], [], []
    with open(path, newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["id", *FEATURES]:
            raise ValueError(f"{path}: expected id followed by f000 through f255")
        seen = set()
        for line, record in enumerate(reader, 2):
            name = record["id"]
            if not name or name in seen:
                raise ValueError(f"{path}:{line}: empty or duplicate ID")
            seen.add(name)
            try:
                values = [int(record[k]) for k in FEATURES]
                if any(v < 0 or v > np.iinfo(np.int32).max for v in values):
                    raise ValueError("negative or out-of-range count")
            except (ValueError, TypeError):
                failed.append({"id": name, "reason": "invalid_count"})
                continue
            if not any(values):
                failed.append({"id": name, "reason": "empty_fingerprint"})
                continue
            ids.append(name)
            rows.append(values)
    return ids, np.asarray(rows, dtype=np.int32).reshape(-1, 256), failed


def nearest(query, training, ids):
    if len(training) != len(ids) or not len(ids):
        raise ValueError("need at least one training vector and matching ID")
    numerator = np.minimum(training, query).sum(axis=1, dtype=np.int64)
    denominator = np.maximum(training, query).sum(axis=1, dtype=np.int64)
    if np.any(denominator == 0):
        raise ValueError("undefined weighted Jaccard for two empty vectors")
    # Use integer cross-products to compare rational scores exactly (Python ints
    # avoid overflow); report a deterministic ID and the full tie count.
    best = 0
    for i in range(1, len(ids)):
        if int(numerator[i]) * int(denominator[best]) > int(numerator[best]) * int(denominator[i]):
            best = i
    tied = [i for i in range(len(ids)) if int(numerator[i]) * int(denominator[best]) == int(numerator[best]) * int(denominator[i])]
    chosen = min(tied, key=lambda i: ids[i])
    return ids[chosen], int(numerator[chosen]), int(denominator[chosen]), len(tied)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--audit", required=True)
    args = parser.parse_args()
    train_ids, train, train_fail = read_vectors(args.training)
    query_ids, query, query_fail = read_vectors(args.query)
    if not train_ids:
        raise ValueError("no valid training vectors")
    with open(args.output, "x", newline="", encoding="utf-8") as stream:
        fields = ["query_id", "training_id", "similarity", "intersection_count", "union_count", "tie_count", "training_candidates"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for name, vector in zip(query_ids, query):
            neighbor, numerator, denominator, ties = nearest(vector, train, train_ids)
            writer.writerow(dict(query_id=name, training_id=neighbor, similarity=numerator / denominator, intersection_count=numerator, union_count=denominator, tie_count=ties, training_candidates=len(train_ids)))
    Path(args.audit).write_text(json.dumps({"training_valid": len(train_ids), "query_valid": len(query_ids), "training_excluded": train_fail, "query_excluded": query_fail, "note": "Precomputed fingerprints; paper-equivalence of generation is not established."}, indent=2) + "\n")


if __name__ == "__main__":
    main()
