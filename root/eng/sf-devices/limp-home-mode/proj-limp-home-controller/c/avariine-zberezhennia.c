// Обробник немаскованого переривання PVD (C99)
void PVD_IRQHandler(void) {
    if (PWR->CSR & PWR_CSR_PVDO) {
        // Напруга 3.3В почала падати!
        // 1. Апаратно знеструмлюємо всі навантаження Tier 1..3
        GPIO_SHED_PORT->BSRR = (PIN_TIER1 | PIN_TIER2 | PIN_TIER3) << 16;
        
        // 2. Миттєво копіюємо останній Freeze Frame у Backup SRAM (енергонезалежні регістри RTC)
        RTC_BKP_DR0 = g_last_freeze_frame.code;
        RTC_BKP_DR1 = (uint32_t)(g_last_freeze_frame.mosfet_temp_c * 100.0f);
        RTC_BKP_DR2 = (uint32_t)(g_last_freeze_frame.min_cell_voltage_v * 1000.0f);
        RTC_BKP_DR3 = g_last_freeze_frame.crc16;
    }
}
