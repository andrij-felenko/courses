#ifndef LWIPOPTS_H
#define LWIPOPTS_H

/* Профіль 1 — «мікроконтролерний мінімум».
 * Bare-metal (без RTOS), лише Raw/Callback API: STM32F103, F401, LPC1768.
 * У проєкті файл лежить під іменем lwipopts.h — lwIP шукає саме його.
 *
 * Бюджет RAM (ті самі числа рахує cpp/lwip-profile.hpp у constexpr):
 *   купа MEM_SIZE .......................... 8192 Б
 *   PBUF_POOL: 8 x вирівняне(16 + 512) ..... 4224 Б
 *   керуючі пули PCB/SEG/PBUF ............... 972 Б
 *   ------------------------------------------------
 *   разом стеку ........................... ~13.1 КБ
 * Понад це плата платить стеком застосунку і дескрипторами Ethernet DMA,
 * тож профіль розрахований на систему, де мережі віддали 16-24 КБ SRAM.
 */

/* --- Ядро й планування ---------------------------------------------- */
#define NO_SYS                          1   /* усе крутиться в головному циклі */
#define SYS_LIGHTWEIGHT_PROT            0   /* без RTOS критичні секції стеку зайві */
#define LWIP_TIMERS                     1   /* main() смикає sys_check_timeouts() */

/* --- Купа mem.c ------------------------------------------------------ */
#define MEM_LIBC_MALLOC                 0   /* власний менеджер: ізоляція від купи проєкту */
#define MEMP_MEM_MALLOC                 0   /* пули — окремі статичні масиви в .bss */
#define MEM_ALIGNMENT                   4   /* Cortex-M3/M4 без D-Cache */
#define MEM_SIZE                        (8 * 1024)
#define MEMP_OVERFLOW_CHECK             0   /* 1..2 лише коли ловимо псування пам'яті */
#define MEMP_SANITY_CHECK               0

/* --- Пули memp.c ------------------------------------------------------ */
#define MEMP_NUM_PBUF                   8   /* PBUF_ROM/PBUF_REF: віддача сторінок із флеша */
#define MEMP_NUM_RAW_PCB                0
#define MEMP_NUM_UDP_PCB                2   /* DHCP + DNS */
#define MEMP_NUM_TCP_PCB                2   /* два одночасні з'єднання, більше не тягнемо */
#define MEMP_NUM_TCP_PCB_LISTEN         1   /* один слухач: HTTP-конфігуратор */
#define MEMP_NUM_TCP_SEG                16  /* >= TCP_SND_QUEUELEN, інакше асерт у tcp.c */
#define MEMP_NUM_ARP_QUEUE              2
#define MEMP_NUM_SYS_TIMEOUT            6   /* ARP, TCP, DHCP (два), DNS, запас */

/* --- Вхідний пул ------------------------------------------------------ */
#define PBUF_POOL_SIZE                  8
#define PBUF_POOL_BUFSIZE               512 /* кадр 1514 Б лягає в ланцюжок із трьох буферів */
#define PBUF_LINK_ENCAPSULATION_HLEN    0

/* --- IP --------------------------------------------------------------- */
#define LWIP_IPV4                       1
#define LWIP_IPV6                       0
#define IP_REASSEMBLY                   0   /* збірка фрагментів їсть купу — вимкнено */
#define IP_FRAG                         0
#define LWIP_ICMP                       1
#define LWIP_RAW                        0
#define LWIP_DHCP                       1
#define LWIP_DNS                        1
#define DNS_TABLE_SIZE                  2
#define DNS_MAX_NAME_LENGTH             64

/* --- TCP -------------------------------------------------------------- */
#define LWIP_TCP                        1
#define TCP_TTL                         255
#define TCP_MSS                         536 /* мінімум RFC 879: найдешевші буфери */
#define TCP_WND                         (2 * TCP_MSS)   /* 1072 Б: ~21 КБ/с при RTT 50 мс */
#define TCP_SND_BUF                     (2 * TCP_MSS)
#define TCP_SND_QUEUELEN                ((4 * TCP_SND_BUF) / TCP_MSS)  /* = 8 */
#define TCP_QUEUE_OOSEQ                 0   /* немає RAM на позачергові сегменти */
#define LWIP_TCP_SACK_OUT               0
#define TCP_LISTEN_BACKLOG              0

/* --- API -------------------------------------------------------------- */
#define LWIP_NETCONN                    0   /* без RTOS послідовного API не буває */
#define LWIP_SOCKET                     0
#define LWIP_NETIF_LINK_CALLBACK        1
#define LWIP_NETIF_STATUS_CALLBACK      1

/* --- Діагностика (див. c/lwip-diag.c) --------------------------------- */
#define LWIP_STATS                      1
#define MEM_STATS                       1
#define MEMP_STATS                      1
#define LINK_STATS                      1
#define LWIP_STATS_DISPLAY              0   /* назви пулів у флеші — вмикати за потреби */
#define LWIP_DEBUG                      0

#endif /* LWIPOPTS_H */
