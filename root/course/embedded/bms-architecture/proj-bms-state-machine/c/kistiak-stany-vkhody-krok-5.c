void bms_request_on(void)
{
    if (bms.state != BMS_OFF) return;     // вмикаємось лише зі спокою
    if (!safety_ok()) { enter_fault(FAULT_CELL_PROTECT); return; }

    // Старт хореографії: спершу «мінус» — спільна земля з навантаженням.
    contactor_neg(true);
    contactor_pre(true);                  // одразу й передзарядний: R заряджає C
    bms.state   = BMS_PRECHARGE;
    bms.t_enter = now_ms();               // звідси відлічуємо таймаут передзаряду
}
