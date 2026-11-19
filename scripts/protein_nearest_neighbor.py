#!/usr/bin/env python3
"""Exploratory nearest protein sequence identity; delimiter handling is unverified.

Uses released metadata `seq` and `type`. `reject` retains only comparisons that
need no delimiter interpretation; `strip` concatenates chains and is an explicit
sensitivity assumption, not an established paper method.
"""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import Bio
from Bio import Align
from Bio.Align import substitution_matrices

MATRIX = substitution_matrices.load('BLOSUM62')
ALPHABET = set(MATRIX.alphabet)


def normalise(seq, policy):
    if not seq:
        return None, 'missing_sequence'
    if ':' in seq:
        if policy == 'reject':
            return None, 'unresolved_chain_separator'
        seq = seq.replace(':', '')
    if not seq or set(seq) - ALPHABET:
        return None, 'unsupported_residue'
    return seq, 'ok'


def aligner():
    a = Align.PairwiseAligner()
    a.mode = 'global'
    a.substitution_matrix = MATRIX
    a.open_gap_score = -10
    a.extend_gap_score = -0.5
    return a


def identity(a, s, t):
    aligned = a.align(s, t)[0]
    # Aligned blocks exclude gap columns; identical residues in those blocks
    # divided by all alignment columns is the journal's definition.
    same = sum(s[i+k] == t[j+k] for (i, e), (j, _) in zip(*aligned.aligned)
               for k in range(e-i))
    return same, aligned.shape[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ids(path):
    with open(path, newline='') as f:
        data = [r['id'] for r in csv.DictReader(f)]
    if len(set(data)) != len(data):
        raise ValueError('duplicate cohort ID')
    return data


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--metadata', required=True)
    p.add_argument('--train', required=True)
    p.add_argument('--query', required=True)
    p.add_argument('--chain-policy', required=True, choices=['reject', 'strip'])
    p.add_argument('--output', required=True)
    args = p.parse_args()
    train, query = ids(args.train), ids(args.query)
    if set(train) & set(query):
        raise ValueError('overlapping training and query IDs')
    with open(args.metadata, newline='') as f:
        rows = list(csv.DictReader(f))
    meta = {r['']: r for r in rows}
    if len(meta) != len(rows):
        raise ValueError('duplicate metadata ID')
    if set(train + query) - meta.keys():
        raise ValueError('cohort ID missing from metadata')
    states = {i: normalise(meta[i]['seq'], args.chain_policy) for i in train + query}
    groups = defaultdict(list)
    for i in sorted(train):
        if states[i][1] == 'ok' and meta[i]['type']:
            groups[meta[i]['type']].append(i)
    a = aligner()
    out = Path(args.output)
    with out.open('w', newline='') as f:
        fields = ['query_id', 'nearest_training_id', 'similarity', 'matches', 'alignment_columns',
                  'tie_count', 'eligible_training', 'excluded_same_category', 'status']
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        query_cache = {}
        for q in sorted(query):
            seq, state = states[q]
            category = meta[q]['type']
            if state != 'ok' or not category:
                w.writerow({'query_id':q, 'status':state if category else 'missing_category'})
                continue
            cache_key = (category, seq)
            if cache_key in query_cache:
                w.writerow(dict(query_cache[cache_key], query_id=q))
                continue
            comparable = groups[category]
            expected = sum(meta[i]['type'] == category for i in train)
            excluded = expected - len(comparable)
            # Missing categories are excluded, not assumed different.
            valid_cross = [i for i in train if meta[i]['type'] and meta[i]['type'] != category]
            best, bestpair, ties = -1.0, None, 0
            cache = {}
            for i in comparable:
                ts = states[i][0]
                if ts not in cache:
                    cache[ts] = identity(a, seq, ts)
                matches, cols = cache[ts]
                score = matches / cols
                if score > best:
                    best, bestpair, ties = score, (i, matches, cols), 1
                elif score == best:
                    ties += 1
            # Cross-category score is exactly zero regardless of sequence validity.
            if valid_cross and best <= 0:
                if best < 0:
                    best, bestpair, ties = 0.0, (sorted(valid_cross)[0], '', ''), len(valid_cross)
                else:
                    ties += len(valid_cross)
                    if min(valid_cross) < bestpair[0]:
                        bestpair = (min(valid_cross), '', '')
            if bestpair is None:
                w.writerow({'query_id':q, 'status':'no_eligible_training', 'excluded_same_category':excluded})
                continue
            status = 'partial' if excluded or any(not meta[i]['type'] for i in train) else 'ok'
            result = {'nearest_training_id':bestpair[0], 'similarity':best,
                      'matches':bestpair[1], 'alignment_columns':bestpair[2], 'tie_count':ties,
                      'eligible_training':len(comparable) + len(valid_cross),
                      'excluded_same_category':excluded, 'status':status}
            query_cache[cache_key] = result
            w.writerow(dict(result, query_id=q))
    audit = {'method':'global BLOSUM62 open=-10 extend=-0.5; first optimal alignment; matched residues / alignment columns; cross-category=0',
             'chain_policy':args.chain_policy, 'warning':'Chain handling and author historical software unverified; not exact reproduction.',
             'biopython':Bio.__version__, 'metadata_sha256':digest(args.metadata),
             'train_sha256':digest(args.train), 'query_sha256':digest(args.query), 'output_sha256':digest(out),
             'train_total':len(train), 'query_total':len(query),
             'invalid_train':{i:states[i][1] for i in train if states[i][1]!='ok'},
             'invalid_query':{i:states[i][1] for i in query if states[i][1]!='ok'}}
    Path(str(out)+'.audit.json').write_text(json.dumps(audit, indent=2)+'\n')

if __name__ == '__main__':
    main()
