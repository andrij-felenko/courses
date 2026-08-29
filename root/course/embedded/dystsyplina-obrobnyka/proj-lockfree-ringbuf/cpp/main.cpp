// Перевірка буфера справжньою одночасністю. На мікроконтролері постачальник —
// це переривання, що витісняє головний цикл; тут його роль грає окремий потік,
// і на x86 з його чергами запису умови навіть суворіші, ніж на Cortex-M.
//
// Що доводить прогін: жоден елемент не приходить зіпсованим, порядок строго
// зростає, а сума «прийнято + втрачено» дорівнює надісланому. Тобто буфер
// втрачає рівно те, на що не було місця, і нічого понад те.

#include "ring_buffer.hpp"

#include <array>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <thread>

namespace {

struct Sample {
    std::uint32_t seq;     // номер вимірювання: дірки в ньому = втрати
    std::int16_t  value;
};

using RxQueue = rb::SpscRingBuffer<Sample, 64>;

constexpr std::uint32_t kTotal = 200'000;

// Значення жорстко пов'язане з номером — інакше не відрізнити правильно
// прочитаний елемент від чужого сміття, що лежало в комірці до нього.
constexpr std::int16_t expected_value(std::uint32_t seq) noexcept {
    return static_cast<std::int16_t>(seq * 7u + 13u);
}

class Checker {
public:
    void feed(const Sample& s) noexcept {
        if (s.value != expected_value(s.seq)) {
            ++corrupted_;
        }
        if (empty_) {
            gaps_ += s.seq;            // втрати ще до першого прийнятого
            empty_ = false;
        } else if (s.seq <= last_seq_) {
            ++out_of_order_;
        } else {
            gaps_ += s.seq - last_seq_ - 1;
        }
        last_seq_ = s.seq;
        ++received_;
    }

    // Хвіст потоку теж міг потонути: після останнього прийнятого номера
    // до кінця нумерації лишається стільки ж загублених.
    void finish(std::uint32_t total) noexcept {
        gaps_ += empty_ ? total : total - 1 - last_seq_;
    }

    [[nodiscard]] std::uint64_t received() const noexcept { return received_; }
    [[nodiscard]] std::uint64_t gaps() const noexcept { return gaps_; }
    [[nodiscard]] std::uint64_t corrupted() const noexcept { return corrupted_; }
    [[nodiscard]] std::uint64_t out_of_order() const noexcept { return out_of_order_; }

private:
    std::uint64_t received_ = 0;
    std::uint64_t gaps_ = 0;
    std::uint64_t corrupted_ = 0;
    std::uint64_t out_of_order_ = 0;
    std::uint32_t last_seq_ = 0;
    bool empty_ = true;
};

void concurrent_scene() {
    RxQueue queue;
    std::atomic<bool> producing{true};
    Checker checker;

    // «Переривання»: сипле без пауз, місця не чекає ніколи.
    std::thread producer([&] {
        for (std::uint32_t seq = 0; seq < kTotal; ++seq) {
            queue.push_from_isr(Sample{seq, expected_value(seq)});
        }
        producing.store(false, std::memory_order_release);
    });

    // Головний цикл: вичитує пачками, як робив би між іншими справами.
    std::thread consumer([&] {
        std::array<Sample, 16> chunk{};

        for (;;) {
            const std::size_t n = queue.pop(chunk);
            if (n == 0) {
                if (!producing.load(std::memory_order_acquire) && queue.empty()) {
                    break;   // постачальник скінчив і черга суха
                }
                std::this_thread::yield();
                continue;
            }
            for (std::size_t i = 0; i < n; ++i) {
                checker.feed(chunk[i]);
            }
        }
    });

    producer.join();
    consumer.join();
    checker.finish(kTotal);

    const std::uint64_t dropped = queue.dropped();
    std::printf("[1] одночасний потік, місткість %zu\n", RxQueue::capacity());
    std::printf("    надіслано %u, прийнято %llu, втрачено %llu, сума %llu\n",
                kTotal,
                static_cast<unsigned long long>(checker.received()),
                static_cast<unsigned long long>(dropped),
                static_cast<unsigned long long>(checker.received() + dropped));
    std::printf("    дірок у нумерації %llu, зіпсованих %llu, поза порядком %llu\n",
                static_cast<unsigned long long>(checker.gaps()),
                static_cast<unsigned long long>(checker.corrupted()),
                static_cast<unsigned long long>(checker.out_of_order()));

    const bool ok = (checker.received() + dropped == kTotal) &&
                    checker.corrupted() == 0 && checker.out_of_order() == 0 &&
                    checker.gaps() == dropped;
    std::printf("    підсумок: %s\n\n", ok ? "буфер цілий" : "ПОРУШЕННЯ ІНВАРІАНТА");
}

// Дані, де цінні лише найсвіжіші: споживач не чекає й не благає постачальника
// спинитися, а сам викидає старе — tail належить йому.
void freshest_scene() {
    RxQueue queue;

    for (std::uint32_t seq = 0; seq < 200; ++seq) {
        queue.push_from_isr(Sample{seq, expected_value(seq)});
    }
    std::printf("[2] важливі лише найсвіжіші\n");
    std::printf("    у черзі %zu, втрачено в «ISR» %llu\n",
                queue.size(), static_cast<unsigned long long>(queue.dropped()));

    constexpr std::size_t kKeep = 4;
    const std::size_t queued = queue.size();
    const std::size_t thrown =
        queue.discard_oldest(queued > kKeep ? queued - kKeep : 0);
    std::printf("    викинуто найстаріших %zu, лишилось %zu:", thrown, queue.size());

    while (const std::optional<Sample> s = queue.pop()) {
        std::printf(" #%u", s->seq);
    }
    std::printf("\n");
}

}  // namespace

int main() {
    concurrent_scene();
    freshest_scene();
    return 0;
}
