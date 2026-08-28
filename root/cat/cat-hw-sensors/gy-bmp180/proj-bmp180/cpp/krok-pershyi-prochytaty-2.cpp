// Калібрувальні коефіцієнти конкретного екземпляра давача.
struct BMP180_Calib {
  int16_t  AC1, AC2, AC3;      // знакові
  uint16_t AC4, AC5, AC6;      // беззнакові
  int16_t  B1, B2;             // знакові
  int16_t  MB, MC, MD;         // знакові
};

static BMP180_Calib cal;       // заповнимо один раз на старті

// Прочитати всі 11 коефіцієнтів. Викликати ОДИН раз у setup().
// Повертає false, якщо давач мовчить або на місці не BMP180.
bool bmp180_read_calibration() {
  // Перевірка «чи це взагалі BMP180»: регістр 0xD0 має дати 0x55.
  Wire.beginTransmission(BMP180_ADDR);
  Wire.write(0xD0);
  Wire.endTransmission(false);
  Wire.requestFrom((int)BMP180_ADDR, 1);
  if (Wire.read() != 0x55) return false;

  cal.AC1 = bmp180_read_s16(0xAA);
  cal.AC2 = bmp180_read_s16(0xAC);
  cal.AC3 = bmp180_read_s16(0xAE);
  cal.AC4 = bmp180_read_u16(0xB0);   // беззнакове!
  cal.AC5 = bmp180_read_u16(0xB2);   // беззнакове!
  cal.AC6 = bmp180_read_u16(0xB4);   // беззнакове!
  cal.B1  = bmp180_read_s16(0xB6);
  cal.B2  = bmp180_read_s16(0xB8);
  cal.MB  = bmp180_read_s16(0xBA);
  cal.MC  = bmp180_read_s16(0xBC);
  cal.MD  = bmp180_read_s16(0xBE);

  // Захист від «мертвого» давача: якщо всі байти читаються як 0x0000
  // або 0xFFFF, коефіцієнти биті — далі рахувати немає сенсу.
  if (cal.AC1 == 0 || cal.AC1 == (int16_t)0xFFFF) return false;
  return true;
}
