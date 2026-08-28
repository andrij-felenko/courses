/* ana_dump.c — зчитування та розбір журналу NVMe ANA мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

#define NVME_LOG_ANA_LID 0x0c
#define BUFFER_SIZE 4096

/* Двійкові структури специфікації NVMe 1.4 / 2.0 */
struct nvme_ana_group_desc {
    uint32_t grpid;
    uint32_t nnsids;
    uint64_t chgcnt;
    uint8_t  state;
    uint8_t  rsvd17[15];
    uint32_t nsids[];
};

struct nvme_ana_log {
    uint64_t chgcnt;
    uint16_t ngrps;
    uint8_t  rsvd10[6];
};

static const char *ana_state_to_str(uint8_t state) {
    switch (state & 0x0f) {
        case 0x01: return "OPTIMIZED (AO)";
        case 0x02: return "NON-OPTIMIZED (ANO)";
        case 0x03: return "INACCESSIBLE (AI)";
        case 0x04: return "PERSISTENT LOSS (PL)";
        case 0x0f: return "CHANGE STATE (TRANSITION)";
        default:   return "UNKNOWN";
    }
}

int main(int argc, char *argv[]) {
    const char *dev_path = (argc > 1) ? argv[1] : "/dev/nvme0";
    int fd = open(dev_path, O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття NVMe пристрою");
        return 1;
    }

    uint8_t buffer[BUFFER_SIZE];
    memset(buffer, 0, sizeof(buffer));

    uint32_t numd = (sizeof(buffer) / 4) - 1;
    struct nvme_passthru_cmd cmd;
    memset(&cmd, 0, sizeof(cmd));

    cmd.opcode       = 0x02; /* Get Log Page */
    cmd.nsid         = 0xFFFFFFFF;
    cmd.addr         = (uintptr_t)buffer;
    cmd.data_len     = sizeof(buffer);
    cmd.cdw10        = ((numd & 0xFFFF) << 16) | NVME_LOG_ANA_LID;
    cmd.cdw11        = (numd >> 16) & 0xFFFF;
    cmd.timeout_ms   = 5000;

    if (ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd) < 0) {
        perror("Помилка виконання NVME_IOCTL_ADMIN_CMD");
        close(fd);
        return 1;
    }

    struct nvme_ana_log *log = (struct nvme_ana_log *)buffer;
    printf("=== ЖУРНАЛ СТАНІВ NVMe ANA (%s) ===\n", dev_path);
    printf("Глобальний лічильник змін (Change Counter): %lu\n", (unsigned long)log->chgcnt);
    printf("Кількість груп ANA (Number of Groups):     %u\n\n", (unsigned int)log->ngrps);

    uint8_t *ptr = buffer + sizeof(struct nvme_ana_log);
    uint8_t *end = buffer + sizeof(buffer);

    for (uint16_t i = 0; i < log->ngrps; i++) {
        if (ptr + sizeof(struct nvme_ana_group_desc) > end) {
            fprintf(stderr, "Попередження: буфер переповнено, журнал усічено.\n");
            break;
        }

        struct nvme_ana_group_desc *desc = (struct nvme_ana_group_desc *)ptr;
        size_t desc_size = sizeof(struct nvme_ana_group_desc) + (desc->nnsids * sizeof(uint32_t));

        if (ptr + desc_size > end) {
            fprintf(stderr, "Попередження: неповний дескриптор групи %u.\n", desc->grpid);
            break;
        }

        printf("Група ANA ID: %u\n", desc->grpid);
        printf("  Стан маршруту:       %s (0x%02X)\n", ana_state_to_str(desc->state), desc->state);
        printf("  Лічильник змін:      %lu\n", (unsigned long)desc->chgcnt);
        printf("  Кількість томів:     %u\n", desc->nnsids);
        printf("  Прив'язані томи NSID: ");

        for (uint32_t n = 0; n < desc->nnsids; n++) {
            printf("%u%s", desc->nsids[n], (n + 1 < desc->nnsids) ? ", " : "");
        }
        printf("\n\n");

        ptr += desc_size;
    }

    close(fd);
    return 0;
}
