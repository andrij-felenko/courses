const uint8_t PIN_LDR = A0;

float smoothed = 0;                 // згладжена оцінка (float, щоб α працював тонко)
const float ALPHA = 0.2f;           // 0.1 гладше+лінивіше · 0.5 жвавіше+шумніше

void setup() {
  Serial.begin(9600);
  smoothed = analogRead(PIN_LDR);   // засіяти першим відліком, а не нулем
}

void loop() {
  int raw = analogRead(PIN_LDR);
  smoothed += ALPHA * (raw - smoothed);   // y ← y + α·(нове − y)
  Serial.println((int)smoothed);
  delay(20);
}
