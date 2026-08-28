#include <sys/socket.h>
#include <linux/if_alg.h>
#include <unistd.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

/* Виконання шифрування або дешифрування сектора XTS-AES через AF_ALG */
bool xts_af_alg_process(const uint8_t *key_512bit,
                        const uint8_t *tweak_128bit,
                        const uint8_t *in_data,
                        size_t len,
                        uint8_t *out_data,
                        uint32_t op_type) {
    if (!key_512bit || !tweak_128bit || !in_data || !out_data || len < 16) {
        return false;
    }

    struct sockaddr_alg sa = {
        .salg_family = AF_ALG,
        .salg_type = "skcipher",
        .salg_name = "xts(aes)"
    };

    /* 1. Створення керуючого сокета */
    int tfm_fd = socket(AF_ALG, SOCK_SEQPACKET, 0);
    if (tfm_fd < 0) {
        return false;
    }

    if (bind(tfm_fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        close(tfm_fd);
        return false;
    }

    /* 2. Завантаження 512-бітного подвійного ключа */
    if (setsockopt(tfm_fd, SOL_ALG, ALG_SET_KEY, key_512bit, 64) < 0) {
        close(tfm_fd);
        return false;
    }

    /* 3. Отримання робочого файлового дескриптора */
    int op_fd = accept(tfm_fd, NULL, 0);
    close(tfm_fd);
    if (op_fd < 0) {
        return false;
    }

    /* 4. Формування керуючого буфера з операцією та твіком */
    char cbuf[CMSG_SPACE(sizeof(uint32_t)) + CMSG_SPACE(sizeof(struct af_alg_iv) + 16)] = {0};
    struct msghdr msg = {
        .msg_control = cbuf,
        .msg_controllen = sizeof(cbuf)
    };

    /* Запис типу операції: ALG_OP_ENCRYPT або ALG_OP_DECRYPT */
    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_ALG;
    cmsg->cmsg_type = ALG_SET_OP;
    cmsg->cmsg_len = CMSG_LEN(sizeof(uint32_t));
    *((uint32_t *)CMSG_DATA(cmsg)) = op_type;

    /* Запис 128-бітного твіка як вектора ініціалізації (IV) */
    cmsg = CMSG_NXTHDR(&msg, cmsg);
    cmsg->cmsg_level = SOL_ALG;
    cmsg->cmsg_type = ALG_SET_IV;
    cmsg->cmsg_len = CMSG_LEN(sizeof(struct af_alg_iv) + 16);
    struct af_alg_iv *iv_hdr = (struct af_alg_iv *)CMSG_DATA(cmsg);
    iv_hdr->ivlen = 16;
    memcpy(iv_hdr->iv, tweak_128bit, 16);

    /* Передача вхідних даних через вектор вводу-виводу */
    struct iovec iov = {
        .iov_base = (void *)in_data,
        .iov_len = len
    };
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    if (sendmsg(op_fd, &msg, 0) < 0) {
        close(op_fd);
        return false;
    }

    /* 5. Читання результату */
    ssize_t n_read = read(op_fd, out_data, len);
    close(op_fd);

    return (n_read == (ssize_t)len);
}
