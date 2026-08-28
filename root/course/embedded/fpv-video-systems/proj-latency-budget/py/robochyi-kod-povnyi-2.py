def span_add(a: SpanMs, b: SpanMs) -> SpanMs:
    return SpanMs(a.lo + b.lo, a.hi + b.hi)

# Повна затримка «скло-скло» як діапазон [lo, hi].
def glass_to_glass(s: FpvSystem) -> SpanMs:
    t = SpanMs(0.0, 0.0)
    t = span_add(t, s.sensor)
    t = span_add(t, s.encode)
    t = span_add(t, s.radio)
    t = span_add(t, s.decode)
    t = span_add(t, s.display)
    return t
