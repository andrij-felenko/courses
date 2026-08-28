/* fips_inspector.c — перевірка статусу FIPS ядра та тестування через AF_ALG */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>
#include <linux/if_alg.h>

#ifndef AF_ALG
#define AF_ALG 38
#endif
#ifndef SOL_ALG
#define SOL_ALG 279
#endif

/* Перевірка прапорця в procfs */
static int check_fips_sysctl(void) {
    int fd = open("/proc/sys/crypto/fips_enabled", O_RDONLY);
    if (fd < 0) {
        if (errno == ENOENT) {
            printf("[INFO] /proc/sys/crypto/fips_enabled відсутній (ядро без CONFIG_CRYPTO_FIPS)\n");
            return 0;
        }
        perror("[ERR] Не вдалося відкрити fips_enabled");
        return -1;
    }

    char buf[16];
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    if (n <= 0) return -1;
    buf[n] = '\0';

    int enabled = (buf[0] == '1');
    printf("[INFO] Статус ядра FIPS: %s (fips_enabled = %c)\n",
           enabled ? "АКТИВНИЙ" : "ВИМКНЕНО", buf[0]);
    return enabled;
}

/* Інспекція /proc/crypto на предмет провалених тестів */
static int audit_proc_crypto(void) {
    FILE *f = fopen("/proc/crypto", "r");
    if (!f) {
        perror("[ERR] Не вдалося відкрити /proc/crypto");
        return -1;
    }

    char line[256];
    char current_driver[128] = "unknown";
    int passed_count = 0, failed_count = 0;

    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "driver", 6) == 0) {
            char *colon = strchr(line, ':');
            if (colon) {
                sscanf(colon + 1, "%127s", current_driver);
            }
        } else if (strncmp(line, "selftest", 8) == 0) {
            char *colon = strchr(line, ':');
            if (colon) {
                char status[32];
                sscanf(colon + 1, "%31s", status);
                if (strcmp(status, "passed") == 0) {
                    passed_count++;
                } else if (strcmp(status, "failed") == 0) {
                    printf("[WARN] Алгоритм %s провалив KAT (selftest: failed)!\n", current_driver);
                    failed_count++;
                }
            }
        }
    }
    fclose(f);
    printf("[INFO] Реєстр /proc/crypto: перевірено %d алгоритмів, помилок: %d\n",
           passed_count, failed_count);
    return failed_count == 0 ? 0 : -1;
}

/* Тест дозволеного AES-CBC через AF_ALG */
static int test_af_alg_aes_cbc(void) {
    /* NIST SP 800-38A вектор: Key 128, Plaintext 16, IV 16 */
    static const unsigned char key[16] = {
        0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
        0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c
    };
    static const unsigned char iv[16] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f
    };
    static const unsigned char pt[16] = {
        0x6b, 0xc1, 0xbe, 0xe2, 0x2e, 0x40, 0x9f, 0x96,
        0xe9, 0x3d, 0x7e, 0x11, 0x73, 0x93, 0x17, 0x2a
    };
    static const unsigned char expected_ct[16] = {
        0x76, 0x49, 0xab, 0xac, 0x81, 0x19, 0xb2, 0x46,
        0xce, 0xe9, 0x8e, 0x9b, 0x12, 0xe9, 0x19, 0x7d
    };

    int sock = socket(AF_ALG, SOCK_SEQPACKET, 0);
    if (sock < 0) {
        perror("[ERR] socket(AF_ALG)");
        return -1;
    }

    struct sockaddr_alg sa = {
        .salg_family = AF_ALG,
        .salg_type = "skcipher",
        .salg_name = "cbc(aes)"
    };

    if (bind(sock, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("[ERR] bind(cbc(aes))");
        close(sock);
        return -1;
    }

    if (setsockopt(sock, SOL_ALG, ALG_SET_KEY, key, sizeof(key)) < 0) {
        perror("[ERR] setsockopt(ALG_SET_KEY)");
        close(sock);
        return -1;
    }

    int op_fd = accept(sock, NULL, 0);
    close(sock);
    if (op_fd < 0) {
        perror("[ERR] accept(op_fd)");
        return -1;
    }

    /* Підготовка структури керування для передачі IV та команди шифрування */
    char cbuf[CMSG_SPACE(sizeof(__u32)) + CMSG_SPACE(sizeof(struct af_alg_iv) + 16)];
    memset(cbuf, 0, sizeof(cbuf));

    struct msghdr msg = {0};
    struct iovec iov = { .iov_base = (void *)pt, .iov_len = sizeof(pt) };
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cbuf;
    msg.msg_controllen = sizeof(cbuf);

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_ALG;
    cmsg->cmsg_type = ALG_SET_OP;
    cmsg->cmsg_len = CMSG_LEN(sizeof(__u32));
    *(__u32 *)CMSG_DATA(cmsg) = ALG_OP_ENCRYPT;

    cmsg = CMSG_NXTHDR(&msg, cmsg);
    cmsg->cmsg_level = SOL_ALG;
    cmsg->cmsg_type = ALG_SET_IV;
    cmsg->cmsg_len = CMSG_LEN(sizeof(struct af_alg_iv) + 16);
    struct af_alg_iv *iv_msg = (struct af_alg_iv *)CMSG_DATA(cmsg);
    iv_msg->ivlen = 16;
    memcpy(iv_msg->iv, iv, 16);

    if (sendmsg(op_fd, &msg, 0) < 0) {
        perror("[ERR] sendmsg()");
        close(op_fd);
        return -1;
    }

    unsigned char ct[16];
    if (read(op_fd, ct, sizeof(ct)) != sizeof(ct)) {
        perror("[ERR] read(ct)");
        close(op_fd);
        return -1;
    }
    close(op_fd);

    if (memcmp(ct, expected_ct, sizeof(ct)) == 0) {
        printf("[OK] Тест шифрування cbc(aes) через ядро: ВЕКТОР ЗБІГСЯ\n");
        return 0;
    } else {
        printf("[FAIL] Шифротекст cbc(aes) не відповідає еталону!\n");
        return -1;
    }
}

/* Негативний тест спроби ініціалізації забороненого алгоритму */
static int test_disallowed_cipher(void) {
    int sock = socket(AF_ALG, SOCK_SEQPACKET, 0);
    if (sock < 0) return -1;

    struct sockaddr_alg sa = {
        .salg_family = AF_ALG,
        .salg_type = "hash",
        .salg_name = "md5"
    };

    int res = bind(sock, (struct sockaddr *)&sa, sizeof(sa));
    int saved_errno = errno;
    close(sock);

    if (res < 0 && saved_errno == ENOENT) {
        printf("[OK] Заборонений алгоритм md5 успішно заблоковано ядром (ENOENT)\n");
        return 0;
    } else if (res == 0) {
        printf("[WARN] Алгоритм md5 успішно створено (FIPS не заблокував алгоритм)\n");
        return 1;
    } else {
        printf("[INFO] bind(md5) повернув несподіваний статус: errno=%d\n", saved_errno);
        return -1;
    }
}

int main(void) {
    printf("=== Інспекція FIPS-режиму ядра Linux ===\n");
    int fips = check_fips_sysctl();
    audit_proc_crypto();
    test_af_alg_aes_cbc();
    test_disallowed_cipher();
    return 0;
}
