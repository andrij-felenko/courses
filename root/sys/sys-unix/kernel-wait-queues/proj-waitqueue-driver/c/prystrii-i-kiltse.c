static inline unsigned int ring_used(const struct wqdemo *d) { return d->head - d->tail; }
static inline unsigned int ring_free(const struct wqdemo *d) { return RING_SIZE - ring_used(d); }

/* обидві копіюють у пам'ять ЯДРА і кличуться ЛИШЕ під d->lock */
static unsigned int ring_put(struct wqdemo *d, const char *src, unsigned int n)
{
    unsigned int i;

    n = min(n, ring_free(d));
    for (i = 0; i < n; i++)
        d->ring[(d->head + i) & (RING_SIZE - 1)] = src[i];
    d->head += n;
    return n;
}

static unsigned int ring_get(struct wqdemo *d, char *dst, unsigned int n)
{
    unsigned int i;

    n = min(n, ring_used(d));
    for (i = 0; i < n; i++)
        dst[i] = d->ring[(d->tail + i) & (RING_SIZE - 1)];
    d->tail += n;
    return n;
}
