#include <stdint.h>
#include <stdbool.h>

#define TCA9548A_ADDR   0x70
#define SENSOR_IMU_ADDR 0x68

extern bool i2c_master_write(uint8_t dev_addr, const uint8_t* data, uint16_t len);
extern bool i2c_master_read(uint8_t dev_addr, uint8_t* data, uint16_t len);

// Функція вибору активного каналу комутатора (0..7)
bool tca9548a_select_channel(uint8_t channel)
{
    if (channel > 7) return false;
    uint8_t control_mask = (1 << channel);
    return i2c_master_write(TCA9548A_ADDR, &control_mask, 1);
}

// Опитування двох однакових давачів на різних гілках
bool read_two_conflicting_sensors(int16_t* accel_sensor1, int16_t* accel_sensor2)
{
    uint8_t reg_addr = 0x3B; // Регістр старту даних акселерометра
    uint8_t buf[2];

    // 1. Опитування першого давача на каналі 0
    if (!tca9548a_select_channel(0)) return false;
    if (!i2c_master_write(SENSOR_IMU_ADDR, &reg_addr, 1)) return false;
    if (!i2c_master_read(SENSOR_IMU_ADDR, buf, 2)) return false;
    *accel_sensor1 = (int16_t)((buf[0] << 8) | buf[1]);

    // 2. Опитування другого давача на каналі 1
    if (!tca9548a_select_channel(1)) return false;
    if (!i2c_master_write(SENSOR_IMU_ADDR, &reg_addr, 1)) return false;
    if (!i2c_master_read(SENSOR_IMU_ADDR, buf, 2)) return false;
    *accel_sensor2 = (int16_t)((buf[0] << 8) | buf[1]);

    return true;
}
