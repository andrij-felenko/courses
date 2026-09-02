#pragma once

#include <cstdint>
#include <memory>
#include <optional>
#include <string_view>

#include "controller.hpp"
#include "posix_fd.hpp"

namespace servo {

/* Послідовний канал до автопілота: читаємо HIGHRES_IMU, пишемо
 * SET_ATTITUDE_TARGET. Генерований мегазаголовок MAVLink підключає лише .cpp,
 * тому стан парсера схований за вказівником на реалізацію. */
class MavlinkLink {
public:
    /* Кидає std::system_error, якщо порт не відкрився чи не налаштувався:
     * контролер без каналу до автопілота стартувати не повинен. */
    MavlinkLink(std::string_view device, int baud);
    ~MavlinkLink();

    MavlinkLink(const MavlinkLink&) = delete;
    MavlinkLink& operator=(const MavlinkLink&) = delete;

    /* Вичитує все, що прийшло, не блокуючись. Порожній результат означає
     * «свіжих гіроскопів цього такту не було» — це нормальний стан. */
    std::optional<BodyRates> poll();

    /* Кутові швидкості з уставок плюс нормована вертикальна тяга [0..1]. */
    bool send_rates(const GuidanceSetpoints& sp, float thrust, std::uint32_t boot_ms);

    [[nodiscard]] unsigned imu_messages() const noexcept { return imu_msgs_; }

private:
    struct Parser;

    PosixFd fd_;
    std::unique_ptr<Parser> parser_;
    std::uint8_t sysid_{1};
    std::uint8_t compid_{};
    std::uint8_t target_sysid_{1};
    std::uint8_t target_compid_{};
    unsigned imu_msgs_{0};
};

}  // namespace servo
