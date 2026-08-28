// НЕБЕЗПЕЧНО: обробник тримає СВІЙ прихований стан між викликами
static int purchase_counter = 0;              // глобальний, спільний

static long disc_every_fifth(long total, const void *p) {
    (void)p;
    purchase_counter++;                       // побічний ефект: змінив зовнішнє
    if (purchase_counter % 5 == 0)
        return total;                          // кожна п'ята — безкоштовно
    return 0;
}
