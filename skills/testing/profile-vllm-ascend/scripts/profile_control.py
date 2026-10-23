#!/usr/bin/env python3
"""Control one existing serving profiler; never retry an ambiguous action.

Adapted from pisceskkk/vllm-ascend-skills, MIT, Copyright (c) 2026 Qi Mao.
See ../LICENSE. No service launch, benchmark traffic or implicit cleanup.
"""
import argparse
from contextlib import nullcontext
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def control(base_url, action, timeout=600):
    parsed = urllib.parse.urlsplit(base_url)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError('base-url must be an HTTP(S) service root without query or fragment')
    if action not in ('start_profile', 'stop_profile') or timeout <= 0:
        raise ValueError('invalid action or timeout')
    result = dict(url=base_url.rstrip('/')+'/'+action, action=action,
                  started_wall_ns=time.time_ns(), ok=False, completion='unknown')
    started = time.monotonic()
    request = urllib.request.Request(result['url'], method='POST')
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result.update(status=response.status, body=response.read().decode('utf-8', errors='replace'))
        result.update(ok=True, completion='HTTP response received; inspect capture/export state')
    except urllib.error.HTTPError as exc:
        result.update(status=exc.code, body=exc.read().decode('utf-8', errors='replace'),
                      error=str(exc))
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        result['error'] = str(exc)
    result.update(finished_wall_ns=time.time_ns(), elapsed_seconds=time.monotonic()-started)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--action', choices=('start_profile', 'stop_profile'), required=True)
    parser.add_argument('--timeout', type=float, default=600)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    # Validate/reserve the output before mutating the profiler state.
    with (args.output.open('x', encoding='utf-8', newline='\n') if args.output else nullcontext(None)) as output:
        result = control(args.base_url, args.action, args.timeout)
        payload = json.dumps(result, ensure_ascii=False, indent=2)+'\n'
        if output is not None:
            output.write(payload)
    print(payload, end='')
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
