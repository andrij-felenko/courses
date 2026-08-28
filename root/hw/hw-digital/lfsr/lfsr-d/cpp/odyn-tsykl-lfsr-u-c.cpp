#include <stdint.h>

// Відводи многочлена x^4 + x + 1 — це біти 3 і 0.
static uint8_t lfsr4_step(uint8_t state) {   // state — 4 молодші біти
    uint8_t b3 = (state >> 3) & 1u;          // старший відвід
    uint8_t b0 =  state       & 1u;          // молодший відвід
    uint8_t feedback = b3 ^ b0;              // XOR — новий біт
    state = (uint8_t)((state << 1) | feedback) & 0x0Fu;  // зсув ліворуч + вкидання
    return state;
}
