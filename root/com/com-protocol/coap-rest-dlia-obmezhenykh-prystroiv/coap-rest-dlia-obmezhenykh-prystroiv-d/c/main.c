#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define COAP_PORT 5683
#define BUFFER_SIZE 512

/* Обробка вхідного CoAP-пакета та формування двійкової відповіді */
size_t handle_coap_packet(const uint8_t *in, size_t in_len, uint8_t *out, size_t out_max) {
    if (in_len < 4) return 0;

    uint8_t version = (in[0] >> 6) & 0x03;
    uint8_t type = (in[0] >> 4) & 0x03;
    uint8_t tkl = in[0] & 0x0F;
    uint8_t code = in[1];
    uint16_t mid = ((uint16_t)in[2] << 8) | in[3];

    if (version != 1 || tkl > 8 || in_len < (size_t)(4 + tkl)) {
        return 0;
    }

    const uint8_t *token = &in[4];
    size_t offset = 4 + tkl;

    /* Витягуємо Uri-Path (опція 11) */
    char path[64] = {0};
    size_t path_len = 0;
    uint16_t cur_opt = 0;

    while (offset < in_len && in[offset] != 0xFF) {
        uint8_t h = in[offset++];
        uint16_t delta = (h >> 4) & 0x0F;
        uint16_t len = h & 0x0F;

        if (delta == 13) delta = (uint16_t)in[offset++] + 13;
        if (len == 13) len = (uint16_t)in[offset++] + 13;

        cur_opt += delta;
        if (cur_opt == 11 && len < sizeof(path) - path_len - 2) {
            if (path_len > 0) path[path_len++] = '/';
            memcpy(&path[path_len], &in[offset], len);
            path_len += len;
            path[path_len] = '\0';
        }
        offset += len;
    }

    const uint8_t *payload = NULL;
    size_t payload_len = 0;
    if (offset < in_len && in[offset] == 0xFF) {
        payload = &in[offset + 1];
        payload_len = in_len - offset - 1;
    }

    /* Формуємо попутний ACK (Type=2) */
    out[0] = (1 << 6) | (2 << 4) | (tkl & 0x0F);
    out[2] = (uint8_t)(mid >> 8);
    out[3] = (uint8_t)(mid & 0xFF);
    size_t resp_len = 4;

    if (tkl > 0) {
        memcpy(&out[resp_len], token, tkl);
        resp_len += tkl;
    }

    /* Маршрутизація ресурсів */
    if (code == 1 && strcmp(path, "temp") == 0) {
        /* GET /temp -> 2.05 Content */
        out[1] = (2 << 5) | 5; /* 2.05 */
        out[resp_len++] = (12 << 4) | 0; /* Option 12 (Content-Format), len 0 -> text/plain */
        out[resp_len++] = 0xFF; /* Payload marker */

        const char *data = "23.5 C";
        size_t dlen = strlen(data);
        memcpy(&out[resp_len], data, dlen);
        resp_len += dlen;
    } else if (code == 3 && strcmp(path, "led") == 0) {
        /* PUT /led -> 2.04 Changed */
        out[1] = (2 << 5) | 4; /* 2.04 Changed */
        if (payload_len > 0 && payload[0] == '1') {
            /* Світлодіод увімкнено */
        }
    } else {
        /* 4.04 Not Found */
        out[1] = (4 << 5) | 4;
    }

    return resp_len;
}

int main(void) {
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) return 1;

    struct sockaddr_in servaddr, cliaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = INADDR_ANY;
    servaddr.sin_port = htons(COAP_PORT);

    if (bind(sockfd, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
        close(sockfd);
        return 1;
    }

    uint8_t rx_buf[BUFFER_SIZE];
    uint8_t tx_buf[BUFFER_SIZE];

    while (1) {
        socklen_t clen = sizeof(cliaddr);
        ssize_t n = recvfrom(sockfd, rx_buf, sizeof(rx_buf), 0, (struct sockaddr *)&cliaddr, &clen);
        if (n > 0) {
            size_t tx_len = handle_coap_packet(rx_buf, (size_t)n, tx_buf, sizeof(tx_buf));
            if (tx_len > 0) {
                sendto(sockfd, tx_buf, tx_len, 0, (const struct sockaddr *)&cliaddr, clen);
            }
        }
    }

    close(sockfd);
    return 0;
}
