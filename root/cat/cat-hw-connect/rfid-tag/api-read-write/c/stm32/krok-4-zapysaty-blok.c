// Записати 16 байтів у блок 4. Спершу — та сама автентифікація.
static const uint8_t key_a[6] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };

uint8_t block = 4;

// Дані на запис — РІВНО 16 байтів. Тут: рядок-мітка + число балансу.
uint8_t data[16] = {
    'B', 'A', 'L', 0x00,               // сигнатура «BAL» + роздільник
    0x00, 0x00, 0x27, 0x10,            // баланс = 0x2710 = 10000 (напр. копійок)
    0x00, 0x00, 0x00, 0x00,            // решта — про запас, нулі
    0x00, 0x00, 0x00, 0x00
};
char line[80];
int  k;

picc_status_t st = pcd_authenticate(PICC_CMD_MF_AUTH_KEY_A, block, key_a, uid, uid_len);
if (st != PICC_OK) {
    k = snprintf(line, sizeof line, "Авт. перед записом не вдалась: %s\r\n", picc_status_name(st));
    HAL_UART_Transmit(&huart2, (uint8_t *)line, k, HAL_MAX_DELAY);
    picc_halt_a();
    pcd_stop_crypto1();
    return;
}

// Запис: РІВНО 16 байтів, розмір теж 16 — CRC додає рівень протоколу
st = mifare_write(block, data, 16);
k = (st == PICC_OK)
      ? snprintf(line, sizeof line, "Записано.\r\n")
      : snprintf(line, sizeof line, "Запис не вдався: %s\r\n", picc_status_name(st));
HAL_UART_Transmit(&huart2, (uint8_t *)line, k, HAL_MAX_DELAY);

picc_halt_a();
pcd_stop_crypto1();
