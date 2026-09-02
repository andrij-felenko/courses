#pragma once

// Конфігурація lwIP як значення, а не як набір макросів: профіль можна
// порахувати, порівняти й перевірити компілятором до першої прошивки.
// Числа тут ті самі, що в c/lwipopts-*.h — розходження ловлять static_assert.

#include <cstddef>
#include <cstdint>
#include <string_view>

namespace lwipcfg {

// Розміри службових структур lwIP 2.1 на 32-бітному Cortex-M (sizeof із мапи лінкера).
inline constexpr std::size_t kPbufHeader = 16;
inline constexpr std::size_t kTcpPcb = 200;
inline constexpr std::size_t kTcpPcbListen = 44;
inline constexpr std::size_t kTcpSeg = 20;
inline constexpr std::size_t kUdpPcb = 40;
inline constexpr std::size_t kNetconn = 44;
inline constexpr std::size_t kNetbuf = 16;

// Службові заголовки перед корисними даними кадру: Ethernet 14 + IP 20 + TCP 20.
inline constexpr std::size_t kFrameOverhead = 54;

struct Profile {
  std::string_view name;
  bool no_sys;
  bool sockets_api;
  std::size_t mem_alignment;
  std::size_t mem_size;
  std::size_t pbuf_pool_size;
  std::size_t pbuf_pool_bufsize;
  std::size_t num_pbuf;
  std::size_t num_tcp_pcb;
  std::size_t num_tcp_pcb_listen;
  std::size_t num_tcp_seg;
  std::size_t num_udp_pcb;
  std::size_t num_netconn;
  std::size_t num_netbuf;
  std::uint16_t tcp_mss;
  std::uint32_t tcp_wnd;
  std::uint32_t tcp_snd_buf;
  std::size_t tcp_snd_queuelen;
  bool queue_ooseq;
};

constexpr std::size_t align_up(std::size_t value, std::size_t alignment) noexcept {
  return (value + alignment - 1) / alignment * alignment;
}

// memp вирівнює КОЖЕН елемент пулу — на профілі з 32-байтовим рядком кеша
// це помітний податок: дескриптор сегмента на 20 байтів займає 32.
constexpr std::size_t pool_bytes(const Profile& p, std::size_t element, std::size_t count) noexcept {
  return align_up(element, p.mem_alignment) * count;
}

// Формула зі статті: PBUF_POOL_SIZE * (заголовок + PBUF_POOL_BUFSIZE), вирівняно.
constexpr std::size_t rx_pool_bytes(const Profile& p) noexcept {
  return p.pbuf_pool_size * align_up(kPbufHeader + p.pbuf_pool_bufsize, p.mem_alignment);
}

constexpr std::size_t control_pool_bytes(const Profile& p) noexcept {
  return pool_bytes(p, kPbufHeader, p.num_pbuf) + pool_bytes(p, kTcpPcb, p.num_tcp_pcb) +
         pool_bytes(p, kTcpPcbListen, p.num_tcp_pcb_listen) + pool_bytes(p, kTcpSeg, p.num_tcp_seg) +
         pool_bytes(p, kUdpPcb, p.num_udp_pcb) + pool_bytes(p, kNetconn, p.num_netconn) +
         pool_bytes(p, kNetbuf, p.num_netbuf);
}

struct Budget {
  std::size_t heap;
  std::size_t rx_pool;
  std::size_t control_pools;

  constexpr std::size_t total() const noexcept { return heap + rx_pool + control_pools; }
};

constexpr Budget budget_of(const Profile& p) noexcept {
  return Budget{p.mem_size, rx_pool_bytes(p), control_pool_bytes(p)};
}

// BDP: більше за вікно, поділене на час обігу, з одного з'єднання не вичавити.
constexpr std::size_t throughput_ceiling(const Profile& p, unsigned rtt_ms) noexcept {
  return rtt_ms == 0 ? 0 : static_cast<std::size_t>(p.tcp_wnd) * 1000u / rtt_ms;
}

// Ціна одного активного з'єднання: PCB + черга сегментів + вихідні дані в купі
// (+ netconn/netbuf, якщо ввімкнено послідовний API). Вхідний пул спільний,
// тому в ціну сокета не входить.
constexpr std::size_t bytes_per_socket(const Profile& p) noexcept {
  std::size_t cost = align_up(kTcpPcb, p.mem_alignment) +
                     align_up(kTcpSeg, p.mem_alignment) * p.tcp_snd_queuelen + p.tcp_snd_buf;
  if (p.sockets_api) {
    cost += align_up(kNetconn, p.mem_alignment) + align_up(kNetbuf, p.mem_alignment);
  }
  return cost;
}

// Скільки сокетів прогодує заданий залишок SRAM — головне питання теми.
constexpr std::size_t sockets_within(const Profile& p, std::size_t ram_bytes) noexcept {
  const std::size_t cost = bytes_per_socket(p);
  return cost == 0 ? 0 : ram_bytes / cost;
}

// --- Узгодженість конфігурації ------------------------------------------
// lwIP ловить це асертами в рантаймі на живій платі; тут воно падає на етапі
// компіляції з іменем зламаного правила.

constexpr bool queuelen_matches_snd_buf(const Profile& p) noexcept {
  return p.tcp_snd_queuelen >= (2u * p.tcp_snd_buf) / p.tcp_mss;
}

constexpr bool segs_cover_queue(const Profile& p) noexcept {
  return p.num_tcp_seg >= p.tcp_snd_queuelen;
}

constexpr bool rx_pool_holds_window(const Profile& p) noexcept {
  return p.pbuf_pool_size * p.pbuf_pool_bufsize >= p.tcp_wnd;
}

// Zero-copy вимагає, щоб кадр цілком лягав в один буфер пулу.
constexpr bool frame_fits_single_pbuf(const Profile& p) noexcept {
  return p.pbuf_pool_bufsize >= p.tcp_mss + kFrameOverhead;
}

constexpr bool netconn_covers_pcbs(const Profile& p) noexcept {
  return !p.sockets_api || p.num_netconn >= p.num_tcp_pcb + p.num_udp_pcb;
}

constexpr bool alignment_is_sane(const Profile& p) noexcept {
  return p.mem_alignment == 4 || p.mem_alignment == 8 || p.mem_alignment == 32;
}

const Profile& minimal();
const Profile& industrial();
const Profile& zero_copy();

}  // namespace lwipcfg
