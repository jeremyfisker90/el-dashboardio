"""Stop an unconvertible schema from killing every conversation.

voluptuous_openapi returns an UNSUPPORTED sentinel for any schema it cannot
express as OpenAPI. entity.py feeds convert()'s output straight into the
Anthropic tool definitions, so one unconvertible parameter anywhere - in a tool,
or in a custom intent exposed through the Assist API - puts that sentinel in the
request body and json.dumps refuses it:

    TypeError: Object of type _Unsupported is not JSON serializable

Every request then fails, which reads as the assistant hearing you and doing
nothing at all.

entity.py imports convert exactly once, so shadowing it at the import site fixes
all eight call sites without touching any of them. The sentinel becomes a
permissive {"type": "string"} - the parameter survives in a form the model can
still fill in, and the API will accept.
"""
import io
import os

SRC = 'entity_orig.py'
OUT = 'entity_patched.py'

OLD = 'from voluptuous_openapi import convert\n'

NEW = '''from voluptuous_openapi import convert as _vo_convert

try:
    from voluptuous_openapi import UNSUPPORTED as _VO_UNSUPPORTED
except ImportError:  # older releases did not export the sentinel
    _VO_UNSUPPORTED = None


def _sanitize_schema(node):
    """Swap voluptuous_openapi's UNSUPPORTED sentinel for a permissive type.

    The sentinel is not JSON-serializable, so one unconvertible parameter would
    otherwise fail the entire request instead of just that field.
    """
    if _VO_UNSUPPORTED is not None and node is _VO_UNSUPPORTED:
        return {"type": "string"}
    if type(node).__name__ == "_Unsupported":      # belt and braces
        return {"type": "string"}
    if isinstance(node, dict):
        return {k: _sanitize_schema(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_sanitize_schema(v) for v in node]
    return node


def convert(*args, **kwargs):
    """convert() with the sentinel scrubbed out of the result."""
    return _sanitize_schema(_vo_convert(*args, **kwargs))

'''

src = io.open(SRC, encoding='utf-8').read()
if OLD not in src:
    raise SystemExit('import line not found - upstream changed')
if src.count(OLD) != 1:
    raise SystemExit('expected exactly one import of convert')

out = src.replace(OLD, NEW, 1)

tmp = OUT + '.tmp'
io.open(tmp, 'w', encoding='utf-8').write(out)
os.replace(tmp, OUT)
print('shadowed convert() at the import site; %d call sites inherit the fix'
      % out.count('convert('))
