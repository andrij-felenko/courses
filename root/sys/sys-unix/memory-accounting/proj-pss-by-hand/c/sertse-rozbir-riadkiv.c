/* Ім'я ділянки — шосте поле заголовка; його може не бути. */
static const char *vma_name(const char *line, size_t len, size_t *out_n)
{
    size_t i = 0;
    for (int field = 0; field < 5; field++) {
        while (i < len && line[i] != ' ') i++;
        while (i < len && line[i] == ' ') i++;
    }
    if (i >= len) { *out_n = 6; return "[anon]"; }
    *out_n = len - i;
    return line + i;
}

/* Розбирає весь smaps у таблицю tab[]. */
static void parse_smaps(char *buf, size_t len)
{
    struct region *cur = NULL;
    char *p = buf, *end = buf + len;

    while (p < end) {
        char  *line = p;
        char  *nl   = memchr(p, '\n', (size_t)(end - p));
        size_t llen = nl ? (size_t)(nl - p) : (size_t)(end - p);
        p = nl ? nl + 1 : end;
        if (llen == 0)
            continue;

        /* Адреси — малими літерами, назви полів — з великої. */
        if (line[0] < 'A' || line[0] > 'Z') {
            size_t n;
            const char *nm = vma_name(line, llen, &n);
            cur = bucket(nm, n);
            continue;
        }
        if (!cur)
            continue;

        const char *colon = memchr(line, ':', llen);
        if (!colon)
            continue;
        size_t klen = (size_t)(colon - line);

        for (size_t k = 0; k < sizeof FIELDS / sizeof FIELDS[0]; k++) {
            if (FIELDS[k].len != klen || memcmp(line, FIELDS[k].key, klen) != 0)
                continue;
            const char *v = colon + 1;
            while (*v == ' ') v++;
            *(unsigned long *)((char *)cur + FIELDS[k].off) += strtoul(v, NULL, 10);
            break;
        }
    }
}
