// Викликати ЧАСТО й КОРОТКО — напр. раз на 1 мс із головного циклу.
void bms_step(void)
{
    uint32_t t = now_ms();

    switch (bms.state) {

    case BMS_OFF:
        // Спокій. Чекаємо зовнішньої команди «увімкнути».
        // (саму команду обробляє bms_request_on(), див. нижче)
        break;

    case BMS_PRECHARGE:
        if (!safety_ok()) { enter_fault(FAULT_CELL_PROTECT); break; }
        precharge_step(t);
        break;

    case BMS_ON:
        if (!safety_ok()) { enter_fault(FAULT_CELL_PROTECT); break; }
        on_step(t);
        break;

    case BMS_FAULT:
        // Пастка. Тут НЕ намагаємось «полагодитись» самі.
        // Вихід — лише через явне bms_reset() (нижче).
        break;
    }
}
