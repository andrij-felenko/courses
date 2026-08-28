// sensor.h — спільний контракт для обох збірок:
int sensor_read_temp(void);

// sensor_hw.c — лінкуємо в бойову прошивку:
int sensor_read_temp(void) { return read_i2c_sensor(); }   // справжнє залізо

// sensor_fake.c — лінкуємо в тест замість sensor_hw.c:
static int g_next;
void sensor_set_temp(int t) { g_next = t; }                // тест задає сценарій
int sensor_read_temp(void) { return g_next; }              // підроблена відповідь
