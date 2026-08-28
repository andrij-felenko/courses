#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/if_alg.h>

int af_alg_hmac_sha256(const unsigned char *key, size_t key_len,
                       const unsigned char *msg, size_t msg_len,
                       unsigned char *out_tag, size_t out_tag_len) {
    int tfm_fd = -1;
    int op_fd = -1;
    int success = 0;

    struct sockaddr_alg sa = {
        .salg_family = AF_ALG,
        .salg_type   = "hash",
        .salg_name   = "hmac(sha256)"
    };

    tfm_fd = socket(AF_ALG, SOCK_SEQPACKET, 0);
    if (tfm_fd < 0) return 0;

    if (bind(tfm_fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) goto out;
    if (setsockopt(tfm_fd, SOL_ALG, ALG_SET_KEY, key, key_len) < 0) goto out;

    op_fd = accept(tfm_fd, NULL, 0);
    if (op_fd < 0) goto out;

    if (write(op_fd, msg, msg_len) != (ssize_t)msg_len) goto out;
    if (read(op_fd, out_tag, out_tag_len) != (ssize_t)out_tag_len) goto out;

    success = 1;

out:
    if (op_fd >= 0) close(op_fd);
    if (tfm_fd >= 0) close(tfm_fd);
    return success;
}
