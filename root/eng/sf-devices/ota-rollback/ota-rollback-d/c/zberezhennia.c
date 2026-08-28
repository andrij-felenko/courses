typedef struct {
    uint32_t magic;            /* Маркер наявності аварійного дампу (0xDEADBEEF) */
    uint32_t reset_reason;     /* Причина скидання з регістрів RCC->CSR */
    uint32_t fault_cfsr;       /* Configurable Fault Status Register (SCB->CFSR) */
    uint32_t fault_hfsr;       /* HardFault Status Register (SCB->HFSR) */
    uint32_t fault_mmfar;      /* MemManage Fault Address Register (SCB->MMFAR) */
    uint32_t fault_bfar;       /* BusFault Address Register (SCB->BFAR) */
    uint32_t stacked_r0;       /* Значення регістрів на момент виникнення винятку */
    uint32_t stacked_r1;
    uint32_t stacked_r2;
    uint32_t stacked_r3;
    uint32_t stacked_r12;
    uint32_t stacked_lr;       /* Link Register (адреса виклику) */
    uint32_t stacked_pc;       /* Program Counter (адреса збійної інструкції) */
    uint32_t stacked_psr;      /* Program Status Register */
    uint32_t crc32;            /* Контрольна сума дампу */
} __attribute__((packed)) crash_dump_t;
