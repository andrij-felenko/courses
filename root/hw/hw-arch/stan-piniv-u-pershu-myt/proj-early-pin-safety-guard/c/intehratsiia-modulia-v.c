// Таблиця критичних пінів виробу
static const PinGuardConfig_t g_safety_pin_table[] = {
    // PA5: Затвор нижнього силового транзистора (Active-High, очікується зовнішній Pull-Down 4.7k)
    { 0x48000000UL, 5, EXT_PULL_DOWN_HARD, PIN_TARGET_OUTPUT_LOW, true,  "HS_INVERTER_LOW_GATE" },
    // PA6: Затвор верхнього силового транзистора (Active-High, очікується зовнішній Pull-Down 4.7k)
    { 0x48000000UL, 6, EXT_PULL_DOWN_HARD, PIN_TARGET_OUTPUT_LOW, true,  "HS_INVERTER_HIGH_GATE" },
    // PB2: Вхід аварійного термозапобіжника (очікується зовнішній Pull-Up 10k)
    { 0x48000400UL, 2, EXT_PULL_UP_HARD,   PIN_TARGET_INPUT,       false, "THERMAL_FAULT_SENSE" }
};

void System_EarlySafetyEntry(void) {
    PinGuardReport_t report;
    PinGuardStatus_t status = EarlyPinGuard_Execute(g_safety_pin_table,
                                                    sizeof(g_safety_pin_table) / sizeof(g_safety_pin_table[0]),
                                                    &report);

    if (status != PIN_GUARD_OK) {
        // Фіксація критичної апаратної відмови заліза!
        EarlyPinGuard_FatalErrorHandler(&report);
    }
}
