/* sensedecode.c — розбір сенс-даних SCSI й вирок, що його ухвалило б ядро.
   Складання: cc -O2 -Wall -Wextra -o sensedecode sensedecode.c
   Запуск:    ./sensedecode f0 00 03 00 00 20 03 0a 00 00 00 00 11 00 00 00 00 00
              ./sensedecode -s 28                       (статус без сенс-даних) */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ── 1. Нормалізація: розкладка, ключ, ASC, ASCQ ─────────────────────────── */

struct sense_hdr {
    uint8_t response_code;      /* 0x70…0x73 — уже без біта VALID           */
    uint8_t sense_key;          /* молодші 4 біти свого байта               */
    uint8_t asc, ascq;
    uint8_t additional_length;  /* байт 7; лише в описовій розкладці        */
};

static bool sense_valid(uint8_t rc)    { return (rc & 0x70) == 0x70; }
static bool sense_deferred(uint8_t rc) { return rc >= 0x70 && (rc & 1); }

static bool normalize_sense(const uint8_t *b, int len, struct sense_hdr *h)
{
    memset(h, 0, sizeof *h);
    if (!b || len <= 0)
        return false;

    h->response_code = b[0] & 0x7f;         /* старший біт — VALID, не код  */
    if (!sense_valid(h->response_code))
        return false;

    if (h->response_code >= 0x72) {                       /* описова        */
        if (len > 1) h->sense_key = b[1] & 0x0f;
        if (len > 2) h->asc  = b[2];
        if (len > 3) h->ascq = b[3];
        if (len > 7) h->additional_length = b[7];
    } else {                                              /* фіксована      */
        if (len > 2) h->sense_key = b[2] & 0x0f;
        if (len > 7) {
            int filled = b[7] + 8;          /* стільки пристрій заповнив    */
            if (filled < len)
                len = filled;               /* далі — сміття з минулого разу */
            if (len > 12) h->asc  = b[12];
            if (len > 13) h->ascq = b[13];
        }
    }
    return true;
}

/* ── 2. Пошук описувача заданого типу ───────────────────────────────────── */

static const uint8_t *desc_find(const uint8_t *b, int len, uint8_t type)
{
    if (len < 8 || b[7] == 0)
        return NULL;
    if ((b[0] & 0x7f) < 0x72 || (b[0] & 0x7f) > 0x73)
        return NULL;

    int left = b[7];                        /* стільки байтів обіцяє пристрій */
    if (left > len - 8)
        left = len - 8;                     /* але не більше, ніж нам дали    */

    const uint8_t *d = b + 8;
    for (int k = 0; k + 2 <= left; ) {
        int step = d[1] + 2;                /* тип + байт довжини + вміст     */
        if (k + step > left)
            break;                          /* описувач обрізано — стоп       */
        if (d[0] == type)
            return d;
        d += step;
        k += step;
    }
    return NULL;
}

/* ── 3. Поле «інформація» — номер збійного блока ─────────────────────────── */

static bool sense_info(const uint8_t *b, int len, uint64_t *out)
{
    if (len < 7)
        return false;

    switch (b[0] & 0x7f) {
    case 0x70:
    case 0x71:
        if (!(b[0] & 0x80))                 /* біт VALID знято — число ні про що */
            return false;
        *out = ((uint64_t)b[3] << 24) | ((uint64_t)b[4] << 16) |
               ((uint64_t)b[5] <<  8) |  (uint64_t)b[6];
        return true;
    case 0x72:
    case 0x73: {
        const uint8_t *d = desc_find(b, len, 0x00);   /* описувач «інформація» */
        if (!d || d[1] != 0x0a)
            return false;
        uint64_t v = 0;
        for (int i = 0; i < 8; i++)
            v = (v << 8) | d[4 + i];
        *out = v;
        return true;
    }
    default:
        return false;
    }
}

/* ── 4. Вирок ───────────────────────────────────────────────────────────── */

enum disposition { NEEDS_RETRY, ADD_TO_MLQUEUE, SUCCESS, FAILED };

static const char *verdict_name(enum disposition d)
{
    switch (d) {
    case NEEDS_RETRY:    return "NEEDS_RETRY    — повторити ту саму команду";
    case ADD_TO_MLQUEUE: return "ADD_TO_MLQUEUE — назад у чергу пристрою";
    case SUCCESS:        return "SUCCESS        — суд закінчено, віддати нагору";
    case FAILED:         return "FAILED         — до обробника помилок";
    }
    return "?";
}

/* спрощене scsi_check_sense(): без прапорців пристрою (allow_restart,
   retry_hwerror, expecting_cc_ua) — лише те, що видно із самих сенс-даних */
static enum disposition check_sense(const uint8_t *b, int len)
{
    struct sense_hdr h;

    if (!normalize_sense(b, len, &h))
        return FAILED;                      /* сенс-даних нема — хай збере EH */
    if (sense_deferred(h.response_code))
        return NEEDS_RETRY;                 /* провал не цієї команди         */

    switch (h.sense_key) {
    case 0x0:                               /* NO SENSE                       */
    case 0x1:  return SUCCESS;              /* RECOVERED ERROR                */
    case 0xb:                               /* ABORTED COMMAND                */
        return h.asc == 0x10 ? SUCCESS : NEEDS_RETRY;   /* 0x10 — захист даних */
    case 0x2:                               /* NOT READY                      */
    case 0x6:                               /* UNIT ATTENTION                 */
        if (h.asc == 0x04 && h.ascq == 0x01) return NEEDS_RETRY;  /* готується */
        if (h.asc == 0x04 && h.ascq == 0x02) return FAILED;       /* мотор     */
        if (h.asc == 0x3f && h.ascq == 0x0e) return NEEDS_RETRY;  /* нові LUN  */
        return SUCCESS;
    case 0x3:                               /* MEDIUM ERROR                   */
        if (h.asc == 0x11 || h.asc == 0x13 || h.asc == 0x14)
            return SUCCESS;                 /* безнадійно: нагору як помилка  */
        return NEEDS_RETRY;
    default:   return SUCCESS;              /* ILLEGAL REQUEST, DATA PROTECT… */
    }
}

static enum disposition decide(uint8_t status, const uint8_t *b, int len)
{
    switch (status) {
    case 0x08:                              /* BUSY                           */
    case 0x28: return ADD_TO_MLQUEUE;       /* TASK SET FULL                  */
    case 0x02: return check_sense(b, len);  /* CHECK CONDITION                */
    default:   return SUCCESS;              /* GOOD, RESERVATION CONFLICT…    */
    }
}

/* ── 5. Друк ────────────────────────────────────────────────────────────── */

static const char *key_name(uint8_t k)
{
    static const char *n[16] = {
        "NO SENSE", "RECOVERED ERROR", "NOT READY", "MEDIUM ERROR",
        "HARDWARE ERROR", "ILLEGAL REQUEST", "UNIT ATTENTION", "DATA PROTECT",
        "BLANK CHECK", "VENDOR SPECIFIC", "COPY ABORTED", "ABORTED COMMAND",
        "(зарезервовано)", "VOLUME OVERFLOW", "MISCOMPARE", "COMPLETED",
    };
    return n[k & 0x0f];
}

int main(int argc, char **argv)
{
    uint8_t buf[264];                       /* стеля розкладки: 8 + 255       */
    int len = 0, i = 1;
    uint8_t status = 0x02;                  /* типово CHECK CONDITION         */
    bool have_status = false;

    if (argc > 2 && strcmp(argv[1], "-s") == 0) {
        status = (uint8_t)strtoul(argv[2], NULL, 16);
        have_status = true;
        i = 3;
    }
    for (; i < argc && len < (int)sizeof buf; i++) {
        char *end;
        unsigned long v = strtoul(argv[i], &end, 16);
        if (*end != '\0' || v > 0xff) {
            fprintf(stderr, "не байт: %s\n", argv[i]);
            return 2;
        }
        buf[len++] = (uint8_t)v;
    }
    if (len == 0 && !have_status) {
        fprintf(stderr, "вжиток: %s [-s статус] <байти сенс-даних, 16-ково>\n",
                argv[0]);
        return 2;
    }

    struct sense_hdr h;
    printf("статус       : %02x\n", status);
    if (len == 0) {
        printf("сенс-дані    : не надіслано\n");
    } else if (!normalize_sense(buf, len, &h)) {
        printf("сенс-дані    : непридатні (перший байт %02x)\n", buf[0]);
    } else {
        uint64_t info;
        printf("формат       : %s%s\n",
               h.response_code >= 0x72 ? "описовий" : "фіксований",
               sense_deferred(h.response_code) ? ", ВІДКЛАДЕНА помилка" : "");
        printf("сенс-ключ    : %x  %s\n", h.sense_key, key_name(h.sense_key));
        printf("ASC/ASCQ     : %02x/%02x\n", h.asc, h.ascq);
        if (sense_info(buf, len, &info))
            printf("збійний блок : %llu\n", (unsigned long long)info);
        else
            printf("збійний блок : не вказано\n");
    }
    printf("вирок        : %s\n", verdict_name(decide(status, buf, len)));
    return 0;
}
