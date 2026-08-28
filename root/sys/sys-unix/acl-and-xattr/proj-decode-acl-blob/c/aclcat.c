/* aclcat.c — друкує список доступу, прочитавши атрибут як звичайні байти.
   Збірка: cc -Wall -Wextra -O2 -o aclcat aclcat.c
   Виклик: ./aclcat [-x] ШЛЯХ...       (-x додає шістнадцятковий вигляд запису) */
#define _GNU_SOURCE
#include <errno.h>
#include <grp.h>
#include <pwd.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/xattr.h>

#define ACL_XATTR_VERSION 0x0002u
#define TAG_USER_OBJ  0x01u
#define TAG_USER      0x02u
#define TAG_GROUP_OBJ 0x04u
#define TAG_GROUP     0x08u
#define TAG_MASK      0x10u
#define TAG_OTHER     0x20u

#define HDR 4   /* заголовок: u32 версія                        */
#define REC 8   /* запис: u16 тег + u16 права + u32 ідентифікатор */

/* Числа на носії little-endian незалежно від машини — тому збираємо
   їх із байтів руками, а не накладаємо struct на буфер.          */
static uint16_t le16(const unsigned char *p)
{
    return (uint16_t)(p[0] | (p[1] << 8));
}

static uint32_t le32(const unsigned char *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8)
         | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static char *rwx(unsigned perm, char out[4])
{
    out[0] = (perm & 4) ? 'r' : '-';
    out[1] = (perm & 2) ? 'w' : '-';
    out[2] = (perm & 1) ? 'x' : '-';
    out[3] = '\0';
    return out;
}

static void who_name(uint32_t id, int group, char *out, size_t n)
{
    if (group) {
        struct group *g = getgrgid((gid_t)id);
        if (g) { snprintf(out, n, "%s", g->gr_name); return; }
    } else {
        struct passwd *u = getpwuid((uid_t)id);
        if (u) { snprintf(out, n, "%s", u->pw_name); return; }
    }
    snprintf(out, n, "%u", id);                 /* немає в базі — лишаємо число */
}

/* Двокроковий шаблон: спитати розмір, виділити, прочитати.
   Список міг вирости між викликами — тоді ERANGE, і все спочатку. */
static ssize_t slurp(const char *path, const char *name, unsigned char **out)
{
    for (int attempt = 0; attempt < 8; attempt++) {
        ssize_t need = getxattr(path, name, NULL, 0);
        if (need < 0) return -1;                /* ENODATA, EOPNOTSUPP, EACCES… */
        unsigned char *buf = malloc(need ? (size_t)need : 1);
        if (!buf) { errno = ENOMEM; return -1; }
        ssize_t got = getxattr(path, name, buf, (size_t)need);
        if (got >= 0) { *out = buf; return got; }
        free(buf);
        if (errno != ERANGE) return -1;
    }
    errno = ERANGE;
    return -1;
}

static void print_rec(const unsigned char *r, unsigned mask, int have_mask,
                      const char *prefix, int hex)
{
    unsigned tag = le16(r), perm = le16(r + 2);
    uint32_t id = le32(r + 4);
    char who[128], name[64], a[4], b[4];

    switch (tag) {
    case TAG_USER_OBJ:  snprintf(who, sizeof who, "%suser::",  prefix); break;
    case TAG_GROUP_OBJ: snprintf(who, sizeof who, "%sgroup::", prefix); break;
    case TAG_MASK:      snprintf(who, sizeof who, "%smask::",  prefix); break;
    case TAG_OTHER:     snprintf(who, sizeof who, "%sother::", prefix); break;
    case TAG_USER:
    case TAG_GROUP:
        who_name(id, tag == TAG_GROUP, name, sizeof name);
        snprintf(who, sizeof who, "%s%s:%s:", prefix,
                 tag == TAG_GROUP ? "group" : "user", name);
        break;
    default:
        printf("# запис із невідомим тегом 0x%02x\n", tag);
        return;
    }

    /* маска стелить лише середній клас: іменовані записи і group:: */
    int capped = have_mask &&
                 (tag == TAG_USER || tag == TAG_GROUP || tag == TAG_GROUP_OBJ);
    unsigned eff = capped ? (perm & mask) : perm;

    if (hex)
        printf("%02x %02x %02x %02x %02x %02x %02x %02x  ",
               r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]);
    printf("%s%s", who, rwx(perm, a));
    if (eff != perm) printf("\t#effective:%s", rwx(eff, b));
    putchar('\n');
}

static int print_list(const unsigned char *raw, size_t size,
                      const char *prefix, int hex)
{
    if (size < HDR || (size - HDR) % REC) {
        fprintf(stderr, "довжина %zu не складається із заголовка й цілих записів\n",
                size);
        return -1;
    }
    if (le32(raw) != ACL_XATTR_VERSION) {
        fprintf(stderr, "версія формату 0x%04x, а розбирати вміємо лише 0x%04x\n",
                (unsigned)le32(raw), ACL_XATTR_VERSION);
        return -1;
    }

    size_t n = (size - HDR) / REC;
    unsigned mask = 0;
    int have_mask = 0;
    for (size_t i = 0; i < n; i++) {            /* маску шукаємо першим проходом */
        const unsigned char *r = raw + HDR + i * REC;
        if (le16(r) == TAG_MASK) { mask = le16(r + 2); have_mask = 1; }
    }
    for (size_t i = 0; i < n; i++)
        print_rec(raw + HDR + i * REC, mask, have_mask, prefix, hex);
    return 0;
}

static int dump(const char *path, int hex)
{
    struct stat st;
    char nm[64], a[4];

    if (stat(path, &st)) { perror(path); return 1; }   /* stat, як і getxattr,
                                                          іде за символьним
                                                          посиланням          */
    who_name(st.st_uid, 0, nm, sizeof nm);
    printf("# file: %s\n# owner: %s\n", path, nm);
    who_name(st.st_gid, 1, nm, sizeof nm);
    printf("# group: %s\n", nm);

    unsigned char *raw = NULL;
    ssize_t size = slurp(path, "system.posix_acl_access", &raw);
    if (size < 0) {
        if (errno != ENODATA) {                 /* ENODATA — не помилка */
            fprintf(stderr, "%s: %s\n", path, strerror(errno));
            return 1;
        }
        printf("user::%s\n",  rwx((st.st_mode >> 6) & 7, a));
        printf("group::%s\n", rwx((st.st_mode >> 3) & 7, a));
        printf("other::%s\n", rwx(st.st_mode & 7, a));
        printf("# атрибута немає: список мінімальний, це самі біти режиму\n");
    } else {
        int bad = print_list(raw, (size_t)size, "", hex);
        free(raw);
        if (bad) return 1;
    }

    if (S_ISDIR(st.st_mode)) {                  /* шаблон буває лише в каталогу */
        raw = NULL;
        size = slurp(path, "system.posix_acl_default", &raw);
        if (size >= 0) {
            print_list(raw, (size_t)size, "default:", hex);
            free(raw);
        } else if (errno != ENODATA) {
            fprintf(stderr, "%s (default): %s\n", path, strerror(errno));
        }
    }
    return 0;
}

int main(int argc, char **argv)
{
    int hex = 0, i = 1;
    if (i < argc && !strcmp(argv[i], "-x")) { hex = 1; i++; }
    if (i >= argc) {
        fprintf(stderr, "вжиток: %s [-x] ШЛЯХ...\n", argv[0]);
        return 2;
    }
    int first = i, rc = 0;
    for (; i < argc; i++) {
        if (i > first) putchar('\n');
        if (dump(argv[i], hex)) rc = 1;
    }
    return rc;
}
