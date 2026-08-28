#include <string.h>

static uint8_t key[6] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };  // заводський ключ FF·6
static const uint8_t block = 4;   // перший блок даних сектора 1

// CRC_A рахує сам чип: команда CalcCRC, результат у CRCResultReg
static void crc_a(const uint8_t *d, int n, uint8_t *out) {
    wr(0x01, 0x00); wr(0x05, 0x04); wr(0x0A, 0x80);  // Idle, скинути CRCIRq, чистити FIFO
    for (int i = 0; i < n; i++) wr(0x09, d[i]);
    wr(0x01, 0x03);                                  // CommandReg = CalcCRC
    while (!(rd(0x05) & 0x04)) { }                   // DivIrqReg.CRCIRq
    out[0] = rd(0x22); out[1] = rd(0x21);            // молодший байт, тоді старший
}

// КРОК 1: довести знання ключа A саме для цього сектора
static int authenticate(const uint8_t *uid) {
    uint8_t f[12] = { 0x60, block };                 // 0x60 — автентифікація ключем A
    memcpy(f + 2, key, 6);
    memcpy(f + 8, uid, 4);                           // 4 байти UID цієї мітки
    wr(0x01, 0x00); wr(0x04, 0x7F); wr(0x0A, 0x80);
    for (int i = 0; i < 12; i++) wr(0x09, f[i]);
    wr(0x01, 0x0E);                                  // CommandReg = MFAuthent
    for (int i = 0; i < 20 && !(rd(0x04) & 0x10); i++) HAL_Delay(1);
    return rd(0x08) & 0x08;                          // Status2Reg.MFCrypto1On — ключ підійшов
}

void read_block(const uint8_t *uid) {
    char line[64];  int k = 0;
    if (!authenticate(uid)) {
        k = snprintf(line, sizeof line, "Ключ не підійшов — сектор замкнений\r\n");
        HAL_UART_Transmit(&huart2, (uint8_t *)line, k, HAL_MAX_DELAY);
        return;                                      // без ключа далі ходу немає
    }
    // КРОК 2: сектор відкритий — читаємо блок (кадр 0x30, номер, CRC_A)
    uint8_t cmd[4] = { 0x30, block }, buf[18];       // 16 байтів даних + 2 контрольної суми
    crc_a(cmd, 2, cmd + 2);
    if (transceive(cmd, 4, 0, buf, 18) >= 16) {
        for (int i = 0; i < 16; i++)
            k += snprintf(line + k, sizeof line - k, "%02X ", buf[i]);
        k += snprintf(line + k, sizeof line - k, "\r\n");
        HAL_UART_Transmit(&huart2, (uint8_t *)line, k, HAL_MAX_DELAY);
    }
    wr(0x08, rd(0x08) & ~0x08);   // ЗАВЖДИ зняти MFCrypto1On після роботи
}
