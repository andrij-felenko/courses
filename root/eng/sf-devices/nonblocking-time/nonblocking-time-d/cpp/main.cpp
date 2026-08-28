unsigned long lastBlink = 0;
unsigned long lastRead  = 0;
const unsigned long blinkInterval = 500;   // мс
const unsigned long readInterval  = 100;   // мс

void loop() {
  unsigned long now = millis();

  if (now - lastBlink >= blinkInterval) {   // діло 1: блимати
    lastBlink += blinkInterval;
    ledState = !ledState;
    digitalWrite(LED, ledState);
  }

  if (now - lastRead >= readInterval) {     // діло 2: опитати давач
    lastRead += readInterval;
    readSensor();
  }

  // кнопки й будь-що інше — теж тут, нічого не блокує
}
