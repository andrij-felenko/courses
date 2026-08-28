#include <stdint.h>
#define SYNC   0xAA
#define MAXLEN 32

enum state { WAIT_SYNC, GET_LEN, GET_DATA, GET_CRC };

static enum state st = WAIT_SYNC;        // стан, що живе між викликами
static uint8_t buf[MAXLEN];
static uint8_t len, idx, crc;

// простий XOR-CRC задля прикладу: ініціалізація і покрокове оновлення
static uint8_t crc_init(uint8_t b)            { return b; }
static uint8_t crc_update(uint8_t c, uint8_t b) { return c ^ b; }

void feed(uint8_t b) {
    switch (st) {
    case WAIT_SYNC:
        if (b == SYNC) st = GET_LEN;          // інакше просто ігноруємо
        break;
    case GET_LEN:
        if (b == 0 || b > MAXLEN) {           // захист: 0 або завелика довжина
            st = WAIT_SYNC; break;
        }
        len = b; idx = 0; crc = crc_init(b);  // CRC накриває й байт довжини
        st = GET_DATA;
        break;
    case GET_DATA:
        buf[idx++] = b;
        crc = crc_update(crc, b);             // CRC рахуємо на льоту
        if (idx == len) st = GET_CRC;
        break;
    case GET_CRC:
        if (b == crc) handle_packet(buf, len);// цілий пакет — у роботу
        st = WAIT_SYNC;                        // у будь-якому разі — наново
        break;
    }
}
