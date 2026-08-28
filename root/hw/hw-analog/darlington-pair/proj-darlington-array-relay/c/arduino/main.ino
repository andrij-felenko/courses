// Вісім входів масиву (IN1..IN8) на восьми виводах контролера.
// Масив — стік: логічна 1 на INk відкриває канал і притягує OUTk до землі,
// тож реле k спрацьовує. Логічний 0 — канал закритий, реле відпущене.
const uint8_t IN_PIN[8] = {2, 3, 4, 5, 6, 7, 8, 9};

void setup() {
  for (uint8_t ch = 0; ch < 8; ch++) {
    pinMode(IN_PIN[ch], OUTPUT);
    digitalWrite(IN_PIN[ch], LOW);      // старт: усі канали закриті, реле відпущені
  }
}

void relayOn(uint8_t ch)  { digitalWrite(IN_PIN[ch], HIGH); }  // увімкнути реле ch
void relayOff(uint8_t ch) { digitalWrite(IN_PIN[ch], LOW);  }  // відпустити реле ch

// Виставити одразу весь банк за бітовою маскою: біт k = 1 → реле k увімкнено.
// Один байт задає стан восьми реле воднораз.
void relayBank(uint8_t mask) {
  for (uint8_t ch = 0; ch < 8; ch++)
    digitalWrite(IN_PIN[ch], (mask >> ch) & 1 ? HIGH : LOW);
}

void loop() {
  relayOn(0);              // клацнули перше реле
  delay(500);
  relayOff(0);
  delay(500);
  relayBank(0b10101010);   // увімкнули реле 1, 3, 5, 7 воднораз
  delay(500);
  relayBank(0x00);         // усі відпустили
  delay(500);
}
