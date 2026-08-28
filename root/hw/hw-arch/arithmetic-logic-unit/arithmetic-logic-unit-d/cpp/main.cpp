#include <cstdint>
#include <cstdio>

// Спрощений АЛП: одна лінія sub перемикає додавання/віднімання.
// Повертає 8-бітний результат; через cout віддає перенос-вихід.
uint8_t alu_addsub(uint8_t a, uint8_t b, uint8_t sub, uint8_t &cout) {
    uint8_t b_eff = b ^ (sub ? 0xFF : 0x00);   // sub=1 інвертує всі біти B (~B)
    uint16_t wide = (uint16_t)a + b_eff + sub;  // +sub додає ту саму +1
    cout = (wide >> 8) & 1;                      // 9-й біт — перенос-вихід
    return (uint8_t)wide;                        // молодші 8 бітів — результат
}

int main() {
    uint8_t carry;
    uint8_t r = alu_addsub(7, 5, 1, carry);      // 7 − 5
    std::printf("7 - 5 = %u, carry=%u\n", r, carry);  // 7 - 5 = 2, carry=1
}
