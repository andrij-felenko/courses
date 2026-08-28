/* Розбір хвоста. Повертає 0 або від'ємний код помилки; заповнює
   таблицю вказівників на знайдені атрибути. */
static int pacer_parse(const void *buf, size_t len,
                       const struct pacer_attr *tab[], u16 maxtype)
{
        size_t off = 0;

        memset(tab, 0, (maxtype + 1) * sizeof(tab[0]));

        while (off < len) {
                const struct pacer_attr *a;
                size_t alen, step;

                if (len - off < PACER_ATTR_HDRLEN)
                        return -EINVAL;        /* обрізаний заголовок */

                a    = (const struct pacer_attr *)((const char *)buf + off);
                alen = a->len;
                step = PACER_ATTR_ALIGN(alen);

                if (alen < PACER_ATTR_HDRLEN || step > len - off)
                        return -EINVAL;        /* довжині не можна вірити */
                if (a->type > maxtype)
                        return -EOPNOTSUPP;    /* прохання, якого ми не розуміємо */
                if (tab[a->type])
                        return -EINVAL;        /* той самий атрибут двічі */

                tab[a->type] = a;
                off += step;
        }
        return 0;
}
