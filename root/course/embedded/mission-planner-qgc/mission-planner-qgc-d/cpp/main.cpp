// Записати параметр WPNAV_SPEED = 800 (см/с) — те саме роблять
// і Mission Planner, і QGroundControl, лише з різних кнопок.
mavlink_message_t msg;
mavlink_msg_param_set_pack(
    gcs_sysid, gcs_compid, &msg,
    target_sys, target_comp,        // адреса борту з його HEARTBEAT
    "WPNAV_SPEED",                  // ім'я параметра (до 16 символів)
    800.0f,                         // нове значення
    MAV_PARAM_TYPE_REAL32);         // тип значення
uint8_t buf[MAVLINK_MAX_PACKET_LEN];
int n = mavlink_msg_to_send_buffer(buf, &msg);
link_write(buf, n);

// Борт підтверджує запис, надіславши PARAM_VALUE з НОВИМ значенням —
// станція (будь-яка) чекає його, щоб переконатися, що зміна лягла.
mavlink_param_value_t pv;
if (wait_param_value("WPNAV_SPEED", &pv, /*timeout_ms=*/1000) &&
    pv.param_value == 800.0f) {
    // успіх: на борту тепер 800; обидві станції побачать це однаково
}
