// Дві половини одного вузла: NPN тримає низ, PNP — верх.
// Обидва керуються з піна, але з протилежною полярністю.
Switch low_side (5, Switch::ACTIVE_HIGH);   // NPN низом:  HIGH → увімк
Switch high_side(6, Switch::ACTIVE_LOW);    // PNP верхом: LOW  → увімк

void setup() {
    low_side.begin();
    high_side.begin();     // обидва вимкнені (кожен у свій «вимкнено»)
}

void loop() {
    // Попри протилежну апаратну полярність, семантика ОДНАКОВА:
    low_side.on();         // digitalWrite(5, HIGH)
    high_side.on();        // digitalWrite(6, LOW) — але це теж «увімкнути»
    delay(1000);
    low_side.off();
    high_side.off();
    delay(1000);
}
