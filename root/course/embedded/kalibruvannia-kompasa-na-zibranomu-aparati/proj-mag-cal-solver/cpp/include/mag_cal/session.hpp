// ===========================================================================
//  mag_cal/session.hpp — автомат процедури калібрування
//
//      Idle ──старт──► Collecting ──покриття 80 %──► Solving
//                          ▲   │                        │
//                тайм-аут  │   └──60 с без точок──► Idle│
//                                                       ├─RMS > 3.0──► Rejected
//                                                       └─RMS ≤ 3.0──► Validating
//                                                                          │
//                                                        cond(W) < 2.5 і   │
//                                                        запис із CRC32 ───► Saved
//
//  Сесія не знає ні про RTOS, ні про драйвери: результат розв'язувача їй
//  подають ззовні готовим, бо рахується він 2–4 мс і не має права крутитися
//  всередині виклику із сенсорного потоку.
// ===========================================================================
#pragma once

#include <cstdint>
#include <expected>

#include "mag_cal/calibration.hpp"
#include "mag_cal/collector.hpp"
#include "mag_cal/solver.hpp"
#include "mag_cal/storage.hpp"
#include "mag_cal/telemetry.hpp"

namespace mag_cal {

class CalibrationSession {
public:
    enum class State : std::uint8_t {
        Idle,
        Collecting,
        Solving,
        Validating,
        Rejected,
        Saved
    };

    CalibrationSession(std::uint8_t system_id, std::uint8_t component_id,
                       std::uint8_t compass_id, float earth_field_ut) noexcept;

    // Старт плати: підняти коефіцієнти з Flash і звірити CRC32
    std::expected<Calibration, StorageError> boot(std::uint32_t now_ms) noexcept;

    bool start(std::uint32_t now_ms) noexcept;
    void cancel(std::uint32_t now_ms) noexcept;

    // Швидкий шлях сенсорного потоку
    PushResult push(const Vec3& raw, const Vec3& gyro_rad_s,
                    std::uint32_t now_ms) noexcept;

    [[nodiscard]] bool ready_to_solve() const noexcept;
    void begin_solve(std::uint32_t now_ms) noexcept;
    void submit(const std::expected<Calibration, SolveFailure>& outcome,
                std::uint32_t now_ms) noexcept;

    // Тайм-аут бездіяльності й телеметрія прогресу
    void service(std::uint32_t now_ms) noexcept;

    [[nodiscard]] Vec3 correct(const Vec3& raw) const noexcept {
        return active_.apply(raw);
    }
    [[nodiscard]] bool arming_allowed() const noexcept;
    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] const Collector& collector() const noexcept { return collector_; }
    [[nodiscard]] const Calibration& active() const noexcept { return active_; }
    [[nodiscard]] bool mag_fault() const noexcept { return mag_fault_; }

private:
    void enter(State next, std::uint32_t now_ms) noexcept;
    void set_fault(bool fault) noexcept;

    Collector collector_;
    MavlinkReporter reporter_;
    Calibration active_{};      // чинні коефіцієнти польоту
    Calibration candidate_{};   // результат останнього прогону
    State state_{State::Idle};
    std::uint32_t state_since_ms_{0};
    bool mag_fault_{true};      // доки Flash не прочитано — відмова
};

// Порт плати: сигналізація відмови компаса
namespace board_port {
void set_fault_led(bool on) noexcept;
}  // namespace board_port

}  // namespace mag_cal
