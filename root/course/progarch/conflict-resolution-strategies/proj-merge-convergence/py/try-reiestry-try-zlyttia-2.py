# ── 3. OR-Set: на елемент — теги додавань і теги знятих (тумбстоуни) ──
def or_merge(a, b):
    out = {"add": {}, "rem": {}}
    for s in (a, b):
        for kind in ("add", "rem"):
            for e, tags in s[kind].items():
                out[kind].setdefault(e, set()).update(tags)
    return out

# елемент живий, поки має бодай один доданий, але не знятий тег
def or_value(s):
    return {e for e, tags in s["add"].items()
            if tags - s["rem"].get(e, set())}
