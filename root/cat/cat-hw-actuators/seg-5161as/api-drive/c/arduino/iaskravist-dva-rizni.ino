// Яскравість 0..255 через програмний ШІМ на спільному виводі.
// Тут COM_PIN — це спільний катод індикатора, заведений НЕ на землю
// напряму, а на вивід МК (через транзистор, якщо струм великий).
const uint8_t COM_PIN = 10;
uint8_t brightness = 255;      // 0 = згашено, 255 = повна

void setup() {
  disp.begin();
  pinMode(COM_PIN, OUTPUT);
}

// Викликати часто; тримає задану цифру із заданою яскравістю.
void refresh(uint8_t hex, bool dot) {
  disp.showHex(hex, dot);                // виставити сегменти
  // ── один період ШІМ (≈ сотні Гц при таких паузах) ──
  digitalWrite(COM_PIN, LOW);            // катод на землю → сегменти світять
  delayMicroseconds(1 + brightness * 6); // «увімкнено» пропорційно яскравості
  digitalWrite(COM_PIN, HIGH);           // катод підняти → усе гасне
  delayMicroseconds(1 + (255 - brightness) * 6); // решта періоду — темрява
}

void loop() {
  refresh(0x3, false);                   // показуємо «3»
  // brightness можна плавно міняти десь у програмі
}
