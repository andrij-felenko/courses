#include <iostream>
#include <ranges>
#include <vector>
#include <chrono>
#include <thread>
#include <semaphore>

using namespace std::chrono_literals;

// 1. Корутина симуляції надходження телеметричних пакетів
Generator<ThermalReading> simulate_telemetry_stream(std::uint64_t max_count) {
    const std::vector<std::string> ids = {"REACTOR-1", "COOLING-2", "TURBINE-A"};
    double base_temperature_k = 345.0; // ~71.85 °C

    for (std::uint64_t i = 1; i <= max_count; ++i) {
        // Симуляція коливань показників та сплесків температури
        double jitter = ((i % 6 == 0) ? 58.0 : ((i % 2 == 0) ? 14.0 : -6.0));
        co_yield ThermalReading{
            .timestamp_ms = i * 100,
            .sensor_id = ids[i % ids.size()],
            .raw_value = base_temperature_k + jitter,
            .calibrated = (i % 17 != 0) // Періодична симуляція відмови калібрування
        };
    }
}

// 2. Функція побудови лінивого конвеєра діапазонів
template<SensorReading R>
auto create_anomaly_pipeline(Generator<R>& stream, double alert_celsius_threshold) {
    namespace rv = std::views;

    return stream
        | rv::filter([](const R& reading) {
            return reading.is_valid();
          })
        | rv::transform([](const R& reading) -> ProcessedAlarm {
            return ProcessedAlarm{
                .timestamp_ms = reading.timestamp_ms,
                .sensor_id = reading.sensor_id,
                .celsius = reading.raw_value - 273.15 // Перетворення з Кельвінів у градуси Цельсія
            };
          })
        | rv::filter([alert_celsius_threshold](const ProcessedAlarm& alarm) {
            return alarm.celsius >= alert_celsius_threshold;
          });
}

// 3. Головна функція запуску та координації
int main() {
    std::cout << "=== Запуск системи моніторингу на базі C++20 ===" << std::endl;

    std::binary_semaphore worker_started{0};

    // Запуск фонового робітника в окремому потоці std::jthread
    std::jthread worker([&worker_started](std::stop_token stop) {
        worker_started.release(); // Сигналізуємо головному потоку про успішний старт

        auto stream = simulate_telemetry_stream(60);
        auto alarms = create_anomaly_pipeline(stream, 80.0); // Поріг тривоги: >= 80 °C

        for (const ProcessedAlarm& alarm : alarms) {
            if (stop.stop_requested()) {
                std::cout << "Отримано сигнал зупинки stop_token. Переривання обробки." << std::endl;
                break;
            }

            // Вивід структурованого аварійного сповіщення
            std::cout << std::format("{}", alarm) << "\n";
            std::this_thread::sleep_for(25ms);
        }
    });

    worker_started.acquire();
    std::this_thread::sleep_for(180ms);

    // При виході з main деструктор worker автоматично надішле запит на зупинку
    // та дочекається завершення потоку (RAII Auto-Join)
    std::cout << "=== Головний потік ініціює завершення програми ===" << std::endl;
    return 0;
}
