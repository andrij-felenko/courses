typedef struct {
    char*        sName;             /* Назва каналу (наприклад, "Terminal") */
    char*        pBuffer;           /* Вказівник на масив буфера в SRAM */
    unsigned int SizeOfBuffer;      /* Розмір буфера в байтах */
    unsigned int WrOff;             /* Зсув запису (пише MCU) */
    unsigned int RdOff;             /* Зсув читання (пише Host) */
    unsigned int Flags;             /* Режим: SKIP / TRIM / BLOCK */
} SEGGER_RTT_BUFFER;

typedef struct {
    char              acID[16];          /* Сигнатурний рядок "SEGGER RTT" */
    int               MaxNumUpBuffers;   /* Кількість каналів виводу MCU -> Host */
    int               MaxNumDownBuffers; /* Кількість каналів вводу Host -> MCU */
    SEGGER_RTT_BUFFER aUp[3];            /* Канали передачі */
    SEGGER_RTT_BUFFER aDown[3];          /* Канали прийому */
} SEGGER_RTT_CB;
