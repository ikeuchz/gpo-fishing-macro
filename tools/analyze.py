"""Static extraction of the supplied PyInstaller entry point; Python 3.14."""
import dis
import hashlib
import importlib.util
import json
import marshal
from pathlib import Path
import struct
import sys
import types
import zlib

EXPECTED = '31f6923fcb0999d5bddf8dca1363109a2bcb8740cb6e8e8158c2b66caddb64f5'

def main():
    if sys.version_info[:2] != (3, 14):
        raise SystemExit('Use Python 3.14.')
    data = Path(sys.argv[1]).read_bytes()
    if hashlib.sha256(data).hexdigest() != EXPECTED:
        raise SystemExit('Hash differs from the analyzed executable.')
    end = data.rfind(b'MEI\014\013\012\013\016')
    if end < 0:
        raise ValueError('Missing PyInstaller cookie')
    _, total, offset, length, version, library = struct.unpack('!8sIIII64s', data[end:end+88])
    start = end + 88 - total
    toc = data[start+offset:start+offset+length]
    rows, entry, i = [], None, 0
    while i < len(toc):
        size, offset, compressed, uncompressed, flag, kind = struct.unpack('!iIIIBc', toc[i:i+18])
        if size < 18 or i + size > len(toc):
            raise ValueError('Invalid entry')
        name = toc[i+18:i+size].split(b'\0')[0].decode()
        i += size
        rows.append({'name': name, 'type': kind.decode(), 'size': uncompressed})
        if name == 'z' and kind == b's':
            entry = data[start+offset:start+offset+compressed]
            entry = zlib.decompress(entry) if flag else entry
            if len(entry) != uncompressed:
                raise ValueError('Size mismatch')
    if entry is None:
        raise ValueError('Missing entry point')
    code = marshal.loads(entry)
    if not isinstance(code, types.CodeType):
        raise ValueError('Not a code object')
    output = Path(sys.argv[2])
    output.mkdir(parents=True, exist_ok=True)
    functions = []
    def visit(code):
        functions.append({'name': code.co_qualname, 'line': code.co_firstlineno,
                          'arguments': list(code.co_varnames[:code.co_argcount]),
                          'names': list(code.co_names),
                          'constants': [v for v in code.co_consts if isinstance(v, (str, int, float, bool)) or v is None]})
        for value in code.co_consts:
            if isinstance(value, types.CodeType):
                visit(value)
    visit(code)
    (output/'functions.json').write_text(json.dumps(functions, ensure_ascii=False, indent=2), encoding='utf-8')
    (output/'archive_inventory.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    (output/'main.pyc').write_bytes(importlib.util.MAGIC_NUMBER + b'\0'*12 + entry)
    with (output/'disassembly.txt').open('w', encoding='utf-8') as stream:
        dis.dis(code, file=stream, show_caches=False)
    print(f'{len(rows)} archive entries; {len(functions)} code objects; no code executed.')

if __name__ == '__main__':
    main()
