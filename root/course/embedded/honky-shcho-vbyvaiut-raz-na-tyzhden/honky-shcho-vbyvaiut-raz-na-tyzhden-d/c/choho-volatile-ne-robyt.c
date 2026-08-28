/* НАЇВНИЙ, НЕБЕЗПЕЧНИЙ КОД */
volatile bool g_data_ready = false;
volatile uint32_t g_shared_sensor_data[4];

/* Головний цикл */
void update_sensor(void) {
    g_shared_sensor_data[0] = read_adc_ch0();
    g_shared_sensor_data[1] = read_adc_ch1();
    g_shared_sensor_data[2] = read_adc_ch2();
    g_shared_sensor_data[3] = read_adc_ch3();
    
    /* Розробник сподівається, що це безпечно сповістить переривання */
    g_data_ready = true;
}

/* Обробник переривання періодичного опитування */
void TIM2_IRQHandler(void) {
    if (g_data_ready) {
        /* ГОНКА: компілятор або процесор міг переставити запис 
         * g_data_ready ДО завершення запису елементів масиву! */
        transmit_telemetry((const uint32_t *)g_shared_sensor_data, 4);
        g_data_ready = false;
    }
}
