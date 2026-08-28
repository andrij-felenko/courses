// Висхідний мотив «до-ре-мі-фа-соль» і назад, остання нота довша.
const Note scaleUpDown[] = {
  {NOTE_C4, 200}, {NOTE_D4, 200}, {NOTE_E4, 200}, {NOTE_F4, 200},
  {NOTE_G4, 200}, {NOTE_F4, 200}, {NOTE_E4, 200}, {NOTE_D4, 200},
  {NOTE_C4, 500},
};

void setup() {
  pinMode(PIN_BUZ, OUTPUT);
  playMelody(scaleUpDown, sizeof(scaleUpDown) / sizeof(scaleUpDown[0]));
}

void loop() {
  buzzerUpdate();     // ← мелодія рухається тут, фоном
  // ...усе інше живе паралельно: поки грає гама, пристрій опитує кнопки...
}
