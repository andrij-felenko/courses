// mav_parse.c — потоковий розбірник кадру MAVLink v1 (машина стану, по байту).
// Показує кістяк: як із потоку виловити один цілий кадр. Реальний CRC (CRC-16/MCRF4XX
// з домішком CRC_EXTRA) тут спрощено — ми лише ЗБИРАЄМО два байти CRC, не звіряючи їх;
// вага в СТРУКТУРІ кадру, а місце звірки чітко позначене.
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define MAV_STX_V1  0xFE          // стартовий байт версії 1
#define MAX_PAYLOAD 255

typedef struct {
    uint8_t seq, sysid, compid;   // лічильник і адреса відправника
    uint8_t msgid;                // тип повідомлення (v1 — один байт)
    uint8_t len;                  // довжина корисних даних
    uint8_t payload[MAX_PAYLOAD];
    uint16_t crc;                 // зібрана двобайтова контрольна сума
} mav_msg_t;

// Стани машини: чого ЧЕКАЄМО наступним байтом.
enum { WAIT_STX, WANT_LEN, WANT_SEQ, WANT_SYS, WANT_COMP, WANT_MSGID,
       WANT_PAYLOAD, WANT_CRC_LO, WANT_CRC_HI };

typedef struct {
    int state;
    mav_msg_t msg;
    int payload_idx;
} mav_parser_t;

// Згодувати парсеру один байт. Повертає 1, коли зібрано ЦІЛИЙ кадр (у *out).
// Кожен стан названо за тим, який байт він ЧЕКАЄ, тож читається як послідовність кадру.
int mav_parse_byte(mav_parser_t *p, uint8_t b, mav_msg_t *out) {
    switch (p->state) {
    case WAIT_STX:
        if (b == MAV_STX_V1) p->state = WANT_LEN;   // упіймали початок кадру
        break;
    case WANT_LEN:                                   // LEN — скільки буде даних
        p->msg.len = b;
        p->payload_idx = 0;
        p->state = WANT_SEQ;
        break;
    case WANT_SEQ:   p->msg.seq    = b; p->state = WANT_SYS;   break;
    case WANT_SYS:   p->msg.sysid  = b; p->state = WANT_COMP;  break;
    case WANT_COMP:  p->msg.compid = b; p->state = WANT_MSGID; break;
    case WANT_MSGID:
        p->msg.msgid = b;                            // тип повідомлення
        // якщо даних нема — одразу чекаємо CRC, інакше збираємо payload
        p->state = (p->msg.len == 0) ? WANT_CRC_LO : WANT_PAYLOAD;
        break;
    case WANT_PAYLOAD:
        p->msg.payload[p->payload_idx++] = b;        // збираємо рівно LEN байтів
        if (p->payload_idx >= p->msg.len) p->state = WANT_CRC_LO;
        break;
    case WANT_CRC_LO:                                // молодший байт CRC
        p->msg.crc = b;
        p->state = WANT_CRC_HI;
        break;
    case WANT_CRC_HI:                                // старший байт CRC — кадр повний
        p->msg.crc |= (uint16_t)b << 8;
        // ТУТ у справжньому коді: порахувати CRC-16/MCRF4XX по заголовку+даних
        // із домішком CRC_EXTRA і звірити з p->msg.crc; не зійшлось — відкинути.
        // Ми ж, показавши структуру, вважаємо кадр зібраним і віддаємо його.
        *out = p->msg;
        p->state = WAIT_STX;                         // готові ловити наступний старт
        return 1;                                    // ЦІЛИЙ кадр!
    }
    return 0;
}

// Демонстрація: годуємо парсеру байти й друкуємо тип кожного зібраного кадру.
int main(void) {
    mav_parser_t p; memset(&p, 0, sizeof p); p.state = WAIT_STX;
    // штучний кадр HEARTBEAT: FE 09 2A 01 01 00 [9 байтів даних] + 2 байти CRC
    uint8_t wire[] = {0xFE,0x09,0x2A,0x01,0x01,0x00,
                      0,0,0,0,0,0,0,0,0,   // 9 байтів даних HEARTBEAT
                      0x11,0x22};           // два байти CRC (тут умовні)
    mav_msg_t got;
    for (size_t i = 0; i < sizeof wire; i++) {
        if (mav_parse_byte(&p, wire[i], &got)) {
            printf("кадр: MSG ID=%u, від SYS=%u COMP=%u, %u байтів даних\n",
                   got.msgid, got.sysid, got.compid, got.len);
            if (got.msgid == 0) printf("  -> це HEARTBEAT (апарат живий)\n");
        }
    }
    return 0;
}
