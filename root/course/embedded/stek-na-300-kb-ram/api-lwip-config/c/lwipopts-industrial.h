#ifndef LWIPOPTS_H
#define LWIPOPTS_H

/* Профіль 2 — «промисловий стандарт RTOS».
 * FreeRTOS, BSD-сокети, 4-8 одночасних з'єднань: STM32F407, ESP32.
 * Шлюз Modbus TCP, веб-сервер керування, MQTT-клієнт у сусідній задачі.
 *
 * Бюджет RAM:
 *   купа MEM_SIZE ......................... 20480 Б
 *   PBUF_POOL: 16 x вирівняне(16 + 512) .... 8448 Б
 *   керуючі пули (PCB, SEG, NETCONN, ...) .. 3616 Б
 *   -------------------------------------------------
 *   разом стеку ........................... ~31.8 КБ
 * Понад це — стек tcpip_thread (4 КБ) і стеки задач застосунку.
 */

/* --- Ядро й планування ---------------------------------------------- */
#define NO_SYS                          0   /* є RTOS: працює tcpip_thread */
#define SYS_LIGHTWEIGHT_PROT            1
#define LWIP_TCPIP_CORE_LOCKING         1   /* один м'ютекс замість черги повідомлень на кожен виклик */
#define LWIP_TCPIP_CORE_LOCKING_INPUT   0   /* драйвер віддає кадри через tcpip_input() */

/* --- Купа mem.c ------------------------------------------------------ */
#define MEM_LIBC_MALLOC                 0
#define MEMP_MEM_MALLOC                 0
#define MEM_ALIGNMENT                   4
#define MEM_SIZE                        (20 * 1024)
#define MEMP_OVERFLOW_CHECK             0
#define MEMP_SANITY_CHECK               0

/* --- Пули memp.c ------------------------------------------------------ */
#define MEMP_NUM_PBUF                   16
#define MEMP_NUM_RAW_PCB                2
#define MEMP_NUM_UDP_PCB                4   /* DHCP, DNS, SNTP, службовий broadcast */
#define MEMP_NUM_TCP_PCB                8
#define MEMP_NUM_TCP_PCB_LISTEN         4   /* HTTP, Modbus 502, телеметрія, оновлення */
#define MEMP_NUM_TCP_SEG                32  /* свідома пересписка: 8 сокетів по 12 разом не насичуються */
#define MEMP_NUM_NETCONN                12  /* = MEMP_NUM_TCP_PCB + MEMP_NUM_UDP_PCB */
#define MEMP_NUM_NETBUF                 16
#define MEMP_NUM_ARP_QUEUE              4
#define MEMP_NUM_REASSDATA              4
#define MEMP_NUM_FRAG_PBUF              4
#define MEMP_NUM_SYS_TIMEOUT            10

/* --- Вхідний пул ------------------------------------------------------ */
#define PBUF_POOL_SIZE                  16
#define PBUF_POOL_BUFSIZE               512 /* короткі ACK і ARP не марнують по 1.5 КБ */
#define PBUF_LINK_ENCAPSULATION_HLEN    0

/* --- IP --------------------------------------------------------------- */
#define LWIP_IPV4                       1
#define LWIP_IPV6                       0
#define IP_REASSEMBLY                   1   /* чужі вузли шлють фрагменти — збираємо */
#define IP_FRAG                         1
#define IP_REASS_MAX_PBUFS              8
#define LWIP_ICMP                       1
#define LWIP_DHCP                       1
#define LWIP_DNS                        1
#define DNS_TABLE_SIZE                  4

/* --- TCP -------------------------------------------------------------- */
#define LWIP_TCP                        1
#define TCP_MSS                         1460            /* MTU 1500 - 20 (IP) - 20 (TCP) */
#define TCP_WND                         (3 * TCP_MSS)   /* 4380 Б: ~85 КБ/с при RTT 50 мс */
#define TCP_SND_BUF                     (3 * TCP_MSS)
#define TCP_SND_QUEUELEN                12              /* = 4 * TCP_SND_BUF / TCP_MSS */
#define TCP_QUEUE_OOSEQ                 1
#define TCP_OOSEQ_MAX_PBUFS             4               /* стеля на сокет, щоб один потік не з'їв пул */
#define LWIP_TCP_SACK_OUT               0
#define TCP_LISTEN_BACKLOG              1
#define TCP_DEFAULT_LISTEN_BACKLOG      4

/* --- Послідовний API і сокети ----------------------------------------- */
#define LWIP_NETCONN                    1
#define LWIP_SOCKET                     1
#define LWIP_SO_RCVTIMEO                1   /* без таймауту задача зависає назавжди */
#define LWIP_SO_SNDTIMEO                1
#define LWIP_SO_RCVBUF                  1
#define SO_REUSE                        1   /* перезапуск служби без очікування TIME_WAIT */
#define LWIP_TCP_KEEPALIVE              1   /* обірваний кабель інакше лишає мертвий PCB */
#define LWIP_NETIF_LINK_CALLBACK        1
#define LWIP_NETIF_STATUS_CALLBACK      1

/* --- Черги й задачі RTOS ---------------------------------------------- */
#define TCPIP_THREAD_NAME               "tcpip"
#define TCPIP_THREAD_STACKSIZE          1024            /* слів FreeRTOS = 4096 Б */
#define TCPIP_THREAD_PRIO               5
#define TCPIP_MBOX_SIZE                 16              /* переповнення = дроп на рівні драйвера */
#define DEFAULT_THREAD_STACKSIZE        512
#define DEFAULT_THREAD_PRIO             3
#define DEFAULT_RAW_RECVMBOX_SIZE       8
#define DEFAULT_UDP_RECVMBOX_SIZE       8
#define DEFAULT_TCP_RECVMBOX_SIZE       16
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
