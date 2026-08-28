seen = []
_orig = Locator.get.__func__

def traced(cls, key):
    import traceback
    fr = traceback.extract_stack()[-2]
    seen.append((key, f"{fr.name}:{fr.lineno}"))
    return _orig(cls, key)

Locator.get = classmethod(traced)
# → [('gateway.eu', 'pay:124'), ('gateway.us', 'pay:124')]
