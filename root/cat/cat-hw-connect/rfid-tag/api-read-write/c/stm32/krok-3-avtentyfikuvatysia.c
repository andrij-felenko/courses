// Ті самі чотири кроки; замість Serial — UART, замість StatusCode — свій enum.
static const uint8_t key_a[6] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };  // заводський ключ

uint8_t block = 4;
uint8_t buf[18];                  // 16 байтів даних + 2 байти CRC — МУСИТЬ бути 18
uint8_t size = sizeof(buf);       // передаємо ЄМНІСТЬ буфера (18), не 16
char    line[80];
int     k;

// КРОК 2: довести знання ключа A саме цього сектора (команда чипа MFAuthent).
picc_status_t st = pcd_authenticate(PICC_CMD_MF_AUTH_KEY_A, block, key_a, uid, uid_len);
if (st != PICC_OK) {
    k = snprintf(line, sizeof line, "Автентифікація не вдалась: %s\r\n", picc_status_name(st));
    HAL_UART_Transmit(&huart2, (uint8_t *)line, k, HAL_MAX_DELAY);
    picc_halt_a();
    pcd_stop_crypto1();           // навіть після невдачі — опустити шифрування
    return;
}

// КРОК 3: сектор відкрито — читаємо 16 байтів блока
st = mifare_read(block, buf, &size);
if (st == PICC_OK) {
    k = snprintf(line, sizeof line, "Блок %u:", block);
    for (uint8_t i = 0; i < 16; i++)           // друкуємо ЛИШЕ 16, не 18
        k += snprintf(line + k, sizeof line - k, " %02X", buf[i]);
    k += snprintf(line + k, sizeof line - k, "\r\n");
} else {
    k = snprintf(line, sizeof line, "Читання не вдалось: %s\r\n", picc_status_name(st));
}
HAL_UART_Transmit(&huart2, (uint8_t *)line, k, HAL_MAX_DELAY);

picc_halt_a();                    // відпустити мітку
pcd_stop_crypto1();               // ОБОВ'ЯЗКОВО опустити шифрування
