const int PIN_SOIL = A0;      // AOUT давача
const int PIN_PUMP = 7;       // реле помпи

// калібрувальні межі — зняти для СВОГО щупа (див. нижче)
const int AIR   = 610;        // сухо (щуп у повітрі)
const int WATER = 330;        // мокро (щуп у воді)

void setup() {
  pinMode(PIN_PUMP, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int raw = analogRead(PIN_SOIL);            // 0…1023; сухо ≈ вище
  // перевести в «відсотки вологості»: мокро → 100, сухо → 0
  int pct = map(raw, AIR, WATER, 0, 100);
  pct = constrain(pct, 0, 100);

  Serial.print("raw="); Serial.print(raw);
  Serial.print("  moisture="); Serial.print(pct); Serial.println("%");

  digitalWrite(PIN_PUMP, pct < 30 ? HIGH : LOW);  // сухіше 30% → полити
  delay(1000);
}
