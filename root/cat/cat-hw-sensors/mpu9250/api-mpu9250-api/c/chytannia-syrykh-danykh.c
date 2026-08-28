#define REG_ACCEL_XOUT_H  0x3B

typedef struct {
    int16_t ax, ay, az;      // акселерометр, сирі
    int16_t temp;            // температура, сира
    int16_t gx, gy, gz;      // гіроскоп, сирі
} mpu_raw_t;

void mpu_read_raw(mpu_raw_t *r) {
    uint8_t b[14];
    i2c_read_regs(MPU_ADDR, REG_ACCEL_XOUT_H, b, 14);   // одне читання — усе

    // MPU віддає старший байт першим (big-endian):
    r->ax   = (int16_t)((b[0]  << 8) | b[1]);
    r->ay   = (int16_t)((b[2]  << 8) | b[3]);
    r->az   = (int16_t)((b[4]  << 8) | b[5]);
    r->temp = (int16_t)((b[6]  << 8) | b[7]);
    r->gx   = (int16_t)((b[8]  << 8) | b[9]);
    r->gy   = (int16_t)((b[10] << 8) | b[11]);
    r->gz   = (int16_t)((b[12] << 8) | b[13]);
}
