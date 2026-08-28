#define REG_PWR_MGMT_1   0x6B
#define REG_GYRO_CONFIG   0x1B
#define REG_ACCEL_CONFIG  0x1C
#define REG_CONFIG        0x1A
#define REG_SMPLRT_DIV    0x19

void delay_ms(uint32_t ms);   // пауза платформи

void mpu_init(void) {
    // 1. Повний скид: біт 7 (DEVICE_RESET) → чип перезавантажує регістри.
    i2c_write_reg(MPU_ADDR, REG_PWR_MGMT_1, 0x80);
    delay_ms(100);                       // чекаємо, поки скид завершиться

    // 2. Прокинутися й узяти такт від PLL гіроскопа (значення 0x01),
    //    а не від грубого внутрішнього генератора (0x00).
    i2c_write_reg(MPU_ADDR, REG_PWR_MGMT_1, 0x01);
    delay_ms(10);

    // 3. Цифровий ФНЧ: смуга ~41 Гц (значення 0x03) — прибирає високочастотний
    //    шум і вібрацію; для дрона зазвичай беруть 20–40 Гц.
    i2c_write_reg(MPU_ADDR, REG_CONFIG, 0x03);

    // 4. Дільник частоти вибірки: 1 кГц / (1 + div). div=0 → 1 кГц.
    i2c_write_reg(MPU_ADDR, REG_SMPLRT_DIV, 0x00);

    // 5. Діапазони — див. нижче окремою функцією.
}
