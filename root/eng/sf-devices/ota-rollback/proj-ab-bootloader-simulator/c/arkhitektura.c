typedef struct {
    uint32_t magic;              /* Магічне число валідності (0xDEADBEEF) */
    uint32_t reset_reason;       /* Прапорці регістру RCC_CSR (IWDG, PIN, POR, SFT) */
    uint32_t cfsr;               /* Регістр Configurable Fault Status Register */
    uint32_t hfsr;               /* Регістр HardFault Status Register */
    uint32_t mmar;               /* Регістр адреси помилки пам'яті MemManage Fault */
    uint32_t bfar;               /* Регістр адреси помилки шини Bus Fault */
    uint32_t pc;                 /* Вказівник інструкції Program Counter у момент краху */
    uint32_t lr;                 /* Регістр зв'язку Link Register */
    uint32_t sp;                 /* Вказівник стека Stack Pointer */
    uint32_t stack_snapshot[64]; /* Знімок останніх 64 слів стека */
    uint32_t dump_crc;           /* Контрольна сума CRC32 для валідації */
} __attribute__((packed)) crash_dump_t;

__attribute__((section(".noinit"))) static crash_dump_t g_crash_dump;
