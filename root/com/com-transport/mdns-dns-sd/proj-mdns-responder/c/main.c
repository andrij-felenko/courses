#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

#define MDNS_PORT 5353
#define MDNS_MULTICAST_IPV4 "224.0.0.251"
#define BUFFER_SIZE 1472

#define DNS_TYPE_A     1
#define DNS_TYPE_PTR   12
#define DNS_TYPE_TXT   16
#define DNS_TYPE_AAAA  28
#define DNS_TYPE_SRV   33
#define DNS_TYPE_ANY  255

#define DNS_CLASS_IN        1
#define MDNS_CACHE_FLUSH    0x8000
#define MDNS_UNICAST_RESP   0x8000

#pragma pack(push, 1)
typedef struct {
    uint16_t id;
    uint16_t flags;
    uint16_t qdcount;
    uint16_t ancount;
    uint16_t nscount;
    uint16_t arcount;
} mdns_header_t;
#pragma pack(pop)

typedef struct {
    const char *hostname;        /* наприклад, "sensor-node" */
    const char *service_type;    /* наприклад, "_http._tcp" */
    const char *instance_name;   /* наприклад, "Датчик Клімату" */
    uint16_t port;               /* наприклад, 80 */
    uint32_t ipv4_addr;          /* наприклад, 192.168.1.120 */
    const char *txt_records[4];  /* наприклад, {"version=1.0", "path=/api", NULL} */
} mdns_service_config_t;

typedef struct {
    int sock_fd;
    struct sockaddr_in mcast_addr;
    mdns_service_config_t config;
    uint8_t rx_buf[BUFFER_SIZE];
    uint8_t tx_buf[BUFFER_SIZE];
} mdns_responder_t;

/* Допоміжні функції запису DNS-міток */
static size_t write_label(uint8_t *buf, size_t offset, size_t max_len, const char *label) {
    size_t len = strlen(label);
    if (offset + len + 1 >= max_len || len > 63) return 0;
    buf[offset++] = (uint8_t)len;
    memcpy(&buf[offset], label, len);
    return len + 1;
}

static size_t write_domain_name(uint8_t *buf, size_t offset, size_t max_len, const char *name) {
    char temp[256];
    strncpy(temp, name, sizeof(temp) - 1);
    temp[sizeof(temp) - 1] = '\0';

    char *saveptr = NULL;
    char *token = strtok_r(temp, ".", &saveptr);
    size_t written = 0;

    while (token != NULL) {
        size_t n = write_label(buf, offset + written, max_len, token);
        if (n == 0) return 0;
        written += n;
        token = strtok_r(NULL, ".", &saveptr);
    }
    if (offset + written >= max_len) return 0;
    buf[offset + written++] = 0x00; /* Термінатор */
    return written;
}

/* Формування повного пакету анонсу (Answer: PTR; Additional: SRV, TXT, A) */
static size_t build_full_announcement(mdns_responder_t *res, uint32_t ttl, uint8_t *buf, size_t max_len) {
    if (max_len < sizeof(mdns_header_t)) return 0;

    mdns_header_t *hdr = (mdns_header_t *)buf;
    hdr->id = 0;
    hdr->flags = htons(0x8400); /* QR=1 (Response), AA=1 (Authoritative) */
    hdr->qdcount = 0;
    hdr->ancount = htons(1);    /* 1 Answer RR: PTR */
    hdr->nscount = 0;
    hdr->arcount = htons(3);    /* 3 Additional RRs: SRV, TXT, A */

    size_t cur = sizeof(mdns_header_t);

    /* 1. Answer: PTR-запис (_http._tcp.local -> Instance._http._tcp.local) */
    size_t ptr_service_offset = cur;
    char service_fqdn[128];
    snprintf(service_fqdn, sizeof(service_fqdn), "%s.local", res->config.service_type);
    cur += write_domain_name(buf, cur, max_len, service_fqdn);

    *(uint16_t *)&buf[cur] = htons(DNS_TYPE_PTR); cur += 2;
    *(uint16_t *)&buf[cur] = htons(DNS_CLASS_IN); cur += 2; /* Shared (Cache-Flush = 0) */
    *(uint32_t *)&buf[cur] = htonl(ttl);          cur += 4;

    size_t rdlength_pos_ptr = cur;
    cur += 2; /* Місце для RDLENGTH */
    size_t rdata_start_ptr = cur;

    size_t instance_fqdn_offset = cur;
    cur += write_label(buf, cur, max_len, res->config.instance_name);
    /* Компресія: вказівник на service_fqdn (0xC000 | ptr_service_offset) */
    buf[cur++] = 0xC0 | (uint8_t)(ptr_service_offset >> 8);
    buf[cur++] = (uint8_t)(ptr_service_offset & 0xFF);

    *(uint16_t *)&buf[rdlength_pos_ptr] = htons((uint16_t)(cur - rdata_start_ptr));

    /* 2. Additional: SRV-запис (Instance._http._tcp.local -> host.local:port) */
    /* Компресія: вказівник на повне ім'я екземпляра */
    buf[cur++] = 0xC0 | (uint8_t)(instance_fqdn_offset >> 8);
    buf[cur++] = (uint8_t)(instance_fqdn_offset & 0xFF);

    *(uint16_t *)&buf[cur] = htons(DNS_TYPE_SRV); cur += 2;
    *(uint16_t *)&buf[cur] = htons(DNS_CLASS_IN | MDNS_CACHE_FLUSH); cur += 2;
    *(uint32_t *)&buf[cur] = htonl(ttl);          cur += 4;

    size_t rdlength_pos_srv = cur;
    cur += 2;
    size_t rdata_start_srv = cur;

    *(uint16_t *)&buf[cur] = htons(0); cur += 2; /* Priority */
    *(uint16_t *)&buf[cur] = htons(0); cur += 2; /* Weight */
    *(uint16_t *)&buf[cur] = htons(res->config.port); cur += 2; /* Port */

    size_t host_fqdn_offset = cur;
    char host_fqdn[128];
    snprintf(host_fqdn, sizeof(host_fqdn), "%s.local", res->config.hostname);
    cur += write_domain_name(buf, cur, max_len, host_fqdn);

    *(uint16_t *)&buf[rdlength_pos_srv] = htons((uint16_t)(cur - rdata_start_srv));

    /* 3. Additional: TXT-запис (Instance._http._tcp.local) */
    buf[cur++] = 0xC0 | (uint8_t)(instance_fqdn_offset >> 8);
    buf[cur++] = (uint8_t)(instance_fqdn_offset & 0xFF);

    *(uint16_t *)&buf[cur] = htons(DNS_TYPE_TXT); cur += 2;
    *(uint16_t *)&buf[cur] = htons(DNS_CLASS_IN | MDNS_CACHE_FLUSH); cur += 2;
    *(uint32_t *)&buf[cur] = htonl(ttl);          cur += 4;

    size_t rdlength_pos_txt = cur;
    cur += 2;
    size_t rdata_start_txt = cur;

    for (int i = 0; res->config.txt_records[i] != NULL && i < 4; i++) {
        size_t txt_len = strlen(res->config.txt_records[i]);
        if (txt_len > 255 || cur + txt_len + 1 >= max_len) break;
        buf[cur++] = (uint8_t)txt_len;
        memcpy(&buf[cur], res->config.txt_records[i], txt_len);
        cur += txt_len;
    }
    if (cur == rdata_start_txt) { /* Порожній TXT: 1 байт 0x00 */
        buf[cur++] = 0x00;
    }
    *(uint16_t *)&buf[rdlength_pos_txt] = htons((uint16_t)(cur - rdata_start_txt));

    /* 4. Additional: A-запис (host.local -> IPv4) */
    buf[cur++] = 0xC0 | (uint8_t)(host_fqdn_offset >> 8);
    buf[cur++] = (uint8_t)(host_fqdn_offset & 0xFF);

    *(uint16_t *)&buf[cur] = htons(DNS_TYPE_A); cur += 2;
    *(uint16_t *)&buf[cur] = htons(DNS_CLASS_IN | MDNS_CACHE_FLUSH); cur += 2;
    *(uint32_t *)&buf[cur] = htonl(120); /* TTL для адресного запису хоста: 120 с */
    cur += 4;
    *(uint16_t *)&buf[cur] = htons(4); cur += 2; /* RDLENGTH */
    *(uint32_t *)&buf[cur] = res->config.ipv4_addr; cur += 4; /* RDATA */

    return cur;
}

/* Ініціалізація мережевого сокета */
int mdns_responder_init(mdns_responder_t *res, const mdns_service_config_t *cfg) {
    memset(res, 0, sizeof(*res));
    res->config = *cfg;

    res->sock_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (res->sock_fd < 0) {
        perror("socket");
        return -1;
    }

    int reuse = 1;
    setsockopt(res->sock_fd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));
#ifdef SO_REUSEPORT
    setsockopt(res->sock_fd, SOL_SOCKET, SO_REUSEPORT, &reuse, sizeof(reuse));
#endif

    struct sockaddr_in bind_addr;
    memset(&bind_addr, 0, sizeof(bind_addr));
    bind_addr.sin_family = AF_INET;
    bind_addr.sin_port = htons(MDNS_PORT);
    bind_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(res->sock_fd, (struct sockaddr *)&bind_addr, sizeof(bind_addr)) < 0) {
        perror("bind");
        close(res->sock_fd);
        return -1;
    }

    /* Приєднання до групи 224.0.0.251 */
    struct ip_mreq mreq;
    mreq.imr_multiaddr.s_addr = inet_addr(MDNS_MULTICAST_IPV4);
    mreq.imr_interface.s_addr = res->config.ipv4_addr;

    if (setsockopt(res->sock_fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) < 0) {
        mreq.imr_interface.s_addr = htonl(INADDR_ANY);
        if (setsockopt(res->sock_fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) < 0) {
            perror("IP_ADD_MEMBERSHIP");
            close(res->sock_fd);
            return -1;
        }
    }

    unsigned char ttl = 255;
    setsockopt(res->sock_fd, IPPROTO_IP, IP_MULTICAST_TTL, &ttl, sizeof(ttl));

    memset(&res->mcast_addr, 0, sizeof(res->mcast_addr));
    res->mcast_addr.sin_family = AF_INET;
    res->mcast_addr.sin_port = htons(MDNS_PORT);
    res->mcast_addr.sin_addr.s_addr = inet_addr(MDNS_MULTICAST_IPV4);

    return 0;
}

/* Надсилання анонсу */
void mdns_send_announcement(mdns_responder_t *res, uint32_t ttl) {
    size_t len = build_full_announcement(res, ttl, res->tx_buf, sizeof(res->tx_buf));
    if (len > 0) {
        sendto(res->sock_fd, res->tx_buf, len, 0,
               (struct sockaddr *)&res->mcast_addr, sizeof(res->mcast_addr));
    }
}

/* Обробка вхідного пакету запиту */
void mdns_process_packet(mdns_responder_t *res, const uint8_t *buf, size_t len) {
    if (len < sizeof(mdns_header_t)) return;
    const mdns_header_t *hdr = (const mdns_header_t *)buf;

    /* Ігноруємо відповіді інших вузлів (QR=1) */
    if (ntohs(hdr->flags) & 0x8000) return;

    uint16_t qdcount = ntohs(hdr->qdcount);
    if (qdcount == 0) return;

    /* Відповідаємо комбінованим анонсом */
    mdns_send_announcement(res, 4500);
}

/* Головний цикл респондера */
int main(void) {
    mdns_service_config_t cfg = {
        .hostname = "sensor-node",
        .service_type = "_http._tcp",
        .instance_name = "Embedded Sensor",
        .port = 80,
        .ipv4_addr = inet_addr("192.168.1.120"),
        .txt_records = {"model=BME280", "firmware=2.1.0", NULL}
    };

    mdns_responder_t res;
    if (mdns_responder_init(&res, &cfg) < 0) {
        fprintf(stderr, "Помилка ініціалізації mDNS респондера\n");
        return 1;
    }

    printf("mDNS респондер запущено: %s.local -> %s._http._tcp.local:80\n",
           cfg.hostname, cfg.instance_name);

    /* 1. Фаза оголошення (2 анонси з інтервалом 1 с) */
    mdns_send_announcement(&res, 4500);
    sleep(1);
    mdns_send_announcement(&res, 4500);

    /* 2. Робочий цикл слухання запитів */
    struct pollfd pfd = { .fd = res.sock_fd, .events = POLLIN };
    for (int i = 0; i < 30; i++) { /* Демонстраційний цикл на 30 секунд */
        int ret = poll(&pfd, 1, 1000);
        if (ret > 0 && (pfd.revents & POLLIN)) {
            ssize_t n = recvfrom(res.sock_fd, res.rx_buf, sizeof(res.rx_buf), 0, NULL, NULL);
            if (n > 0) {
                mdns_process_packet(&res, res.rx_buf, (size_t)n);
            }
        }
    }

    /* 3. Оголошення про вихід (Good-bye, TTL = 0) */
    printf("Надсилання Good-bye пакету перед вимкненням...\n");
    mdns_send_announcement(&res, 0);

    close(res.sock_fd);
    return 0;
}
