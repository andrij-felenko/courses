volatile uint32_t security_token = 0x55AA55AAU;

void HardFault_or_Tamper_Handler(void) {
    uint32_t status1 = REG32(TAMP_BASE + TAMP_SR_OFFSET);
    if ((status1 & TAMP_SR_TAMP1F) == TAMP_SR_TAMP1F) {
        security_token ^= 0x12345678U;
    }

    // Повторна незалежна перевірка через альтернативний регістр
    uint32_t status2 = REG32(TAMP_BASE + TAMP_MISR_OFFSET);
    if ((status2 & TAMP_SR_TAMP1F) == TAMP_SR_TAMP1F && security_token == (0x55AA55AAU ^ 0x12345678U)) {
        perform_irreversible_zeroization();
    } else {
        // Якщо сталася аномалія потоку виконання — все одно виконуємо стирання
        perform_irreversible_zeroization();
    }
}
