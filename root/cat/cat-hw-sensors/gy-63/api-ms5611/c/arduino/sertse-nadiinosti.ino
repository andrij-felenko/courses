void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);               // ESP32: SDA=21, SCL=22

  if (!ms5611_reset())   { Serial.println(F("MS5611: немає ACK на скид")); while (1) {} }
  if (!ms5611_read_prom()) { Serial.println(F("MS5611: не прочитав PROM"));  while (1) {} }

  if (!ms5611_prom_crc_ok(g_prom)) {
    Serial.println(F("MS5611: CRC-4 калібрування НЕ зійшлася — коефіцієнти пошкоджені!"));
    while (1) {}                     // працювати з такими даними не можна
  }
  Serial.println(F("MS5611: PROM цілий, коефіцієнти дійсні."));
}
