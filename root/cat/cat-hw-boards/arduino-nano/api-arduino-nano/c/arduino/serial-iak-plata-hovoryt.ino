void setup() {
    Serial.begin(9600);            // 9600 бод — обидва боки мусять збігтися
    Serial.println(F("Готовий")); // F() тримає рядок у флеші, не в SRAM
}

void loop() {
    // приймання: одна літера-команда
    if (Serial.available() > 0) {      // у буфері є хоч байт?
        char cmd = Serial.read();
        if (cmd == '1') digitalWrite(LED_BUILTIN, HIGH);
        if (cmd == '0') digitalWrite(LED_BUILTIN, LOW);
    }

    // передавання: показник щосекунди
    static unsigned long last = 0;
    if (millis() - last >= 1000) {
        last = millis();
        int v = analogRead(A0);
        Serial.print(F("A0 = "));
        Serial.println(v);             // число + перехід рядка
    }
}
