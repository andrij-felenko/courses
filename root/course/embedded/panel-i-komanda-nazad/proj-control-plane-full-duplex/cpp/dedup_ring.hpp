#pragma once

#include <array>
#include <chrono>
#include <mutex>
#include <optional>
#include <string>
#include <string_view>
#include <utility>

#include "protocol.hpp"

namespace cp {

/* Останній відомий результат команди: на повтор відповідаємо ним,
   а не новим рухом приводу. */
struct Outcome {
    std::string state{"QUEUED"};
    int         progressPct{0};
    int         valuePct{0};
    ErrCode     err{ErrCode::None};
};

/* Кільце фіксованої довжини: пам'ять під історію виділяється один раз.
   Пишуть його два потоки — мережевий (нові команди) і воркер (результати),
   тому замок живе всередині, а не в тому, хто кличе. */
class DedupRing {
public:
    static constexpr std::size_t Capacity = 16;

    [[nodiscard]] std::optional<Outcome> find(std::string_view cmdId) const
    {
        const std::scoped_lock lock{mutex_};
        for (std::size_t i = 0; i < count_; ++i) {
            if (slots_[i].cmdId == cmdId) {
                return slots_[i].outcome;
            }
        }
        return std::nullopt;
    }

    void remember(std::string_view cmdId, std::chrono::seconds now)
    {
        const std::scoped_lock lock{mutex_};
        slots_[head_] = Slot{std::string{cmdId}, now, Outcome{}};
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) {
            ++count_;
        }
    }

    void update(std::string_view cmdId, Outcome outcome)
    {
        const std::scoped_lock lock{mutex_};
        for (std::size_t i = 0; i < count_; ++i) {
            if (slots_[i].cmdId == cmdId) {
                slots_[i].outcome = std::move(outcome);
                return;
            }
        }
    }

private:
    struct Slot {
        std::string          cmdId;
        std::chrono::seconds stamp{0};
        Outcome              outcome;
    };

    mutable std::mutex          mutex_;
    std::array<Slot, Capacity>  slots_{};
    std::size_t                 head_{0};
    std::size_t                 count_{0};
};

}  // namespace cp
