// НЕБЕЗПЕЧНО: так робити НЕ можна. Розберемо, чому саме.
uint8_t *get_ptr_broken(uint8_t bank, uint16_t off) {
    select_bank(bank);
    return (uint8_t *)&WINDOW[off];   // повертаємо адресу у вікні
}

void caller_broken(void) {
    uint8_t *p = get_ptr_broken(2, 0x0100);   // адреса 0xC100, банк 2 активний
    // …десь між цими рядками інший код перемикає банк…
    select_bank(5);                            // тепер у вікні банк 5
    uint8_t x = *p;                            // читаємо 0xC100 — але з БАНКУ 5!
}
