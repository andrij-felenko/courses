// Записати нове значення в кільце (WL_DATA_LEN байтів). Розмазує знос і
// переживає обрив живлення: новий слот пишеться в наступну позицію, стара
// голова недоторкана до кінця запису; дійсним новий стає лише з правильною CRC.
void wl_put(wl_ring_t *r, const uint8_t *data) {
    // 1. Наступний слот по колу (найстаріший — його й затираємо).
    uint16_t next_slot = (uint16_t)((r->head_slot + 1) % WL_SLOTS);
    uint32_t next_seq  = r->head_seq + 1;      // монотонно росте
    if (r->head_seq == 0) { next_slot = 0; next_seq = 1; }  // перший запис у житті

    // 2. Зібрати слот у буфері: дані | послідовність | CRC (останнім байтом).
    uint8_t buf[WL_SLOT_LEN];
    memcpy(buf, data, WL_DATA_LEN);
    buf[WL_DATA_LEN + 0] = (uint8_t)(next_seq      );
    buf[WL_DATA_LEN + 1] = (uint8_t)(next_seq >>  8);
    buf[WL_DATA_LEN + 2] = (uint8_t)(next_seq >> 16);
    buf[WL_DATA_LEN + 3] = (uint8_t)(next_seq >> 24);
    buf[WL_SLOT_LEN - 1] = crc8(buf, WL_SLOT_LEN - WL_CRC_LEN);

    // 3. Записати ОДНИМ викликом. Драйвер сам поріже по сторінках і дочекається
    //    готовності EEPROM. Стара голова весь цей час ціла й недоторкана.
    eeprom_write(WL_BASE + next_slot * WL_SLOT_LEN, buf, WL_SLOT_LEN);

    // 4. Лише тепер, коли новий слот повністю ліг, зсуваємо голову в RAM.
    //    Якщо живлення впало ДО цього рядка — при старті wl_mount() усе одно
    //    знайде правильну голову за максимумом послідовності серед ЦІЛИХ слотів.
    r->head_slot = next_slot;
    r->head_seq  = next_seq;
}
