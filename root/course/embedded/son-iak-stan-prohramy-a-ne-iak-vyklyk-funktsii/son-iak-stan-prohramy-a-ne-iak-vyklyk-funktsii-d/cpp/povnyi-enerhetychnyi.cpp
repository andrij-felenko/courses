/* Головний цикл обробки подій з диспетчером живлення (C++20) */
#include <cstdint>
#include <optional>

namespace emb {

struct Event {};

class EventQueue {
public:
    [[nodiscard]] std::optional<Event> pop() noexcept { return std::nullopt; }
    [[nodiscard]] bool empty() const noexcept { return true; }
};

class TimerManager {
public:
    [[nodiscard]] uint32_t millisecondsToNextDeadline() const noexcept { return 1000U; }
};

void dispatchEvent(const Event&) noexcept {}

void runMainLoop(EventQueue& queue, TimerManager& timers) noexcept {
    while (true) {
        // 1. Диспетчеризація всіх подій черги
        while (auto event = queue.pop()) {
            dispatchEvent(*event);
        }

        // 2. Оцінка часу бездіяльності та безпечне занурення в сон
        const uint32_t idleMs = timers.millisecondsToNextDeadline();
        // pm::PowerManager::instance().sleepIfIdle(idleMs);
        (void)idleMs;
    }
}

} // namespace emb
