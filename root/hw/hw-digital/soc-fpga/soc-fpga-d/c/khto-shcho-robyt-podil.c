#include <stdint.h>

#define ACCEL_BASE   0x43C00000u
#define REG_CTRL     (*(volatile uint32_t *)(ACCEL_BASE + 0x00))
#define REG_RESULT   (*(volatile uint32_t *)(ACCEL_BASE + 0x08))  // підсумок з тканини
#define REG_COUNT    (*(volatile uint32_t *)(ACCEL_BASE + 0x0C))  // скільки відліків оброблено

#define THRESHOLD    100000u

void supervise(void) {
    REG_CTRL = 0x1u;                        // «працюй» — далі тканина сама

    for (;;) {
        // Процесор НЕ чіпає окремі відліки: їх фільтрує тканина паралельно,
        // ловлячи кожен на своїй частоті. Процесор бачить лише підсумок.
        uint32_t level = REG_RESULT;        // готове число з тканини за адресою

        if (level > THRESHOLD) {
            // Розгалужене «розумне» рішення — це робота саме процесора:
            log_event(level, REG_COUNT);    // запис у файл, повідомлення в мережу
            raise_alarm();
        }
        sleep_ms(10);                       // процесор неспішний — тканина встигає
    }
}
