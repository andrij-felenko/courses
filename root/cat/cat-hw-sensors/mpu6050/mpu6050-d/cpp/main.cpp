#include <Wire.h>

const uint8_t ADDR    = 0x68;   // AD0 на землі
const uint8_t PWR_MGMT_1 = 0x6B;
const uint8_t ACCEL_XOUT = 0x3B;

void writeReg(uint8_t reg, uint8_t val) {
    Wire.beginTransmission(ADDR);
    Wire.write(reg);
    Wire.write(val);
    Wire.endTransmission();
}

// Зчитати одне 16-бітне значення: спершу старший байт, тоді молодший.
int16_t read16() {
    uint8_t hi = Wire.read();
    uint8_t lo = Wire.read();
    return (int16_t)((hi << 8) | lo);
}

void setup() {
    Serial.begin(115200);
    Wire.begin();
    // Розбудити: скинути біт SLEEP у PWR_MGMT_1 (0 = працювати).
    // При старті чип спить — без цього рядка даних не буде.
    writeReg(PWR_MGMT_1, 0x00);
    delay(100);
}

void loop() {
    // Один пакет: 14 байтів поспіль від ACCEL_XOUT_H.
    Wire.beginTransmission(ADDR);
    Wire.write(ACCEL_XOUT);
    Wire.endTransmission(false);          // repeated start, не відпускаємо шину
    Wire.requestFrom(ADDR, (uint8_t)14);

    // Кожна вісь — два байти, СТАРШИЙ приходить першим (big-endian).
    // Читаємо їх окремими рядками: порядок двох Wire.read() в одному
    // виразі C не гарантує — інакше байти можуть мовчки помінятись місцями.
    int16_t ax = read16();
    int16_t ay = read16();
    int16_t az = read16();
    int16_t t  = read16();    // температура
    int16_t gx = read16();
    int16_t gy = read16();
    int16_t gz = read16();

    // Сире число → фізична величина (діапазони за замовчуванням ±2g, ±250°/s)
    float accX = ax / 16384.0f;           // g
    float gyrX = gx / 131.0f;             // °/s

    Serial.print(accX); Serial.print('\t');
    Serial.println(gyrX);
    delay(50);
}
