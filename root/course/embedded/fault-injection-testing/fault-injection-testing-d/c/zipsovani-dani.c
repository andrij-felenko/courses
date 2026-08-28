int16_t read_temperature(void) {
    int16_t t = adc_to_celsius(adc_read());

#ifdef FAULT_INJECTION
    // вкидаємо несправність: давач «здурів» і віддає неможливе значення
    if (fault_active(FAULT_SENSOR_INSANE))
        t = 850;                    // 850 °C — фізично неможливо для цієї системи
#endif

    return t;
}
