/* askdrive.c — три питання до носія одним наскрізним каналом.
   Складання: cc -O2 -Wall -Wextra -o askdrive askdrive.c
   Запуск:    sudo ./askdrive /dev/sda      (вузол ЦІЛОГО диска, не розділу) */
#include <errno.h>
#include <fcntl.h>
#include <scsi/sg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

enum { INQ_LEN = 96, ID_LEN = 512, SENSE_MAX = 64 };

struct reply {
    uint8_t  status;              /* байт стану від пристрою                */
    uint8_t  host;                /* вирок контролера-ініціатора            */
    uint8_t  sense[SENSE_MAX];
    unsigned sense_len;
    unsigned got;                 /* скільки байтів пристрій справді віддав */
    uint8_t  key, asc, ascq;      /* розібраний звіт про відмову            */
    uint8_t  ata[14];             /* описовий блок ATA Status Return (09h)  */
    int      have_ata;
};

/* Розкласти сенс-дані обох форматів і витягти описовий блок 09h. */
static void parse_sense(struct reply *r)
{
    const uint8_t *s = r->sense;
    unsigned code;

    if (r->sense_len < 8) return;                 /* звіту фактично немає */
    code = s[0] & 0x7F;

    if (code == 0x72 || code == 0x73) {           /* описовий формат */
        unsigned addl = s[7], off;
        r->key = s[1] & 0x0F; r->asc = s[2]; r->ascq = s[3];
        if (8u + addl > r->sense_len)             /* буфер виявився замалим */
            addl = r->sense_len - 8u;
        for (off = 8; off + 2u <= 8u + addl; off += (unsigned)s[off + 1] + 2u) {
            if (s[off] == 0x09 && s[off + 1] >= 12 && off + 14u <= r->sense_len) {
                memcpy(r->ata, s + off, 14);
                r->have_ata = 1;
            }
        }
    } else if (code == 0x70 || code == 0x71) {    /* сталий формат */
        r->key = s[2] & 0x0F;
        if (r->sense_len > 13) { r->asc = s[12]; r->ascq = s[13]; }
    }
}

/* Надіслати команду й розсудити результат.
    0 — пристрій виконав команду;
    1 — пристрій відповів ненульовим станом (звіт розібрано в r);
   -1 — до пристрою не дійшло: r->host ≠ 0 — дорога, інакше дивись errno. */
static int ask(int fd, const uint8_t *cdb, unsigned cdb_len,
               void *data, unsigned data_len, struct reply *r)
{
    sg_io_hdr_t io;

    memset(r, 0, sizeof *r);
    memset(&io, 0, sizeof io);
    io.interface_id    = 'S';
    io.dxfer_direction = data_len ? SG_DXFER_FROM_DEV : SG_DXFER_NONE;
    io.cmd_len         = (unsigned char)cdb_len;
    io.cmdp            = (unsigned char *)cdb;    /* ядро цих байтів не змінює */
    io.dxferp          = data;
    io.dxfer_len       = data_len;
    io.sbp             = r->sense;
    io.mx_sb_len       = SENSE_MAX;
    io.timeout         = 10000;                   /* мілісекунд */

    if (ioctl(fd, SG_IO, &io) < 0)                /* конверт не поїхав */
        return -1;

    r->status    = io.status;
    r->host      = io.host_status;
    r->sense_len = io.sb_len_wr;
    r->got       = io.resid > 0 ? data_len - (unsigned)io.resid : data_len;
    if (r->sense_len) parse_sense(r);

    if (io.host_status) return -1;                /* дорога, а не пристрій */
    return io.status ? 1 : 0;
}

static void complain(const char *what, const struct reply *r)
{
    if (r->host)
        fprintf(stderr, "%s: команда не доїхала, host_status = %02x\n", what, r->host);
    else if (r->status)
        fprintf(stderr, "%s: пристрій відмовив: стан %02x, ключ %x, ASC/ASCQ %02x/%02x\n",
                what, r->status, r->key, r->asc, r->ascq);
    else
        fprintf(stderr, "%s: %s\n", what, strerror(errno));
}

/* Поле INQUIRY доповнене пробілами праворуч. */
static void scsi_field(const uint8_t *p, int len, char *out)
{
    memcpy(out, p, (size_t)len);
    out[len] = '\0';
    while (len > 0 && out[len - 1] == ' ') out[--len] = '\0';
}

/* Рядок з IDENTIFY DEVICE: у кожному 16-бітному слові байти переставлені. */
static void ata_string(const uint8_t *id, int first_word, int nwords, char *out)
{
    int n = nwords * 2, i;
    for (i = 0; i < n; i += 2) {
        out[i]     = (char)id[first_word * 2 + i + 1];
        out[i + 1] = (char)id[first_word * 2 + i];
    }
    out[n] = '\0';
    while (n > 0 && out[n - 1] == ' ') out[--n] = '\0';
}

int main(int argc, char **argv)
{
    uint8_t inq[INQ_LEN], id[ID_LEN];
    struct reply r;
    char s[64];
    int fd, ata_ok = 0;

    if (argc != 2) { fprintf(stderr, "вжиток: %s /dev/sdX\n", argv[0]); return 2; }
    fd = open(argv[1], O_RDONLY | O_NONBLOCK);    /* читання досить для питань */
    if (fd < 0) { perror(argv[1]); return 1; }

    /* ── Крок 1: INQUIRY — рідною мовою каналу ─────────────────────────── */
    {
        const uint8_t cdb[6] = { 0x12, 0, 0, 0, INQ_LEN, 0 };
        if (ask(fd, cdb, sizeof cdb, inq, sizeof inq, &r) != 0) {
            complain("INQUIRY", &r);
            return 1;
        }
        if (r.got < 36) {                          /* коротша відповідь — не наша */
            fprintf(stderr, "INQUIRY: віддано лише %u байтів\n", r.got);
            return 1;
        }
        printf("тип пристрою : %02x\n", inq[0] & 0x1F);
        scsi_field(inq +  8,  8, s); printf("виробник     : %s\n", s);
        scsi_field(inq + 16, 16, s); printf("виріб        : %s\n", s);
        scsi_field(inq + 32,  4, s); printf("версія       : %s\n", s);
    }

    /* ── Крок 2: ATA PASS-THROUGH (16) з IDENTIFY DEVICE ───────────────── */
    {
        uint8_t cdb[16] = { 0 };
        cdb[0]  = 0x85;        /* ATA PASS-THROUGH (16)                       */
        cdb[1]  = 4 << 1;      /* PROTOCOL = 4 (PIO Data-In), EXTEND = 0      */
        cdb[2]  = 0x0E;        /* T_DIR=1 з пристрою, BYT_BLOK=1, T_LENGTH=2  */
        cdb[6]  = 1;           /* SECTOR_COUNT = 1 сектор                     */
        cdb[14] = 0xEC;        /* COMMAND = ECh, IDENTIFY DEVICE              */

        if (ask(fd, cdb, sizeof cdb, id, sizeof id, &r) != 0) {
            complain("IDENTIFY DEVICE", &r);
            fprintf(stderr, "  (пристрій не розуміє ATA PASS-THROUGH — далі не йдемо)\n");
        } else {
            unsigned rpm = (unsigned)id[217 * 2] | ((unsigned)id[217 * 2 + 1] << 8);
            ata_ok = 1;
            ata_string(id, 27, 20, s); printf("модель ATA   : %s\n", s);
            ata_string(id, 10, 10, s); printf("серійний     : %s\n", s);
            ata_string(id, 23,  4, s); printf("прошивка     : %s\n", s);
            if (rpm == 1)
                printf("носій        : без обертових частин\n");
            else if (rpm >= 0x0401 && rpm <= 0xFFFE)
                printf("носій        : %u об/хв\n", rpm);
        }
    }

    /* ── Крок 3: SMART RETURN STATUS із CK_COND ────────────────────────── */
    if (ata_ok) {
        uint8_t cdb[16] = { 0 };
        cdb[0]  = 0x85;
        cdb[1]  = 3 << 1;      /* PROTOCOL = 3 (Non-data)                     */
        cdb[2]  = 0x20;        /* CK_COND = 1; даних немає, T_LENGTH = 0      */
        cdb[4]  = 0xDA;        /* FEATURES = DAh, SMART RETURN STATUS         */
        cdb[10] = 0x4F;        /* LBA_MID  = 4Fh — підпис SMART               */
        cdb[12] = 0xC2;        /* LBA_HIGH = C2h — підпис SMART               */
        cdb[14] = 0xB0;        /* COMMAND  = B0h, SMART                       */

        /* Тут «1» — очікуваний результат: CK_COND навмисно дає CHECK CONDITION. */
        if (ask(fd, cdb, sizeof cdb, NULL, 0, &r) < 0 || !r.have_ata) {
            complain("SMART RETURN STATUS", &r);
            if (r.status && !r.have_ata)
                fprintf(stderr, "  (регістрів не повернуто: CK_COND не спрацював)\n");
        } else {
            uint8_t err = r.ata[3], mid = r.ata[9], high = r.ata[11], st = r.ata[13];
            printf("регістри     : STATUS %02x  ERROR %02x  LBA_MID %02x  LBA_HIGH %02x\n",
                   st, err, mid, high);
            if (st & 0x01)                                  /* біт ERR у STATUS */
                printf("SMART        : команду відхилено самим диском\n");
            else if (mid == 0x4F && high == 0xC2)
                printf("SMART        : пороги не перевищено\n");
            else if (mid == 0xF4 && high == 0x2C)
                printf("SMART        : ПОРІГ ПЕРЕВИЩЕНО — диск попереджає про відмову\n");
            else
                printf("SMART        : незрозуміла пара %02x/%02x\n", mid, high);
        }
    }

    close(fd);
    return 0;
}
