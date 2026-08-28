// Чотири засувки на межах п'яти стадій IF-ID-EX-MEM-WB.
enum { IF_ID, ID_EX, EX_MEM, MEM_WB, NLATCH };

typedef struct {
    Latch    L[NLATCH];   // засувки на межах стадій
    uint16_t pc;          // лічильник команд
    int32_t  reg[8];      // регістровий файл
    int32_t  dmem[256];   // пам'ять даних
    bool     fetch_halted;// вибірка спинена (зустріли HALT)
} CPU;
