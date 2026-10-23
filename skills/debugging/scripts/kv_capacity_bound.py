#!/usr/bin/env python3
"""Evaluate supplied independent full/sliding KV states, not a scheduler.

Input JSON: block_bytes, independent_allocations:true, groups:[{name,
block_tokens,window_tokens?}], checks:[{label,requests:[{id,allocation_end,
reclaim_frontier}],other_unavailable_blocks?,reserved_blocks?,watermark_blocks?}].
Optional pool_blocks enables margin reporting. Each request includes the extent
required at that check, including the proposed new allocation where applicable.
"""
import argparse
import json
from pathlib import Path


def integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f'{name} must be an integer >= {minimum}')
    return value


def evaluate(document):
    if document.get('independent_allocations') is not True:
        raise ValueError('requires explicitly independent allocations; shared/CoW layouts unsupported')
    stride = integer(document['block_bytes'], 'block_bytes', 1)
    nulls = integer(document.get('null_blocks', 1), 'null_blocks')
    groups = document['groups']
    if not groups or len({g['name'] for g in groups}) != len(groups):
        raise ValueError('nonempty uniquely named groups required')
    for group in groups:
        if set(group)-{'name', 'block_tokens', 'window_tokens'}:
            raise ValueError('unsupported group fields/layout')
        integer(group['block_tokens'], 'block_tokens', 1)
        if group.get('window_tokens') is not None:
            integer(group['window_tokens'], 'window_tokens', 1)
    rows = []
    for check in document['checks']:
        requests = check['requests']
        if len({r['id'] for r in requests}) != len(requests):
            raise ValueError('duplicate request IDs within check')
        components = []
        for request in requests:
            end = integer(request['allocation_end'], 'allocation_end')
            frontier = integer(request['reclaim_frontier'], 'reclaim_frontier')
            if frontier > end:
                raise ValueError('reclaim frontier exceeds allocated extent')
            counts = {}
            for group in groups:
                size, window = group['block_tokens'], group.get('window_tokens')
                skipped = 0 if window is None else max(0, frontier-window+1)//size
                counts[group['name']] = max(0, (end+size-1)//size-skipped)
            components.append(dict(id=request['id'], groups=counts, blocks=sum(counts.values())))
        extras = {key: integer(check.get(key, 0), key) for key in
                  ('other_unavailable_blocks', 'reserved_blocks', 'watermark_blocks')}
        total = nulls+sum(c['blocks'] for c in components)+sum(extras.values())
        row = dict(label=check['label'], requests=components, null_blocks=nulls,
                   extras=extras, required_blocks=total, required_GiB=total*stride/2**30)
        if 'pool_blocks' in document:
            row['margin_blocks'] = integer(document['pool_blocks'], 'pool_blocks')-total
        rows.append(row)
    if not rows:
        raise ValueError('at least one check required')
    return dict(scope='Conditional arithmetic over supplied independent states; no scheduling or release proof.',
                checks=rows, peak=max(rows, key=lambda row:row['required_blocks']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate(json.loads(args.input.read_text(encoding='utf-8'))), indent=2))


if __name__ == '__main__':
    main()
