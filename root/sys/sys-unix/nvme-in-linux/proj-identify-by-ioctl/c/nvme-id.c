/* nvme-id.c — Identify і журнал ANA власними руками.
 *   cc -O2 -Wall -std=gnu11 -o nvme-id nvme-id.c
 *   sudo ./nvme-id /dev/nvme0 1
 */
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

enum { OP_GET_LOG = 0x02, OP_IDENTIFY = 0x06 };
enum { CNS_NS = 0x00, CNS_CTRL = 0x01 };
enum { LID_ANA = 0x0c };
#define NSID_ALL 0xffffffffu

/* Відповідь пристрою — little-endian і без C-вирівнювання: читаємо байтами. */
static uint16_t le16(const uint8_t *p) { return (uint16_t)(p[0] | p[1] << 8); }
static uint32_t le32(const uint8_t *p) { return le16(p) | (uint32_t)le16(p + 2) << 16; }
static uint64_t le64(const uint8_t *p) { return le32(p) | (uint64_t)le32(p + 4) << 32; }

/* Єдине місце, де розрізняють «не дійшло» і «дійшло, та контролер відмовив». */
static int admin(int fd, struct nvme_passthru_cmd *c, const char *what)
{
    int rc = ioctl(fd, NVME_IOCTL_ADMIN_CMD, c);

    if (rc < 0) {                       /* команду навіть не подали */
        fprintf(stderr, "%s: %s\n", what, strerror(errno));
        return -1;
    }
    if (rc > 0) {                       /* подали, відмовив контролер */
        unsigned st = (unsigned)rc;     /* біти: 14 DNR · 10:8 SCT · 7:0 SC */
        fprintf(stderr, "%s: статус NVMe SCT=%u SC=0x%02x%s\n", what,
                (st >> 8) & 0x7, st & 0xff, (st & 0x4000) ? ", DNR" : "");
        return -1;
    }
    return 0;
}

static int identify(int fd, uint32_t cns, uint32_t nsid, void *buf)
{
    struct nvme_passthru_cmd c = {
        .opcode   = OP_IDENTIFY,
        .nsid     = nsid,
        .addr     = (uint64_t)(uintptr_t)buf,
        .data_len = 4096,               /* Identify віддає рівно 4 КіБ */
        .cdw10    = cns,                /* CNS — молодший байт CDW10 */
    };
    return admin(fd, &c, "Identify");
}

/* Рядкові поля доповнені пробілами і НЕ завершені нулем. */
static void ascii(char *dst, const uint8_t *src, size_t n)
{
    memcpy(dst, src, n);
    while (n && (dst[n - 1] == ' ' || dst[n - 1] == '\0'))
        n--;
    dst[n] = '\0';
}

static const char *ana_state(unsigned s)
{
    switch (s) {
    case 1:    return "optimized";
    case 2:    return "non-optimized";
    case 3:    return "inaccessible";
    case 4:    return "persistent-loss";
    case 0xf:  return "change";
    default:   return "невідомий";
    }
}

int main(int argc, char **argv)
{
    const char *node = argc > 1 ? argv[1] : "/dev/nvme0";
    uint32_t nsid = argc > 2 ? (uint32_t)strtoul(argv[2], NULL, 0) : 1;
    size_t page = (size_t)sysconf(_SC_PAGESIZE);
    uint8_t *buf, *log;
    int fd;

    fd = open(node, O_RDONLY);
    if (fd < 0) {
        perror(node);
        return 1;
    }
    /* Вирівнювання на сторінку: інакше ядро мовчки скопіює буфер у свій. */
    if (posix_memalign((void **)&buf, page, 4096)) {
        perror("posix_memalign");
        return 1;
    }

    /* ── 1. Identify Controller, CNS 01h: NSID тут не потрібен ───────────── */
    if (identify(fd, CNS_CTRL, 0, buf))
        return 1;

    char mn[41], sn[21], fr[9], nqn[257];
    ascii(mn,  buf +  24, 40);
    ascii(sn,  buf +   4, 20);
    ascii(fr,  buf +  64,  8);
    ascii(nqn, buf + 768, 256);

    unsigned cmic      = buf[76];       /* біт 1 — багато контролерів, біт 3 — ANA */
    unsigned mdts      = buf[77];
    uint32_t nanagrpid = le32(buf + 348);
    uint32_t nn        = le32(buf + 516);
    uint32_t mnan      = le32(buf + 540);

    printf("модель       %s\n", mn);
    printf("серійний     %s\n", sn);
    printf("прошивка     %s\n", fr);
    printf("NQN          %s\n", nqn);
    printf("CMIC 0x%02x    ANA: %s · контролерів у підсистемі: %s\n", cmic,
           (cmic & 8) ? "є" : "нема", (cmic & 2) ? "багато" : "один");
    printf("MDTS %u · просторів імен %u · ANA-груп %u\n", mdts, nn, nanagrpid);

    /* ── 2. Identify Namespace, CNS 00h: а тут NSID обов'язковий ─────────── */
    if (identify(fd, CNS_NS, nsid, buf))
        return 1;

    unsigned flbas = buf[26];
    unsigned fmt   = (flbas & 0x0f) | ((flbas >> 5) & 0x03) << 4;
    const uint8_t *lbaf = buf + 128 + 4u * fmt;   /* дескриптор чинного формату */

    printf("\nпростір імен %u\n", nsid);
    printf("  блоків     %llu × %u Б, метаданих %u Б на блок\n",
           (unsigned long long)le64(buf), 1u << lbaf[2], (unsigned)le16(lbaf));
    printf("  ANAGRPID   %u\n", le32(buf + 92));
    printf("  NGUID      ");                       /* нулі = ідентифікатора немає */
    for (int i = 0; i < 16; i++) printf("%02x", buf[104 + i]);
    printf("\n  EUI-64     ");
    for (int i = 0; i <  8; i++) printf("%02x", buf[120 + i]);
    putchar('\n');

    /* ── 3. Сторінка журналу ANA, LID 0Ch ────────────────────────────────── */
    if (!(cmic & 8)) {
        printf("\nконтролер не повідомляє ANA — журналу в нього немає\n");
        return 0;
    }
    if (!mnan || mnan > nn) {
        fprintf(stderr, "MNAN=%u при NN=%u — числу не віримо\n", mnan, nn);
        return 1;
    }

    size_t len = 16 + (size_t)nanagrpid * 32 + (size_t)mnan * 4;
    if (posix_memalign((void **)&log, page, len)) {
        perror("posix_memalign");
        return 1;
    }
    uint32_t numd = (uint32_t)(len / 4) - 1;      /* довжина у двослів'ях, з нуля */
    struct nvme_passthru_cmd c = {
        .opcode   = OP_GET_LOG,
        .nsid     = NSID_ALL,
        .addr     = (uint64_t)(uintptr_t)log,
        .data_len = (uint32_t)len,
        .cdw10    = LID_ANA | (numd & 0xffff) << 16,
        .cdw11    = numd >> 16,
    };
    if (admin(fd, &c, "Get Log Page ANA"))
        return 1;

    unsigned ngrps = le16(log + 8);
    const uint8_t *d = log + 16, *end = log + len;

    printf("\nжурнал ANA: лічильник змін %llu, груп %u\n",
           (unsigned long long)le64(log), ngrps);

    for (unsigned i = 0; i < ngrps; i++) {
        /* Довжини прийшли з пристрою — рахуємо їх ворожими, поки не перевірені. */
        if (d + 32 > end)
            break;
        uint32_t nnsids = le32(d + 4);
        if (nnsids > (uint32_t)((end - d - 32) / 4))
            break;

        printf("  група %-4u %-16s простори імен:", le32(d), ana_state(d[16] & 0x0f));
        for (uint32_t j = 0; j < nnsids; j++)
            printf(" %u", le32(d + 32 + 4u * j));
        putchar('\n');
        d += 32 + 4u * nnsids;
    }
    return 0;
}
