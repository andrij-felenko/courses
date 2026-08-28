#ifndef LWIPOPTS_H
#define LWIPOPTS_H

#define NO_SYS                          0
#define MEM_LIBC_MALLOC                 0
#define MEM_ALIGNMENT                   32      /* Вирівнювання за рядком D-Cache */
#define MEM_SIZE                        (32 * 1024)

#define MEMP_NUM_PBUF                   32
#define MEMP_NUM_TCP_PCB                16
#define MEMP_NUM_TCP_PCB_LISTEN         4
#define MEMP_NUM_TCP_SEG                64
#define MEMP_NUM_UDP_PCB                8
#define MEMP_NUM_NETCONN                24
#define MEMP_NUM_NETBUF                 32

/* Повний розмір Ethernet кадру в одному pbuf для прямої роботи DMA */
#define PBUF_POOL_SIZE                  24
#define PBUF_POOL_BUFSIZE               1536

#define TCP_MSS                         1460
#define TCP_WND                         (6 * TCP_MSS)
#define TCP_SND_BUF                     (6 * TCP_MSS)
#define TCP_SND_QUEUELEN                16
#define TCP_QUEUE_OOSEQ                 1

#define TCPIP_MBOX_SIZE                 32
#define DEFAULT_TCP_RECVMBOX_SIZE       32

#define LWIP_NETCONN                    1
#define LWIP_SOCKET                     1
#define LWIP_CHECKSUM_CTRL_PER_NETIF    1       /* Апаратний розрахунок контрольних сум */
#define CHECKSUM_GEN_IP                 0
#define CHECKSUM_GEN_UDP                0
#define CHECKSUM_GEN_TCP                0
#define CHECKSUM_CHECK_IP               0
#define CHECKSUM_CHECK_UDP              0
#define CHECKSUM_CHECK_TCP              0

#endif /* LWIPOPTS_H */
