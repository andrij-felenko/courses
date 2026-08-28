#ifdef HIL_BUILD
    // СТЕНДОВА збірка: вимір беремо з останнього HIL-повідомлення,
    // яке симулятор надіслав по USB/UART. Драйвер чипа не чіпаємо.
    static volatile imu_sample_t g_injected;   // оновлює приймач HIL-пакета

    bool imu_read(imu_sample_t *out) {
        *out = g_injected;      // модельний вимір замість справжнього гіроскопа
        return true;
    }
#else
    // БОЙОВА збірка: справжній драйвер справжнього гіроскопа по SPI.
    bool imu_read(imu_sample_t *out) {
        return icm20948_read(out);   // реальне залізо
    }
#endif
