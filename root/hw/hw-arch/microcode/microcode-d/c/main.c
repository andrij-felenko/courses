#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

typedef enum { UOP_LOAD, UOP_ADD, UOP_STORE, UOP_END } Uop;

// Рецепт = послідовність мікрооперацій, що завершується UOP_END.
typedef struct { const Uop *seq; } Recipe;

// «ROM мікрокоду»: рецепт на кожну машинну команду.
enum { OP_ADD, OP_ADDM, OP_COUNT };

static const Uop rom_add[]   = { UOP_ADD, UOP_END };
// УВАГА: у цьому рецепті помилка — бракує UOP_STORE (результат не збережеться).
static const Uop rom_addm[]  = { UOP_LOAD, UOP_ADD, UOP_END };

static const Recipe rom[OP_COUNT] = {
    [OP_ADD]  = { rom_add },
    [OP_ADDM] = { rom_addm },
};

// «patch RAM»: спершу порожня (усі покажчики NULL) — заповнює прошивка на старті.
static const Uop *patch[OP_COUNT] = { 0 };

// Рушій: вибрати рецепт (патч має пріоритет над ROM) і виконати мікрооперації.
void run_instruction(int opcode) {
    const Uop *seq = patch[opcode] ? patch[opcode]   // є патч → беремо його
                                   : rom[opcode].seq; // інакше — рідний ROM
    for (int i = 0; seq[i] != UOP_END; i++) {
        switch (seq[i]) {
        case UOP_LOAD:  puts("  µop: load  t <- [mem]"); break;
        case UOP_ADD:   puts("  µop: add   t += reg");   break;
        case UOP_STORE: puts("  µop: store [mem] <- t"); break;
        default: break;
        }
    }
}

// Виправлений рецепт ADDM — уже з кроком збереження.
static const Uop fixed_addm[] = { UOP_LOAD, UOP_ADD, UOP_STORE, UOP_END };

// Прошивка на старті заливає патч у patch RAM (тут — після перевірки підпису).
void load_microcode_patch(void) {
    patch[OP_ADDM] = fixed_addm;   // підмінити помилковий рецепт виправленим
}

int main(void) {
    puts("ADDM до патча (помилковий рецепт, без store):");
    run_instruction(OP_ADDM);

    load_microcode_patch();        // <- те, що робить BIOS/ОС на кожному старті

    puts("ADDM після патча (виправлено):");
    run_instruction(OP_ADDM);
    return 0;
}
