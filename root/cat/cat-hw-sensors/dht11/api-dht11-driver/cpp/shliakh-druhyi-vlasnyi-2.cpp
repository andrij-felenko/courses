void setup() {
    Serial.begin(9600);
    delay(1500);                  // даємо давачу очуняти після ввімкнення
}

void loop() {
    int t, h;
    if (dht11_read(&t, &h)) {
        Serial.print(F("T = ")); Serial.print(t);
        Serial.print(F(" C, RH = ")); Serial.print(h); Serial.println(F(" %"));
    } else {
        Serial.println(F("читання не вдалося — повторю"));
    }
    delay(2000);                  // ≥ 1 с між читаннями
}
