// Діапазони акселерометра: біти 4:3 регістра ACCEL_CONFIG.
#define ACCEL_FS_2G   (0 << 3)   // ±2 g,  16384 LSB/g  (найточніше)
#define ACCEL_FS_4G   (1 << 3)   // ±4 g,   8192 LSB/g
#define ACCEL_FS_8G   (2 << 3)   // ±8 g,   4096 LSB/g
#define ACCEL_FS_16G  (3 << 3)   // ±16 g,  2048 LSB/g  (найгрубіше)

// Діапазони гіроскопа: біти 4:3 регістра GYRO_CONFIG.
#define GYRO_FS_250   (0 << 3)   // ±250 °/с, 131.0 LSB/(°/с)
#define GYRO_FS_500   (1 << 3)   // ±500 °/с,  65.5 LSB/(°/с)
#define GYRO_FS_1000  (2 << 3)   // ±1000 °/с, 32.8 LSB/(°/с)
#define GYRO_FS_2000  (3 << 3)   // ±2000 °/с, 16.4 LSB/(°/с)

void mpu_set_ranges(uint8_t accel_fs, uint8_t gyro_fs) {
    i2c_write_reg(MPU_ADDR, REG_ACCEL_CONFIG, accel_fs);
    i2c_write_reg(MPU_ADDR, REG_GYRO_CONFIG,  gyro_fs);
}
