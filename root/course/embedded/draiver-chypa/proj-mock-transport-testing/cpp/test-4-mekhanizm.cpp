// C++20: Запуск тестів з сучасними асертами та перевірками статусів
int main() {
    using namespace embedded::testing;
    using namespace embedded::drivers;

    std::cout << "=== Запуск C++20 Unit-тестів драйвера чипа ===\n";

    MockTransport mock;
    ChipSensor sensor(mock, 0x19);

    // --- Тест 1: Успішна ініціалізація ---
    mock.reset();
    auto init_status = sensor.init();
    assert(init_status == Status::Ok);
    assert(sensor.isInitialized());
    assert(mock.writeLog().size() >= 2);
    std::cout << "[PASS] Тест 1: Ініціалізація та запис конфігурації\n";

    // --- Тест 2: Некоректний ідентифікатор пристрою ---
    mock.reset();
    mock.write(MockTransport::RegWhoAmI, std::array<const std::uint8_t, 1>{0xAA});
    auto fail_status = sensor.init();
    assert(fail_status == Status::DeviceNotFound);
    std::cout << "[PASS] Тест 2: Виявлення невідповідності ідентифікатора чипа\n";

    // --- Тест 3: Читання та фізичне масштабування SI ---
    mock.reset();
    sensor.init();
    sensor.setRange(2); // ±2g
    mock.setRawXyz(0, 0, 16384); // 1g по осі Z

    auto sample = sensor.readAccelerationSi();
    assert(sample.has_value());
    assert(sample->x >= -0.01F && sample->x <= 0.01F);
    assert(sample->y >= -0.01F && sample->y <= 0.01F);
    assert(sample->z >= 9.75F && sample->z <= 9.85F);
    std::cout << "[PASS] Тест 3: Конвертація в м/с² та перевірка границь похибки\n";

    // --- Тест 4: Автоматичне відновлення після короткочасного збою ---
    mock.reset();
    sensor.init();
    mock.setRawXyz(0, 0, 16384);
    mock.injectReadFailures(2);

    auto recovered_sample = sensor.readAccelerationSi();
    assert(recovered_sample.has_value());
    std::cout << "[PASS] Тест 4: Успішне відновлення через механізм повторів (Retries)\n";

    std::cout << "\n>>> Усі C++20 тести успішно виконані на комп'ютері розробника! <<<\n";
    return 0;
}
