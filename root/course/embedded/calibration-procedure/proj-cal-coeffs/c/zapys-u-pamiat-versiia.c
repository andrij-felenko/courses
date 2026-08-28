#define CAL_MAGIC    0xCA10B00Fu   // «тут лежить калібрування» (з теми)
#define CAL_VERSION  2u            // версія РОЗКЛАДКИ цієї структури

typedef struct {
    uint32_t magic;      // == CAL_MAGIC
    uint16_t version;    // == CAL_VERSION; інша версія → «не моє»
    uint16_t _pad;       // вирівнювання до 4 байт (щоб розкладка була стабільна)
    float    k;
    float    b;
    uint32_t seq;        // лічильник записів ЦЬОГО слота (більший = новіший)
    uint32_t crc;        // CRC32 усіх байтів ВИЩЕ (від magic до seq включно)
} cal_store_t;

// Невелика портативна CRC32 (поліном 0x04C11DB7, відбитий → 0xEDB88320).
// На ESP32 те саме дає ROM-функція esp_crc32_le(0, buf, len) з esp_crc.h.
static uint32_t crc32(const void *data, size_t len)
{
    const uint8_t *p = (const uint8_t *)data;
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < len; i++) {
        crc ^= p[i];
        for (int b = 0; b < 8; b++)
            crc = (crc >> 1) ^ (0xEDB88320u & (uint32_t)(-(int32_t)(crc & 1u)));
    }
    return ~crc;
}

// Зібрати запис із коефіцієнтів: проставити magic, версію, seq та CRC.
static void store_pack(cal_store_t *s, const cal_t *c, uint32_t seq)
{
    memset(s, 0, sizeof *s);          // _pad та хвости — у нуль, щоб CRC був стабільний
    s->magic   = CAL_MAGIC;
    s->version = CAL_VERSION;
    s->seq     = seq;
    s->k = c->k;
    s->b = c->b;
    // CRC рахуємо по всьому ДО поля crc (offsetof — зміщення цього поля).
    s->crc = crc32(s, offsetof(cal_store_t, crc));
}

// Перевірити піднятий запис: magic, версія, CRC. true ⇔ можна вірити.
static bool store_valid(const cal_store_t *s)
{
    if (s->magic != CAL_MAGIC)     return false;   // не калібрування / чиста flash
    if (s->version != CAL_VERSION) return false;   // чужий формат
    return s->crc == crc32(s, offsetof(cal_store_t, crc));  // байти цілі?
}
