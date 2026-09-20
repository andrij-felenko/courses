#ifndef RVDT_DECODER_HPP
#define RVDT_DECODER_HPP

#include <cstdint>
#include <array>
#include <optional>
#include <cmath>

namespace controls {

// Структура сирих аналогових вимірювань з RVDT-датчика (у вольтах)
struct RVDTRawSample {
    float s1_volts;    // Напруга вторинної обмотки 1
    float s2_volts;    // Напруга вторинної обмотки 2
    float v_ref_volts; // Опорна напруга збудження (для валідації лінії)
};

// Інтерфейс апаратної абстракції АЦП (HAL)
class IAdcHal {
public:
    virtual ~IAdcHal() = default;
    
    // Зчитування миттєвих напруг з трьох аналогових каналів
    virtual std::optional<RVDTRawSample> readSample() = 0;
};

// Параметри полінома корекції нелінійності: y = c0 + c1*x + c2*x^2 + c3*x^3
struct LinearizationPoly {
    float c0{0.0f};
    float c1{1.0f};
    float c2{0.0f};
    float c3{0.0f};

    [[nodiscard]] float evaluate(float x) const noexcept {
        return c0 + x * (c1 + x * (c2 + x * c3));
    }
};

// Конфігурація декодера RVDT
struct RVDTConfig {
    float sensitivity_deg_per_ratio{40.0f}; // Коефіцієнт масштабування (град / (відношення напруг))
    float min_valid_vref{1.0f};              // Мінімальний поріг опорної напруги для виявлення обриву кабелю
    float iir_alpha{0.15f};                   // Коефіцієнт згладжування ІІР-фільтра (0 < alpha <= 1)
    LinearizationPoly poly_corr{};           // Поліноміальна корекція крайніх зон
};

// Результат декодування кутового переміщення
struct RVDTResult {
    float angle_degrees{0.0f}; // Обчислений та відфільтрований кут у градусах
    float raw_ratio{0.0f};     // Нормалізоване відношення (S1 - S2) / (S1 + S2)
    bool is_valid{false};      // Прапор дійсності даних (відсутність помилок АЦП та обривів)
};

// Клас-обгортка декодування сигналів RVDT
class RVDTDecoder {
public:
    explicit RVDTDecoder(IAdcHal& adc_hal, const RVDTConfig& config = RVDTConfig{})
        : adc_hal_(adc_hal), config_(config) {}

    // Опитування АЦП, цифрове фільтрування та перетворення у кут
    std::optional<RVDTResult> update();

    // Скидання стану цифрового фільтра
    void resetFilter() noexcept {
        filtered_ratio_.reset();
    }

    // Оновлення налаштувань
    void updateConfig(const RVDTConfig& new_config) noexcept {
        config_ = new_config;
    }

private:
    IAdcHal& adc_hal_;
    RVDTConfig config_;
    std::optional<float> filtered_ratio_{std::nullopt};
};

} // namespace controls

#endif // RVDT_DECODER_HPP
