for (uint8_t ch = 0; ch < 8; ch++) {
  mux_select(ch);
  for (uint8_t addr = 0x08; addr <= 0x77; addr++) {
    if (addr == MUX_ADDR) continue;       // не чіпати сам комутатор
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("гілка "); Serial.print(ch);
      Serial.print(": 0x");   Serial.println(addr, HEX);
    }
  }
}
