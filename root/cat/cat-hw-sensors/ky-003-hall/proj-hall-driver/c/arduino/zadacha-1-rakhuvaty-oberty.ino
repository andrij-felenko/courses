// ЯК НЕ ТРЕБА: підрахунок у головному циклі
int count = 0;
bool prev = HIGH;
void loop() {
    bool now = digitalRead(HALL);
    if (prev == HIGH && now == LOW) count++;   // спіймали спад
    prev = now;
    Serial.println(count);   // ← поки це друкується, магніт проскочив
    delay(100);              // ← а тут ми взагалі спимо й нічого не бачимо
}
