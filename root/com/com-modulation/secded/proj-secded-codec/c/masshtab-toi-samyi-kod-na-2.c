typedef enum {
    SECDED72_NO_ERROR = 0,
    SECDED72_CORRECTED_SINGLE,
    SECDED72_PARITY_BIT_ERROR,
    SECDED72_DETECTED_DOUBLE,
    SECDED72_DETECTED_UNCORRECTABLE   /* синдром не вказує на жодну позицію */
} secded72_status;

typedef struct {
    secded72_status status;
    uint64_t        data;
    uint8_t         syndrome;
    int             position;      /* 1..71 — позиція; 72 — сам P₀; 0 — нема */
} secded72_result;

secded72_result secded72_decode(uint64_t data, uint8_t check)
{
    secded72_result r;
    uint8_t s = 0;
    int j, odd, idx;

    /* Запитання перше: перерахувати СІМ парностей Геммінга і звірити з прийнятими. */
    for (j = 0; j < N_HAM; j++)
        s |= (uint8_t)((par64(data & MASK[j]) ^ ((check >> j) & 1)) << j);

    /* Запитання друге, НЕЗАЛЕЖНЕ: парність усіх 72 бітів, як вони прийшли.
       Саме тут не можна брати P₀ з перерахунку — див. пастку другу. */
    odd = par64(data) ^ __builtin_parity(check);

    r.data = data;
    r.syndrome = s;
    r.position = 0;

    if (s == 0 && !odd) { r.status = SECDED72_NO_ERROR;         return r; }
    if (s == 0)         { r.status = SECDED72_PARITY_BIT_ERROR;
                          r.position = 72;                      return r; }
    if (!odd)           { r.status = SECDED72_DETECTED_DOUBLE;  return r; }

    idx = SYN_TO_DATA[s];              /* s ≤ 127, таблиця на 128 — вихід за межі неможливий */

    if (idx >= 0) {                             /* синдром указав на біт даних */
        r.data = data ^ ((uint64_t)1 << idx);
        r.status = SECDED72_CORRECTED_SINGLE;
        r.position = POS_OF[idx];
    } else if (idx == -2) {                     /* збій самого контролю — дані цілі */
        r.status = SECDED72_CORRECTED_SINGLE;
        r.position = s;
    } else {                                    /* idx == −1: адреси НЕМА */
        r.status = SECDED72_DETECTED_UNCORRECTABLE;
        r.data = 0;
    }
    return r;
}
