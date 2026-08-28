// Запис аварійного зліпка в енергонезалежний домен RTC
void EarlyPinGuard_SaveCrashDump(const PinGuardReport_t* report) {
    // Дозвіл доступу до домену Backup
    PWR->CR1 |= PWR_CR1_DBP;

    // Регістр 0: Магічне число аварії
    TAMP->BKP0R = 0xDEADBEEFUL;
    // Регістр 1: Код помилки (PinGuardStatus_t)
    TAMP->BKP1R = (uint32_t)report->failure_reason;
    // Регістр 2: Індекс дефектного піна в таблиці
    TAMP->BKP2R = report->failed_pin_index;
    // Регістр 3: Фізичний стан вхідного регістра IDR на момент аварії
    TAMP->BKP3R = ((GpioHw_t*)g_safety_pin_table[report->failed_pin_index].port_base)->IDR;
}
