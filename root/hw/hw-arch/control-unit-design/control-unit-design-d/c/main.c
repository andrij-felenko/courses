#include <stdint.h>
#include <stdbool.h>

// Одна горизонтальна мікрокоманда: керувальні біти прямо, плюс керування μPC.
typedef struct {
    // --- керувальні лінії (кожен біт = один "дріт") ---
    bool alu_add, alu_sub;     // яку операцію ввімкнути в АЛП
    bool reg_write;            // защіпнути результат у регістр
    bool mem_read;             // читати з пам'яті шиною
    // --- керування послідовністю ---
    uint8_t cond;              // на який прапорець дивитися (0 = безумовно)
    uint16_t next;             // куди вести μPC на розвилці
} Micro;

enum { COND_NONE = 0, COND_ZERO, COND_CARRY };   // вибір умови

// Прапорці стану від АЛП (те, на що дивиться логіка наступної адреси).
typedef struct { bool zero, carry; } Flags;

extern Micro   store[];        // сховище мікрокоманд (control store)
extern void    apply(const Micro *m);   // виставити біти рядка на дроти
extern Flags   alu_flags;      // поточний стан від АЛП

// Один такт мікрорушія: прочитати рядок, виконати, порахувати наступну адресу.
uint16_t micro_step(uint16_t upc) {
    Micro m = store[upc];      // ЧИТАННЯ зі сховища — саме цей зайвий такт
    apply(&m);                 // біти рядка йдуть прямо на керувальні лінії

    // --- логіка наступної адреси (друга машина — послідовність) ---
    bool take = false;
    switch (m.cond) {          // чи спрацювала умова розгалуження?
    case COND_ZERO:  take = alu_flags.zero;  break;
    case COND_CARRY: take = alu_flags.carry; break;
    case COND_NONE:  take = false;           break;  // просто далі
    }
    return take ? m.next : (uint16_t)(upc + 1);   // стрибок або наступний рядок
}
