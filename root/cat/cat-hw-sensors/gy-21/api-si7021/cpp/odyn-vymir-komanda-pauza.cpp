#include <Wire.h>

static const uint8_t GY21_ADDR = 0x40;   // фіксована адреса, джамперами не змінюється
static const uint8_t CMD_TEMP  = 0xF3;   // вимір T, no-hold master
static const uint8_t CMD_HUM   = 0xF5;   // вимір RH, no-hold master

// Перевірка CRC-8 (означимо трохи нижче):
uint8_t si7021_crc8(const uint8_t *data, uint8_t len);

// Спільне ядро: послати команду `cmd`, зачекати `wait_ms`, прочитати 3 байти,
// звірити CRC і повернути 16-бітне СИРЕ значення (з обнуленими службовими бітами).
// Повертає true при успіху; false — якщо давач не відповів або CRC не зійшлася.
static bool gy21_read_raw(uint8_t cmd, uint16_t wait_ms, uint16_t *raw_out) {
  // -- Крок 1: послати командний байт --
  Wire.beginTransmission(GY21_ADDR);
  Wire.write(cmd);
  if (Wire.endTransmission() != 0) return false;   // давач не підтвердив команду

  // -- Крок 2: витримати паузу, поки давач міряє --
  delay(wait_ms);

  // -- Крок 3: прочитати рівно 3 байти (MSB, LSB, CRC) --
  if (Wire.requestFrom((int)GY21_ADDR, 3) != 3) return false;
  uint8_t msb = Wire.read();
  uint8_t lsb = Wire.read();
  uint8_t crc = Wire.read();

  // -- Крок 4a: перевірити контрольну суму над двома байтами даних --
  uint8_t buf[2] = { msb, lsb };
  if (si7021_crc8(buf, 2) != crc) return false;     // зіпсовано в дорозі — відкинути

  // -- Крок 4b: зібрати число й обнулити 2 службових біти --
  uint16_t raw = ((uint16_t)msb << 8) | lsb;
  raw &= 0xFFFC;

  *raw_out = raw;
  return true;
}

// Публічні читання: та сама функція, різний командний байт і пауза + формула.
bool gy21_read_temperature(float *t_out) {
  uint16_t raw;
  if (!gy21_read_raw(CMD_TEMP, 10, &raw)) return false;
  *t_out = 175.72f * raw / 65536.0f - 46.85f;
  return true;
}

bool gy21_read_humidity(float *rh_out) {
  uint16_t raw;
  if (!gy21_read_raw(CMD_HUM, 20, &raw)) return false;
  float rh = 125.0f * raw / 65536.0f - 6.0f;
  // Формула може дати трохи <0 або трохи >100 біля країв — притиснути до 0..100:
  if (rh < 0.0f)   rh = 0.0f;
  if (rh > 100.0f) rh = 100.0f;
  *rh_out = rh;
  return true;
}
