#ifndef LWIPOPTS_H
#define LWIPOPTS_H

/* Профіль 3 — «високошвидкісний Zero-Copy».
 * 100 Мбіт/с потоком: STM32F7/H7 з D-Cache, дескриптори Ethernet DMA
 * дивляться прямо в буфери PBUF_POOL, копіювання на прийомі немає.
 *
 * Бюджет RAM:
 *   купа MEM_SIZE .......................... 32768 Б
 *   PBUF_POOL: 24 x вирівняне(16 + 1536) ... 37632 Б
 *   керуючі пули ............................ 9984 Б
 *   --------------------------------------------------
 *   разом стеку ............................ ~78.5 КБ
 * Вирівнювання 32 Б — це рядок D-Cache: інакше clean/invalidate зачепить
 * сусідній буфер, і DMA перезапише щойно записані процесором байти.
 * Сам пул кладеться лінкером у некешовану область (MPU) або чиститься
 * вручну — інакше zero-copy не працює.
 */

/* --- Ядро й планування ---------------------------------------------- */
#define NO_SYS                          0
#define SYS_LIGHTWEIGHT_PROT            1
#define LWIP_TCPIP_CORE_LOCKING         1
#define LWIP_TCPIP_CORE_LOCKING_INPUT   1   /* драйвер заходить у стек прямо з ISR-задачі */

/* --- Купа mem.c ------------------------------------------------------ */
#define MEM_LIBC_MALLOC                 0
#define MEMP_MEM_MALLOC                 0
#define MEM_ALIGNMENT                   32  /* рядок D-Cache Cortex-M7 */
#define MEM_SIZE                        (32 * 1024)
#define MEMP_OVERFLOW_CHECK             0

/* --- Пули memp.c ------------------------------------------------------ */
#define MEMP_NUM_PBUF                   32
#define MEMP_NUM_RAW_PCB                2
#define MEMP_NUM_UDP_PCB                8
#define MEMP_NUM_TCP_PCB                16
#define MEMP_NUM_TCP_PCB_LISTEN         4
#define MEMP_NUM_TCP_SEG                64
#define MEMP_NUM_NETCONN                24  /* = MEMP_NUM_TCP_PCB + MEMP_NUM_UDP_PCB */
#define MEMP_NUM_NETBUF                 32
#define MEMP_NUM_ARP_QUEUE              8
#define MEMP_NUM_SYS_TIMEOUT            12

/* --- Вхідний пул: кадр у один буфер ----------------------------------- */
#define PBUF_POOL_SIZE                  24
#define PBUF_POOL_BUFSIZE               1536 /* 1514 Б кадру + запас, кратно 32 */
#define PBUF_LINK_ENCAPSULATION_HLEN    0
#define LWIP_SUPPORT_CUSTOM_PBUF        1    /* pbuf_custom поверх дескриптора DMA */
#define LWIP_NETIF_TX_SINGLE_PBUF       1    /* один дескриптор на кадр при передачі */

/* --- IP --------------------------------------------------------------- */
#define LWIP_IPV4                       1
#define LWIP_IPV6                       0
#define IP_REASSEMBLY                   1
#define IP_FRAG                         1
#define IP_REASS_MAX_PBUFS              10
#define LWIP_ICMP                       1
#define LWIP_DHCP                       1
#define LWIP_DNS                        1

/* --- TCP -------------------------------------------------------------- */
#define LWIP_TCP                        1
#define TCP_MSS                         1460
#define TCP_WND                         (6 * TCP_MSS)   /* 8760 Б: ~856 КБ/с при RTT 10 мс */
#define TCP_SND_BUF                     (6 * TCP_MSS)
#define TCP_SND_QUEUELEN                24              /* = 4 * TCP_SND_BUF / TCP_MSS */
#define TCP_QUEUE_OOSEQ                 1
#define TCP_OOSEQ_MAX_PBUFS             6
#define LWIP_TCP_SACK_OUT               1               /* на швидкому лінку рятує від зайвих ретрансмісій */
#define TCP_LISTEN_BACKLOG              1

/* --- Апаратний розрахунок контрольних сум ------------------------------ */
#define LWIP_CHECKSUM_CTRL_PER_NETIF    1
#define CHECKSUM_GEN_IP                 0
#define CHECKSUM_GEN_UDP                0
#define CHECKSUM_GEN_TCP                0
#define CHECKSUM_GEN_ICMP               0
#define CHECKSUM_CHECK_IP               0
#define CHECKSUM_CHECK_UDP              0
#define CHECKSUM_CHECK_TCP              0
#define CHECKSUM_CHECK_ICMP             0

/* --- Послідовний API і сокети ----------------------------------------- */
#define LWIP_NETCONN                    1
#define LWIP_SOCKET                     1
#define LWIP_SO_RCVTIMEO                1
#define LWIP_SO_SNDTIMEO                1
#define SO_REUSE                        1
#define LWIP_TCP_KEEPALIVE              1
#define LWIP_NETIF_LINK_CALLBACK        1
#define LWIP_NETIF_STATUS_CALLBACK      1

/* --- Черги й задачі RTOS ---------------------------------------------- */
#define TCPIP_THREAD_NAME               "tcpip"
#define TCPIP_THREAD_STACKSIZE          2048            /* слів = 8192 Б */
#define TCPIP_THREAD_PRIO               6
#define TCPIP_MBOX_SIZE                 32
#define DEFAULT_UDP_RECVMBOX_SIZE       16
#define DEFAULT_TCP_RECVMBOX_SIZE       32
#define DEFAULT_ACCEPTMBOX_SIZE         8

/* --- Діагностика (див. c/lwip-diag.c) --------------------------------- */
#define LWIP_STATS                      1
#define MEM_STATS                       1
#define MEMP_STATS                      1
#define LINK_STATS                      1
#define TCP_STATS                       1
#define LWIP_STATS_DISPLAY              1
#define LWIP_DEBUG                      0

#endif /* LWIPOPTS_H */
