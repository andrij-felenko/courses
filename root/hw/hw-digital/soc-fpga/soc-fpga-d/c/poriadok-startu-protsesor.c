#include <stdint.h>

// Тканина після скидання порожня. Процесор сам заливає в неї бітстрім,
// а вже потім бачить її реєстри як звичайну пам'ять за адресами.

#define PL_ACCEL_BASE   0x43C00000u        // адреса нашого блока в тканині
#define REG_CONTROL     (*(volatile uint32_t *)(PL_ACCEL_BASE + 0x00))
#define REG_STATUS      (*(volatile uint32_t *)(PL_ACCEL_BASE + 0x04))
#define CTRL_ENABLE     0x1u

int soc_bring_up(const void *bitstream, uint32_t len) {
    // 1. Процесор ллє бітстрім у тканину — тканина набуває схеми.
    if (fpga_load_bitstream(bitstream, len) != 0)
        return -1;                          // конфігурація не вдалася

    // 2. Тепер реєстри блока в тканині доступні як пам'ять — вмикаємо його.
    REG_CONTROL = CTRL_ENABLE;

    // 3. Чекаємо, поки блок звітує про готовність (біт 0 у STATUS).
    while ((REG_STATUS & 0x1u) == 0)
        ;                                   // тканина ще піднімається
    return 0;                               // гібрид готовий до роботи
}
