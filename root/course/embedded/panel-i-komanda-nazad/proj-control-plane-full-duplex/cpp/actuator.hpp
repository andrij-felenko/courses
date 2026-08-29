#pragma once

#include <chrono>
#include <cstddef>
#include <deque>
#include <mutex>
#include <optional>
#include <string>
#include <string_view>

#include "dedup_ring.hpp"
#include "protocol.hpp"
#include "valve.hpp"

namespace cp {

using Millis = std::chrono::milliseconds;

/* Апаратний воркер. submit() кличе мережевий потік, poll() — потік приводу;
   між ними черга під замком (на FreeRTOS її роль виконує xQueueHandle). */
class Actuator {
public:
    struct Job {
        std::string cmdId;
        int         targetPct{0};
    };

    /* Конструктор — це і є старт після скидання: тут розбирається маневр,
       обірваний просіданням живлення. */
    Actuator(Valve& valve, DedupRing& dedup);

    [[nodiscard]] bool submit(Job job);      // false — інбокс переповнений
    [[nodiscard]] bool busy() const;
    [[nodiscard]] int  position() const;

    void poll(Millis now);                   // ніколи не блокує

private:
    static constexpr std::size_t InboxLimit = 4;
    static constexpr Millis      MoveTimeout{6000};
    static constexpr Millis      ProgressPeriod{500};
    static constexpr int         TolerancePct = 2;

    std::optional<Job> takeJob();
    void begin(Job job, Millis now);
    void finish(std::string_view state, int progress, int pos, ErrCode err);
    void report(std::string_view state, int progress, int value, ErrCode err);
    [[nodiscard]] bool reached(int pos) const;
    [[nodiscard]] int  progressPct(int pos) const;

    Valve&     valve_;
    DedupRing& dedup_;

    mutable std::mutex inboxMutex_;
    std::deque<Job>    inbox_;

    bool        moving_{false};
    std::string cmdId_;
    int         targetPct_{0};
    int         startPct_{0};
    Millis      startedAt_{0};
    Millis      lastReport_{0};
};

}  // namespace cp
