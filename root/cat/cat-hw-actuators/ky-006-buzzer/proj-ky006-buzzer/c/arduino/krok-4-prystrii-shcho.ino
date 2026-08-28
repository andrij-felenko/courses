// Межі звуку. Нижню беремо не з підвалу: KY-006 нижче ~150 Гц ледь чутний,
// а найдзвінкіше — ближче до резонансу пластини (~2 кГц), тож туди й ведемо верх.
const int TONE_MIN_HZ = 200;    // найнижчий (найтихіший край шкали)
const int TONE_MAX_HZ = 2000;   // найвищий (найгучніший, коло резонансу)

// Заспівати значення value з діапазону [valMin; valMax].
// invert=true → більше значення дає НИЖЧИЙ тон (як паркрадар: ближче → вище).
void sonify(long value, long valMin, long valMax, bool invert) {
  value = constrain(value, valMin, valMax);   // ← 1) затиснути в межі ОБОВ'ЯЗКОВО
  int f;
  if (invert)
    f = map(value, valMin, valMax, TONE_MAX_HZ, TONE_MIN_HZ);
  else
    f = map(value, valMin, valMax, TONE_MIN_HZ, TONE_MAX_HZ);
  tone(PIN_BUZ, f);   // безперервний тон, що «їздить» за значенням; noTone() коли не треба
}

void loop() {
  buzzerUpdate();
  long dist = readDistanceCm();          // напр. 5…100 см
  sonify(dist, 5, 100, /*invert=*/true); // ближче стіна → вищий писк
}
