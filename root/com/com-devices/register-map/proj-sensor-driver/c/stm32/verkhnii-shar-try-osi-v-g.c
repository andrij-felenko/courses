int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_I2C1_Init();                          // hi2c1: 400 кГц, піни — з CubeMX

    if (!mpu_present()) Error_Handler();     // біда з дротами/адресою
    if (mpu_begin() != HAL_OK) Error_Handler();  // збій налаштування

    float ax, ay, az;
    while (1) {
        if (mpu_read_accel(&ax, &ay, &az) == HAL_OK) {
            // ax, ay, az — у g, можна використовувати
        }
        HAL_Delay(20);
    }
}
