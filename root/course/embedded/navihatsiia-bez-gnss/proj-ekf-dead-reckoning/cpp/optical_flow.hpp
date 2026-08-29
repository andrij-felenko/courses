// optical_flow.hpp — сирий кадр PMW3901 → вимірювання горизонтальної
// швидкості, придатне для фільтра.
//
// Сенсор віддає не швидкість, а зсув текстури в пікселях за час кадру. Між
// цим зсувом і швидкістю апарата стоять три речі, і кожна вміє зіпсувати
// вимірювання мовчки:
//
//   · обертання. Кадр зсувається однаково і коли апарат летить, і коли він
//     просто нахиляється. Без деротації гіроскопом фільтр приймає нахил за
//     політ — найдорожча помилка в усій схемі;
//   · дальність. Кутова швидкість перетворюється на лінійну множенням на
//     відстань до поверхні: помилка дальності входить множником, не доданком;
//   · якість поверхні. Над однорідним асфальтом, водою чи в темряві сенсор
//     віддає правдоподібні числа, які означають шум. Про це попереджає
//     єдиний показник — SQUAL.
#pragma once

#include "ekf.hpp"

#include <cstdint>
#include <expected>
#include <numbers>

namespace nav {

// Один зчитаний кадр разом з усім, що описує ТОЙ САМИЙ момент часу.
struct FlowFrame {
    std::int16_t dpx{};        // регістри Delta_X/Delta_Y, пікселі за dt
    std::int16_t dpy{};
    std::uint8_t squal{};      // показник якості поверхні, 0..255
    float dt{};                // час накопичення кадру, с
    Vec3 gyro{};               // кутові швидкості тіла, рад/с
    Mat3 Rwb{};                // поворот «тіло → світ»
    float rangeRaw{};          // дальність ToF уздовж осі тіла Z, м
};

struct FlowMeasurement {
    float vx{};                // швидкість у світовій системі NED, м/с
    float vy{};
    float r{};                 // дисперсія саме цього вимірювання
    float range{};             // дальність по нормалі до поверхні, м
};

enum class FlowReject : std::uint8_t {
    Quality,    // поверхня без текстури або темрява
    Rate,       // кадр змазаний: кутова швидкість поза межами
    Range,      // сенсор не фокусується або втратив контраст
    Tilt,       // нахил такий, що дальність уже не перерахувати
    Numeric     // NaN на вході
};

class OpticalFlow {
public:
    struct Counters {
        std::uint32_t quality{};
        std::uint32_t rate{};
        std::uint32_t range{};
        std::uint32_t tilt{};
        std::uint32_t numeric{};
    };

    std::expected<FlowMeasurement, FlowReject> measure(FlowFrame const& f) noexcept;

    Counters const& rejections() const noexcept { return counters_; }

private:
    // Паспорт PMW3901: поле зору 42° на 35 пікселів матриці.
    static constexpr float kRadPerPixel =
        static_cast<float>(42.0 * std::numbers::pi / 180.0 / 35.0);
    static constexpr std::uint8_t kSqualMin = 30;
    static constexpr float kSqualRef = 100.0f;
    static constexpr float kMaxRate = 7.0f;      // рад/с — вище це вже змаз
    static constexpr float kMinRange = 0.08f;    // м
    static constexpr float kMaxRange = 8.0f;     // м
    static constexpr float kMinTiltCos = 0.70f;  // нахил до ≈45°
    static constexpr float kRbase = 0.02f;       // (м/с)² на 1 м дальності

    Counters counters_{};
};

}  // namespace nav
