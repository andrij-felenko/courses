#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Означення структури апаратного інтерфейсу GPIO для драйвера 74HC165
typedef struct {
    void (*set_pl)(bool state);    // Функція керування лінією PL (Parallel Load)
    void (*set_cp)(bool state);    // Функція керування лінією CP (Clock Pulse)
    bool (*read_q7)(void);         // Функція зчитування лінії Q7 (Data Out)
    void (*delay_us)(uint32_t us);  // Функція мікросекундної затримки
} shift165_hw_t;

// Ініціалізація та первинне налаштування ліній драйвера
void shift165_init(const shift165_hw_t *hw) {
    if (hw == NULL) return;
    // Початковий стан: PL у високому рівні (режим зсуву), CP у низькому
    hw->set_pl(true);
    hw->set_cp(false);
}

// Зчитування масиву байтів із N каскадованих регістрів 74HC165 (MSB First)
bool shift165_read_bytes(const shift165_hw_t *hw, uint8_t *buffer, uint8_t num_chips) {
    if (hw == NULL || buffer == NULL || num_chips == 0) {
        return false;
    }

    // 1. Асинхронна фіксація даних: короткий від'ємний імпульс PL
    hw->set_pl(false);
    hw->delay_us(1); // Гарантування мінімальної тривалості t_w_PL
    hw->set_pl(true);
    hw->delay_us(1);

    // 2. Послідовне зчитування байтів з каскаду.
    // Першим зчитується останній чип у ланцюжку (підключений безпосередньо до MCU)
    for (int8_t chip = num_chips - 1; chip >= 0; chip--) {
        uint8_t byte_val = 0;

        for (uint8_t bit = 0; bit < 8; bit++) {
            // Зсув накопиченого значення вліво на 1 позицію
            byte_val <<= 1;

            // Зчитування поточного стану виходу Q7
            if (hw->read_q7()) {
                byte_val |= 0x01;
            }

            // Формування тактового імпульсу CP для висування наступного біта
            // Спад імпульсу подається після зчитування поточного значення
            hw->set_cp(true);
            hw->delay_us(1);
            hw->set_cp(false);
            hw->delay_us(1);
        }

        buffer[chip] = byte_val;
    }

    return true;
}
