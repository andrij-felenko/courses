#pragma once

#include <cstdint>
#include <expected>

#include "dma_ring.hpp"
#include "pbuf_ref.hpp"

namespace net {

/// Кожен дескриптор прийому вічно тримає буфер із PBUF_POOL, тож ці числа —
/// прямий відрахунок від бюджету RAM: 8 буферів по 1536 байтів це 12 КБ.
inline constexpr std::size_t kRxDescCount = 4;
inline constexpr std::size_t kTxDescCount = 4;

/// Мусить збігатися з PBUF_POOL_BUFSIZE: інакше пул віддасть ланцюжок ланок,
/// а дескриптор уміє лише один суцільний буфер.
inline constexpr std::uint16_t kFrameBufSize = 1536;

enum class InitError {
    PoolExhausted,   ///< PBUF_POOL не дав буферів на все кільце
    ChainedBuffer,   ///< PBUF_POOL_BUFSIZE менший за кадр — вийшов ланцюжок
    Misaligned,      ///< MEM_ALIGNMENT менший за кеш-лінію
};

enum class TxError {
    EmptyFrame,
    RingFull,          ///< усі дескриптори ще в роботі DMA
    TooManySegments,   ///< у ланцюжку ланок більше, ніж дескрипторів у кільці
    SegmentTooLong,    ///< ланка не влазить у поле TBS1
};

/// Драйвер Ethernet MAC без проміжного копіювання: дескриптори DMA дивляться
/// просто в payload буферів lwIP.
class ZeroCopyMac {
public:
    /// Кільця, буфери, запуск DMA. Кличеться ПІСЛЯ ініціалізації MAC/PHY.
    [[nodiscard]] std::expected<void, InitError> init() noexcept;

    /// Наступний прийнятий кадр; порожній результат — кадрів немає.
    [[nodiscard]] PbufRef receive() noexcept;

    /// Ставить кадр (можливо, ланцюжок pbuf) у кільце передачі.
    [[nodiscard]] std::expected<void, TxError> send(pbuf* frame) noexcept;

    /// Віддає в пул буфери, які DMA вже відправив. Тільки з контексту задачі.
    void reclaimSent() noexcept;

    /// Обробка переривання ETH: жодної роботи з пам'яттю, лише прапорці.
    void serviceIrq() noexcept;

private:
    void returnToDma(Descriptor& d) noexcept;
    void resumeReceiver() noexcept;

    DescriptorRing<kRxDescCount> rx_{};
    DescriptorRing<kTxDescCount> tx_{};

    /// Прив'язка «дескриптор → буфер». Час життя буфера і є час життя цього
    /// елемента масиву: жодного окремого «не забудь звільнити».
    std::array<PbufRef, kRxDescCount> rxBuffers_{};
    std::array<PbufRef, kTxDescCount> txFrames_{};
};

/// Контролер Ethernet на кристалі один, тож і драйвер один.
[[nodiscard]] ZeroCopyMac& mac() noexcept;

}  // namespace net
