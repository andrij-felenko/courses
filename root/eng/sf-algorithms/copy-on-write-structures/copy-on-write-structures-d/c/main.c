typedef struct { int refs; size_t len; char data[]; } block_t;

/* Записати байт b у позицію i за принципом «копія-на-запис».
   Приймає покажчик на власний покажчик, бо може його перенаправити. */
void cow_write(block_t **owned, size_t i, char b) {
    block_t *blk = *owned;
    if (blk->refs > 1) {                 /* блок спільний — треба відколотись */
        block_t *copy = malloc(sizeof(block_t) + blk->len);
        copy->refs = 1;
        copy->len  = blk->len;
        memcpy(copy->data, blk->data, blk->len);
        blk->refs--;                     /* нас у старому блоці більше нема   */
        *owned = blk = copy;             /* тепер ми на власній копії         */
    }
    blk->data[i] = b;                    /* refs == 1 — пишемо прямо на місці */
}
