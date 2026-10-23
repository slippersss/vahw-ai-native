#!/usr/bin/env python3
"""Stream trace event dictionaries from a JSON array or traceEvents object.

CLI filtering emits JSONL with original zero-based event indices. --limit
stops early; only exhausting the iterator validates the whole document.
"""
import argparse
import gzip
import json
from pathlib import Path


class JsonStream:
    def __init__(self, handle, chunk_size):
        if chunk_size <= 0:
            raise ValueError('chunk_size must be positive')
        self.handle, self.chunk_size = handle, chunk_size
        self.buffer, self.pos, self.eof = '', 0, False
        self.decoder = json.JSONDecoder()

    def fill(self):
        more = self.handle.read(self.chunk_size)
        self.buffer = self.buffer[self.pos:]+more
        self.pos = 0
        self.eof = not more

    def peek(self):
        while True:
            while self.pos < len(self.buffer) and self.buffer[self.pos].isspace():
                self.pos += 1
            if self.pos < len(self.buffer):
                return self.buffer[self.pos]
            if self.eof:
                return ''
            self.fill()

    def take(self, expected):
        if self.peek() != expected:
            raise ValueError(f'expected {expected!r}, got {self.peek()!r}')
        self.pos += 1

    def value(self):
        if not self.peek():
            raise ValueError('unexpected end of JSON')
        while True:
            try:
                value, end = self.decoder.raw_decode(self.buffer, self.pos)
            except json.JSONDecodeError as exc:
                if self.eof:
                    raise ValueError('invalid or truncated JSON value') from exc
                self.fill()
                continue
            # Numeric values can end exactly on a read boundary or be a
            # prefix of a longer token; wait for a delimiter before accepting.
            if end == len(self.buffer) and not self.eof:
                self.fill()
                continue
            if end < len(self.buffer) and self.buffer[end] not in ' \t\r\n,]}:':
                if not self.eof:
                    self.fill()
                    continue
                raise ValueError('invalid JSON token boundary')
            self.pos = end
            return value

    def array(self):
        self.take('[')
        if self.peek() == ']':
            self.take(']')
            return
        while True:
            value = self.value()
            if not isinstance(value, dict):
                raise ValueError('trace event must be an object')
            yield value
            if self.peek() == ']':
                self.take(']')
                return
            self.take(',')


def events(path, chunk_size=4*1024*1024):
    path = Path(path)
    opener = gzip.open if path.suffix.lower() == '.gz' else open
    with opener(path, 'rt', encoding='utf-8-sig') as handle:
        stream = JsonStream(handle, chunk_size)
        if stream.peek() == '[':
            yield from stream.array()
        else:
            stream.take('{')
            found = False
            if stream.peek() != '}':
                while True:
                    key = stream.value()
                    if not isinstance(key, str):
                        raise ValueError('object key must be a string')
                    stream.take(':')
                    if key == 'traceEvents':
                        if found:
                            raise ValueError('duplicate traceEvents key')
                        found = True
                        yield from stream.array()
                    else:
                        stream.value()
                    if stream.peek() == '}':
                        break
                    stream.take(',')
            stream.take('}')
            if not found:
                raise ValueError('missing traceEvents array')
        if stream.peek():
            raise ValueError('trailing content after JSON document')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', type=Path)
    parser.add_argument('--contains', default='', help='case-sensitive event-name substring')
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    if args.limit is not None and args.limit <= 0:
        parser.error('--limit must be positive')
    count = 0
    for index, event in enumerate(events(args.path)):
        if args.contains not in str(event.get('name', '')):
            continue
        print(json.dumps(dict(source=str(args.path), event_index=index, event=event), ensure_ascii=False))
        count += 1
        if args.limit is not None and count >= args.limit:
            break


if __name__ == '__main__':
    main()
