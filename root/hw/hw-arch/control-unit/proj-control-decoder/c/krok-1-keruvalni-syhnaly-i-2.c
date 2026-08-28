#define NREG 16
#define MEMSZ 256

typedef struct {
    uint16_t reg[NREG];      // регістри загального призначення
    uint8_t  mem[MEMSZ];     // "повільна" пам'ять

    uint16_t addr_bus;       // що зараз на шині адреси
    uint16_t data_bus;       // що зараз на шині даних
    bool     mem_ready;      // пам'ять підняла "дані готові"

    // модель повільної пам'яті: скільки тактів ще "їхати" до відповіді
    int      mem_countdown;
} Datapath;
