#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/random.h>
#include <sys/types.h>
#include <linux/types.h>

/* Локальне оголошення системних структур для AMD SEV-SNP */
#ifndef SNP_GET_REPORT

struct snp_report_req {
    __u8 user_data[64];
    __u32 vmpl;
    __u8 rsvd[28];
};

struct snp_report_resp {
    __u8 data[4000];
};

struct snp_guest_request_ioctl {
    __u8 msg_version;
    __u64 req_data;
    __u64 resp_data;
    __u64 fw_error;
};

#define SNP_GUEST_REQ_IOC_TYPE 'S'
#define SNP_GET_REPORT _IOWR(SNP_GUEST_REQ_IOC_TYPE, 0x0, struct snp_guest_request_ioctl)

#endif

/* Функція генерації криптографічно стійкого nonce */
static int generate_secure_nonce(unsigned char nonce[64]) {
    ssize_t ret = getrandom(nonce, 64, 0);
    if (ret != 64) {
        perror("Помилка генерації випадкових даних через getrandom()");
        return -1;
    }
    return 0;
}

/* Функція звернення до пристрою AMD SEV-SNP */
static int fetch_sev_snp_report(const unsigned char nonce[64], unsigned char out_measurement[48]) {
    int fd = open("/dev/sev-guest", O_RDWR);
    if (fd < 0) {
        perror("Не вдалося відкрити символьний пристрій /dev/sev-guest");
        return -1;
    }

    struct snp_report_req req;
    struct snp_report_resp resp;
    struct snp_guest_request_ioctl ioctl_req;

    /* Явне занулення пам'яті для запобігання витоку даних зі стака */
    memset(&req, 0, sizeof(req));
    memset(&resp, 0, sizeof(resp));
    memset(&ioctl_req, 0, sizeof(ioctl_req));

    memcpy(req.user_data, nonce, 64);
    req.vmpl = 0; /* Виклик від імені найвищого рівня привілеїв ВМ VMPL0 */

    ioctl_req.msg_version = 1;
    ioctl_req.req_data = (unsigned long)&req;
    ioctl_req.resp_data = (unsigned long)&resp;

    printf("[C-Driver] Надсилання ioctl(SNP_GET_REPORT) до апаратного процесора ASP...\n");
    if (ioctl(fd, SNP_GET_REPORT, &ioctl_req) < 0) {
        perror("[C-Driver] Помилка системного виклику ioctl");
        if (ioctl_req.fw_error != 0) {
            fprintf(stderr, "[C-Driver] Апаратна відмова прошивки ASP. Код: 0x%llx\n", 
                    (unsigned long long)ioctl_req.fw_error);
        }
        close(fd);
        return -1;
    }

    /* 
     * Хеш виміру SHA-384 (Launch Measurement Digest) розташовано за зсувом 0x90 
     * у структурі snp_attestation_report (довжина 48 байтів)
     */
    memcpy(out_measurement, &resp.data[0x90], 48);

    /* Перевірка ехо-відповіді user_data у звіті (зсув 0x50) */
    if (memcmp(&resp.data[0x50], nonce, 64) != 0) {
        fprintf(stderr, "[C-Driver] КРИТИЧНА ПОМИЛКА: Nonce у звіті не збігається з переданим!\n");
        close(fd);
        return -1;
    }

    close(fd);
    return 0;
}

int main(void) {
    unsigned char nonce[64];
    unsigned char measurement[48];

    printf("=== Демон атестації AMD SEV-SNP (Мова C) ===\n");

    if (generate_secure_nonce(nonce) != 0) {
        return EXIT_FAILURE;
    }

    if (fetch_sev_snp_report(nonce, measurement) == 0) {
        printf("Успішно отримано та валідовано SHA-384 Launch Digest ВМ:\n");
        for (int i = 0; i < 48; i++) {
            printf("%02x", measurement[i]);
        }
        printf("\n");
        return EXIT_SUCCESS;
    } else {
        fprintf(stderr, "Процедура атестації завершилася помилкою.\n");
        return EXIT_FAILURE;
    }
}
