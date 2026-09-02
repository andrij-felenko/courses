#include "stats-report.hpp"

#include <algorithm>
#include <cstdio>
#include <format>

// Заголовки lwIP самі загорнуті в extern "C".
#include "lwip/memp.h"
#include "lwip/opt.h"
#include "lwip/stats.h"

#if !NO_SYS
#include "lwip/tcpip.h"
#endif

namespace lwipdiag {
namespace {

// Парні LOCK_TCPIP_CORE()/UNLOCK_TCPIP_CORE() легко розбігаються на ранньому
// поверненні — тримаємо їх областю видимості.
class CoreLock {
 public:
  CoreLock() noexcept {
#if !NO_SYS && LWIP_TCPIP_CORE_LOCKING
    LOCK_TCPIP_CORE();
#endif
  }
  ~CoreLock() noexcept {
#if !NO_SYS && LWIP_TCPIP_CORE_LOCKING
    UNLOCK_TCPIP_CORE();
#endif
  }
  CoreLock(const CoreLock&) = delete;
  CoreLock& operator=(const CoreLock&) = delete;
};

struct Entry {
  Pool pool;
  std::string_view name;
  memp_t index;
};

// Пул, вимкнений у lwipopts.h, просто не потрапляє в таблицю.
constexpr Entry kEntries[] = {
    {Pool::PbufPool, "PBUF_POOL", MEMP_PBUF_POOL},
    {Pool::Pbuf, "PBUF_REF", MEMP_PBUF},
#if LWIP_TCP
    {Pool::TcpPcb, "TCP_PCB", MEMP_TCP_PCB},
    {Pool::TcpListen, "TCP_LISTEN", MEMP_TCP_PCB_LISTEN},
    {Pool::TcpSeg, "TCP_SEG", MEMP_TCP_SEG},
#endif
#if LWIP_UDP
    {Pool::UdpPcb, "UDP_PCB", MEMP_UDP_PCB},
#endif
#if LWIP_NETCONN
    {Pool::Netconn, "NETCONN", MEMP_NETCONN},
#endif
};
static_assert(std::size(kEntries) <= kMaxPools, "kMaxPools менший за таблицю пулів");

template <class... Args>
void emit(std::format_string<Args...> fmt, Args&&... args) {
  // Без динамічної пам'яті: рядок, що не вліз, обрізаємо, а не падаємо.
  std::array<char, 160> line{};
  const auto result = std::format_to_n(line.data(), line.size() - 1, fmt, std::forward<Args>(args)...);
  *result.out = '\0';
  std::fputs(line.data(), stdout);
}

}  // namespace

std::optional<Snapshot> Snapshot::collect() noexcept {
#if LWIP_STATS && MEMP_STATS && MEM_STATS
  Snapshot snapshot;
  const CoreLock lock;

  for (const Entry& entry : kEntries) {
    const stats_mem& stats = *lwip_stats.memp[entry.index];
    snapshot.pools_[snapshot.count_++] = PoolUsage{
        entry.pool,
        entry.name,
        static_cast<std::uint32_t>(stats.avail),
        static_cast<std::uint32_t>(stats.used),
        static_cast<std::uint32_t>(stats.max),
        static_cast<std::uint32_t>(stats.err),
    };
  }

  snapshot.heap_ = HeapUsage{
      static_cast<std::uint32_t>(lwip_stats.mem.avail),
      static_cast<std::uint32_t>(lwip_stats.mem.used),
      static_cast<std::uint32_t>(lwip_stats.mem.max),
      static_cast<std::uint32_t>(lwip_stats.mem.err),
  };
  return snapshot;
#else
  return std::nullopt;
#endif
}

std::optional<PoolUsage> Snapshot::find(Pool pool) const noexcept {
  const auto span = pools();
  const auto it = std::ranges::find(span, pool, &PoolUsage::pool);
  if (it == span.end()) {
    return std::nullopt;
  }
  return *it;
}

std::optional<PoolUsage> Snapshot::tightest() const noexcept {
  const auto span = pools();
  const auto it = std::ranges::max_element(span, {}, &PoolUsage::peak_percent);
  if (it == span.end()) {
    return std::nullopt;
  }
  return *it;
}

// Порядок питань навмисний: спершу те, що вже втратило дані, потім те,
// що лише вперлося в стелю. Перша відповідь і є вузьке місце.
Verdict Snapshot::verdict() const noexcept {
  if (const auto rx = find(Pool::PbufPool); rx && rx->starved()) {
    return Verdict::RxPoolStarved;
  }
  if (heap_.failures > 0) {
    return Verdict::HeapExhausted;
  }
  if (const auto seg = find(Pool::TcpSeg); seg && seg->at_ceiling()) {
    return Verdict::SegmentsExhausted;
  }
  if (const auto pcb = find(Pool::TcpPcb); pcb && pcb->at_ceiling()) {
    return Verdict::SocketsExhausted;
  }
  return Verdict::Healthy;
}

std::string_view describe(Verdict verdict) noexcept {
  switch (verdict) {
    case Verdict::Healthy:
      return "запас є";
    case Verdict::RxPoolStarved:
      return "вичерпано PBUF_POOL: збільшити PBUF_POOL_SIZE або пришвидшити обробку";
    case Verdict::HeapExhausted:
      return "вичерпано купу MEM_SIZE: збільшити MEM_SIZE або зменшити TCP_SND_BUF";
    case Verdict::SegmentsExhausted:
      return "вичерпано TCP_SEG: підняти MEMP_NUM_TCP_SEG під TCP_SND_QUEUELEN";
    case Verdict::SocketsExhausted:
      return "вичерпано TCP_PCB: підняти MEMP_NUM_TCP_PCB або закривати з'єднання";
  }
  return "невідомий стан";
}

void print(const Snapshot& snapshot) {
  emit("lwIP: пам'ять і пули\n");
  emit("{:<12}{:>8}{:>8}{:>8}{:>7}{:>9}\n", "пул", "усього", "зайн", "пік", "пік%", "відмов");

  for (const PoolUsage& pool : snapshot.pools()) {
    emit("{:<12}{:>8}{:>8}{:>8}{:>6}%{:>9}{}\n", pool.name, pool.avail, pool.used, pool.peak,
         pool.peak_percent(), pool.failures, pool.starved() ? "  <-- відмови" : "");
  }

  const HeapUsage& heap = snapshot.heap();
  emit("{:<12}{:>8}{:>8}{:>8}{:>6}%{:>9}   (байтів)\n", "HEAP(mem)", heap.avail, heap.used, heap.peak,
       heap.peak_percent(), heap.failures);

  if (const auto tight = snapshot.tightest(); tight) {
    emit("найтісніше: {} ({}% піку)\n", tight->name, tight->peak_percent());
  }
  emit("присуд: {}\n", describe(snapshot.verdict()));
}

void dump() {
  const auto snapshot = Snapshot::collect();
  if (!snapshot) {
    emit("lwIP: статистику вимкнено (LWIP_STATS/MEMP_STATS/MEM_STATS у lwipopts.h)\n");
    return;
  }

  print(*snapshot);

#if LWIP_STATS_DISPLAY
  stats_display();  // повна рідна карта: протоколи, лічильники помилок, netif
#endif
}

}  // namespace lwipdiag
