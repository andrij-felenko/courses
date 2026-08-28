// Подати один байт у парсер. Повертає true, коли зібрано ЦІЛИЙ і ПЕРЕВІРЕНИЙ кадр
// (тоді p->data / p->len дійсні). У решті випадків — false.
bool frame_feed(frame_parser_t *p, uint8_t b) {
    switch (p->state) {

    case WAIT_SYNC:
        if (b == FRAME_SYNC) {     // зачепилися за початок
            p->idx = 0;
            p->crc = 0;
            p->state = READ_LEN;
        }
        // будь-що інше — мовчки відкидаємо (самовідновлення)
        return false;

    case READ_LEN:
        if (b == 0 || b > MAX_PAYLOAD) {
            // 0 або задовга довжина — це не наш кадр (сміття чи побитий байт).
            // Не довіряємо й вертаємось чекати свіжий SYNC.
            // Виняток: якщо цей самий байт сам є SYNC — почнемо кадр заново з нього.
            p->state = WAIT_SYNC;
            return frame_feed(p, b);   // переграти байт у стані WAIT_SYNC
        }
        p->len = b;
        p->crc = crc8_step(p->crc, b);  // LEN входить у CRC
        p->state = READ_DATA;
        return false;

    case READ_DATA:
        p->data[p->idx++] = b;
        p->crc = crc8_step(p->crc, b);  // кожен байт даних — у CRC
        if (p->idx >= p->len)           // зібрали всі дані
            p->state = READ_CRC;
        return false;

    case READ_CRC:
        p->state = WAIT_SYNC;           // хай там що — далі знову чекаємо SYNC
        if (b == p->crc) {              // CRC зійшовся — кадр цілий
            return true;                // дані готові до вжитку
        }
        return false;                   // CRC не зійшовся — кадр тихо відкинуто
    }
    return false;
}
