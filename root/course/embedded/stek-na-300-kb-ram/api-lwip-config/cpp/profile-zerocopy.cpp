#include "lwip-profile.hpp"

namespace lwipcfg {
namespace {

// Профіль 3 — «високошвидкісний Zero-Copy»: STM32F7/H7, 100 Мбіт/с потоком.
constexpr Profile kZeroCopy{
    .name = "високошвидкісний zero-copy (D-Cache, DMA)",
    .no_sys = false,
    .sockets_api = true,
    .mem_alignment = 32,
    .mem_size = 32 * 1024,
    .pbuf_pool_size = 24,
    .pbuf_pool_bufsize = 1536,
    .num_pbuf = 32,
    .num_tcp_pcb = 16,
    .num_tcp_pcb_listen = 4,
    .num_tcp_seg = 64,
    .num_udp_pcb = 8,
    .num_netconn = 24,
    .num_netbuf = 32,
    .tcp_mss = 1460,
    .tcp_wnd = 6 * 1460,
    .tcp_snd_buf = 6 * 1460,
    .tcp_snd_queuelen = 24,
    .queue_ooseq = true,
};

constexpr std::size_t kSramForStack = 100 * 1024;

static_assert(alignment_is_sane(kZeroCopy));
static_assert(kZeroCopy.mem_alignment == 32,
              "з увімкненим D-Cache вирівнювання менше за рядок кеша псує сусідній буфер");
static_assert(queuelen_matches_snd_buf(kZeroCopy));
static_assert(segs_cover_queue(kZeroCopy));
static_assert(rx_pool_holds_window(kZeroCopy));
static_assert(netconn_covers_pcbs(kZeroCopy));

// Головна вимога профілю: кадр 1514 Б лягає в один буфер, тож дескриптор DMA
// дивиться прямо в pbuf і копіювання на прийомі немає взагалі.
static_assert(frame_fits_single_pbuf(kZeroCopy),
              "PBUF_POOL_BUFSIZE менший за повний кадр — zero-copy на прийомі не вийде");

// 32768 + 37632 + 9984 = 80384 байтів, плюс 8 КБ стека tcpip_thread.
static_assert(budget_of(kZeroCopy).total() + 8 * 1024 <= kSramForStack,
              "профіль не влазить у 100 КБ SRAM");

// Вхідний пул тут коштує більше за купу — саме він і є ціна швидкості.
static_assert(budget_of(kZeroCopy).rx_pool > budget_of(kZeroCopy).heap);

// Вікно 8760 Б при RTT 10 мс дає ~856 КБ/с — це і є цільові 100 Мбіт/с
// на одному з'єднанні в локальній мережі.
static_assert(throughput_ceiling(kZeroCopy, 10) >= 800 * 1024,
              "вікна не стане на заявлену швидкість: піднімати TCP_WND");

// 64 КБ вільної SRAM — це ще шість потокових з'єднань по ~9.6 КБ.
static_assert(sockets_within(kZeroCopy, 64 * 1024) >= 6);

}  // namespace

const Profile& zero_copy() { return kZeroCopy; }

}  // namespace lwipcfg
