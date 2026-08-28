#include <iostream>
#include <vector>
#include <list>
#include <memory>
#include <functional>
#include <cstdint>
#include <stdexcept>
#include <string>

class TimerWheel {
public:
    using Callback = std::function<void(std::uint64_t id)>;

    struct TimerEntry {
        std::uint64_t id;
        std::uint64_t expires;
        Callback callback;
    };

    explicit TimerWheel(std::uint64_t start_tick = 0)
        : current_tick_(start_tick),
          tv1_(TV1_SIZE),
          tv2_(TV2_SIZE) {}

    // Додавання нового таймера
    void schedule(std::uint64_t id, std::uint64_t delay, Callback cb) {
        if (!cb) {
            throw std::invalid_argument("Callback cannot be empty");
        }

        auto entry = std::make_shared<TimerEntry>(TimerEntry{id, current_tick_ + delay, std::move(cb)});
        std::uint64_t delta = entry->expires - current_tick_;

        if (delta < TV1_SIZE) {
            std::size_t slot = entry->expires & TV1_MASK;
            tv1_[slot].push_back(entry);
        } else if (delta < (1ULL << (TV1_BITS + TV2_BITS))) {
            std::size_t slot = (entry->expires >> TV1_BITS) & TV2_MASK;
            tv2_[slot].push_back(entry);
        } else {
            throw std::out_of_range("Timer delay exceeds maximum supported range");
        }
    }

    // Просування часу на 1 крок (Tick)
    void tick() {
        current_tick_++;
        std::size_t tv1_slot = current_tick_ & TV1_MASK;

        // Повний оберт TV1 -> виконуємо каскадування з TV2
        if (tv1_slot == 0) {
            std::size_t tv2_slot = (current_tick_ >> TV1_BITS) & TV2_MASK;
            cascade(tv2_slot);
        }

        // Отримуємо таймери поточного слота TV1
        std::list<std::shared_ptr<TimerEntry>> expired;
        expired.swap(tv1_[tv1_slot]);

        for (const auto& timer : expired) {
            if (timer && timer->callback) {
                timer->callback(timer->id);
            }
        }
    }

    [[nodiscard]] std::uint64_t current_tick() const noexcept {
        return current_tick_;
    }

private:
    static constexpr std::size_t TV1_BITS = 8;
    static constexpr std::size_t TV1_SIZE = 1U << TV1_BITS; // 256
    static constexpr std::size_t TV2_BITS = 6;
    static constexpr std::size_t TV2_SIZE = 1U << TV2_BITS; // 64
    static constexpr std::size_t TV2_MASK = TV2_SIZE - 1;

    void cascade(std::size_t tv2_slot) {
        std::list<std::shared_ptr<TimerEntry>> bucket;
        bucket.swap(tv2_[tv2_slot]);

        for (auto& timer : bucket) {
            std::size_t tv1_slot = timer->expires & TV1_MASK;
            tv1_[tv1_slot].push_back(std::move(timer));
        }
    }

    std::uint64_t current_tick_{0};
    std::vector<std::list<std::shared_ptr<TimerEntry>>> tv1_;
    std::vector<std::list<std::shared_ptr<TimerEntry>>> tv2_;
};

int main() {
    TimerWheel tw;

    tw.schedule(101, 5, [](std::uint64_t id) {
        std::cout << "[C++ TICK] Timer " << id << " triggered at short interval!\n";
    });

    tw.schedule(202, 300, [](std::uint64_t id) {
        std::cout << "[C++ TICK] Timer " << id << " triggered after cascade!\n";
    });

    for (int step = 0; step < 320; ++step) {
        tw.tick();
    }

    return 0;
}
