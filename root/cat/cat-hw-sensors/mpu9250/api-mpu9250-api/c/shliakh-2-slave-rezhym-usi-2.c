typedef struct {
    int16_t ax, ay, az, temp, gx, gy, gz;   // сирі акселерометр/темп/гіро
    int16_t mx, my, mz;                     // сирий магнетометр
    uint8_t mag_ovf;                        // прапорець перевантаження поля
} imu9_t;

void imu_read_9(imu9_t *d) {
    uint8_t a[14], m[8];
    i2c_read_regs(MPU_ADDR, REG_ACCEL_XOUT_H,    a, 14);  // акс/темп/гіро
    i2c_read_regs(MPU_ADDR, REG_EXT_SENS_DATA_00, m, 8);  // магнетометр

    // Акселерометр/гіроскоп — старший байт першим (big-endian):
    d->ax = (int16_t)((a[0] << 8)|a[1]);   d->ay = (int16_t)((a[2] << 8)|a[3]);
    d->az = (int16_t)((a[4] << 8)|a[5]);   d->temp=(int16_t)((a[6] << 8)|a[7]);
    d->gx = (int16_t)((a[8] << 8)|a[9]);   d->gy = (int16_t)((a[10]<<8)|a[11]);
    d->gz = (int16_t)((a[12]<<8)|a[13]);

    // m[0] = ST1; далі шість байтів поля МОЛОДШИМ першим (little-endian!);
    // m[7] = ST2. Порядок байтів у магнетометра ПРОТИЛЕЖНИЙ до MPU:
    d->mx = (int16_t)((m[2] << 8)|m[1]);   // HXH<<8 | HXL
    d->my = (int16_t)((m[4] << 8)|m[3]);
    d->mz = (int16_t)((m[6] << 8)|m[5]);
    d->mag_ovf = (m[7] & 0x08) ? 1 : 0;    // ST2 біт 3 = HOFL (перевантаження)
}
