// Один каскадний рівень БЕЗ обробки колізій (одна картка в полі).
// sel      — SEL_CL1/CL2/CL3
// uid_out  — сюди пишемо 4 байти блоку цього каскаду (UID0..3 або CT+UID)
// sak_out  — сюди байт SAK
static pcd_status_t select_level_single(uint8_t sel,
                                        uint8_t uid_out[4], uint8_t *sak_out)
{
    uint8_t frame[9];
    uint8_t rx[5], rx_len, coll;

    // ── Фаза ANTICOLLISION: «шліть увесь блок UID» ──
    frame[0] = sel;
    frame[1] = 0x20;                       // NVB: 2 байти відомо (лише SEL+NVB)
    rx_len = sizeof(rx);
    pcd_status_t s = pcd_transceive(frame, 2, 0, rx, &rx_len, 0, &coll);
    if (s != PCD_OK || rx_len != 5)        // очікуємо UID0..3 + BCC = 5 байтів
        return (s == PCD_COLLISION) ? PCD_COLLISION : PCD_ERR;

    // Перевірка BCC: контрольний XOR має збігтися.
    if ((rx[0] ^ rx[1] ^ rx[2] ^ rx[3]) != rx[4])
        return PCD_ERR;                    // побитий кадр
    memcpy(uid_out, rx, 4);

    // ── Фаза SELECT: «беру цей UID цілком» ──
    frame[0] = sel;
    frame[1] = 0x70;                       // NVB: усі 7 байтів (32 біти UID) відомі
    memcpy(&frame[2], rx, 5);              // UID0..3 + BCC
    pcd_crc_a(frame, 7, &frame[7]);        // CRC_A над SEL..BCC → frame[7],frame[8]

    rx_len = sizeof(rx);
    s = pcd_transceive(frame, 9, 0, rx, &rx_len, 0, &coll);
    if (s != PCD_OK || rx_len < 1)
        return PCD_ERR;

    *sak_out = rx[0];                      // SAK (SAK+CRC — фронтенд перевірить CRC сам)
    return PCD_OK;
}
