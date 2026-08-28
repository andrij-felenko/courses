// Пройти ОДИН каскадний рівень із повною обробкою колізій.
// Повертає 4 байти блоку (uid_out) і SAK. Обробляє довільну кількість
// карток у цій гілці, спускаючись деревом до єдиної.
static pcd_status_t select_level(uint8_t sel,
                                 uint8_t uid_out[4], uint8_t *sak_out)
{
    uint8_t buf[9];
    uint8_t rx[5], rx_len, coll_pos;
    uint8_t known = 0;                     // відомих біт UID цього каскаду (0..32)

    // Буфер занулюємо ПОВНІСТЮ: біти UID накопичуємо через OR (|=), тож
    // незаповнені позиції buf[2..6] мусять стартувати з 0 — інакше перший
    // же OR змішає UID зі сміттям, що лежало на стеку, і SELECT піде з
    // побитим ідентифікатором.
    memset(buf, 0, sizeof(buf));
    buf[0] = sel;

    for (;;) {
        // ── Спакувати NVB і розріз за поточним `known` ──
        uint8_t whole = known / 8;         // повних байтів UID відомо
        uint8_t rem   = known % 8;         // зайвих біт у частковому байті
        uint8_t tx_last_bits, tx_len, rx_align;

        if (known >= 32) {
            // Усі 32 біти відомі → це вже SELECT, а не ANTICOLLISION.
            buf[1] = 0x70;                 // NVB = 7 байтів
            buf[6] = buf[2] ^ buf[3] ^ buf[4] ^ buf[5];   // BCC
            pcd_crc_a(buf, 7, &buf[7]);    // + CRC_A
            tx_len = 9; tx_last_bits = 0; rx_align = 0;
        } else {
            // ANTICOLLISION: передаємо SEL, NVB і `known` біт UID.
            buf[1] = ((2 + whole) << 4) | rem;            // NVB із точністю до біта
            tx_len = 2 + whole + (rem ? 1 : 0);           // байтів у кадрі
            tx_last_bits = rem;                           // розріз останнього байта
            rx_align = rem;                               // відповідь ляже з того ж біта
        }

        rx_len = sizeof(rx);
        pcd_status_t s = pcd_transceive(buf, tx_len, tx_last_bits,
                                        rx, &rx_len, rx_align, &coll_pos);

        if (s == PCD_COLLISION) {
            // Колізія на біті coll_pos (1..32). Довизначаємо цей біт = 1
            // і подовжуємо префікс. Зшиваємо прийняте з нашим буфером.
            //
            // coll_pos — абсолютний номер біта UID (1-based). Індекс байта в
            // buf[2..5] і номер біта в ньому:
            uint8_t bit_idx  = coll_pos - 1;              // 0-based біт UID
            uint8_t byte_i   = 2 + bit_idx / 8;           // байт у буфері
            uint8_t bit_in_b = bit_idx % 8;

            // Спершу вклеїмо частину, яку картка ВСТИГЛА договорити до колізії,
            // — фронтенд поклав її в rx з вирівнюванням rx_align. Для простоти
            // копіюємо повернені байти поверх ще невідомих позицій буфера:
            uint8_t whole_rx = (coll_pos) / 8;            // цілих нових байтів
            for (uint8_t i = 0; i <= whole_rx && (2 + i) <= byte_i; i++)
                if (i < rx_len) buf[2 + i] |= rx[i];      // OR, бо старші біти вже стоять

            // Тепер виставляємо колізійний біт у 1 (обрана гілка):
            buf[byte_i] |= (uint8_t)(1u << bit_in_b);
            known = coll_pos;                             // префікс подовжено
            continue;                                     // новий прохід, глибше
        }

        if (s != PCD_OK)
            return PCD_ERR;

        if (known >= 32) {
            // Це була відповідь на SELECT → rx[0] = SAK.
            memcpy(uid_out, &buf[2], 4);   // віддаємо зібрані 4 байти блоку UID
            *sak_out = rx[0];
            return PCD_OK;
        }

        // Відповідь на ANTICOLLISION без колізії: картка договорила весь блок.
        // rx містить решту UID+BCC, вирівняну по rx_align — доклеїмо й перевіримо.
        for (uint8_t i = 0; i < rx_len && (whole + i) < 5; i++)
            buf[2 + whole + i] |= rx[i];
        known = 32;                                        // тепер знаємо все → наступний прохід зробить SELECT
    }

    // сюди не доходимо
}
