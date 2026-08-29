#pragma once

#include "flight_log.hpp"

#include <cstddef>
#include <string>
#include <vector>

namespace pid {

/// Чому вимірювання не можна довіряти.
enum class Distortion : unsigned {
    None = 0,
    GyroClip = 1u << 0,   ///< гіроскоп упирався в межу діапазону
    VbatSag = 1u << 1     ///< напруга просіла нижче порога відсічки
};

constexpr Distortion operator|(Distortion a, Distortion b) noexcept {
    return static_cast<Distortion>(static_cast<unsigned>(a) | static_cast<unsigned>(b));
}
constexpr Distortion& operator|=(Distortion& a, Distortion b) noexcept { return a = a | b; }
constexpr bool has(Distortion set, Distortion flag) noexcept {
    return (static_cast<unsigned>(set) & static_cast<unsigned>(flag)) != 0;
}
[[nodiscard]] std::string describe(Distortion set);

/// Вікно однієї сходинки в індексах логу.
struct StepWindow {
    std::size_t quietBegin{};   ///< початок спокійної передісторії
    std::size_t begin{};        ///< останній відлік перед фронтом
    std::size_t edgeEnd{};      ///< завдання вийшло на плато
    std::size_t end{};          ///< кінець вікна аналізу
    double amplitude{};         ///< Δ завдання, deg/s
    Distortion distortion{Distortion::None};

    [[nodiscard]] bool clean() const noexcept { return distortion == Distortion::None; }
};

/// Пороги триетапної фільтрації подій.
struct DetectConfig {
    double edgeSlopeMin = 600.0;   ///< |d(SetPoint)/dt|, deg/s²
    double edgeMinAmp = 40.0;      ///< deg/s
    Millis edgeMax{30.0};          ///< фронт має вкластися в цей час
    Millis quiet{80.0};            ///< скільки спокою вимагаємо перед фронтом
    double quietErrMax = 15.0;     ///< допустиме |SetPoint − Gyro|, deg/s
    Millis plateau{150.0};         ///< скільки завдання тримається після фронту
    double plateauTol = 5.0;       ///< тремтіння стіка на плато, deg/s
    Millis analysis{250.0};        ///< повна довжина вікна аналізу
    double gyroClip = 2000.0;      ///< межа діапазону гіроскопа, deg/s
    double vbatCutoff = 13.6;      ///< поріг відсічки батареї, В
};

/// Скільки фронтів і чому відсіялось — без цього видно лише «знайдено 0».
struct Rejections {
    std::size_t edges{};
    std::size_t ramp{};       ///< завдання їхало довше за edgeMax
    std::size_t small{};      ///< амплітуда менша за edgeMinAmp
    std::size_t noisy{};      ///< апарат ще коливався від попереднього маневру
    std::size_t noPlateau{};  ///< стік смикнули назад раніше часу
};

struct Search {
    std::vector<StepWindow> steps;
    Rejections rejected;
};

/// Виділяє з логу сходинки, придатні до вимірювання.
[[nodiscard]] Search findSteps(std::span<const Sample> log, const DetectConfig& cfg = {});

} // namespace pid
