FlameFlicker flick(A0);
const int MIN_LEVEL = 120;   // мінімум середнього ІЧ, щоб взагалі розглядати

void setup() {
  Serial.begin(9600);
  flick.begin();
}

void loop() {
  flick.sample();                        // семплюй якомога частіше

  bool bright   = flick.level() > MIN_LEVEL;   // є помітний ІЧ
  bool flickers = flick.flame();               // і він пульсує 2..20 Гц
  bool realFire = bright && flickers;          // вогонь, а не сонце

  static uint32_t t = 0;
  if (millis() - t > 200) {              // друкуй нечасто, семплюй часто
    t = millis();
    Serial.print("рівень="); Serial.print(flick.level());
    Serial.print("  f=");     Serial.print(flick.freq(), 1);
    Serial.print(" Гц  →  "); Serial.println(realFire ? "ВОГОНЬ" : "спокій");
  }
}
