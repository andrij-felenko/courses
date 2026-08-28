typedef struct {            // порядок строго як кладе ядро
    uint32_t r0, r1, r2, r3, r12;
    uint32_t lr;            // звідки прийшли
    uint32_t pc;            // де саме впало
    uint32_t xpsr;
} fault_frame_t;

#define SCB_CFSR (*(volatile uint32_t *)0xE000ED28)
#define SCB_HFSR (*(volatile uint32_t *)0xE000ED2C)
#define SCB_BFAR (*(volatile uint32_t *)0xE000ED38)

void hardfault_report(fault_frame_t *frame) {
    uint32_t cfsr = SCB_CFSR;

    printf("PC   = 0x%08lx\n", frame->pc);   // → addr2line дасть рядок
    printf("LR   = 0x%08lx\n", frame->lr);   // зворотний слід
    printf("CFSR = 0x%08lx\n", cfsr);
    printf("HFSR = 0x%08lx\n", SCB_HFSR);

    if (cfsr & (1u << 9))                     // PRECISERR (біт 9)
        printf("точна шинна помилка\n");
    if (cfsr & (1u << 25))                    // DIVBYZERO (біт 25)
        printf("ділення на нуль\n");
    if (cfsr & (1u << 15))                    // BFARVALID (біт 15): адреса дійсна?
        printf("BFAR = 0x%08lx\n", SCB_BFAR);
    for (;;) { }                              // спинитись для відлагоджувача
}
