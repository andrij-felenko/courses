#include <span>
#include <array>
#include <cstdint>
#include <optional>
#include <concepts>

extern "C" {
#include "lwip/opt.h"
#include "lwip/pbuf.h"
}

namespace embedded::net {

inline constexpr size_t kRxDescCount = 4;
inline constexpr size_t kTxDescCount = 4;
inline constexpr size_t kFrameBufSize = 1536;
inline constexpr size_t kCacheLineSize = 32;

enum class DmaStatus : uint32_t {
    OwnByDma  = 0x80000000U,
    FirstSeg  = 0x20000000U,
    LastSeg   = 0x10000000U,
    IntOnComp = 0x40000000U,
    RxEndOfRing = 0x00008000U,
};

struct alignas(kCacheLineSize) DmaDescriptor {
    volatile uint32_t status{0};
    volatile uint32_t controlBufferSize{0};
    volatile uint32_t buffer1Addr{0};
    volatile uint32_t buffer2NextDescAddr{0};
};

class PbufScopedRef {
public:
    explicit PbufScopedRef(struct pbuf* p) noexcept : pbuf_(p) {
        if (pbuf_ != nullptr) {
            pbuf_ref(pbuf_);
        }
    }

    ~PbufScopedRef() noexcept {
        if (pbuf_ != nullptr) {
            pbuf_free(pbuf_);
        }
    }

    PbufScopedRef(const PbufScopedRef&) = delete;
    PbufScopedRef& operator=(const PbufScopedRef&) = delete;

    PbufScopedRef(PbufScopedRef&& other) noexcept : pbuf_(other.pbuf_) {
        other.pbuf_ = nullptr;
    }

    [[nodiscard]] struct pbuf* get() const noexcept { return pbuf_; }
    [[nodiscard]] struct pbuf* release() noexcept {
        struct pbuf* tmp = pbuf_;
        pbuf_ = nullptr;
        return tmp;
    }

private:
    struct pbuf* pbuf_{nullptr};
};

class EthernetZeroCopyDriver {
public:
    EthernetZeroCopyDriver() noexcept = default;

    [[nodiscard]] bool init() noexcept {
        for (size_t i = 0; i < kRxDescCount; ++i) {
            struct pbuf* p = pbuf_alloc(PBUF_RAW, kFrameBufSize, PBUF_POOL);
            if (p == nullptr) {
                return false;
            }

            rxPbufs_[i] = p;
            rxRing_[i].buffer1Addr = reinterpret_cast<uint32_t>(p->payload);
            rxRing_[i].controlBufferSize = kFrameBufSize;
            rxRing_[i].buffer2NextDescAddr = reinterpret_cast<uint32_t>(&rxRing_[(i + 1) % kRxDescCount]);

            if (i == kRxDescCount - 1) {
                rxRing_[i].controlBufferSize |= static_cast<uint32_t>(DmaStatus::RxEndOfRing);
            }

            invalidateCache(p->payload, kFrameBufSize);
            rxRing_[i].status = static_cast<uint32_t>(DmaStatus::OwnByDma);
        }

        cleanCache(rxRing_.data(), sizeof(rxRing_));
        rxHead_ = 0;
        return true;
    }

    [[nodiscard]] std::optional<struct pbuf*> receivePacket() noexcept {
        auto& desc = rxRing_[rxHead_];
        invalidateCache(&desc, sizeof(DmaDescriptor));

        if ((desc.status & static_cast<uint32_t>(DmaStatus::OwnByDma)) != 0) {
            return std::nullopt; /* Кадр ще не надійшов */
        }

        const uint32_t frameLen = (desc.status >> 16) & 0x3FFFU;
        struct pbuf* received = rxPbufs_[rxHead_];

        /* Виділяємо свіжий pbuf під наступний прийом */
        struct pbuf* freshPbuf = pbuf_alloc(PBUF_RAW, kFrameBufSize, PBUF_POOL);
        if (freshPbuf != nullptr) {
            received->len = static_cast<u16_t>(frameLen);
            received->tot_len = static_cast<u16_t>(frameLen);
            invalidateCache(received->payload, frameLen);

            rxPbufs_[rxHead_] = freshPbuf;
            desc.buffer1Addr = reinterpret_cast<uint32_t>(freshPbuf->payload);
            invalidateCache(freshPbuf->payload, kFrameBufSize);
        } else {
            /* При вичерпанні пулу скидаємо пакет та перевикористовуємо буфер */
            received = nullptr;
        }

        desc.status = static_cast<uint32_t>(DmaStatus::OwnByDma);
        cleanCache(&desc, sizeof(DmaDescriptor));

        rxHead_ = (rxHead_ + 1) % kRxDescCount;
        return received != nullptr ? std::make_optional(received) : std::nullopt;
    }

    [[nodiscard]] bool sendPacket(struct pbuf* p) noexcept {
        if (p == nullptr) {
            return false;
        }

        auto& desc = txRing_[txHead_];
        invalidateCache(&desc, sizeof(DmaDescriptor));

        if ((desc.status & static_cast<uint32_t>(DmaStatus::OwnByDma)) != 0) {
            return false; /* Кільце передачі заповнене */
        }

        /* Звільняємо старий pbuf після підтвердження DMA */
        if (txPbufs_[txHead_] != nullptr) {
            pbuf_free(txPbufs_[txHead_]);
            txPbufs_[txHead_] = nullptr;
        }

        pbuf_ref(p);
        txPbufs_[txHead_] = p;

        cleanCache(p->payload, p->len);

        desc.buffer1Addr = reinterpret_cast<uint32_t>(p->payload);
        desc.controlBufferSize = p->len;
        desc.status = static_cast<uint32_t>(DmaStatus::OwnByDma) |
                      static_cast<uint32_t>(DmaStatus::FirstSeg) |
                      static_cast<uint32_t>(DmaStatus::LastSeg)  |
                      static_cast<uint32_t>(DmaStatus::IntOnComp);

        cleanCache(&desc, sizeof(DmaDescriptor));
        txHead_ = (txHead_ + 1) % kTxDescCount;
        return true;
    }

private:
    static void invalidateCache(const void* addr, size_t size) noexcept {
        const auto a = reinterpret_cast<uintptr_t>(addr) & ~(kCacheLineSize - 1);
        const auto s = size + (reinterpret_cast<uintptr_t>(addr) - a);
        /* SCB_InvalidateDCache_by_Addr(reinterpret_cast<uint32_t*>(a), static_cast<int32_t>(s)); */
        (void)a; (void)s;
    }

    static void cleanCache(const void* addr, size_t size) noexcept {
        const auto a = reinterpret_cast<uintptr_t>(addr) & ~(kCacheLineSize - 1);
        const auto s = size + (reinterpret_cast<uintptr_t>(addr) - a);
        /* SCB_CleanDCache_by_Addr(reinterpret_cast<uint32_t*>(a), static_cast<int32_t>(s)); */
        (void)a; (void)s;
    }

    alignas(kCacheLineSize) std::array<DmaDescriptor, kRxDescCount> rxRing_{};
    alignas(kCacheLineSize) std::array<DmaDescriptor, kTxDescCount> txRing_{};
    std::array<struct pbuf*, kRxDescCount> rxPbufs_{};
    std::array<struct pbuf*, kTxDescCount> txPbufs_{};

    size_t rxHead_{0};
    size_t txHead_{0};
};

} // namespace embedded::net
