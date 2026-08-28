#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <arpa/inet.h>

#define DHCP_CHADDR_LEN     16
#define DHCP_SNAME_LEN      64
#define DHCP_FILE_LEN       128
#define DHCP_MAGIC_COOKIE   0x63825363
#define DHCP_MIN_OPTIONS    312
#define DHCP_MAX_PACKET_LEN 576

#define OPT_PAD             0
#define OPT_SUBNET_MASK     1
#define OPT_ROUTER          3
#define OPT_DNS_SERVER      6
#define OPT_HOST_NAME       12
#define OPT_DOMAIN_NAME     15
#define OPT_REQUESTED_IP    50
#define OPT_LEASE_TIME      51
#define OPT_MSG_TYPE        53
#define OPT_SERVER_ID       54
#define OPT_PARAM_REQ_LIST  55
#define OPT_CLIENT_ID       61
#define OPT_END             255

#define DHCP_DISCOVER       1
#define DHCP_OFFER          2
#define DHCP_REQUEST        3
#define DHCP_ACK            5

#pragma pack(push, 1)
struct dhcp_packet {
    uint8_t  op;
    uint8_t  htype;
    uint8_t  hlen;
    uint8_t  hops;
    uint32_t xid;
    uint16_t secs;
    uint16_t flags;
    uint32_t ciaddr;
    uint32_t yiaddr;
    uint32_t siaddr;
    uint32_t giaddr;
    uint8_t  chaddr[DHCP_CHADDR_LEN];
    char     sname[DHCP_SNAME_LEN];
    char     file[DHCP_FILE_LEN];
    uint32_t magic_cookie;
    uint8_t  options[DHCP_MIN_OPTIONS];
};
#pragma pack(pop)

/* Структура вилучених параметрів конфігурації */
struct dhcp_parsed_info {
    uint32_t xid;
    uint32_t offered_ip;
    uint32_t server_ip;
    uint32_t subnet_mask;
    uint32_t router_ip;
    uint32_t dns_ip;
    uint32_t lease_time;
    uint8_t  msg_type;
    bool     valid;
};

/* Створення пакета DHCPDISCOVER */
size_t build_dhcp_discover(uint8_t *buffer, size_t max_len, const uint8_t mac[6], uint32_t xid) {
    if (!buffer || max_len < sizeof(struct dhcp_packet)) return 0;

    struct dhcp_packet *pkt = (struct dhcp_packet *)buffer;
    memset(pkt, 0, sizeof(struct dhcp_packet));

    pkt->op = 1;        /* BOOTREQUEST */
    pkt->htype = 1;     /* 10Mb Ethernet */
    pkt->hlen = 6;      /* MAC length */
    pkt->hops = 0;
    pkt->xid = htonl(xid);
    pkt->secs = htons(0);
    pkt->flags = htons(0x8000); /* Broadcast Flag: просимо широкомовну відповідь */
    pkt->ciaddr = 0;
    pkt->yiaddr = 0;
    pkt->siaddr = 0;
    pkt->giaddr = 0;
    memcpy(pkt->chaddr, mac, 6);
    pkt->magic_cookie = htonl(DHCP_MAGIC_COOKIE);

    size_t opt_idx = 0;

    /* Option 53: DHCP Message Type = DHCPDISCOVER */
    pkt->options[opt_idx++] = OPT_MSG_TYPE;
    pkt->options[opt_idx++] = 1;
    pkt->options[opt_idx++] = DHCP_DISCOVER;

    /* Option 61: Client Identifier (Hardware Type 1 = Ethernet + MAC) */
    pkt->options[opt_idx++] = OPT_CLIENT_ID;
    pkt->options[opt_idx++] = 7;
    pkt->options[opt_idx++] = 1;
    memcpy(&pkt->options[opt_idx], mac, 6);
    opt_idx += 6;

    /* Option 55: Parameter Request List */
    pkt->options[opt_idx++] = OPT_PARAM_REQ_LIST;
    pkt->options[opt_idx++] = 4;
    pkt->options[opt_idx++] = OPT_SUBNET_MASK;
    pkt->options[opt_idx++] = OPT_ROUTER;
    pkt->options[opt_idx++] = OPT_DNS_SERVER;
    pkt->options[opt_idx++] = OPT_DOMAIN_NAME;

    /* Option 255: End */
    pkt->options[opt_idx++] = OPT_END;

    return 240 + opt_idx;
}

/* Безпечний розбір отриманої відповіді */
bool parse_dhcp_response(const uint8_t *buffer, size_t len, const uint8_t mac[6],
                         uint32_t expected_xid, struct dhcp_parsed_info *out_info) {
    if (!buffer || !out_info || len < 240) return false;

    const struct dhcp_packet *pkt = (const struct dhcp_packet *)buffer;

    /* Верифікація інваріантів заголовка */
    if (pkt->op != 2) return false; /* Очікуємо BOOTREPLY */
    if (ntohl(pkt->xid) != expected_xid) return false;
    if (memcmp(pkt->chaddr, mac, 6) != 0) return false;
    if (ntohl(pkt->magic_cookie) != DHCP_MAGIC_COOKIE) return false;

    memset(out_info, 0, sizeof(*out_info));
    out_info->xid = ntohl(pkt->xid);
    out_info->offered_ip = ntohl(pkt->yiaddr);

    /* Ітеративний захищений обхід опцій TLV */
    size_t offset = 240;
    while (offset < len) {
        uint8_t opt_code = buffer[offset++];

        if (opt_code == OPT_PAD) continue;
        if (opt_code == OPT_END) break;

        if (offset >= len) return false;
        uint8_t opt_len = buffer[offset++];

        if (offset + opt_len > len) return false; /* Захист від виходу за межі */

        const uint8_t *val = &buffer[offset];

        switch (opt_code) {
            case OPT_MSG_TYPE:
                if (opt_len >= 1) out_info->msg_type = val[0];
                break;
            case OPT_SERVER_ID:
                if (opt_len >= 4) {
                    uint32_t raw;
                    memcpy(&raw, val, 4);
                    out_info->server_ip = ntohl(raw);
                }
                break;
            case OPT_SUBNET_MASK:
                if (opt_len >= 4) {
                    uint32_t raw;
                    memcpy(&raw, val, 4);
                    out_info->subnet_mask = ntohl(raw);
                }
                break;
            case OPT_ROUTER:
                if (opt_len >= 4) {
                    uint32_t raw;
                    memcpy(&raw, val, 4);
                    out_info->router_ip = ntohl(raw);
                }
                break;
            case OPT_DNS_SERVER:
                if (opt_len >= 4) {
                    uint32_t raw;
                    memcpy(&raw, val, 4);
                    out_info->dns_ip = ntohl(raw);
                }
                break;
            case OPT_LEASE_TIME:
                if (opt_len >= 4) {
                    uint32_t raw;
                    memcpy(&raw, val, 4);
                    out_info->lease_time = ntohl(raw);
                }
                break;
            default:
                break;
        }

        offset += opt_len;
    }

    out_info->valid = (out_info->msg_type == DHCP_OFFER || out_info->msg_type == DHCP_ACK);
    return out_info->valid;
}

int main(void) {
    uint8_t client_mac[6] = {0x00, 0x1A, 0x2B, 0x3C, 0x4D, 0x5E};
    uint32_t xid = 0x39A4F2B1;
    uint8_t tx_buf[DHCP_MAX_PACKET_LEN];

    size_t tx_len = build_dhcp_discover(tx_buf, sizeof(tx_buf), client_mac, xid);
    printf("Сформовано DHCPDISCOVER довжиною %zu байтів.\n", tx_len);

    uint8_t rx_buf[DHCP_MAX_PACKET_LEN];
    memset(rx_buf, 0, sizeof(rx_buf));
    struct dhcp_packet *resp = (struct dhcp_packet *)rx_buf;
    resp->op = 2;
    resp->htype = 1;
    resp->hlen = 6;
    resp->xid = htonl(xid);
    resp->yiaddr = htonl(0xC0A80169); /* 192.168.1.105 */
    memcpy(resp->chaddr, client_mac, 6);
    resp->magic_cookie = htonl(DHCP_MAGIC_COOKIE);

    size_t o = 240;
    rx_buf[o++] = OPT_MSG_TYPE; rx_buf[o++] = 1; rx_buf[o++] = DHCP_OFFER;
    rx_buf[o++] = OPT_SERVER_ID; rx_buf[o++] = 4;
    uint32_t s_ip = htonl(0xC0A80101); memcpy(&rx_buf[o], &s_ip, 4); o += 4;
    rx_buf[o++] = OPT_SUBNET_MASK; rx_buf[o++] = 4;
    uint32_t mask = htonl(0xFFFFFF00); memcpy(&rx_buf[o], &mask, 4); o += 4;
    rx_buf[o++] = OPT_LEASE_TIME; rx_buf[o++] = 4;
    uint32_t lease = htonl(86400); memcpy(&rx_buf[o], &lease, 4); o += 4;
    rx_buf[o++] = OPT_END;

    struct dhcp_parsed_info info;
    if (parse_dhcp_response(rx_buf, o, client_mac, xid, &info)) {
        struct in_addr ip_addr;
        ip_addr.s_addr = htonl(info.offered_ip);
        printf("Успішно розібрано DHCPOFFER:\n");
        printf("  Запропонована адреса: %s\n", inet_ntoa(ip_addr));
        printf("  Час оренди: %u секунд\n", info.lease_time);
    }

    return 0;
}
