// Ніжки мікроконтролера, куди прийшли керувальні лінії дисплея
const int PIN_RS = 8;
const int PIN_E  = 9;
const int PIN_D4 = 4, PIN_D5 = 5, PIN_D6 = 6, PIN_D7 = 7;

// Виставити один напівбайт (молодші 4 біти value) на лінії D4–D7
void putNibble(uint8_t value) {
    digitalWrite(PIN_D4, (value >> 0) & 1);
    digitalWrite(PIN_D5, (value >> 1) & 1);
    digitalWrite(PIN_D6, (value >> 2) & 1);
    digitalWrite(PIN_D7, (value >> 3) & 1);
}

// Клацнути строб: підняти E, витримати, опустити — на спаді контролер читає лінії
void pulseE() {
    digitalWrite(PIN_E, HIGH);
    delayMicroseconds(1);      // тримаємо E високим ≥ 0.45 мкс (беремо із запасом)
    digitalWrite(PIN_E, LOW);
    delayMicroseconds(50);     // даємо контролеру перетравити (звичайна команда ~37 мкс)
}
