// Перевести всі задіяні ноги на вихід і почати з темного екрана.
static void segments_init(void)
{
    for (uint8_t i = 0; i < 8; i++)                    // 8 сегментних ніг → вихід
        *seg_ddr(SEG[i].port) |= SEG[i].mask;
    for (uint8_t i = 0; i < 4; i++)                    // 4 катодні ноги → вихід
        *seg_ddr(CAT[i].port) |= CAT[i].mask;
    put_segments(0x00);      // усі сегменти згашені
    all_digits_off();        // усі розряди закриті — стартуємо з чорного екрана
}
