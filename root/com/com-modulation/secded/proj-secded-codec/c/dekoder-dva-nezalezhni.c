typedef enum {
    SECDED_NO_ERROR = 0,        /* синдром 0, парність сходиться               */
    SECDED_CORRECTED_SINGLE,    /* один біт — знайдено й виправлено            */
    SECDED_PARITY_BIT_ERROR,    /* перевернувся сам P₀ — дані цілі             */
    SECDED_DETECTED_DOUBLE      /* два біти — ВИЯВЛЕНО; дані НЕ віддано        */
} secded_status;

typedef struct {
    secded_status status;
    uint8_t       data;      /* має сенс ⟺ status != SECDED_DETECTED_DOUBLE   */
    uint8_t       position;  /* 1..7 — виправлена позиція; 8 — сам P₀; 0 — нема */
    uint8_t       syndrome;  /* сирий синдром — те, що ECC-контролер пише в лог */
} secded_result;

static uint8_t data_of(uint8_t w)
{
    return (uint8_t)((((w >> 2) & 1u) << 3)    /* позиція 3 → D1 */
                   | (((w >> 4) & 1u) << 2)    /* позиція 5 → D2 */
                   | (((w >> 5) & 1u) << 1)    /* позиція 6 → D3 */
                   | (((w >> 6) & 1u) << 0));  /* позиція 7 → D4 */
}

secded_result secded_decode(uint8_t w)
{
    secded_result r;

    /* Запитання перше: синдром Геммінга. Значення = НОМЕР зіпсованої позиції. */
    uint8_t s = (uint8_t)((parity8(w & M_P1) << 0)
                        | (parity8(w & M_P2) << 1)
                        | (parity8(w & M_P4) << 2));

    /* Запитання друге, НЕЗАЛЕЖНЕ: парне чи непарне число одиниць у ВСІХ 8 бітах. */
    int odd = parity8(w);

    r.syndrome = s;
    r.position = 0;

    if (s == 0 && !odd) {
        r.status = SECDED_NO_ERROR;
    } else if (s == 0) {                      /* отже odd: цілий Геммінг, крива парність */
        r.status = SECDED_PARITY_BIT_ERROR;   /* перевернувся сам P₀ — дані цілі */
        r.position = 8;
        w ^= 0x80u;
    } else if (odd) {
        r.status = SECDED_CORRECTED_SINGLE;   /* синдром = адреса, просто перевернути */
        r.position = s;
        w ^= (uint8_t)(1u << (s - 1));
    } else {
        /* Синдром кричить, а парність спокійна — незмивний підпис ДВОХ помилок. */
        r.status = SECDED_DETECTED_DOUBLE;
        r.data = 0;            /* дані не віддаємо: вони брехливі */
        return r;
    }

    r.data = data_of(w);
    return r;
}
