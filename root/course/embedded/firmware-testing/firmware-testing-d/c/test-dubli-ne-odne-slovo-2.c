// ШПИГУН за драйвером шини: робить вигляд, що шле байт, але запам'ятовує що й скільки
static uint8_t spy_bytes[64];
static int     spy_count = 0;

int bus_send(uint8_t b) {
    if (spy_count < 64) spy_bytes[spy_count++] = b;   // нотуємо
    return 0;                                          // ніби успішно надіслали
}
// ...пізніше в тесті:
//   assert(spy_count == 2);
//   assert(spy_bytes[0] == 0xA0 && spy_bytes[1] == 0x01);
