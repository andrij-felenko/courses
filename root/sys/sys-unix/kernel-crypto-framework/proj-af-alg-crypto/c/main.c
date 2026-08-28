#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/if_alg.h>
#include <errno.h>

#ifndef SOL_ALG
#define SOL_ALG 279
#endif

int calculate_sha256_kernel(const unsigned char *data, size_t len, unsigned char hash_out[32])
{
    int tfm_fd = -1;
    int op_fd = -1;
    ssize_t ret;
    struct sockaddr_alg sa = {
        .salg_family = AF_ALG,
        .salg_type = "hash",
        .salg_name = "sha256"
    };

    tfm_fd = socket(AF_ALG, SOCK_SEQPACKET, 0);
    if (tfm_fd < 0) {
        perror("socket(AF_ALG)");
        return -1;
    }

    if (bind(tfm_fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("bind(AF_ALG)");
        close(tfm_fd);
        return -1;
    }

    op_fd = accept(tfm_fd, NULL, 0);
    if (op_fd < 0) {
        perror("accept(AF_ALG)");
        close(tfm_fd);
        return -1;
    }

    ret = write(op_fd, data, len);
    if (ret != (ssize_t)len) {
        perror("write(op_fd)");
        close(op_fd);
        close(tfm_fd);
        return -1;
    }

    ret = read(op_fd, hash_out, 32);
    if (ret != 32) {
        perror("read(op_fd)");
        close(op_fd);
        close(tfm_fd);
        return -1;
    }

    close(op_fd);
    close(tfm_fd);
    return 0;
}

int main(void)
{
    const char *msg = "Hello, Kernel Crypto API!";
    unsigned char hash[32];
    
    if (calculate_sha256_kernel((const unsigned char *)msg, strlen(msg), hash) == 0) {
        printf("SHA-256 дайджест: ");
        for (int i = 0; i < 32; i++) {
            printf("%02x", hash[i]);
        }
        printf("\n");
    }
    return 0;
}
