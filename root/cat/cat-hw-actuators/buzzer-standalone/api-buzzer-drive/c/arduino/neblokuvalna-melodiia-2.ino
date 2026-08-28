// «Ода до радості», перші такти (частоти в Гц, тривалості в мс)
const Note ODE[] = {
  {330,300},{330,300},{349,300},{392,300},   // мі мі фа соль
  {392,300},{349,300},{330,300},{294,300},   // соль фа мі ре
  {262,300},{262,300},{294,300},{330,300},   // до до ре мі
  {330,450},{294,150},{294,600},             // мі. ре ре(довга)
};

BuzzerPlayer buzzer(8);

void setup() {
  buzzer.play(ODE, sizeof(ODE) / sizeof(ODE[0]));
}

void loop() {
  buzzer.update();               // рухає мелодію, НІЧОГО не блокує

  // …а тут паралельно живе решта пристрою — і воно справді працює:
  if (digitalRead(BUTTON) == LOW && !buzzer.isPlaying())
    buzzer.play(ODE, sizeof(ODE) / sizeof(ODE[0]));   // повтор на кнопку
  // readSensors(); updateDisplay(); handleRadio();   // усе встигає
}
