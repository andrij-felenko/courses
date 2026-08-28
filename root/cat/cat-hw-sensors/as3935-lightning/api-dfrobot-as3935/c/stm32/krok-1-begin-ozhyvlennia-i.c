int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_I2C1_Init();                         // 400 кГц, згенеровано CubeMX

    // Чи озивається чіп за цією адресою: 3 спроби, таймаут 100 мс
    while (HAL_I2C_IsDeviceReady(&hi2c1, AS3935_ADDR, 3, 100) != HAL_OK) {
        printf("AS3935 не відповідає — звір адресу з DIP і дроти\r\n");
        HAL_Delay(1000);
    }
    printf("AS3935 на шині, адресу знайдено\r\n");
