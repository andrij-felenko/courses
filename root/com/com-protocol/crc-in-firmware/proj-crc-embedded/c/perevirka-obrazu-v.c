#define SLOT_BASE  0x08010000U                  /* початок слоту застосунку */
#define SLOT_SIZE  (192U * 1024U)
#define IMG_MAGIC  0x474D4946U                  /* довільна мітка «тут образ» */

typedef struct {
    uint32_t magic;
    uint32_t length;      /* байтів вантажу ПІСЛЯ заголовка */
    uint32_t crc;         /* CRC-32 того самого вантажу */
    uint32_t entry;       /* адреса точки входу */
} img_header;

bool image_is_valid(void) {
    const img_header *h = (const img_header *)SLOT_BASE;

    if (h->magic != IMG_MAGIC)                  /* стертий слот — самі 0xFF, а не образ */
        return false;
    if (h->length == 0U || h->length > SLOT_SIZE - sizeof(img_header))
        return false;                           /* довжині з заголовка ЩЕ не вірять */

    crc32_ctx c;
    crc32_init(&c);
    const uint8_t *p = (const uint8_t *)(SLOT_BASE + sizeof(img_header));
    uint32_t left = h->length;
    while (left) {
        uint32_t chunk = left > 1024U ? 1024U : left;
        crc32_feed(&c, p, chunk);               /* внутрішній флеш адресується напряму */
        p    += chunk;
        left -= chunk;
        watchdog_kick();                        /* 192 КБ довші за вікно сторожа */
    }
    return crc32_final(&c) == h->crc;
}
