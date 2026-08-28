// thermo_api.hpp - Заголовочний файл C++23 інтерфейсу термодинамічного розв'язувача
#ifndef THERMO_API_HPP
#define THERMO_API_HPP

#include <expected>
#include <string_view>
#include <concepts>

namespace thermo::api {

enum class Status {
    Success = 0,
    InvalidPressure,
    InvalidVolume,
    InvalidTemperature,
    InvalidMoles,
    ConvergenceFailed
};

struct State {
    double p{0.0}; // [Па]
    double v{0.0}; // [м³]
    double t{0.0}; // [К]
};

struct GasProperties {
    double molar_mass{0.02897};        // [кг/моль]
    double degrees_of_freedom{5.0};    // i
    double c_v{20.786};                // [Дж/(моль·К)]
    double c_p{29.101};                // [Дж/(моль·К)]
    double gamma{1.400};               // C_p / C_v
};

struct ProcessRecord {
    State initial_state;
    State final_state;
    double n_moles{1.0};
    double work{0.0};     // W [Дж]
    double heat{0.0};     // Q [Дж]
    double delta_u{0.0};  // dU [Дж]
    double delta_h{0.0};  // dH [Дж]
};

} // namespace thermo::api

#endif // THERMO_API_HPP
