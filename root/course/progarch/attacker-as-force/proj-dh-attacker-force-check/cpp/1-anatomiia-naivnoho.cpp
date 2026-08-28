/* cpp */
// Наївна обробка C++: небезпечне копіювання рядка та припущення про вирівнювання
void process_sensor_packet_naive(const std::uint8_t* raw_buf) {
    char sensor_id[32];
    // НЕБЕЗПЕКА: std::strcpy без перевірки розмірів буфера
    std::strcpy(sensor_id, reinterpret_cast<const char*>(raw_buf));
    float temp = *reinterpret_cast<const float*>(raw_buf + 32);

    // Пряме виконання команди без перевірки авторизації
    execute_device_command(sensor_id, temp);
}
