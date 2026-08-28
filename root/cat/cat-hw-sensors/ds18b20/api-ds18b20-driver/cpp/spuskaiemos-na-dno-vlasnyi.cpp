const uint8_t OW_PIN = 4;             // лінія DQ

// «Притиснути лінію до нуля»: ніжка стає виходом у стані LOW.
static inline void ow_low() {
  pinMode(OW_PIN, OUTPUT);
  digitalWrite(OW_PIN, LOW);
}

// «Відпустити лінію»: ніжка стає входом; підтяжка сама тягне її вгору.
static inline void ow_release() {
  pinMode(OW_PIN, INPUT);             // жодного LOW/HIGH — просто перестали тягнути
}

// Прочитати рівень лінії (0 або 1).
static inline uint8_t ow_read() {
  return digitalRead(OW_PIN);
}
