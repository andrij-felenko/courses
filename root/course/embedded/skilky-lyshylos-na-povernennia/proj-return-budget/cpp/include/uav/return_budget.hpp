#pragma once

#include <cstdint>
#include <expected>
#include <string_view>

// Оцінювач енергетичного бюджету повернення. Стан живе в об'єкті Estimator,
// динамічної пам'яті модуль не торкається взагалі.
namespace uav::nav {

enum class State : std::uint8_t {
    Ok,             // запасу вистачає з надлишком
    Caution,        // точка неповернення поруч
    RtlMandatory,   // повертатися треба негайно
    EmergencyLand   // повернення вже неможливе — сідати тут
};

enum class Error : std::uint8_t {
    InvalidConfig,    // конфігурація планера несумісна сама з собою
    InvalidTelemetry, // NaN/inf або від'ємні величини в кадрі телеметрії
    CrosswindLimit,   // бокова складова вітру ≥ повітряної швидкості
    HeadwindTooHigh   // шляхова швидкість зближення впала до нуля
};

[[nodiscard]] constexpr std::string_view toString(State state) noexcept {
    switch (state) {
        case State::Ok:            return "OK";
        case State::Caution:       return "CAUTION";
        case State::RtlMandatory:  return "RTL_MANDATORY";
        case State::EmergencyLand: return "EMERGENCY_LAND";
    }
    return "UNKNOWN";
}

[[nodiscard]] constexpr std::string_view toString(Error error) noexcept {
    switch (error) {
        case Error::InvalidConfig:    return "INVALID_CONFIG";
        case Error::InvalidTelemetry: return "INVALID_TELEMETRY";
        case Error::CrosswindLimit:   return "CROSSWIND_LIMIT";
        case Error::HeadwindTooHigh:  return "HEADWIND_TOO_HIGH";
    }
    return "UNKNOWN";
}

// Горизонтальні складові локальної системи NED
struct Vec2 {
    float north{0.0f};
    float east{0.0f};
};

struct Vec3 {
    float north{0.0f};
    float east{0.0f};
    float down{0.0f};
};

struct Config {
    // Обмеження повітряної швидкості, м/с
    float v_air_min_ms{0.0f};
    float v_air_max_ms{0.0f};
    float v_best_range_still_ms{0.0f};

    // Поляра потужності: P(V) = c_ind / V + c_par * V^3 + p_avionics_watts
    float c_ind{0.0f};
    float c_par{0.0f};
    float p_avionics_watts{0.0f};

    // Набір ешелону повернення й посадка
    float rtl_safe_altitude_m{0.0f};
    float v_climb_ms{0.0f};
    float p_climb_watts{0.0f};
    float p_hover_watts{0.0f};
    float t_land_maneuver_sec{0.0f};

    // Запас і згладжування
    float reserve_margin_ratio{0.0f};
    float filter_time_constant_s{0.0f};

    // Батарея
    float nominal_energy_wh{0.0f};
    float cell_v_cutoff{0.0f};
    std::uint8_t cell_count{0};
};

struct Telemetry {
    Vec3 position{};              // поточна позиція, м
    Vec3 home{};                  // точка Home у тій самій NED, м
    Vec2 wind{};                  // ВЕКТОР ШВИДКОСТІ повітря (куди дме), м/с
    float voltage_v{0.0f};        // напруга пакета під поточним навантаженням
    float r_internal_ohms{0.0f};  // внутрішній опір пакета
    float energy_remaining_wh{0.0f};
    bool airspeed_synthetic{false}; // трубка Піто втрачена, швидкість дає EKF
};

struct Budget {
    float distance_to_home_m{0.0f};
    float time_to_home_sec{0.0f};
    float v_air_optimal_ms{0.0f};
    float v_ground_ret_ms{0.0f};
    float wca_rad{0.0f};

    float e_cruise_wh{0.0f};
    float e_climb_wh{0.0f};
    float e_land_wh{0.0f};
    float e_reserve_wh{0.0f};
    float e_return_total_wh{0.0f};  // повна вартість повернення після фільтра

    float projected_sag_voltage_v{0.0f};
    float e_usable_compensated_wh{0.0f};
    float energy_margin_ratio{0.0f};

    State state{State::Ok};
    bool rtl_mandatory{false};
};

class Estimator {
public:
    // Єдиний спосіб отримати оцінювач: невалідна конфігурація не створює об'єкта.
    [[nodiscard]] static std::expected<Estimator, Error> create(const Config& config) noexcept;

    // Один крок. dt_sec — час від попереднього виклику: стала часу фільтра рахується
    // від нього, тож плавання періоду виклику не міняє смуги згладжування.
    [[nodiscard]] std::expected<Budget, Error> update(const Telemetry& telemetry,
                                                      float dt_sec) noexcept;

    // Скидає фільтр і рішення перед новим польотом.
    void reset() noexcept;

    [[nodiscard]] State state() const noexcept { return state_; }

private:
    explicit Estimator(const Config& config) noexcept : config_{config} {}

    [[nodiscard]] float optimalAirspeed(float headwind_ms) const noexcept;
    [[nodiscard]] float cruisePower(float v_air_ms) const noexcept;

    Config config_{};
    float filtered_return_wh_{0.0f};
    State state_{State::Ok};
};

} // namespace uav::nav
