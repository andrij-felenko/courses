// MOSFET-ключ (2N7000, N-канал, низом). Той самий інтерфейс, що й у NPN:
// HIGH відкриває канал. Базового резистора НЕМА — керуємо напругою на затворі.
Switch mosfet(5);                 // ACTIVE_HIGH за замовчуванням

void setup() {
    mosfet.begin();               // затвор у «0», канал закритий
    // Апаратно: затвор → (опц. 100…220 Ом) → пін; підтяжка 100 кОм затвор→GND.
}

void loop() {
    mosfet.on();   digitalWrite(LED_BUILTIN, HIGH);  delay(500);
    mosfet.off();  digitalWrite(LED_BUILTIN, LOW);   delay(500);
}
