#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

namespace robot::compliance {

inline constexpr std::size_t kDof = 6;          // Fx Fy Fz Tx Ty Tz
inline constexpr float kDtSec = 0.001f;         // контур 1 кГц
inline constexpr std::uint32_t kTareSamples = 500;

using Vector6 = std::array<float, kDof>;
using Vector6View = std::span<const float, kDof>;

enum class Mode : std::uint8_t {
    Idle,
    Taring,
    Active,
    ForceExceeded,
    Retract,
    Fault,
};

enum class Fault : std::uint8_t {
    InvalidConfig, // коефіцієнти не годяться до роботи
    TareDisturbed, // під час тарування інструмент уже щось торкав
    ForceLimit,    // спрацював аварійний ліміт сили
};

struct Config {
    Vector6 virtual_mass{};      // кг, кг·м²
    Vector6 virtual_damping{};   // Н·с/м, Н·м·с/рад
    Vector6 virtual_stiffness{}; // Н/м, Н·м/рад
    Vector6 deadband{};          // Н, Н·м
    Vector6 max_force{};         // Н, Н·м
    Vector6 max_disp{};          // м, рад
    Vector6 max_vel{};           // м/с, рад/с
    float filter_alpha{0.1f};
    float retract_speed{0.05f};

    [[nodiscard]] bool valid() const noexcept;

    // D = 2·sqrt(M·K): zeta = 1, зрив контакту без перерегулювання.
    void set_critical_damping() noexcept;

    [[nodiscard]] static float alpha_for_cutoff(float cutoff_hz) noexcept;
};

struct Command {
    Vector6 pose{};  // номінал, зміщений податливістю
    Vector6 twist{}; // відповідна швидкість
};

// Регулятор адмітансу: сила на вході, зміщена траєкторія на виході.
// Працює в системі силомоментного давача.
class Controller {
public:
    // Негодящі коефіцієнти не дають створити об'єкт — далі перевіряти нічого.
    [[nodiscard]] static std::expected<Controller, Fault> create(const Config& cfg) noexcept;

    void start_tare() noexcept;

    // Квитування аварії: Retract → Active. Набране зміщення лишається,
    // до номіналу його поверне віртуальна пружина.
    void acknowledge() noexcept;

    // f_ext — сила РЕАКЦІЇ у системі давача, вже без ваги інструмента,
    // але ще зі зсувом нуля.
    [[nodiscard]] std::expected<Command, Fault> step(Vector6View f_ext,
                                                     Vector6View x_nominal,
                                                     Vector6View v_nominal) noexcept;

    [[nodiscard]] Mode mode() const noexcept { return mode_; }
    [[nodiscard]] const Vector6& filtered_force() const noexcept { return f_filt_; }
    [[nodiscard]] const Vector6& displacement() const noexcept { return disp_; }
    [[nodiscard]] bool retract_finished() const noexcept;

private:
    explicit Controller(const Config& cfg) noexcept : cfg_{cfg} {}

    [[nodiscard]] Command hold(Vector6View x_nominal) const noexcept;
    [[nodiscard]] std::expected<Command, Fault> step_tare(Vector6View f_ext,
                                                          Vector6View x_nominal,
                                                          Vector6View v_nominal) noexcept;
    [[nodiscard]] Command step_retract(Vector6View x_nominal) noexcept;
    [[nodiscard]] std::expected<Command, Fault> step_active(Vector6View f_ext,
                                                            Vector6View x_nominal,
                                                            Vector6View v_nominal) noexcept;
    void latch_retract_direction() noexcept;

    Config cfg_;
    Vector6 f_raw_offset_{};
    Vector6 f_filt_{};
    Vector6 disp_{};
    Vector6 vel_{};
    Vector6 retract_dir_{};
    Vector6 tare_accum_{};
    std::uint32_t tare_counter_{0};
    Mode mode_{Mode::Idle};
};

} // namespace robot::compliance
