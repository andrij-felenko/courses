/* Бульбашка — порожній пакет: усе нулі, valid = false. */
static slot_t bubble(void) {
    slot_t s;
    memset(&s, 0, sizeof s);
    s.op = OP_NOP;
    s.valid = false;
    return s;
}

/* Вибірка: дістати наступну команду за pc і посунути pc.
   imem[] — пам'ять команд (тут стороння для моделі). */
extern slot_t imem_fetch(uint32_t pc);
static slot_t fetch(cpu_t *c) {
    slot_t s = imem_fetch(c->pc);
    s.valid = true;
    c->pc += 1;
    return s;
}

/* Читання пам'яті даних за адресою (стороннє для моделі). */
extern int32_t mem_read(uint32_t addr);
