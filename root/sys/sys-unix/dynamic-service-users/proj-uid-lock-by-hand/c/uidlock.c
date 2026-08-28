/* uidlock.c — виділення тимчасового UID тим самим способом, що й systemd.
 *   cc -O2 -Wall -o uidlock uidlock.c
 *   sudo ./uidlock <ім'я>        (каталог замків належить root)
 * Програма тримає число, доки її не вб'ють.                              */

#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <pwd.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/file.h>
#include <sys/random.h>
#include <sys/stat.h>
#include <unistd.h>

#define UID_MIN  61184u                    /* 0x0000EF00 */
#define UID_MAX  65519u                    /* 0x0000FFEF */
#define SPAN     (UID_MAX - UID_MIN + 1)   /* 4336 номерів */
#define LOCKDIR  "/run/systemd/dynamic-uid"

/* ── SipHash-2-4, довідкова реалізація ────────────────────────────────── */
#define ROTL(x, b) (((x) << (b)) | ((x) >> (64 - (b))))
#define SIPROUND do {                                             \
        v0 += v1; v1 = ROTL(v1, 13); v1 ^= v0; v0 = ROTL(v0, 32); \
        v2 += v3; v3 = ROTL(v3, 16); v3 ^= v2;                    \
        v0 += v3; v3 = ROTL(v3, 21); v3 ^= v0;                    \
        v2 += v1; v1 = ROTL(v1, 17); v1 ^= v2; v2 = ROTL(v2, 32); \
} while (0)

static uint64_t siphash24(const void *in, size_t len, const uint8_t k[16])
{
    const uint8_t *p = in, *end = p + (len & ~(size_t) 7);
    uint64_t k0 = 0, k1 = 0, m, b = (uint64_t) len << 56;
    uint64_t v0, v1, v2, v3;

    for (int i = 7; i >= 0; i--) {         /* ключ читається молодшим уперед */
        k0 = k0 << 8 | k[i];
        k1 = k1 << 8 | k[8 + i];
    }
    v0 = 0x736f6d6570736575ULL ^ k0;
    v1 = 0x646f72616e646f6dULL ^ k1;
    v2 = 0x6c7967656e657261ULL ^ k0;
    v3 = 0x7465646279746573ULL ^ k1;

    for (; p != end; p += 8) {             /* повні восьмибайтові блоки */
        m = 0;
        for (int i = 7; i >= 0; i--)
            m = m << 8 | p[i];
        v3 ^= m; SIPROUND; SIPROUND; v0 ^= m;
    }
    for (size_t i = len & 7; i-- > 0; )    /* хвіст + довжина у старшому байті */
        b |= (uint64_t) p[i] << (8 * i);

    v3 ^= b; SIPROUND; SIPROUND; v0 ^= b;
    v2 ^= 0xff; SIPROUND; SIPROUND; SIPROUND; SIPROUND;
    return v0 ^ v1 ^ v2 ^ v3;
}

/* Той самий ключ, що зашитий у systemd (src/core/dynamic-user.c). */
static const uint8_t hash_key[16] = {
    0x37, 0x53, 0x7e, 0x31, 0xcf, 0xce, 0x48, 0xf5,
    0x8a, 0xbb, 0x39, 0x57, 0x8d, 0xd9, 0xec, 0x59
};

/* УВАГА: хеш 64-бітний, а остачу беруть від УРІЗАНОГО до 32 біт значення —
   бо в макросі стоїть зведення до uid_t. Без цього зведення число інше.   */
static uid_t uid_from_name(const char *name)
{
    uint64_t h = siphash24(name, strlen(name), hash_key);

    return (uid_t) ((uint32_t) h % SPAN) + UID_MIN;
}

/* Спроба закріпити за собою одне число. Дескриптор замка або -1.          */
static int claim(uid_t uid, const char *name)
{
    char path[64], line[128], holder[128];
    int fd, len;

    if (getpwuid(uid) || getgrgid((gid_t) uid)) {
        fprintf(stderr, "%u: число тримає статичний обліковий запис\n", uid);
        return -1;
    }

    snprintf(path, sizeof path, LOCKDIR "/%u", uid);
    fd = open(path, O_CREAT | O_RDWR | O_NOFOLLOW | O_CLOEXEC | O_NOCTTY, 0600);
    if (fd < 0) {
        perror(path);
        return -1;
    }

    if (flock(fd, LOCK_EX | LOCK_NB) < 0) {          /* зайнято — і ким саме */
        ssize_t n = pread(fd, holder, sizeof holder - 1, 0);

        holder[n > 0 ? n : 0] = '\0';
        holder[strcspn(holder, "\n")] = '\0';
        fprintf(stderr, "%u: замок тримає «%s»\n", uid, n > 0 ? holder : "?");
        close(fd);
        return -1;
    }

    len = snprintf(line, sizeof line, "%s\n", name);   /* зворотний довідник */
    if (pwrite(fd, line, len, 0) != len) {
        perror("pwrite");
        close(fd);
        return -1;
    }
    (void) ftruncate(fd, len);
    return fd;                        /* НЕ закриваємо: закриття зніме замок */
}

int main(int argc, char **argv)
{
    const char *name = argc > 1 ? argv[1] : "uidplay";
    uid_t uid;
    int fd;

    if (mkdir(LOCKDIR, 0755) < 0 && errno != EEXIST) {
        perror(LOCKDIR);
        return 1;
    }

    uid = uid_from_name(name);
    printf("хеш «%s» → %u\n", name, uid);

    fd = claim(uid, name);
    for (unsigned tries = 0; fd < 0 && tries < 100; tries++) {   /* навмання */
        uint32_t r;

        if (getrandom(&r, sizeof r, 0) != (ssize_t) sizeof r)
            return 1;
        uid = r % SPAN + UID_MIN;
        fd = claim(uid, name);
    }
    if (fd < 0) {
        fprintf(stderr, "за сто спроб вільного числа не знайшлося\n");
        return 1;
    }

    printf("узято %u; замок на дескрипторі %d, PID %ld\n",
           uid, fd, (long) getpid());
    printf("вбийте процес — і число звільниться саме\n");
    pause();                          /* тримаємо, доки нас не вб'ють */
    return 0;
}
