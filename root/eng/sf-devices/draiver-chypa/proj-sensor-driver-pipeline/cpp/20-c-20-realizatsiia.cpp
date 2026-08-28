using namespace sf::devices::units::literals;

auto sample = driver.readSynchronous();
if (sample.has_value()) {
    units::Pascals press = sample->pressure;
    units::Celsius temp  = sample->temperature;

    // Зручне перетворення у похідні одиниці без помилок масштабу
    float hpa = press.hectopascals(); // гектопаскалі
    float k   = temp.kelvin();        // Кельвіни

    // Безпечне порівняння з користувацькими літералами
    if (press < 950.0_hPa) {
        triggerLowPressureAlarm();
    }
}
