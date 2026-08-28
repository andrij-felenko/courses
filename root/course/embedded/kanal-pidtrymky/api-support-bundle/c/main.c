typedef struct __attribute__((packed)) {
    uint32_t r0;          /* Регістр загального призначення R0 */
    uint32_t r1;          /* Регістр загального призначення R1 */
    uint32_t r2;          /* Регістр загального призначення R2 */
    uint32_t r3;          /* Регістр загального призначення R3 */
    uint32_t r12;         /* Внутрішньопроцедурний регістр виклику R12 */
    uint32_t lr;          /* Регістр зв'язку (Link Register — адреса повернення) */
    uint32_t pc;          /* Лічильник команд (Program Counter — адреса падіння) */
    uint32_t xpsr;        /* Стан процесора (Program Status Register) */
    uint32_t msp;         /* Вказівник основного стека (Main Stack Pointer) */
    uint32_t psp;         /* Вказівник стека процесів (Process Stack Pointer) */
    uint32_t cfsr;        /* Configurable Fault Status Register (UFSR + BFSR + MMFSR) */
    uint32_t hfsr;        /* HardFault Status Register */
    uint32_t mmfar;       /* Memory Management Fault Address Register */
    uint32_t bfar;        /* BusFault Address Register */
    uint32_t active_task; /* Числовий ID або перші 4 літери імені таски FreeRTOS */
    uint32_t stack_high_water; /* Мінімальний залишок пам'яті стека в байтах */
} fault_context_t;
