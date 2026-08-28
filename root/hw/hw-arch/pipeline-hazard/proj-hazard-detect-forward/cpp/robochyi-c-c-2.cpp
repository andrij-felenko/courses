/* Вибрати актуальне значення регістра r для входу ALU.
   Порядок перевірок = пріоритет джерел: ближче (EX/MEM) — раніше. */
static int32_t forward(const cpu_t *c, uint8_t r) {
    const slot_t *exmem = &c->reg[2];   /* команда на такт попереду */
    const slot_t *memwb = &c->reg[3];   /* команда на два такти попереду */

    /* Джерело 1 — EX/MEM: найсвіжіший результат. Пріоритет над усім. */
    if (exmem->valid && exmem->wen && exmem->rd == r && r != 0)
        return exmem->val;

    /* Джерело 2 — MEM/WB: старіший результат. Беремо, лише якщо ближче не спрацювало. */
    if (memwb->valid && memwb->wen && memwb->rd == r && r != 0)
        return memwb->val;

    /* Пробросу немає — значення вже лежить у регістровому файлі. */
    return c->regfile[r];
}
