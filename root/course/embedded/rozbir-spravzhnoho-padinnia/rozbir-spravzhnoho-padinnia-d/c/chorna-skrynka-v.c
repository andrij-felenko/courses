/* Оголошення аварійного буфера в noinit секції пам'яті */
typedef struct {
    uint32_t magic_header;       /* 0xDEADBEEF для перевірки валідності */
    uint32_t reset_flags;        /* Копія регістра RCC_CSR / MCUSR */
    uint16_t last_timer_ticks;   /* Останнє зафіксоване значення таймера */
    uint16_t last_heartbeat;     /* Час останнього валідного пакету */
    uint8_t  active_task_id;     /* ID поточного завдання RTOS */
    uint8_t  last_error_code;    /* Код останнього аварійного стану */
    uint32_t crc32;              /* Контрольна сума цілісності */
} __attribute__((section(".noinit"))) crash_dump_t;

volatile crash_dump_t g_crash_dump;
