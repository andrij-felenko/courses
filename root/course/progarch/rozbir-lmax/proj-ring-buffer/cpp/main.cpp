#include <atomic>
#include <array>
#include <cstdint>
#include <cstddef>
#include <immintrin.h>   // _mm_pause на x86; на ARM це __yield()

static inline void cpu_relax() {
#if defined(__x86_64__) || defined(_M_X64)
    _mm_pause();          // підказка процесору: ми в короткому спіні
#endif
}

template <typename T, std::size_t N>
class DisruptorSpsc {
    static_assert((N & (N - 1)) == 0, "N мусить бути степенем двійки");
    static constexpr std::int64_t MASK = static_cast<std::int64_t>(N) - 1;
    static constexpr std::size_t  CL   = 64;   // розмір лінії кешу (див. набивку)

    // ── спільні лічильники: КОЖЕН у своїй лінії кешу ──
    alignas(CL) std::atomic<std::int64_t> cursor_{-1};  // опубліковано; пише виробник
    alignas(CL) std::atomic<std::int64_t> gating_{-1};  // спожито;    пише споживач

    // ── дані: наперед виділені, перевикористовувані, ніколи не звільняються ──
    alignas(CL) std::array<T, N> slots_{};

    // ── приватне виробника (окрема лінія — не тривожить чужий кеш) ──
    alignas(CL) std::int64_t next_{0};          // наступний номер на публікацію
    std::int64_t cachedGating_{-1};             // остання бачена стримувальна

    // ── приватне споживача ──
    alignas(CL) std::int64_t nextRead_{0};      // наступний номер на читання

public:
    // ── ВИРОБНИК (рівно один потік) ──
    void publish(const T& event) {
        const std::int64_t seq = next_;              // захоплення = свій лічильник, без атома
        const std::int64_t wrapPoint = seq - static_cast<std::int64_t>(N);   // seq − N

        // Перезаписати слот seq&MASK можна лише коли споживач пройшов його
        // попереднього мешканця — номер seq−N. Кеш береже нас від дотику до
        // чужої лінії, поки ми з запасом попереду.
        if (wrapPoint > cachedGating_) {
            std::int64_t g;
            while (wrapPoint > (g = gating_.load(std::memory_order_acquire)))
                cpu_relax();                         // повно — коротко чекаємо
            cachedGating_ = g;
        }

        slots_[seq & MASK] = event;                          // (1) запис у слот
        cursor_.store(seq, std::memory_order_release);       // (2) ПУБЛІКАЦІЯ: release
        next_ = seq + 1;
    }

    // ── СПОЖИВАЧ (рівно один потік): бере цілий пакет за одне acquire ──
    template <typename Handler>
    std::int64_t drain(Handler&& handle) {
        const std::int64_t available =
            cursor_.load(std::memory_order_acquire);         // одне acquire на ВЕСЬ пакет
        if (available < nextRead_) return 0;                 // нема нового

        for (std::int64_t s = nextRead_; s <= available; ++s)
            handle(slots_[s & MASK]);                        // звичайні читання слотів

        const std::int64_t n = available - nextRead_ + 1;
        nextRead_ = available + 1;
        gating_.store(available, std::memory_order_release); // звільнити весь пробіг
        return n;
    }
};
