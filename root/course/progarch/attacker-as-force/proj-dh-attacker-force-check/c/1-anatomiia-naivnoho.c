/* c */
// Наївна обробка: довіра до довжини та вмісту пакета з мережі
void process_sensor_packet_naive(uint8_t *raw_buf) {
    char sensor_id[32];
    // НЕБЕЗПЕКА: strcpy/memcpy без перевірки меж та валідації джерела!
    strcpy(sensor_id, (char*)raw_buf); 
    float temp = *(float*)(raw_buf + 32);

    // Пряме виконання команди без авторизації
    execute_device_command(sensor_id, temp); 
}
