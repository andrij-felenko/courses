#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct {
    uint32_t regs[4]; // R0, R1, R2, R3
    uint32_t pc;      // Guest Program Counter
    uint32_t zf;      // Zero Flag (1 або 0)
    bool     halted;  // Прапорець завершення роботи
} GuestContext;
