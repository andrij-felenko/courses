void loop() {
    // Монітор (ви друкуєте) → модуль (летить по радіо)
    if (Serial.available()) {
        btSerial.write(Serial.read());
    }
    // Модуль (прийшло по радіо) → монітор (бачите на екрані)
    if (btSerial.available()) {
        Serial.write(btSerial.read());
    }
}
