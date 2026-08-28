ow_reset();
ow_write_byte(0xCC);      // Skip ROM — він на шині один, адресу не диктуємо
ow_write_byte(0x44);      // Convert T — «зміряй температуру»
_delay_ms(750);           // чекаємо, поки чіп рахує (12 біт ≈ 750 мс)

ow_reset();
ow_write_byte(0xCC);      // Skip ROM
ow_write_byte(0xBE);      // Read Scratchpad — «віддай пам'ять із результатом»
uint8_t lo = ow_read_byte();
uint8_t hi = ow_read_byte();
int16_t raw = ((int16_t)hi << 8) | lo;
float celsius = raw / 16.0f;   // у DS18B20 молодший біт = 1/16 °C
