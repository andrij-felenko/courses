// Один такт роботи пристрою керування.
// Повертає сигнали, ВИСТАВЛЕНІ цього такту (зручно для трасування/тестів).
Control cu_step(ControlUnit *cu, Datapath *dp) {
    Control c = {0};   // усі лінії спершу опущені — це важливо (див. пастки)

    switch (cu->stage) {

    case S_FETCH:
        // Привезти команду за PC у IR. (Модель: пам'ять команд миттєва.)
        cu->ir = ((uint16_t)dp->mem[cu->pc] << 8) | dp->mem[cu->pc + 1];
        cu->pc += 2;
        cu->stage = S_DECODE;
        break;

    case S_DECODE:
        decode_fields(cu);                 // розкласти опкод і поля
        switch (cu->op) {                  // обрати ПЛАН за опкодом
        case OP_ADD:
        case OP_SUB:   cu->stage = S_CALC;       break;  // регістрова: одразу рахуємо
        case OP_LOAD:  cu->stage = S_ADDR;       break;  // з пам'яті: спершу адреса
        case OP_STORE: cu->stage = S_ADDR;       break;
        default:       cu->stage = S_DONE;       break;  // невідома → нічого не робимо
        }
        break;

    case S_ADDR:
        // Виставити адресу з регістра a на шину й підняти потрібну лінію шини.
        c.addr_out = true;
        c.reg_a    = cu->a;
        dp->addr_bus = dp->reg[cu->a];
        if (cu->op == OP_LOAD)  c.mem_read  = true;
        else                    c.mem_write = true;
        mem_start(dp);                     // "завести" повільну пам'ять
        cu->stage = (cu->op == OP_LOAD) ? S_READ : S_WRITE_MEM;
        break;

    case S_READ:
        // Тримаємо read і ЧЕКАЄМО. Поки пам'ять не готова — лишаємось тут.
        c.mem_read = true;                 // лінію треба ТРИМАТИ весь час чекання
        if (!dp->mem_ready) {
            // пам'ять ще їде: цей такт — такт чекання, стадію НЕ міняємо
            break;
        }
        // ready=1: дані вже на шині — приймаємо їх
        c.reg_write = true;
        c.reg_dst   = cu->dst;
        dp->reg[cu->dst] = dp->data_bus;
        cu->stage = S_DONE;
        break;

    case S_CALC:
        // Порахувати в АЛП; результат защіпнемо НАСТУПНИМ тактом.
        c.alu_enable = true;
        c.reg_a = cu->a; c.reg_b = cu->b;
        c.alu_op = (cu->op == OP_ADD) ? ALU_ADD : ALU_SUB;
        dp->data_bus = (cu->op == OP_ADD)
                     ? (uint16_t)(dp->reg[cu->a] + dp->reg[cu->b])
                     : (uint16_t)(dp->reg[cu->a] - dp->reg[cu->b]);
        cu->stage = S_WRITE_REG;
        break;

    case S_WRITE_REG:
        c.reg_write = true;
        c.reg_dst   = cu->dst;
        dp->reg[cu->dst] = dp->data_bus;
        cu->stage = S_DONE;
        break;

    case S_WRITE_MEM:
        c.mem_write = true;                // тримаємо write під час чекання
        if (!dp->mem_ready) break;         // так само чекаємо готовності
        dp->mem[dp->addr_bus] = (uint8_t)dp->reg[cu->dst];
        cu->stage = S_DONE;
        break;

    case S_DONE:
        cu->stage = S_FETCH;               // команда завершена → нова
        break;
    }

    return c;
}
