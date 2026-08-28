// Виставити 3-бітну адресу 0..7 на A0 A1 A2 ОДНИМ записом у BSRR.
// Для кожного адресного біта: якщо він 1 — ставимо піну set (молодша половина),
// якщо 0 — ставимо піну reset (старша половина, <<16). Один запис міняє всі три
// піни в один такт шини — жодного проміжного "напівзміненого" стану адреси.
static inline void set_address(uint32_t addr) {
    uint32_t set = 0, reset = 0;
    (addr & 1u) ? (set |= 1u << A0_PIN) : (reset |= 1u << A0_PIN);
    (addr & 2u) ? (set |= 1u << A1_PIN) : (reset |= 1u << A1_PIN);
    (addr & 4u) ? (set |= 1u << A2_PIN) : (reset |= 1u << A2_PIN);
    ADDR_PORT->BSRR = set | (reset << 16);   // set — нижні 16 біт, reset — верхні
}
