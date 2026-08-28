void tick(CPU *c)
{
    // ── СТАДІЯ 5: ЗАПИС (write-back) ─ споживає MEM_WB ──
    Latch w = c->L[MEM_WB];
    if (w.valid) {
        if (w.op == OP_LOAD)  c->reg[w.rd] = w.memdata; // дані з пам'яті → регістр
        else if (w.op == OP_ADD) c->reg[w.rd] = w.alu;  // сума з АЛП → регістр
        // STORE і HALT у регістр нічого не пишуть
    }

    // ── СТАДІЯ 4: ПАМ'ЯТЬ ─ EX_MEM → нова MEM_WB ──
    Latch m = c->L[EX_MEM];
    Latch nmw = (Latch){0};
    if (m.valid) {
        nmw.valid = true; nmw.op = m.op; nmw.rd = m.rd; nmw.alu = m.alu;
        if (m.op == OP_LOAD)  nmw.memdata = c->dmem[m.addr]; // читаємо пам'ять
        else if (m.op == OP_STORE) c->dmem[m.addr] = m.b;    // пишемо пам'ять
    }

    // ── СТАДІЯ 3: ВИКОНАННЯ (АЛП) ─ ID_EX → нова EX_MEM ──
    Latch e = c->L[ID_EX];
    Latch nem = (Latch){0};
    if (e.valid) {
        nem.valid = true; nem.op = e.op; nem.rd = e.rd; nem.b = e.b; nem.addr = e.addr;
        if (e.op == OP_ADD) nem.alu = e.a + e.b;  // власне арифметика
        // для LOAD/STORE адреса вже готова (пряма) — АЛП лише пропускає її далі
    }

    // ── СТАДІЯ 2: ДЕКОДУВАННЯ + читання регістрів ─ IF_ID → нова ID_EX ──
    Latch d = c->L[IF_ID];
    Latch nie = (Latch){0};
    if (d.valid) {
        nie.valid = true; nie.op = d.op; nie.rd = d.rd; nie.addr = d.addr;
        nie.a = c->reg[d.rs1];                    // перший операнд
        nie.b = (d.op == OP_ADD) ? c->reg[d.rs2]  // другий операнд для ADD
                                 : c->reg[d.rs1]; // або значення для STORE
    }

    // ── СТАДІЯ 1: ВИБІРКА ─ пам'ять команд → нова IF_ID ──
    Latch nif = (Latch){0};
    if (!c->fetch_halted && c->pc < PROG_LEN) {
        Instr ins = PROG[c->pc];
        if (ins.op == OP_HALT) {
            c->fetch_halted = true;               // HALT спиняє вибірку; конвеєр дренажить
        } else {
            nif.valid = true; nif.op = ins.op; nif.rd = ins.rd;
            nif.rs1 = ins.rs1; nif.rs2 = ins.rs2; nif.addr = ins.addr;
            c->pc++;                              // PC на наступну команду
        }
    }

    // ── ФРОНТ ТАКТУ: усі засувки клацають РАЗОМ ──
    // Ми вже прочитали кожну засувку у своїй стадії вище (з хвоста в голову),
    // тож тепер безпечно записати всі нові значення.
    c->L[MEM_WB] = nmw;
    c->L[EX_MEM] = nem;
    c->L[ID_EX]  = nie;
    c->L[IF_ID]  = nif;
}
