#include "lwip-profile.hpp"

namespace lwipcfg {
namespace {

// Профіль 1 — «мікроконтролерний мінімум»: STM32F103/F401 без RTOS.
constexpr Profile kMinimal{
    .name = "мікроконтролерний мінімум (bare-metal)",
    .no_sys = true,
    .sockets_api = false,
    .mem_alignment = 4,
    .mem_size = 8 * 1024,
    .pbuf_pool_size = 8,
    .pbuf_pool_bufsize = 512,
    .num_pbuf = 8,
    .num_tcp_pcb = 2,
    .num_tcp_pcb_listen = 1,
    .num_tcp_seg = 16,
    .num_udp_pcb = 2,
    .num_netconn = 0,
    .num_netbuf = 0,
    .tcp_mss = 536,
    .tcp_wnd = 2 * 536,
    .tcp_snd_buf = 2 * 536,
    .tcp_snd_queuelen = 8,
    .queue_ooseq = false,
};

// Стільки SRAM плата віддала мережі; решта — стек і дані застосунку.
constexpr std::size_t kSramForStack = 16 * 1024;

static_assert(alignment_is_sane(kMinimal));
static_assert(queuelen_matches_snd_buf(kMinimal),
              "TCP_SND_QUEUELEN менший за 2*TCP_SND_BUF/TCP_MSS — lwIP упаде на асерті в tcp.c");
static_assert(segs_cover_queue(kMinimal),
              "MEMP_NUM_TCP_SEG не покриває черги відправлення");
static_assert(rx_pool_holds_window(kMinimal),
              "вхідний пул не втримає навіть одного вікна TCP_WND");
static_assert(netconn_covers_pcbs(kMinimal));

// 8192 + 4224 + 972 = 13388 байтів.
static_assert(budget_of(kMinimal).total() <= kSramForStack,
              "профіль не влазить у виділені 16 КБ");

// Кадр 1514 Б свідомо ріжеться на ланцюжок із трьох буферів: за zero-copy тут
// не платимо, бо DMA з ланцюжковими дескрипторами дешевший за 24 КБ пулу.
static_assert(!frame_fits_single_pbuf(kMinimal));

// Два з'єднання по ~1.4 КБ мають лишити місце на стек застосунку.
static_assert(sockets_within(kMinimal, 4 * 1024) >= 2,
              "навіть двох сокетів не прогодує");

// Стеля швидкості на одному з'єднанні: 1072 Б / 50 мс ≈ 21 КБ/с.
static_assert(throughput_ceiling(kMinimal, 50) >= 20 * 1024);

}  // namespace

const Profile& minimal() { return kMinimal; }

}  // namespace lwipcfg
