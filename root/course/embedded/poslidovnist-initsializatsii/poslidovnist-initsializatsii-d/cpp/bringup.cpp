#include <chrono>
#include <print>

#include "sensor.hpp"

namespace bringup {
namespace {
using namespace std::chrono_literals;

constexpr unsigned kMaxAttempts = 3;
constexpr auto kBackoffBase = 50ms;
}  // namespace

std::string_view to_string(InitError error) {
    switch (error) {
        case InitError::Bus:     return "збій шини (NACK або залипла SDA)";
        case InitError::Timeout: return "таймаут готовності";
        case InitError::WrongId: return "невідповідний CHIP_ID";
        case InitError::Verify:  return "Read-Back не підтвердив конфігурацію";
    }
    return "невідома помилка";
}

// Одна повна спроба підйому: скидання -> ідентифікатор -> конфігурація.
std::expected<void, Fault> Sensor::attempt() {
    if (auto result = software_reset(); !result) {
        return result;
    }
    if (auto result = check_id(); !result) {
        return result;
    }
    return apply_config();
}

// Відкат стану: спершу глушимо переривання, інакше зависла лінія INT
// довбатиме процесор нескінченними хибними спрацюваннями.
void Sensor::rollback() noexcept {
    static_cast<void>(bus_.write(addr_, reg::IntEnable, 0x00));
    static_cast<void>(bus_.write(addr_, reg::Power, PowerStandby));
    state_ = State::Fault;
}

std::expected<void, Fault> Sensor::bring_up() {
    state_ = State::Uninitialized;
    attempts_ = 0;
    Fault last{InitError::Bus, 0};

    for (unsigned k = 1; k <= kMaxAttempts; ++k) {
        attempts_ = k;

        // Нульова фаза повтору: розчистити шину після невдалої спроби
        if (k > 1) {
            recover_bus(rail_, addr_);
        }

        auto result = attempt();
        if (result) {
            state_ = State::Ready;
            return {};
        }

        last = result.error();
        std::println("      спроба {}: {} (регістр 0x{:02X})", k, to_string(last.error),
                     last.reg);

        // Не той кремній на адресі — повтори тут безглузді
        if (last.error == InitError::WrongId) {
            break;
        }
        if (k < kMaxAttempts) {
            platform::sleep(kBackoffBase * (1u << (k - 1)));  // 50 -> 100 -> 200 мс
        }
    }

    rollback();
    return std::unexpected(last);
}

}  // namespace bringup
