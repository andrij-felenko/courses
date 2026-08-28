// ФЕЙК енергонезалежного сховища: масив у RAM замість справжньої Flash.
// Інтерфейс той самий — логіка вгорі не бачить різниці.
#define FAKE_SIZE 4096
static uint8_t fake_mem[FAKE_SIZE];

int storage_write(uint32_t addr, const uint8_t *buf, uint32_t len) {
    if (addr + len > FAKE_SIZE) return -1;   // та сама перевірка меж
    for (uint32_t i = 0; i < len; ++i) fake_mem[addr + i] = buf[i];
    return 0;
}
int storage_read(uint32_t addr, uint8_t *buf, uint32_t len) {
    if (addr + len > FAKE_SIZE) return -1;
    for (uint32_t i = 0; i < len; ++i) buf[i] = fake_mem[addr + i];
    return 0;
}
