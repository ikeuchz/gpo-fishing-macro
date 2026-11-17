"""Load the exact Python 3.14 entry module recovered from the supplied executable.

The module name deliberately differs from __main__: its old launcher is not run.
The class implementations and their constants are preserved byte for byte.
"""
import hashlib
import marshal
from pathlib import Path
import sys
import types

CORE_SHA256 = '324dfedd239fb3cc9e16a2ca1a496557d9bc098f3101d13b559c78e08dd9c441'


def load_original():
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError('Esta versão requer Python 3.14 para usar o motor original.')
    payload = (Path(__file__).parent/'assets'/'original_core.marshal').read_bytes()
    if hashlib.sha256(payload).hexdigest() != CORE_SHA256:
        raise RuntimeError('O motor original foi alterado ou está corrompido.')
    module = types.ModuleType('_gpo_original')
    # Preserve the original settings location beside run.py / the executable.
    module.__file__ = str(Path(__file__).resolve().parents[1]/'run.py')
    exec(marshal.loads(payload), module.__dict__)
    return module


core = load_original()
OriginalMacro = core.GPOFishingMacro
