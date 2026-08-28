void loop() {
    if (keypad.getKeys()) {                      // оновити список; true, якщо є активні
        for (int i = 0; i < LIST_MAX; i++) {     // LIST_MAX = 10 (стеля бібліотеки)
            if (keypad.key[i].stateChanged) {    // саме ця клавіша щойно змінила стан
                char k = keypad.key[i].kchar;
                switch (keypad.key[i].kstate) {
                    case PRESSED:  Serial.print("натиснуто "); Serial.println(k); break;
                    case HOLD:     Serial.print("утримують ");  Serial.println(k); break;
                    case RELEASED: Serial.print("відпущено ");  Serial.println(k); break;
                    case IDLE:     break;        // спокій — нічого не робимо
                }
            }
        }
    }
}
