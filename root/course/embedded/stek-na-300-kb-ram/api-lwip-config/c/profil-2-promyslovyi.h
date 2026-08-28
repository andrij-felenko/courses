#ifndef LWIPOPTS_H
#define LWIPOPTS_H

#define NO_SYS                          0
#define MEM_LIBC_MALLOC                 0
#define MEM_ALIGNMENT                   4
#define MEM_SIZE                        (20 * 1024)

#define MEMP_NUM_PBUF                   16
#define MEMP_NUM_TCP_PCB                8
#define MEMP_NUM_TCP_PCB_LISTEN         4
#define MEMP_NUM_TCP_SEG                32
#define MEMP_NUM_UDP_PCB                4
#define MEMP_NUM_NETCONN                12
#define MEMP_NUM_NETBUF                 16

#define PBUF_POOL_SIZE                  16
#define PBUF_POOL_BUFSIZE               512

#define TCP_MSS                         1460
#define TCP_WND                         (3 * TCP_MSS)
#define TCP_SND_BUF                     (3 * TCP_MSS)
#define TCP_SND_QUEUELEN                8
#define TCP_QUEUE_OOSEQ                 1

#define TCPIP_MBOX_SIZE                 16
#define DEFAULT_RAW_RECVMBOX_SIZE       8
#define DEFAULT_UDP_RECVMBOX_SIZE       8
#define DEFAULT_TCP_RECVMBOX_SIZE       16
#define DEFAULT_ACCEPTMBOX_SIZE         8

#define LWIP_NETCONN                    1
#define LWIP_SOCKET                     1
#define SO_REUSE                        1
#define TCP_LISTEN_BACKLOG              1

#endif /* LWIPOPTS_H */
