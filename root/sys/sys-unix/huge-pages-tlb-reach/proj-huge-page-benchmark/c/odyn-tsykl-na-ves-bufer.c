/* Вузол k: своя сторінка, але позиція в ній повзе по 64 байти. */
static inline size_t node_off(size_t k)
{
        return k * PAGE + (k & 63u) * LINE;
}

static inline uintptr_t *slot(char *buf, size_t k)
{
        return (uintptr_t *)(buf + node_off(k));
}
