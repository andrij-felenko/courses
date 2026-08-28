typedef enum { ECC_OK, ECC_CORRECTED, ECC_DOUBLE } ecc_status;
typedef struct { uint64_t data; ecc_status status; unsigned pos; } ecc_result;

/* Зібрати 64 біти даних із не-контрольних позицій 1..71 назад у uint64_t. */
static uint64_t gather(word72 cw) {
    uint64_t data = 0;
    unsigned b = 0;
    for (unsigned p = 1; p <= HAM; ++p)
        if (!is_check(p)) {
            data |= (uint64_t)((cw >> p) & 1) << b;
            ++b;
        }
    return data;
}

ecc_result ecc_decode(word72 cw) {
    ecc_result r = { 0, ECC_OK, 0 };
    unsigned s = syndrome(cw);      /* 0 або номер битої позиції */
    unsigned g = parity(cw);        /* 0 = парна вага, 1 = непарна */

    if (s == 0 && g == 0) {         /* ── ціле ── */
        r.status = ECC_OK;
    } else if (g == 1) {            /* ── непарна вага → рахуємо як одну помилку ── */
        if (s == 0) {               /* перекинувся сам біт загальної парності */
            r.status = ECC_CORRECTED; r.pos = 0;
        } else if (s <= HAM) {      /* биток на позиції s — виправляємо */
            cw ^= (word72)1 << s;
            r.status = ECC_CORRECTED; r.pos = s;
        } else {                    /* s поза словом → збій за межами коду */
            r.status = ECC_DOUBLE;  /* чесно: не виправляємо наосліп */
        }
    } else {                        /* ── g == 0, s != 0 → парна вага (≥2) ── */
        r.status = ECC_DOUBLE;      /* виявили, виправити не можна */
    }

    r.data = gather(cw);            /* на ECC_DOUBLE ці дані НЕ довіряти */
    return r;
}
