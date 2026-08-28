/* Чи треба вставити бульбашку через конфлікт завантаж-використай?
   Дивимося на команду, що ЗАРАЗ у ID/EX (reg[1]) — вона на такт попереду. */
static bool load_use_stall(const cpu_t *c) {
    const slot_t *idex = &c->reg[1];   /* попередня команда, іде у ВК */
    const slot_t *ifid = &c->reg[0];   /* наша команда, готується ввійти в ID/EX */

    if (!idex->valid || idex->op != OP_LOAD || idex->rd == 0)
        return false;                  /* попередня — не завантаження або пише в R0 */
    if (!ifid->valid)
        return false;                  /* нашої команди ще нема — гальмувати нічого */

    /* Наша команда читає регістр, який завантаження ще не встигне віддати? */
    return (ifid->rs1 == idex->rd) || (ifid->rs2 == idex->rd);
}
