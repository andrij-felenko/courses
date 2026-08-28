int main(void) {
    gf_init_tables();
    printf("=== Перевірка коректності арифметики GF(2^8) ===\n");

    int errors = 0;
    for (int i = 1; i < 256; i++) {
        uint8_t elem = (uint8_t)i;
        uint8_t inv = gf_inverse_eea(elem);
        uint8_t prod = gf_mul_fast(elem, inv);

        if (prod != 1) {
            printf("ПОМИЛКА: i=%d (0x%02X), inv=0x%02X, prod=0x%02X\n", i, elem, inv, prod);
            errors++;
        }
    }

    if (errors == 0) {
        printf("УСПІХ: Усі 255 ненульових елементів задовольняють співвідношенню a * a^-1 = 1!\n");
    } else {
        printf("ЗБОЙ: Виявлено %d помилок при обчисленні обернених елементів.\n", errors);
    }
    return errors;
}
