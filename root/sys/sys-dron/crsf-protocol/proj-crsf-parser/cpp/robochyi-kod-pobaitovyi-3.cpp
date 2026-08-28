// Прототип обробника готового кадру (визначимо нижче)
static void crsf_dispatch(const uint8_t *frame, uint8_t len);

// Проштовхнути ОДИН байт із UART. Викликає crsf_dispatch, коли кадр цілий.
void crsf_parser_push(CrsfParser *p, uint8_t byte) {
    switch (p->state) {

    case ST_SYNC:
        // Викидаємо все, крім старту. Це і є (ре)синхронізація.
        if (byte == CRSF_SYNC_BYTE)
            p->state = ST_LEN;
        break;

    case ST_LEN:
        // Перша перевірка: довжина мусить бути в діапазоні.
        if (byte < CRSF_LEN_MIN || byte > CRSF_LEN_MAX) {
            // Це не довжина, а сміття → назад у пошук старту.
            // Тонкість: якщо цей байт САМ є 0xC8, він міг бути справжнім
            // стартом. Тому не просто ST_SYNC, а обробимо його як старт:
            p->state = (byte == CRSF_SYNC_BYTE) ? ST_LEN : ST_SYNC;
            break;
        }
        p->buf[0] = byte;   // збережемо довжину в буфер (стане в пригоді)
        p->need   = byte;   // стільки байтів тіла ще прийде
        p->got    = 0;
        p->state  = ST_BODY;
        break;

    case ST_BODY:
        // Добираємо тіло. buf[0] — довжина, buf[1..] — тип+дані+CRC.
        p->buf[1 + p->got] = byte;
        p->got++;
        if (p->got < p->need)
            break;   // кадр іще не повний — чекаємо наступних байтів

        // Кадр повний. Перевіряємо CRC над типом+даними (без самого CRC).
        {
            const uint8_t *type_and_payload = &p->buf[1];      // з типу
            uint8_t crc_len  = (uint8_t)(p->need - 1);          // тип+дані
            uint8_t crc_calc = crsf_crc8(type_and_payload, crc_len);
            uint8_t crc_recv = p->buf[1 + p->need - 1];         // останній байт

            if (crc_calc == crc_recv) {
                // Цілий кадр! Віддаємо тіло (тип+дані+CRC) диспетчеру.
                crsf_dispatch(&p->buf[1], p->need);
            }
            // І збіг, і промах ведуть в один бік: новий кадр з чистого аркуша.
            crsf_parser_reset(p);
        }
        break;
    }
}
