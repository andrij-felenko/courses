void bms_request_on(void)
{
    if (bms.state != BMS_OFF) return;
    if (!safety_ok()) { enter_fault(FAULT_CELL_PROTECT); return; }

    // Контроль перед стартом: головний МУСИТЬ бути розімкнений.
    if (aux_main_closed()) {            // а він замкнений, поки ми ще нічого не вмикали
        enter_fault(FAULT_CONTACTOR_STUCK);   // зварений з минулого разу
        return;
    }

    contactor_neg(true);
    cmd_main(false);                    // явно фіксуємо: головний наказано тримати РОЗІМКНЕНИМ
    contactor_pre(true);
    bms.state   = BMS_PRECHARGE;
    bms.t_enter = now_ms();
}
