// Свідомий вихід із FAULT. Викликати ЛИШЕ за зовнішньою командою
// (кнопка, команда оператора), і тільки коли біда минула.
bool bms_reset(void)
{
    if (bms.state != BMS_FAULT) return false;

    // Не випускаємо з FAULT, поки тривога ще активна — інакше тут же впадемо назад.
    if (!safety_ok()) return false;

    // Зварений контактор скиданням не лікується: aux мусить показати «розімкнено».
    if (aux_main_closed()) return false;

    nvm_clear_last_fault();             // стерти слід у незалежній пам'яті
    bms = (bms_t){ .state = BMS_OFF, .fault = FAULT_NONE };
    main_cmd = false;
    set_fault_pin(false);
    return true;                        // тепер можна знову bms_request_on()
}
