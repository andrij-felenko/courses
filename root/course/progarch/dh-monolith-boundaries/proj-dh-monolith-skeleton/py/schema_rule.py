# arch/schema_rule.py — жоден модуль не сміє називати чужу схему у своєму SQL
import re, pathlib
from .graph import MODULES
SCHEMAS = MODULES - {"ids"}                          # у кожного модуля однойменна схема; в ids схеми нема

def cross_schema(root="dh"):
    bad, pat = [], re.compile(r"\b(" + "|".join(SCHEMAS) + r")\.[a-z_]+")
    for path in pathlib.Path(root).rglob("*.sql"):   # звужуємо до SQL (DDL + видобуті запити), не весь код
        owner = path.relative_to(root).parts[0]
        if owner not in SCHEMAS:
            continue
        for schema in pat.findall(path.read_text(encoding="utf-8")):
            if schema != owner:
                bad.append((owner, schema, path.name))
    return bad
