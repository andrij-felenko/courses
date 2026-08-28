// Відправник (модуль телеметрії): пакує кадр вручну.
void telemetry_send_battery(float v) {
    uint16_t mv = (uint16_t)(v * 1000.0f);   // 4.15 В -> 4150 мВ
    uint8_t  pct = battery_percent(v);
    uint8_t  frame[3];
    frame[0] = (uint8_t)(mv >> 8);           // старший байт напруги
    frame[1] = (uint8_t)(mv & 0xFF);         // молодший байт
    frame[2] = pct;
    radio_write(frame, 3);
}
