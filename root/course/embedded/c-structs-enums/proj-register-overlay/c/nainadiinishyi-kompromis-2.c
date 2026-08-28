#include <stdint.h>
#include <stddef.h>

typedef struct {
    volatile uint32_t fifo;          // 0x00 — регістр даних FIFO
    volatile uint32_t _rsvd[6];      // 0x04..0x18 — тут інші регістри UART
    UartStatus        status;        // 0x1C — наш статус (union слово+біти)
    volatile uint32_t conf0;         // 0x20 — регістр конфігурації
} UartRegs;

// Вартові розкладки: кожен регістр МУСИТЬ лягти за своїм зсувом із даташита.
// Якщо структура з'їхала (набивка, зайве поле) — збірка впаде ТУТ.
_Static_assert(offsetof(UartRegs, fifo)   == 0x00, "fifo зсув!");
_Static_assert(offsetof(UartRegs, status) == 0x1C, "status зсув!");
_Static_assert(offsetof(UartRegs, conf0)  == 0x20, "conf0 зсув!");

// Покажчик на весь блок = базова адреса периферії:
#define UART0   ((UartRegs *)0x3FF40000u)

// Тепер уся периферія доступна як поля однієї структури:
static inline uint8_t rx_waiting(void) {
    return (uint8_t)(UART0->status.word & 0xFF);   // чесно, масками зі слова
}
