// Сучасний C++ за правилами Core Guidelines: повна типобезпека, RAII та відсутність витоків
#include <string>
#include <vector>
#include <span>
#include <memory>
#include <string_view>

class SensorData {
public:
    // I.13: std::span захищає від виходу за межі масиву без додаткового виділення пам'яті
    // F.16: std::string_view передає рядок без зайвих копіювань
    SensorData(std::string_view name, std::span<const double> initial_data)
        : name_(name), readings_(initial_data.begin(), initial_data.end()) {}

    // C.21 / C.67: Правило нуля — компілятор автоматично генерує коректний деструктор,
    // конструктори переміщення та копіювання без ручного керування пам'яттю
    ~SensorData() = default;
    SensorData(const SensorData&) = default;
    SensorData& operator=(const SensorData&) = default;
    SensorData(SensorData&&) noexcept = default;
    SensorData& operator=(SensorData&&) noexcept = default;

    [[nodiscard]] std::string_view name() const noexcept { return name_; }
    [[nodiscard]] std::span<const double> readings() const noexcept { return readings_; }

private:
    std::string name_;
    std::vector<double> readings_;
};

// R.30: Фабрична функція повертає об'єкт через std::unique_ptr, явно фіксуючи передачу володіння
[[nodiscard]] std::unique_ptr<SensorData> make_sensor(
    std::string_view name, 
    std::span<const double> initial_data) 
{
    return std::make_unique<SensorData>(name, initial_data);
}
