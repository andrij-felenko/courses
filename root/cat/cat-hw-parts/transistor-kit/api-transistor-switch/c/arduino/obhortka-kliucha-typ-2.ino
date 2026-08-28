Switch pump(5);                        // NPN-ключ низом на піні 5: HIGH вмикає
Switch lamp(6, Switch::ACTIVE_LOW);    // PNP-ключ верхом на піні 6: LOW вмикає

void setup() {
    pump.begin();
    lamp.begin();     // обидва стартують ВИМКНЕНИМИ
}

void loop() {
    pump.on();        // «увімкнути насос» — байдуже, що там NPN
    delay(3000);
    pump.off();
    lamp.toggle();    // перемкнути лампу в протилежний стан
    delay(1000);
}
