#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <net/ethernet.h>
#include <netinet/in.h>

#define ETH_P_8021Q 0x8100
#define BUFFER_SIZE 2048

/* Структура 4-байтового тегу 802.1Q у пам'яті */
struct vlan_tag {
    uint16_t tpid; /* 0x8100 */
    uint16_t tci;  /* PCP(3b) + DEI(1b) + VID(12b) */
};

/* Функція розбору та виводу параметрів кадру */
void parse_ethernet_frame(const unsigned char *buffer, ssize_t len) {
    if (len < (ssize_t)sizeof(struct ether_header)) {
        printf("Занадто короткий кадр Ethernet (менше 14 байтів)\n");
        return;
    }

    const struct ether_header *eth = (const struct ether_header *)buffer;
    uint16_t ether_type = ntohs(eth->ether_type);

    printf("MAC: %02x:%02x:%02x:%02x:%02x:%02x -> %02x:%02x:%02x:%02x:%02x:%02x | ",
           eth->ether_shost[0], eth->ether_shost[1], eth->ether_shost[2],
           eth->ether_shost[3], eth->ether_shost[4], eth->ether_shost[5],
           eth->ether_dhost[0], eth->ether_dhost[1], eth->ether_dhost[2],
           eth->ether_dhost[3], eth->ether_dhost[4], eth->ether_dhost[5]);

    /* Перевірка наявність тегу 802.1Q (TPID == 0x8100) */
    if (ether_type == ETH_P_8021Q) {
        if (len < (ssize_t)(sizeof(struct ether_header) + sizeof(struct vlan_tag))) {
            printf("Помилка: занадто короткий кадр 802.1Q\n");
            return;
        }

        const struct vlan_tag *vlan = (const struct vlan_tag *)(buffer + sizeof(struct ether_header));
        uint16_t tci = ntohs(vlan->tci);

        uint8_t  pcp = (tci >> 13) & 0x07;
        uint8_t  dei = (tci >> 12) & 0x01;
        uint16_t vid = tci & 0x0FFF;

        const uint16_t *inner_type_ptr = (const uint16_t *)(buffer + sizeof(struct ether_header) + sizeof(struct vlan_tag));
        uint16_t inner_type = ntohs(*inner_type_ptr);

        printf("[VLAN TAGGED] VID: %u, PCP: %u, DEI: %u | Inner EtherType: 0x%04X\n",
               vid, pcp, dei, inner_type);
    } else {
        printf("[UNTAGGED] EtherType: 0x%04X\n", ether_type);
    }
}

int main(void) {
    /* Створення сирого сокета для перехоплення усіх кадрів Ethernet */
    int sock_fd = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
    if (sock_fd < 0) {
        perror("Помилка створення raw-сокета (потрібні права root)");
        return 1;
    }

    unsigned char buffer[BUFFER_SIZE];
    printf("Запуск аналізатора кадрів 802.1Q... (Очікування 10 кадрів)\n");

    for (int i = 0; i < 10; ++i) {
        ssize_t data_size = recvfrom(sock_fd, buffer, BUFFER_SIZE, 0, NULL, NULL);
        if (data_size < 0) {
            perror("Помилка читання з сокета");
            break;
        }
        parse_ethernet_frame(buffer, data_size);
    }

    close(sock_fd);
    printf("Аналіз завершено, сокет закрито.\n");
    return 0;
}
