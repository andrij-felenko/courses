#ifndef LWIPOPTS_H
#define LWIPOPTS_H

#define NO_SYS                          1
#define MEM_LIBC_MALLOC                 0
#define MEM_ALIGNMENT                   4
#define MEM_SIZE                        (8 * 1024)

#define MEMP_NUM_PBUF                   8
#define MEMP_NUM_TCP_PCB                2
#define MEMP_NUM_TCP_PCB_LISTEN         1
#define MEMP_NUM_TCP_SEG                12
#define MEMP_NUM_UDP_PCB                2

#define PBUF_POOL_SIZE                  8
#define PBUF_POOL_BUFSIZE               512

#define TCP_MSS                         536
#define TCP_WND                         (2 * TCP_MSS)
#define TCP_SND_BUF                     (2 * TCP_MSS)
#define TCP_SND_QUEUELEN                4
#define TCP_QUEUE_OOSEQ                 0

#define LWIP_NETCONN                    0
#define LWIP_SOCKET                     0
#define LWIP_DHCP                       1
#define LWIP_DNS                        1

#endif /* LWIPOPTS_H */
