#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/xfrm.h>

/* Допоміжна функція додавання атрибута rtattr у буфер */
static void add_rtattr(struct nlmsghdr *n, int maxlen, int type, const void *data, int alen) {
    int len = RTA_LENGTH(alen);
    if (NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len) > maxlen) {
        fprintf(stderr, "Помилка: переповнення буфера атрибутів Netlink\n");
        exit(EXIT_FAILURE);
    }
    struct rtattr *rta = (struct rtattr *)(((char *)n) + NLMSG_ALIGN(n->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = len;
    memcpy(RTA_DATA(rta), data, alen);
    n->nlmsg_len = NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len);
}

int main(void) {
    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_XFRM);
    if (fd < 0) {
        perror("socket(AF_NETLINK)");
        return 1;
    }

    /* Буфер для надсилання Netlink-повідомлення XFRM_MSG_NEWSA */
    char buf[1024];
    memset(buf, 0, sizeof(buf));

    struct nlmsghdr *n = (struct nlmsghdr *)buf;
    n->nlmsg_len = NLMSG_LENGTH(sizeof(struct xfrm_usersa_info));
    n->nlmsg_type = XFRM_MSG_NEWSA;
    n->nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
    n->nlmsg_seq = 1;
    n->nlmsg_pid = getpid();

    struct xfrm_usersa_info *sa = (struct xfrm_usersa_info *)NLMSG_DATA(n);

    /* Конфігурація ідентифікатора SA */
    inet_pton(AF_INET, "192.168.1.1", &sa->saddr.a4);
    inet_pton(AF_INET, "192.168.2.1", &sa->id.daddr.a4);
    sa->id.spi = htonl(0x1000);
    sa->id.proto = IPPROTO_ESP;
    sa->family = AF_INET;
    sa->mode = XFRM_MODE_TUNNEL;
    sa->reqid = 100;

    /* Селектор трафіку */
    inet_pton(AF_INET, "10.0.1.0", &sa->sel.saddr.a4);
    inet_pton(AF_INET, "10.0.2.0", &sa->sel.daddr.a4);
    sa->sel.prefixlen_s = 24;
    sa->sel.prefixlen_d = 24;
    sa->sel.family = AF_INET;

    /* Додавання шифру AES-CBC (128 біт = 16 байтів ключа) */
    char crypt_buf[sizeof(struct xfrm_algo) + 16];
    struct xfrm_algo *alg_crypt = (struct xfrm_algo *)crypt_buf;
    strncpy(alg_crypt->alg_name, "cbc(aes)", sizeof(alg_crypt->alg_name));
    alg_crypt->alg_key_len = 128; /* у бітах */
    memcpy(alg_crypt->alg_key, "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10", 16);
    add_rtattr(n, sizeof(buf), XFRMA_ALG_CRYPT, alg_crypt, sizeof(crypt_buf));

    /* Додавання HMAC-SHA256 (256 біт = 32 байти ключа) */
    char auth_buf[sizeof(struct xfrm_algo) + 32];
    struct xfrm_algo *alg_auth = (struct xfrm_algo *)auth_buf;
    strncpy(alg_auth->alg_name, "hmac(sha256)", sizeof(alg_auth->alg_name));
    alg_auth->alg_key_len = 256; /* у бітах */
    memset(alg_auth->alg_key, 0xAA, 32);
    add_rtattr(n, sizeof(buf), XFRMA_ALG_AUTH, alg_auth, sizeof(auth_buf));

    /* Надсилання запиту до ядра */
    struct sockaddr_nl sa_dst;
    memset(&sa_dst, 0, sizeof(sa_dst));
    sa_dst.nl_family = AF_NETLINK;

    if (sendto(fd, n, n->nlmsg_len, 0, (struct sockaddr *)&sa_dst, sizeof(sa_dst)) < 0) {
        perror("sendto(NETLINK_XFRM)");
        close(fd);
        return 1;
    }

    /* Отримання підтвердження від ядра (NLMSG_ERROR) */
    char resp_buf[512];
    ssize_t len = recv(fd, resp_buf, sizeof(resp_buf), 0);
    if (len < 0) {
        perror("recv()");
        close(fd);
        return 1;
    }

    struct nlmsghdr *resp = (struct nlmsghdr *)resp_buf;
    if (resp->nlmsg_type == NLMSG_ERROR) {
        struct nlmsgerr *err = (struct nlmsgerr *)NLMSG_DATA(resp);
        if (err->error == 0) {
            printf("Успіх: XFRM SA з SPI 0x1000 успішно зареєстровано в ядрі.\n");
        } else {
            fprintf(stderr, "Помилка ядра Netlink: %s (%d)\n", strerror(-err->error), err->error);
            close(fd);
            return 1;
        }
    }

    close(fd);
    return 0;
}
