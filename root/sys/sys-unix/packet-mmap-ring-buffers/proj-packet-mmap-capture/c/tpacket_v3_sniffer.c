/* tpacket_v3_sniffer.c — Повна реалізація мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <sys/poll.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <netinet/if_ether.h>
#include <netinet/ip.h>
#include <linux/if_packet.h>

static volatile int keep_running = 1;

static void sig_handler(int sig) {
    (void)sig;
    keep_running = 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <мережевий_інтерфейс>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *ifname = argv[1];
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    /* 1. Створення RAW сокета AF_PACKET */
    int fd = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
    if (fd < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    /* 2. Встановлення версії TPACKET_V3 */
    int version = TPACKET_V3;
    if (setsockopt(fd, SOL_PACKET, PACKET_VERSION, &version, sizeof(version)) < 0) {
        perror("setsockopt PACKET_VERSION");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 3. Налаштування параметрів кільцевого буфера */
    struct tpacket_req3 req;
    memset(&req, 0, sizeof(req));
    req.tp_block_size = 1024 * 1024;    /* 1 MB на блок (кратне PAGE_SIZE) */
    req.tp_block_nr = 64;               /* 64 блоки = 64 MB сумарно */
    req.tp_frame_size = 2048;           /* Верхня межа snaplen кадру */
    req.tp_frame_nr = (req.tp_block_size * req.tp_block_nr) / req.tp_frame_size;
    req.tp_retire_blk_tov = 10;         /* Таймаут віддачі блоку: 10 мс */
    req.tp_feature_req_word = TP_FT_REQ_FILL_RXHASH;

    if (setsockopt(fd, SOL_PACKET, PACKET_RX_RING, &req, sizeof(req)) < 0) {
        perror("setsockopt PACKET_RX_RING");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 4. mmap() відображення спільної пам'яті ядра у простір користувача */
    size_t ring_bytes = (size_t)req.tp_block_size * req.tp_block_nr;
    uint8_t *ring = mmap(NULL, ring_bytes, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_LOCKED, fd, 0);
    if (ring == MAP_FAILED) {
        perror("mmap");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 5. Прив'язка сокета до мережевого інтерфейсу */
    struct sockaddr_ll sll;
    memset(&sll, 0, sizeof(sll));
    sll.sll_family = AF_PACKET;
    sll.sll_protocol = htons(ETH_P_ALL);
    sll.sll_ifindex = if_nametoindex(ifname);
    if (sll.sll_ifindex == 0) {
        fprintf(stderr, "Помилка: мережевий інтерфейс %s не знайдено\n", ifname);
        munmap(ring, ring_bytes);
        close(fd);
        return EXIT_FAILURE;
    }

    if (bind(fd, (struct sockaddr *)&sll, sizeof(sll)) < 0) {
        perror("bind");
        munmap(ring, ring_bytes);
        close(fd);
        return EXIT_FAILURE;
    }

    /* 6. Приєднання до Fanout групи за хешем 4-tuple */
    uint32_t fanout_arg = (42 & 0xffff) | (PACKET_FANOUT_HASH << 16);
    if (setsockopt(fd, SOL_PACKET, PACKET_FANOUT, &fanout_arg, sizeof(fanout_arg)) < 0) {
        perror("setsockopt PACKET_FANOUT");
    }

    printf("Сніфер C запущено на %s (TPACKET_V3, 64MB ring)... Натисніть Ctrl+C для зупинки.\n", ifname);

    unsigned int block_idx = 0;
    uint64_t total_packets = 0;

    struct pollfd pfd;
    memset(&pfd, 0, sizeof(pfd));
    pfd.fd = fd;
    pfd.events = POLLIN | POLLERR;

    /* 7. Основний цикл пакетної обробки блоків */
    while (keep_running) {
        struct block_desc *pbd = (struct block_desc *)(ring + (block_idx * req.tp_block_size));

        /* Перевірка атомарного статусу блоку */
        if ((pbd->h1.block_status & TP_STATUS_USER) == 0) {
            poll(&pfd, 1, 10); /* Засинаємо не більше ніж на 10 мс при відсутності даних */
            continue;
        }

        /* Ітерація по всіх пакетах всередині блоку */
        uint32_t num_pkts = pbd->h1.num_pkts;
        uint8_t *pkt_ptr = (uint8_t *)pbd + pbd->h1.offset_to_first_pkt;

        for (uint32_t i = 0; i < num_pkts; ++i) {
            struct tpacket3_hdr *hdr = (struct tpacket3_hdr *)pkt_ptr;
            uint8_t *eth_data = (uint8_t *)hdr + hdr->tp_mac;

            /* Розбір Ethernet заголовка */
            struct ethhdr *eth = (struct ethhdr *)eth_data;
            if (ntohs(eth->h_proto) == ETH_P_IP) {
                struct iphdr *ip = (struct iphdr *)(eth_data + sizeof(struct ethhdr));
                char src_ip[INET_ADDRSTRLEN], dst_ip[INET_ADDRSTRLEN];
                inet_ntop(AF_INET, &ip->saddr, src_ip, sizeof(src_ip));
                inet_ntop(AF_INET, &ip->daddr, dst_ip, sizeof(dst_ip));
                (void)src_ip; (void)dst_ip;
            }

            total_packets++;
            pkt_ptr += hdr->tp_next_offset; /* Перехід до наступного кадру */
        }

        /* Повертаємо блок ядру */
        pbd->h1.block_status = TP_STATUS_KERNEL;
        block_idx = (block_idx + 1) % req.tp_block_nr;
    }

    printf("\nЗупинено. Всього оброблено пакетів: %lu\n", total_packets);

    /* 8. Звільнення ресурсів */
    munmap(ring, ring_bytes);
    close(fd);
    return EXIT_SUCCESS;
}
