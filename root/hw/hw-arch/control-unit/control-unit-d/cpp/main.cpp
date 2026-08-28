// Керувальні сигнали — по одному "дроту" на поле (модель зашитого декодера).
typedef struct {
    uint8_t reg_a, reg_b, reg_dst; // які регістри читати / куди писати
    uint8_t alu_op;                // яку операцію ввімкнути в АЛП
    bool    reg_write;             // лінія "защіпнути результат у регістр"
    bool    mem_read;              // лінія "читати з пам'яті по шині"
} Control;

enum { OP_ADD = 0x1, OP_SUB = 0x2, OP_LOAD = 0x3 };
enum { ALU_ADD, ALU_SUB, ALU_PASS };

Control decode(uint16_t ir) {
    Control c = {0};                       // усі лінії спершу опущені (0)
    uint8_t op  = (ir >> 12) & 0xF;        // опкод      = старші 4 біти
    uint8_t dst = (ir >>  8) & 0xF;        // призначення = наступні 4
    uint8_t a   = (ir >>  4) & 0xF;        // операнд A
    uint8_t b   =  ir        & 0xF;        // операнд B

    switch (op) {                          // зіставлення опкоду зі взірцем
    case OP_ADD:                           // 0x1 → додати
        c.reg_a = a; c.reg_b = b; c.reg_dst = dst;
        c.alu_op = ALU_ADD;                // увімкнути в АЛП додавання
        c.reg_write = true;                // після рахунку — записати результат
        break;
    case OP_LOAD:                          // 0x3 → завантажити з пам'яті
        c.reg_dst = dst;
        c.mem_read = true;                 // спершу привезти число шиною
        c.reg_write = true;
        break;
    // ... решта опкодів
    }
    return c;                              // готовий набір сигналів на цей такт
}
