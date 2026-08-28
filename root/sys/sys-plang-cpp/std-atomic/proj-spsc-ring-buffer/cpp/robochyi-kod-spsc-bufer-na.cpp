#include <atomic>
#include <cstddef>
#include <cstdint>
#include <new>          // std::hardware_destructive_interference_size

template <typename T, size_t N>
class SpscRing {
    static_assert((N & (N - 1)) == 0, "N мусить бути степенем двійки");
    static constexpr size_t MASK = N - 1;   // загортання через «і» замість %

    // head і tail — у РІЗНИХ кеш-лініях (чому — див. пастку про false sharing).
    alignas(64) std::atomic<size_t> head_{0};   // пише лише продюсер
    alignas(64) std::atomic<size_t> tail_{0};   // пише лише консюмер
    alignas(64) T buf_[N];                       // самі дані — теж окремо

public:
    // ── бік ПРОДЮСЕРА ──────────────────────────────────────────────
    bool push(const T& item) {
        // head_ читаємо relaxed: ми — його ЄДИНИЙ писач, свіжіше нікого нема.
        const size_t h = head_.load(std::memory_order_relaxed);
        const size_t next = (h + 1) & MASK;

        // tail_ читаємо ACQUIRE: треба побачити, які слоти консюмер уже звільнив.
        if (next == tail_.load(std::memory_order_acquire))
            return false;                        // повно → відмова (політика на вибір)

        buf_[h] = item;                          // (1) СПЕРШУ дані у слот

        // (2) ПОТІМ публікуємо новий head RELEASE-записом: він замикає під собою
        //     запис у слот вище, тож консюмер, побачивши next, побачить і дані.
        head_.store(next, std::memory_order_release);
        return true;
    }

    // ── бік КОНСЮМЕРА ──────────────────────────────────────────────
    bool pop(T& out) {
        // tail_ читаємо relaxed: ми — його єдиний писач.
        const size_t t = tail_.load(std::memory_order_relaxed);

        // head_ читаємо ACQUIRE: якщо побачимо новий head, то побачимо й дані,
        //     які продюсер поклав ДО свого release.
        if (t == head_.load(std::memory_order_acquire))
            return false;                        // порожньо

        out = buf_[t];                           // (1) забрати дані зі слота

        // (2) звільнити слот RELEASE-записом tail: продюсер, побачивши новий
        //     tail, знатиме, що слот вільний, — і не перезапише його, поки ми читали.
        tail_.store((t + 1) & MASK, std::memory_order_release);
        return true;
    }

    bool empty() const {
        return head_.load(std::memory_order_acquire) ==
               tail_.load(std::memory_order_acquire);
    }
};
