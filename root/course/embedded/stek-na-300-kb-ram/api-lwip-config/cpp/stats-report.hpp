#pragma once

// Знімок lwip_stats як значення: зібрали під core-lock, віддали далі
// звичайним об'єктом, судимо й друкуємо вже без блокування ядра.

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <string_view>

namespace lwipdiag {

inline constexpr std::size_t kMaxPools = 7;

enum class Pool : std::uint8_t {
  PbufPool,   // вхідні кадри від DMA
  Pbuf,       // PBUF_ROM/PBUF_REF на передачі
  TcpPcb,     // активні з'єднання
  TcpListen,  // слухачі портів
  TcpSeg,     // дескриптори черги відправлення
  UdpPcb,
  Netconn,
};

struct PoolUsage {
  Pool pool{};
  std::string_view name{};
  std::uint32_t avail{};
  std::uint32_t used{};
  std::uint32_t peak{};     // поле max у stats_mem: пік від старту системи
  std::uint32_t failures{}; // поле err: скільки разів виділення не вдалося

  [[nodiscard]] constexpr unsigned peak_percent() const noexcept {
    return avail == 0 ? 0u : static_cast<unsigned>(peak * 100u / avail);
  }
  [[nodiscard]] constexpr bool starved() const noexcept { return failures > 0; }
  [[nodiscard]] constexpr bool at_ceiling() const noexcept {
    return starved() || (avail > 0 && peak >= avail);
  }
};

struct HeapUsage {
  std::uint32_t avail{};  // MEM_SIZE у байтах
  std::uint32_t used{};
  std::uint32_t peak{};
  std::uint32_t failures{};

  [[nodiscard]] constexpr unsigned peak_percent() const noexcept {
    return avail == 0 ? 0u : static_cast<unsigned>(peak * 100u / avail);
  }
};

enum class Verdict : std::uint8_t {
  Healthy,
  RxPoolStarved,
  HeapExhausted,
  SegmentsExhausted,
  SocketsExhausted,
};

class Snapshot {
 public:
  // nullopt — статистику вимкнено в lwipopts.h, рахувати нема чого.
  [[nodiscard]] static std::optional<Snapshot> collect() noexcept;

  [[nodiscard]] std::span<const PoolUsage> pools() const noexcept {
    return {pools_.data(), count_};
  }
  [[nodiscard]] const HeapUsage& heap() const noexcept { return heap_; }
  [[nodiscard]] std::optional<PoolUsage> find(Pool pool) const noexcept;
  [[nodiscard]] std::optional<PoolUsage> tightest() const noexcept;
  [[nodiscard]] Verdict verdict() const noexcept;

 private:
  std::array<PoolUsage, kMaxPools> pools_{};
  std::size_t count_{};
  HeapUsage heap_{};
};

[[nodiscard]] std::string_view describe(Verdict verdict) noexcept;
void print(const Snapshot& snapshot);

// Повний дамп у консоль налагодження: наша таблиця плюс рідний stats_display().
void dump();

}  // namespace lwipdiag
