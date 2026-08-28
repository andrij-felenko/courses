/* Скільки сторінок діапазону справді в пам'яті. Саме цим перевіряють,
   що «холодний» кеш таки холодний, а не здається таким. */
static unsigned long resident(void *addr, size_t len)
{
    size_t n = len / PGSZ;
    unsigned char *vec = malloc(n);
    unsigned long r = 0;
    if (mincore(addr, len, vec) == 0)
        for (size_t i = 0; i < n; i++) r += vec[i] & 1u;
    free(vec);
    return r;
}
