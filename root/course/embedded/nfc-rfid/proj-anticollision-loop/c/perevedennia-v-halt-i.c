// Приспати щойно вибрану картку: вона більше не відповідає на REQA,
// доки не вимкнути й увімкнути поле (або поки не прийде WUPA).
static void picc_halt(void)
{
    uint8_t frame[4] = { CMD_HLTA, 0x00, 0, 0 };
    uint8_t rx[1], rx_len = 0, coll;
    pcd_crc_a(frame, 2, &frame[2]);          // HLTA = 0x50 0x00 + CRC_A (= 0x57 0xCD)
    // Особливість: коректна картка на HLTA НЕ відповідає взагалі.
    // «Успіх» тут — це TIMEOUT (тиша), а не OK. Тому відповідь ігноруємо.
    (void)pcd_transceive(frame, 4, 0, rx, &rx_len, 0, &coll);
}
