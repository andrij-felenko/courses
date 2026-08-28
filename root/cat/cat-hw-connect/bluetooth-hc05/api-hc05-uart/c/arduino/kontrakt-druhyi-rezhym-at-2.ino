// Надіслати AT-команду й дочекатися відповіді.
// Повертає true, якщо у відповіді трапилось "OK"; false — таймаут або "ERROR".
// resp (опційно) — куди скласти повний текст відповіді для друку в монітор.
bool sendAT(const char *cmd, String &resp, uint32_t timeoutMs = 1000) {
    // 1) очистити «хвіст» попередньої відповіді з буфера
    while (btSerial.available()) btSerial.read();

    // 2) надіслати команду + ОБОВ'ЯЗКОВІ \r\n
    btSerial.print(cmd);
    btSerial.print("\r\n");

    // 3) збирати відповідь, доки не побачимо кінець рядка або не вийде час
    resp = "";
    uint32_t start = millis();
    while (millis() - start < timeoutMs) {
        while (btSerial.available()) {
            char c = btSerial.read();
            resp += c;
            // модуль завершує відповідь \r\n; побачивши \n — рядок готовий
            if (c == '\n') {
                return resp.indexOf("OK") >= 0;   // є "OK" → успіх
            }
        }
    }
    return false;   // час вийшов, повного рядка так і не прийшло
}
