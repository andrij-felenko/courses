#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <arpa/inet.h>

#define SSH_AGENT_FAILURE                 5
#define SSH_AGENT_SUCCESS                 6
#define SSH_AGENTC_REQUEST_IDENTITIES     11
#define SSH_AGENT_IDENTITIES_ANSWER       12
#define SSH_AGENTC_SIGN_REQUEST           13
#define SSH_AGENT_SIGN_RESPONSE           14

/* Гарантоване читання точної кількості байтів із сокета */
static int read_exact(int fd, void *buf, size_t len) {
    uint8_t *p = (uint8_t *)buf;
    size_t total = 0;
    while (total < len) {
        ssize_t r = read(fd, p + total, len - total);
        if (r < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        if (r == 0) return -1; /* Передчасне закриття з'єднання */
        total += (size_t)r;
    }
    return 0;
}

/* Гарантований запис точної кількості байтів у сокет */
static int write_exact(int fd, const void *buf, size_t len) {
    const uint8_t *p = (const uint8_t *)buf;
    size_t total = 0;
    while (total < len) {
        ssize_t w = write(fd, p + total, len - total);
        if (w < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        total += (size_t)w;
    }
    return 0;
}

/* Підключення до локального сокета агента через $SSH_AUTH_SOCK */
static int connect_agent(void) {
    const char *sock_path = getenv("SSH_AUTH_SOCK");
    if (!sock_path || strlen(sock_path) == 0) {
        fprintf(stderr, "Помилка: змінна $SSH_AUTH_SOCK не встановлена або порожня\n");
        return -1;
    }

    int fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0) {
        perror("socket");
        return -1;
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, sock_path, sizeof(addr.sun_path) - 1);

    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("connect");
        close(fd);
        return -1;
    }
    return fd;
}

int main(void) {
    int fd = connect_agent();
    if (fd < 0) return 1;

    /* 1. Формуємо запит SSH_AGENTC_REQUEST_IDENTITIES */
    uint32_t req_len = htonl(1);
    uint8_t req_type = SSH_AGENTC_REQUEST_IDENTITIES;
    if (write_exact(fd, &req_len, 4) < 0 || write_exact(fd, &req_type, 1) < 0) {
        perror("Помилка відправки запиту ключів");
        close(fd);
        return 1;
    }

    /* 2. Зчитуємо довжину відповіді */
    uint32_t resp_len_net;
    if (read_exact(fd, &resp_len_net, 4) < 0) {
        perror("Помилка читання довжини відповіді");
        close(fd);
        return 1;
    }
    uint32_t resp_len = ntohl(resp_len_net);
    if (resp_len < 1) {
        fprintf(stderr, "Некоректний розмір відповіді агента\n");
        close(fd);
        return 1;
    }

    uint8_t *resp_buf = malloc(resp_len);
    if (!resp_buf) {
        perror("malloc");
        close(fd);
        return 1;
    }

    if (read_exact(fd, resp_buf, resp_len) < 0) {
        perror("Помилка читання тіла відповіді");
        free(resp_buf);
        close(fd);
        return 1;
    }

    uint8_t resp_type = resp_buf[0];
    if (resp_type != SSH_AGENT_IDENTITIES_ANSWER) {
        fprintf(stderr, "Агент повернув помилку або неочікуваний тип: %u\n", resp_type);
        free(resp_buf);
        close(fd);
        return 1;
    }

    if (resp_len < 5) {
        fprintf(stderr, "Пошкоджена відповідь агента\n");
        free(resp_buf);
        close(fd);
        return 1;
    }

    uint32_t nkeys = 0;
    memcpy(&nkeys, resp_buf + 1, 4);
    nkeys = ntohl(nkeys);
    printf("Завантажено ключів в ssh-agent: %u\n", nkeys);

    size_t offset = 5;
    uint8_t *first_key_blob = NULL;
    uint32_t first_key_len = 0;

    for (uint32_t i = 0; i < nkeys; ++i) {
        if (offset + 4 > resp_len) break;
        uint32_t klen;
        memcpy(&klen, resp_buf + offset, 4);
        klen = ntohl(klen);
        offset += 4;

        if (offset + klen > resp_len) break;
        const uint8_t *key_data = resp_buf + offset;
        offset += klen;

        if (i == 0) {
            first_key_len = klen;
            first_key_blob = malloc(klen);
            if (first_key_blob) memcpy(first_key_blob, key_data, klen);
        }

        if (offset + 4 > resp_len) break;
        uint32_t clen;
        memcpy(&clen, resp_buf + offset, 4);
        clen = ntohl(clen);
        offset += 4;

        if (offset + clen > resp_len) break;
        char *comment = malloc(clen + 1);
        if (comment) {
            memcpy(comment, resp_buf + offset, clen);
            comment[clen] = '\0';
            printf("  [Ключ #%u] Довжина: %u байтів, Коментар: \"%s\"\n", i + 1, klen, comment);
            free(comment);
        }
        offset += clen;
    }

    /* 3. Якщо знайдено хоча б один ключ — виконуємо тестовий підпис */
    if (first_key_blob && first_key_len > 0) {
        const char *challenge = "challenge_session_auth_data_payload_2026";
        uint32_t challenge_len = (uint32_t)strlen(challenge);
        uint32_t flags = 0; /* Прапорці за замовчуванням */

        /* Розрахунок довжини пакета SSH_AGENTC_SIGN_REQUEST:
           1 байт (код) + 4 (key_len) + first_key_len + 4 (data_len) + challenge_len + 4 (flags) */
        uint32_t sign_req_payload_len = 1 + 4 + first_key_len + 4 + challenge_len + 4;
        uint8_t *sign_buf = malloc(4 + sign_req_payload_len);
        if (sign_buf) {
            uint32_t net_sign_len = htonl(sign_req_payload_len);
            memcpy(sign_buf, &net_sign_len, 4);
            sign_buf[4] = SSH_AGENTC_SIGN_REQUEST;

            size_t pos = 5;
            uint32_t net_klen = htonl(first_key_len);
            memcpy(sign_buf + pos, &net_klen, 4); pos += 4;
            memcpy(sign_buf + pos, first_key_blob, first_key_len); pos += first_key_len;

            uint32_t net_dlen = htonl(challenge_len);
            memcpy(sign_buf + pos, &net_dlen, 4); pos += 4;
            memcpy(sign_buf + pos, challenge, challenge_len); pos += challenge_len;

            uint32_t net_flags = htonl(flags);
            memcpy(sign_buf + pos, &net_flags, 4); pos += 4;

            if (write_exact(fd, sign_buf, 4 + sign_req_payload_len) == 0) {
                uint32_t sign_resp_len_net;
                if (read_exact(fd, &sign_resp_len_net, 4) == 0) {
                    uint32_t sign_resp_len = ntohl(sign_resp_len_net);
                    uint8_t *sign_resp_buf = malloc(sign_resp_len);
                    if (sign_resp_buf && read_exact(fd, sign_resp_buf, sign_resp_len) == 0) {
                        if (sign_resp_buf[0] == SSH_AGENT_SIGN_RESPONSE) {
                            uint32_t sig_blob_len;
                            memcpy(&sig_blob_len, sign_resp_buf + 1, 4);
                            sig_blob_len = ntohl(sig_blob_len);
                            printf("Успішний підпис виклику агентом! Розмір підпису: %u байтів\n", sig_blob_len);
                        } else {
                            printf("Агент відхилив запит на підпис (можливо, потрібне підтвердження ssh-add -c)\n");
                        }
                        free(sign_resp_buf);
                    }
                }
            }
            free(sign_buf);
        }
        free(first_key_blob);
    }

    free(resp_buf);
    close(fd);
    return 0;
}
