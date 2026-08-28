#include <stdint.h>

// --- Розкладка пінів (приклад; підстав свої порт і номери) ---
// Три адресні лінії 74HC138: A0, A1, A2
#define ADDR_PORT   GPIOB
#define A0_PIN      0
#define A1_PIN      1
#define A2_PIN      2

// Вхід дозволу дешифратора, куди подаємо СТРОБ.
// Беремо активний-низький вхід (E1 або E2 у 74HC138):
// дешифратор увімкнено, коли тут 0; вимкнено, коли 1.
#define STROBE_PORT GPIOB
#define STROBE_PIN  3          // -> на Ē1 дешифратора (активний нулем)

// BSRR: запис 1 у молодшу половину ВСТАНОВЛЮЄ біт,
//       запис 1 у старшу половину (│<<16) СКИДАЄ біт. Обидва — атомарно.
static inline void pin_high(GPIO_TypeDef *port, uint32_t pin) {
    port->BSRR = (1u << pin);
}
static inline void pin_low(GPIO_TypeDef *port, uint32_t pin) {
    port->BSRR = (1u << (pin + 16));
}
