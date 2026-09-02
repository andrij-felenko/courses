#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

#include "stm32f7xx.h"

namespace net {

/// Довжина кеш-лінії D-Cache на Cortex-M7.
inline constexpr std::size_t kCacheLine = 32;

/// Дескриптор RDES/TDES: чотири 32-бітні слова, які пише апаратура.
/// alignas(32) заразом робить sizeof рівним 32, тобто один дескриптор —
/// рівно одна кеш-лінія: clean/invalidate над ним не зачепить сусіда.
struct alignas(kCacheLine) Descriptor {
    volatile std::uint32_t status{0};   ///< RDES0 / TDES0
    volatile std::uint32_t control{0};  ///< RDES1 / TDES1
    volatile std::uint32_t buffer{0};   ///< RDES2 / TDES2 — адреса даних
    volatile std::uint32_t next{0};     ///< RDES3 / TDES3 — наступний дескриптор
};
static_assert(sizeof(Descriptor) == kCacheLine, "дескриптор мусить займати цілу кеш-лінію");

/// Біти дескриптора прийому.
namespace rdes {
inline constexpr std::uint32_t own = 0x8000'0000U;
inline constexpr std::uint32_t frameLenMask = 0x3FFF'0000U;  ///< довжина разом із FCS
inline constexpr std::uint32_t frameLenShift = 16U;
inline constexpr std::uint32_t errorSummary = 0x0000'8000U;
inline constexpr std::uint32_t firstSeg = 0x0000'0200U;
inline constexpr std::uint32_t lastSeg = 0x0000'0100U;
inline constexpr std::uint32_t chained = 0x0000'4000U;    ///< RDES1: друга адреса — наступний
inline constexpr std::uint32_t endOfRing = 0x0000'8000U;  ///< RDES1
inline constexpr std::uint32_t sizeMask = 0x0000'1FFFU;   ///< RDES1, біти 12..0
}  // namespace rdes

/// Біти дескриптора передачі.
namespace tdes {
inline constexpr std::uint32_t own = 0x8000'0000U;
inline constexpr std::uint32_t interruptOnCompletion = 0x4000'0000U;
inline constexpr std::uint32_t lastSeg = 0x2000'0000U;
inline constexpr std::uint32_t firstSeg = 0x1000'0000U;
inline constexpr std::uint32_t chained = 0x0010'0000U;
inline constexpr std::uint32_t endOfRing = 0x0020'0000U;
inline constexpr std::uint32_t sizeMask = 0x0000'1FFFU;
}  // namespace tdes

/// Операції з кешем даних. Апаратура працює лініями, тому адресу округлюємо
/// ВНИЗ, а розмір доточуємо на той самий зсув — інакше оброблено буде не ту лінію.
namespace cache {

inline void invalidate(const void* addr, std::size_t size) noexcept
{
#if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
    const auto raw = reinterpret_cast<std::uintptr_t>(addr);
    const auto start = raw & ~(static_cast<std::uintptr_t>(kCacheLine) - 1U);
    const auto bytes = size + (raw - start);
    SCB_InvalidateDCache_by_Addr(reinterpret_cast<std::uint32_t*>(start),
                                 static_cast<std::int32_t>(bytes));
#else
    (void)addr;
    (void)size;
    __DSB();
#endif
}

inline void clean(const void* addr, std::size_t size) noexcept
{
#if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
    const auto raw = reinterpret_cast<std::uintptr_t>(addr);
    const auto start = raw & ~(static_cast<std::uintptr_t>(kCacheLine) - 1U);
    const auto bytes = size + (raw - start);
    SCB_CleanDCache_by_Addr(reinterpret_cast<std::uint32_t*>(start),
                            static_cast<std::int32_t>(bytes));
#else
    (void)addr;
    (void)size;
    __DSB();
#endif
}

}  // namespace cache

/// Кільце дескрипторів у режимі ланцюжка: RDES3/TDES3 вказує на наступний,
/// тож 32-байтний крок між дескрипторами апаратура обходить сама. У режимі
/// суцільного кільця довелося б виставляти поле DSL у DMABMR.
template <std::size_t N>
class DescriptorRing {
public:
    static constexpr std::size_t size = N;

    [[nodiscard]] Descriptor& at(std::size_t i) noexcept { return ring_[i % N]; }

    [[nodiscard]] std::uint32_t addressOf(std::size_t i) noexcept
    {
        return reinterpret_cast<std::uint32_t>(&ring_[i % N]);
    }

    [[nodiscard]] std::size_t index() const noexcept { return head_; }
    void advance(std::size_t steps = 1) noexcept { head_ = (head_ + steps) % N; }
    void rewind() noexcept { head_ = 0; }

    /// Замикає ланцюжок і повертає адресу для DMARDLAR/DMATDLAR.
    [[nodiscard]] std::uint32_t link() noexcept
    {
        for (std::size_t i = 0; i < N; ++i) {
            ring_[i].next = addressOf(i + 1);
        }
        return addressOf(0);
    }

    void flush() noexcept { cache::clean(ring_.data(), sizeof(ring_)); }

private:
    alignas(kCacheLine) std::array<Descriptor, N> ring_{};
    std::size_t head_{0};
};

}  // namespace net
