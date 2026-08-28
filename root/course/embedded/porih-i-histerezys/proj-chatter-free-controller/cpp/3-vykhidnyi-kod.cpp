#include <iostream>
#include <vector>
#include <chrono>

int main() {
    using namespace std::chrono_literals;

    // Конфігурація для захисту нагрівача бойлера:
    // Пороги: 58.0 °C (увімк) ... 62.0 °C (вимк)
    // Гарантований час роботи не менше 3000 мс, пауза не менше 5000 мс
    HysteresisController<float, 5>::Config cfg{
        .threshold_low = 58.0f,
        .threshold_high = 62.0f,
        .min_on_time = 3000ms,
        .min_off_time = 5000ms,
        .ema_alpha = 0.3f,
        .mode = HysteresisMode::ActiveLow
    };

    HysteresisController<float, 5> controller(cfg);

    // Тестовий потік вимірювань із аномальними завадами та повільним трендом
    struct TestPoint {
        std::chrono::milliseconds time;
        float raw_adc;
        const char* description;
    };

    const std::vector<TestPoint> test_cases = {
        {   0ms, 65.0f, "Початковий стан: бак гарячий" },
        { 500ms, 61.0f, "Поступове охолодження" },
        {1000ms, 99.0f, "Імпульсна завада від контактора (+99 °C) -> відсікається медіаною" },
        {1500ms, 57.5f, "Температура впала нижче Low (58 °C) -> увімкнення ТЕНа" },
        {2000ms, 57.0f, "Нагрівання розпочато, стан ON" },
        {2500ms, 63.0f, "Швидкий сплеск вище High, але min_on_time ще не минув -> стан ON зберігається" },
        {4600ms, 62.5f, "Пройшло > 3000 мс і температура > High -> коректне вимкнення ТЕНа" },
        {5000ms, 56.0f, "Швидке падіння < Low, але діє min_off_time -> увімкнення заблоковано" },
        {9800ms, 56.0f, "Пауза min_off_time вичерпана -> повторний безпечний пуск ТЕНа" }
    };

    for (const auto& pt : test_cases) {
        bool state = controller.update(pt.raw_adc, pt.time);
        std::cout << "[" << pt.time.count() << " ms] " << pt.description << "\n"
                  << "  Raw: " << pt.raw_adc << " °C | Filtered: " << controller.filtered_value()
                  << " °C | Relay: " << (state ? "ON" : "OFF") << "\n\n";
    }

    return 0;
}
