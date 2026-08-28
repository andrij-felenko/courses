// Концептуальний вигляд статичної рефлексії C++26:
struct DeviceConfig {
    int baud_rate;
    int timeout_ms;
    bool enable_crc;
};

consteval std::string generate_json_schema() {
    // Рефлексія аналізує поля структури через constexpr-алгоритми
    // std::meta::members_of(^^DeviceConfig) повертає вектор дескрипторів
    // Генерація тексту схеми відбувається без жодних сторонніх інструментів
    return "{ ... }";
}
