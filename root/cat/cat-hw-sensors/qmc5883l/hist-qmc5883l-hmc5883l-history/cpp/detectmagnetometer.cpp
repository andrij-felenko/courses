// Приклад програмного визначення типа магнітометра на шині I2C
#include <Wire.h>

enum MagType { MAG_UNKNOWN, MAG_HMC5883L, MAG_QMC5883L };

MagType detectMagnetometer() {
    // 1. Спроба виявлення HMC5883L (адреса 0x1E)
    Wire.beginTransmission(0x1E);
    if (Wire.endTransmission() == 0) {
        Wire.beginTransmission(0x1E);
        Wire.write(0x0A); // Регістр ідентифікатора Identification Register A
        Wire.endTransmission();
        Wire.requestFrom(0x1E, 3);
        if (Wire.available() >= 3) {
            char idA = Wire.read();
            char idB = Wire.read();
            char idC = Wire.read();
            if (idA == 'H' && idB == '4' && idC == '3') {
                return MAG_HMC5883L;
            }
        }
    }
    
    // 2. Спроба виявлення QMC5883L (адреса 0x0D)
    Wire.beginTransmission(0x0D);
    if (Wire.endTransmission() == 0) {
        Wire.beginTransmission(0x0D);
        Wire.write(0x0D); // Chip ID регістр QMC5883L
        Wire.endTransmission();
        Wire.requestFrom(0x0D, 1);
        if (Wire.available() >= 1) {
            uint8_t chipId = Wire.read();
            if (chipId == 0xFF) {
                return MAG_QMC5883L;
            }
        }
    }
    
    return MAG_UNKNOWN;
}
