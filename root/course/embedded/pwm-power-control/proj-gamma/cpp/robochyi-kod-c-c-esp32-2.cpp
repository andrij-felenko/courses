const int PIN = 5;

void setup() {
    ledcAttach(PIN, 5000, PWM_BITS);  // 5 кГц, 12 біт
    buildLUT();                        // одноразовий дорогий прохід
}

void loop() {
    // дихання: 0→255→0
    for (int level = 0; level < 256; level++) {
        ledcWrite(PIN, gammaLUT[level]);  // ЛИШЕ індексація, жодного float
        delay(8);
    }
    for (int level = 255; level >= 0; level--) {
        ledcWrite(PIN, gammaLUT[level]);
        delay(8);
    }
}
