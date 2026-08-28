// Універсальний помічник: ставить альтернативну функцію af (0..15)
// на ніжку pin (0..15) порту port — сам обирає AFRL/AFRH і зсув.
static inline void gpio_set_af(GPIO_TypeDef *port, uint32_t pin, uint32_t af) {
    // режим → альтернативна функція
    port->MODER &= ~(0b11u << (pin * 2));
    port->MODER |=  (0b10u << (pin * 2));
    // функція: індекс регістра pin/8 (0 для 0–7, 1 для 8–15),
    //          зсув у ньому (pin % 8) * 4
    uint32_t idx = pin >> 3;            // pin / 8
    uint32_t shift = (pin & 7u) * 4u;   // (pin % 8) * 4
    port->AFR[idx] &= ~(0xFu << shift);
    port->AFR[idx] |=  ((af & 0xFu) << shift);
}
