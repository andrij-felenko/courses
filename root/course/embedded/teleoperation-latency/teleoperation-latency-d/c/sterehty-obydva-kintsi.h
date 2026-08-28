// Двобічний нагляд за лінком: кожен кінець стереже СВІЙ напрямок
// На РОВЕРІ: чи приходять команди/серцебиття з пульта (uplink)?
uint32_t t_since_uplink = now_ms - last_cmd_from_gcs_ms;
// На ПУЛЬТІ: чи приходить телеметрія з ровера (downlink)?
uint32_t t_since_downlink = now_ms - last_tlm_from_rover_ms;

// Ровер реагує на втрату uplink (їхати наосліп він не має права):
if (t_since_uplink > T_STOP_MS) rover_enter_failsafe();
// Пульт реагує на втрату downlink (попередити оператора, що він осліп):
if (t_since_downlink > T_STOP_MS) gcs_warn_blind_operation();
