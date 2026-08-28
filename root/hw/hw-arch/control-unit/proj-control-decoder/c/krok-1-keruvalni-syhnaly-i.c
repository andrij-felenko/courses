#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

// Сигнали керування — набір ліній НА ОДИН ТАКТ.
// Кожне поле — окремий "дріт": що вмикаємо саме цього такту.
typedef struct {
    bool     addr_out;   // виставити адресу на шину
    bool     mem_read;   // лінія шини "читаю"
    bool     mem_write;  // лінія шини "пишу"
    bool     alu_enable; // подати операнди на АЛП і взяти результат
    uint8_t  alu_op;     // яку операцію ввімкнути в АЛП
    bool     reg_write;  // защіпнути результат/дані у регістр призначення
    uint8_t  reg_dst;    // куди защіпувати
    uint8_t  reg_a;      // операнди для АЛП / регістр-джерело адреси
} Control;

enum { ALU_ADD, ALU_SUB, ALU_PASS };   // операції АЛП
