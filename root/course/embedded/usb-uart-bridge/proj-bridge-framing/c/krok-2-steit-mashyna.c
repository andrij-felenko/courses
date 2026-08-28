#define FRAME_SYNC     0xAA
#define MAX_PAYLOAD    64          // стеля даних — під свій протокол

typedef enum {
    WAIT_SYNC = 0,
    READ_LEN,
    READ_DATA,
    READ_CRC
} frame_state_t;

typedef struct {
    frame_state_t state;
    uint8_t  len;                  // оголошена довжина даних
    uint8_t  idx;                  // скільки байтів даних уже зібрано
    uint8_t  data[MAX_PAYLOAD];    // сюди складаємо корисні дані
    uint8_t  crc;                  // CRC, перерахований на льоту
} frame_parser_t;

static void frame_reset(frame_parser_t *p) {
    p->state = WAIT_SYNC;
    p->idx = 0;
    p->crc = 0;
}
