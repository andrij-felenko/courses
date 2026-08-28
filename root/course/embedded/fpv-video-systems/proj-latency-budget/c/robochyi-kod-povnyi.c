static span_ms span_add(span_ms a, span_ms b) {
    span_ms r = { a.lo + b.lo, a.hi + b.hi };
    return r;
}

// Повна затримка «скло-скло» як діапазон [lo, hi].
span_ms glass_to_glass(const fpv_system *s) {
    span_ms t = { 0.0f, 0.0f };
    t = span_add(t, s->sensor);
    t = span_add(t, s->encode);
    t = span_add(t, s->radio);
    t = span_add(t, s->decode);
    t = span_add(t, s->display);
    return t;
}
