// Виконати ПО ОДНОМУ модулю за раз (лише цей під'єднаний до UART).
// Значення s7 — БАЙТ адреси (7-бітна << 1), тому парне.
// 7-біт 0x54 → байт 0xA8 = 168; 0x55 → 0xAA = 170; 0x56 → 0xAC = 172
void setAddress(uint8_t byteAddr) {         // напр. 168, 170, 172
    char cmd[12], resp[16];
    snprintf(cmd, sizeof(cmd), "s7-%u#", byteAddr);   // "s7-168#"
    if (tofCommand(cmd, resp, sizeof(resp)))
        Serial.print("нова адреса задана, байт="), Serial.println(byteAddr);
    else
        Serial.print("не вдалося, відповідь="), Serial.println(resp);
    // нова адреса діє після перезапуску живлення модуля
}
