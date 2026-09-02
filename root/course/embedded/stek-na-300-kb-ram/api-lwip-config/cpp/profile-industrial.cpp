#include "lwip-profile.hpp"

namespace lwipcfg {
namespace {

// Профіль 2 — «промисловий стандарт RTOS»: STM32F407/ESP32, FreeRTOS, BSD-сокети.
constexpr Profile kIndustrial{
    .name = "промисловий стандарт (FreeRTOS + сокети)",
    .no_sys = false,
    .sockets_api = true,
    .mem_alignment = 4,
    .mem_size = 20 * 1024,
    .pbuf_pool_size = 16,
    .pbuf_pool_bufsize = 512,
    .num_pbuf = 16,
    .num_tcp_pcb = 8,
    .num_tcp_pcb_listen = 4,
    .num_tcp_seg = 32,
    .num_udp_pcb = 4,
    .num_netconn = 12,
    .num_netbuf = 16,
    .tcp_mss = 1460,
    .tcp_wnd = 3 * 1460,
    .tcp_snd_buf = 3 * 1460,
    .tcp_snd_queuelen = 12,
    .queue_ooseq = true,
};

constexpr std::size_t kSramForStack = 48 * 1024;

static_assert(alignment_is_sane(kIndustrial));
static_assert(queuelen_matches_snd_buf(kIndustrial),
              "TCP_SND_QUEUELEN менший за 2*TCP_SND_BUF/TCP_MSS");
static_assert(segs_cover_queue(kIndustrial),
              "MEMP_NUM_TCP_SEG не покриває навіть однієї повної черги TX");
static_assert(rx_pool_holds_window(kIndustrial),
              "вхідний пул менший за вікно прийому: віддалений вузол переповнить його раніше, ніж стек прочитає");
static_assert(netconn_covers_pcbs(kIndustrial),
              "MEMP_NUM_NETCONN має покривати TCP_PCB + UDP_PCB, інакше accept() відмовить при живих PCB");

// 20480 + 8448 + 3616 = 32544 байтів, плюс 4 КБ стека tcpip_thread.
static_assert(budget_of(kIndustrial).total() + 4 * 1024 <= kSramForStack,
              "профіль разом зі стеком tcpip_thread не влазить у 48 КБ");

// Пересписка сегментів свідома: вісім сокетів по 12 елементів черги — це 96,
// а виділено 32. Одночасно насичують канал щонайбільше три з'єднання.
static_assert(kIndustrial.num_tcp_seg < kIndustrial.num_tcp_pcb * kIndustrial.tcp_snd_queuelen);
static_assert(kIndustrial.num_tcp_seg >= 2 * kIndustrial.tcp_snd_queuelen,
              "запасу сегментів не стане й на два активні передавачі");

// Кадр ріжеться на три буфери — DMA потребує ланцюжкових дескрипторів.
static_assert(!frame_fits_single_pbuf(kIndustrial));

// Скільки з'єднань прогодує 32 КБ вільної SRAM: ~4880 Б на сокет.
static_assert(sockets_within(kIndustrial, 32 * 1024) >= 6,
              "заявлених 4-8 одночасних з'єднань профіль не тягне");

}  // namespace

const Profile& industrial() { return kIndustrial; }

}  // namespace lwipcfg
