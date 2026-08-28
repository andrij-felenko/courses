#define _DEFAULT_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <endian.h>
#include <time.h>
#include <errno.h>

struct tz_header {
    char magic[4];
    char version;
    char reserved[15];
    uint32_t ttisgmtcnt;
    uint32_t ttisstdcnt;
    uint32_t leapcnt;
    uint32_t timecnt;
    uint32_t typecnt;
    uint32_t charcnt;
};

struct ttinfo {
    int32_t utoff;      /* Зміщення від UTC у секундах */
    uint8_t isdst;      /* 0 — зимовий / стандартний, 1 — літній DST */
    uint8_t desigidx;   /* Зсув назви абревіатури в таблиці символів */
};

struct parsed_tz {
    uint32_t timecnt;
    uint32_t typecnt;
    int64_t *transitions;
    uint8_t *type_indices;
    struct ttinfo *types;
    char *char_table;
    char posix_tz[128];
};

static int read_header(FILE *f, struct tz_header *hdr) {
    if (fread(hdr, sizeof(struct tz_header), 1, f) != 1) {
        return -1;
    }
    if (memcmp(hdr->magic, "TZif", 4) != 0) {
        return -2;
    }
    hdr->ttisgmtcnt = be32toh(hdr->ttisgmtcnt);
    hdr->ttisstdcnt = be32toh(hdr->ttisstdcnt);
    hdr->leapcnt    = be32toh(hdr->leapcnt);
    hdr->timecnt    = be32toh(hdr->timecnt);
    hdr->typecnt    = be32toh(hdr->typecnt);
    hdr->charcnt    = be32toh(hdr->charcnt);
    return 0;
}

static void free_tz(struct parsed_tz *tz) {
    if (!tz) return;
    free(tz->transitions);
    free(tz->type_indices);
    free(tz->types);
    free(tz->char_table);
    memset(tz, 0, sizeof(*tz));
}

static int parse_tzfile64(const char *path, struct parsed_tz *tz) {
    memset(tz, 0, sizeof(*tz));
    FILE *f = fopen(path, "rb");
    if (!f) return -1;

    struct tz_header h1;
    if (read_header(f, &h1) != 0) {
        fclose(f);
        return -2;
    }

    /* Якщо файл версії 2 або 3, пропускаємо старий 32-бітний блок */
    if (h1.version == '2' || h1.version == '3') {
        long skip_v1 = (long)h1.timecnt * 4       /* transitions (32-bit) */
                     + (long)h1.timecnt * 1       /* type indices */
                     + (long)h1.typecnt * 6       /* ttinfo records (4+1+1) */
                     + (long)h1.charcnt           /* designations */
                     + (long)h1.leapcnt * 8       /* leap records (4+4) */
                     + (long)h1.ttisstdcnt * 1    /* standard/wall flags */
                     + (long)h1.ttisgmtcnt * 1;   /* ut/local flags */

        if (fseek(f, skip_v1, SEEK_CUR) != 0) {
            fclose(f);
            return -3;
        }

        struct tz_header h2;
        if (read_header(f, &h2) != 0) {
            fclose(f);
            return -4;
        }
        h1 = h2;
    }

    tz->timecnt = h1.timecnt;
    tz->typecnt = h1.typecnt;

    /* Виділення пам'яті під таблиці 64-бітного блоку */
    tz->transitions = malloc(sizeof(int64_t) * (h1.timecnt > 0 ? h1.timecnt : 1));
    tz->type_indices = malloc(sizeof(uint8_t) * (h1.timecnt > 0 ? h1.timecnt : 1));
    tz->types = malloc(sizeof(struct ttinfo) * (h1.typecnt > 0 ? h1.typecnt : 1));
    tz->char_table = malloc(h1.charcnt > 0 ? h1.charcnt : 1);

    if (!tz->transitions || !tz->type_indices || !tz->types || !tz->char_table) {
        free_tz(tz);
        fclose(f);
        return -5;
    }

    /* 1. Зчитування 64-бітних часових переходів */
    for (uint32_t i = 0; i < h1.timecnt; ++i) {
        int64_t raw_val;
        if (fread(&raw_val, sizeof(int64_t), 1, f) != 1) {
            free_tz(tz); fclose(f); return -6;
        }
        tz->transitions[i] = (int64_t)be64toh((uint64_t)raw_val);
    }

    /* 2. Зчитування індексів типів */
    if (h1.timecnt > 0 && fread(tz->type_indices, 1, h1.timecnt, f) != h1.timecnt) {
        free_tz(tz); fclose(f); return -7;
    }

    /* 3. Зчитування структур ttinfo (4 байти utoff, 1 байт isdst, 1 байт desigidx) */
    for (uint32_t i = 0; i < h1.typecnt; ++i) {
        int32_t raw_utoff;
        uint8_t isdst, desigidx;
        if (fread(&raw_utoff, 4, 1, f) != 1 ||
            fread(&isdst, 1, 1, f) != 1 ||
            fread(&desigidx, 1, 1, f) != 1) {
            free_tz(tz); fclose(f); return -8;
        }
        tz->types[i].utoff = (int32_t)be32toh((uint32_t)raw_utoff);
        tz->types[i].isdst = isdst;
        tz->types[i].desigidx = desigidx;
    }

    /* 4. Зчитування таблиці назв та абревіатур */
    if (h1.charcnt > 0 && fread(tz->char_table, 1, h1.charcnt, f) != h1.charcnt) {
        free_tz(tz); fclose(f); return -9;
    }

    /* 5. Пропуск високосних записів та прапорців */
    long skip_rest = (long)h1.leapcnt * 12 + (long)h1.ttisstdcnt + (long)h1.ttisgmtcnt;
    fseek(f, skip_rest, SEEK_CUR);

    /* 6. Зчитування завершального рядка POSIX TZ */
    int c = fgetc(f);
    if (c == '\n') {
        size_t idx = 0;
        while ((c = fgetc(f)) != EOF && c != '\n' && idx < sizeof(tz->posix_tz) - 1) {
            tz->posix_tz[idx++] = (char)c;
        }
        tz->posix_tz[idx] = '\0';
    }

    fclose(f);
    return 0;
}

static const struct ttinfo* lookup_time(const struct parsed_tz *tz, int64_t target_time) {
    if (tz->timecnt == 0 || target_time < tz->transitions[0]) {
        /* Якщо переходів немає або час передує першому переходу:
           шукаємо перший тип без прапорця DST */
        for (uint32_t i = 0; i < tz->typecnt; ++i) {
            if (!tz->types[i].isdst) return &tz->types[i];
        }
        return tz->typecnt > 0 ? &tz->types[0] : NULL;
    }

    /* Двійковий пошук переходу, меншого або рівного target_time */
    int32_t left = 0, right = (int32_t)tz->timecnt - 1;
    int32_t best = 0;

    while (left <= right) {
        int32_t mid = left + (right - left) / 2;
        if (tz->transitions[mid] <= target_time) {
            best = mid;
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    uint8_t type_idx = tz->type_indices[best];
    if (type_idx < tz->typecnt) {
        return &tz->types[type_idx];
    }
    return NULL;
}

int main(int argc, char **argv) {
    const char *path = (argc > 1) ? argv[1] : "/etc/localtime";
    time_t now = time(NULL);

    struct parsed_tz tz;
    int err = parse_tzfile64(path, &tz);
    if (err != 0) {
        fprintf(stderr, "Помилка розбору tzfile (%s): код %d (%s)\n", path, err, strerror(errno));
        return 1;
    }

    const struct ttinfo *active = lookup_time(&tz, (int64_t)now);
    if (!active) {
        fprintf(stderr, "Не вдалося визначити активний тип часу.\n");
        free_tz(&tz);
        return 1;
    }

    const char *abbr = &tz.char_table[active->desigidx];
    int hours = active->utoff / 3600;
    int minutes = abs(active->utoff % 3600) / 60;

    printf("Файл часового поясу : %s\n", path);
    printf("Кількість переходів : %u\n", tz.timecnt);
    printf("Поточна мітка time_t: %ld (UTC)\n", (long)now);
    printf("Активне зміщення    : %+03d:%02d (%+d секунд)\n", hours, minutes, active->utoff);
    printf("Режим літнього часу : %s\n", active->isdst ? "ТАК (DST активний)" : "НІ (Стандартний час)");
    printf("Абревіатура зони    : %s\n", abbr);
    if (tz.posix_tz[0]) {
        printf("Правило POSIX TZ    : %s\n", tz.posix_tz);
    }

    free_tz(&tz);
    return 0;
}
