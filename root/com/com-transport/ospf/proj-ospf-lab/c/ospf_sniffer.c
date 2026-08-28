/* ospf_sniffer.c — перехоплення та бінарний розбір пакетів OSPFv2 на C */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <sys/socket.h>

#define OSPF_PROTO 89

#pragma pack(push, 1)
typedef struct {
    uint8_t  version;
    uint8_t  type;
    uint16_t length;
    uint32_t router_id;
    uint32_t area_id;
    uint16_t checksum;
    uint16_t autype;
    uint64_t authentication;
} ospf_header_t;

typedef struct {
    uint32_t network_mask;
    uint16_t hello_interval;
    uint8_t  options;
    uint8_t  priority;
    uint32_t dead_interval;
    uint32_t dr;
    uint32_t bdr;
} ospf_hello_t;
#pragma pack(pop)

static const char* get_ospf_type_str(uint8_t type) {
    switch (type) {
        case 1: return "Hello";
        case 2: return "Database Description (DBD)";
        case 3: return "Link State Request (LSR)";
        case 4: return "Link State Update (LSU)";
        case 5: return "Link State Ack (LSAck)";
        default: return "Unknown";
    }
}

void process_ospf_packet(const uint8_t *payload, ssize_t len) {
    if (len < (ssize_t)sizeof(ospf_header_t)) {
        printf("Помилка: довжина пакета (%zd байтів) менша за заголовок OSPF.
", len);
        return;
    }

    const ospf_header_t *hdr = (const ospf_header_t *)payload;
    struct in_addr rid_addr, area_addr;
    rid_addr.s_addr = hdr->router_id;
    area_addr.s_addr = hdr->area_id;

    printf("
=== Отримано пакет OSPFv%u ===
", hdr->version);
    printf("Тип: %u [%s] | Загальна довжина: %u байтів
",
           hdr->type, get_ospf_type_str(hdr->type), ntohs(hdr->length));
    printf("Router ID: %s | Area ID: %s
", inet_ntoa(rid_addr), inet_ntoa(area_addr));
    printf("Тип автентифікації: %u | Контрольна сума: 0x%04X
",
           ntohs(hdr->autype), ntohs(hdr->checksum));

    if (hdr->type == 1 && len >= (ssize_t)(sizeof(ospf_header_t) + sizeof(ospf_hello_t))) {
        const ospf_hello_t *hello = (const ospf_hello_t *)(payload + sizeof(ospf_header_t));
        struct in_addr mask_addr, dr_addr, bdr_addr;
        mask_addr.s_addr = hello->network_mask;
        dr_addr.s_addr = hello->dr;
        bdr_addr.s_addr = hello->bdr;

        printf("--- Тіло пакета Hello ---
");
        printf("Маска підмережі: %s | Hello: %u с | Dead: %u с
",
               inet_ntoa(mask_addr), ntohs(hello->hello_interval), ntohl(hello->dead_interval));
        printf("Пріоритет вузла: %u | DR: %s | BDR: %s
",
               hello->priority, inet_ntoa(dr_addr), inet_ntoa(bdr_addr));
    }
}

int main(void) {
    int raw_sock = socket(AF_INET, SOCK_RAW, OSPF_PROTO);
    if (raw_sock < 0) {
        perror("Помилка створення raw-сокета (потрібні права root)");
        return 1;
    }

    printf("Прослуховування пакетів OSPF (IP-протокол 89)...
");
    uint8_t buffer[4096];

    while (1) {
        ssize_t received = recvfrom(raw_sock, buffer, sizeof(buffer), 0, NULL, NULL);
        if (received > 0) {
            /* Пропускаємо заголовок IPv4 (розмір визначається полем IHL) */
            uint8_t ip_ihl = (buffer[0] & 0x0F) * 4;
            if (received > ip_ihl) {
                process_ospf_packet(buffer + ip_ihl, received - ip_ihl);
            }
        }
    }

    close(raw_sock);
    return 0;
}
