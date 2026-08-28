#include <stdint.h>
#include <stddef.h>

// Символи з linker-скрипта. Нас цікавить їхня АДРЕСА, не значення.
extern uint8_t _end;       // кінець .bss — нижній край вільної RAM
extern uint8_t _estack;    // початкова вершина стека — верхній край

#define STACK_PATTERN  0xA5u

static uint8_t * const stack_lo = &_end;       // дно вільної ділянки (низька адреса)
static uint8_t * const stack_hi = &_estack;    // вершина стека (висока адреса)
