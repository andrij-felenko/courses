#ifndef OSCILLOSCOPE_TRACE_HPP
#define OSCILLOSCOPE_TRACE_HPP

#include <cstddef>
#include <optional>
#include <utility>
#include <vector>

/**
 * @brief Дискретна вибірка сигналу з цифрового осцилографа.
 */
struct SamplePoint {
    double time_s{0.0};     // Часова мітка відліку в секундах
    double voltage_v{0.0};  // Миттєве значення напруги у вольтах
};

/**
 * @brief Напрямок перехідного процесу (нахил фронту сигналу).
 */
enum class EdgeSlope {
    Rising,  // Наростаючий фронт (перехід від базового рівня до полиці)
    Falling  // Спадний фронт (перехід від верхнього рівня до бази)
};

/**
 * @brief Клас інкапсуляції та обробки часової послідовності осцилограми.
 *
 * Відповідає за валідацію цілісності часових міток, фільтрацію короткочасних
 * викидів дискретизації, визначення квазістаціонарних рівнів напруги (0% і 100%)
 * та субдискретну лінійну інтерполяцію моментів перетину порогових рівнів для
 * точного обчислення тривалості наростання сигналу (rise time).
 */
class OscilloscopeTrace {
public:
    OscilloscopeTrace() = default;
    explicit OscilloscopeTrace(std::vector<SamplePoint> samples);

    // Додавання окремої точки вибірки
    void addSample(double time_s, double voltage_v);
    void addSample(const SamplePoint& sample);

    // Доступ до даних
    [[nodiscard]] const std::vector<SamplePoint>& samples() const noexcept;
    [[nodiscard]] std::size_t sampleCount() const noexcept;
    [[nodiscard]] bool empty() const noexcept;
    void clear() noexcept;

    // Перевірка строгої хронологічної монотонності часової шкали
    [[nodiscard]] bool validateMonotonicity() const noexcept;

    // Фільтрація поодиноких викидів (spikes) амплітудним фільтром сусідів
    void filterOutliers(double max_spike_delta_v = 1.5);

    // Розрахунок стаціонарних рівнів напруги: повертає пару {базова лінія 0%, полиця 100%}
    [[nodiscard]] std::optional<std::pair<double, double>> calculateAmplitudeLevels() const;

    // Субдискретне визначення часової мітки перетину заданої напруги лінійною інтерполяцією
    [[nodiscard]] std::optional<double> findThresholdCrossingTime(double target_voltage,
                                                                 EdgeSlope slope = EdgeSlope::Rising) const;

    // Обчислення тривалості наростання фронту (типово між рівнями 10% та 90%)
    [[nodiscard]] std::optional<double> calculateRiseTime(double lower_percent = 0.10,
                                                          double upper_percent = 0.90) const;

private:
    std::vector<SamplePoint> samples_;
};

#endif // OSCILLOSCOPE_TRACE_HPP
