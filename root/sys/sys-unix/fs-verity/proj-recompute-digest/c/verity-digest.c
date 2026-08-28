/* verity-digest.c — цифра fs-verity, порахована в просторі користувача.
 * Збірка: cc -O2 -o verity-digest verity-digest.c -lcrypto
 * Виклик: ./verity-digest ФАЙЛ [СІЛЬ-ШІСТНАДЦЯТКОВО]                */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>
#include <endian.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <linux/fsverity.h>
#include <openssl/evp.h>

#define BLOCK     4096u   /* розмір блока даних і блока дерева */
#define LOGBLOCK  12u     /* log2(BLOCK) — саме це йде в дескриптор */
#define HASH      32u     /* довжина гешу SHA-256 */

static uint8_t  salt[64];     /* сіль, УЖЕ доповнена нулями до 64 байтів */
static unsigned salt_size;    /* справжня довжина солі, 0..32 */
static unsigned salt_hashed;  /* скільки байтів домішуємо: 0 або 64 */

static uint64_t ceil_div(uint64_t a, uint64_t b) { return (a + b - 1) / b; }

/* Геш одного блока: [доповнена сіль] + рівно BLOCK байтів. */
static void hash_block(const uint8_t *blk, uint8_t out[HASH])
{
    EVP_MD_CTX *c = EVP_MD_CTX_new();
    unsigned int n;

    EVP_DigestInit_ex(c, EVP_sha256(), NULL);
    if (salt_hashed)
        EVP_DigestUpdate(c, salt, salt_hashed);
    EVP_DigestUpdate(c, blk, BLOCK);
    EVP_DigestFinal_ex(c, out, &n);
    EVP_MD_CTX_free(c);
}

/* Прочитати блок idx; усе за кінцем файлу лишається нулями. */
static void read_block(int fd, uint64_t idx, uint8_t *buf)
{
    size_t got = 0;
    memset(buf, 0, BLOCK);
    while (got < BLOCK) {
        ssize_t n = pread(fd, buf + got, BLOCK - got,
                          (off_t)(idx * BLOCK + got));
        if (n < 0) { perror("pread"); exit(1); }
        if (n == 0) break;            /* кінець файлу — доповнення нулями */
        got += (size_t)n;
    }
}

static uint8_t *alloc_level(uint64_t hashes, uint64_t *blocks)
{
    *blocks = ceil_div(hashes * HASH, BLOCK);   /* округлення ВГОРУ */
    uint8_t *p = calloc(*blocks, BLOCK);        /* calloc і є доповнення */
    if (!p) { perror("calloc"); exit(1); }
    return p;
}

/* Рівень 0: геші всіх блоків файлу, у порядку блоків. */
static uint8_t *level_from_file(int fd, uint64_t blocks, uint64_t *out_blocks)
{
    uint8_t *out = alloc_level(blocks, out_blocks);
    uint8_t buf[BLOCK];

    for (uint64_t i = 0; i < blocks; i++) {
        read_block(fd, i, buf);
        hash_block(buf, out + i * HASH);
    }
    return out;
}

/* Згорнути рівень у наступний тим самим правилом. */
static uint8_t *fold(uint8_t *lvl, uint64_t blocks, uint64_t *out_blocks)
{
    uint8_t *out = alloc_level(blocks, out_blocks);

    for (uint64_t i = 0; i < blocks; i++)
        hash_block(lvl + i * BLOCK, out + i * HASH);
    free(lvl);
    return out;
}

struct __attribute__((packed)) descriptor {
    uint8_t  version, hash_algorithm, log_blocksize, salt_size;
    uint32_t reserved_0x04;
    uint64_t data_size;
    uint8_t  root_hash[64];
    uint8_t  salt[32];
    uint8_t  reserved[144];
};
_Static_assert(sizeof(struct descriptor) == 256, "дескриптор — рівно 256 байтів");

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "вжиток: %s ФАЙЛ [сіль-шістнадцятково]\n", argv[0]);
        return 2;
    }
    if (argc > 2) {
        salt_size = (unsigned)strlen(argv[2]) / 2;
        if (salt_size > 32) { fprintf(stderr, "сіль довша за 32 байти\n"); return 2; }
        for (unsigned i = 0; i < salt_size; i++)
            sscanf(argv[2] + 2 * i, "%2hhx", &salt[i]);
        if (salt_size)             /* без солі ядро нічого не домішує */
            salt_hashed = 64;      /* доповнення до входу стиску SHA-256 */
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) { perror("open"); return 1; }
    struct stat st;
    if (fstat(fd, &st)) { perror("fstat"); return 1; }

    uint64_t size   = (uint64_t)st.st_size;
    uint64_t blocks = ceil_div(size, BLOCK);
    uint8_t  root[HASH];
    memset(root, 0, HASH);            /* порожній файл: корінь — самі нулі */

    if (blocks == 1) {                /* рівнів нуль: корінь — геш блока даних */
        uint8_t buf[BLOCK];
        read_block(fd, 0, buf);
        hash_block(buf, root);
    } else if (blocks > 1) {
        uint8_t *lvl = level_from_file(fd, blocks, &blocks);
        while (blocks > 1)
            lvl = fold(lvl, blocks, &blocks);
        hash_block(lvl, root);        /* корінь — геш єдиного верхнього блока */
        free(lvl);
    }

    struct descriptor d;
    memset(&d, 0, sizeof d);          /* резерв і хвости слотів занулено одразу */
    d.version        = 1;
    d.hash_algorithm = FS_VERITY_HASH_ALG_SHA256;
    d.log_blocksize  = LOGBLOCK;      /* 12, а не 4096 */
    d.salt_size      = (uint8_t)salt_size;   /* довжина НЕдоповненої солі */
    d.data_size      = htole64(size);
    memcpy(d.root_hash, root, HASH);
    memcpy(d.salt, salt, salt_size);

    uint8_t mine[HASH];
    unsigned int n;
    EVP_Digest(&d, sizeof d, mine, &n, EVP_sha256(), NULL);

    printf("наша цифра:  sha256:");
    for (unsigned i = 0; i < HASH; i++) printf("%02x", mine[i]);
    putchar('\n');

    /* Те саме число з ядра — за сталий час, без читання файлу.
       Об'єднання дає і місце під сам геш, і потрібне вирівнювання. */
    union {
        struct fsverity_digest d;
        uint8_t space[sizeof(struct fsverity_digest) + 64];
    } k;
    memset(&k, 0, sizeof k);
    k.d.digest_size = 64;
    if (ioctl(fd, FS_IOC_MEASURE_VERITY, &k.d) == 0) {
        printf("ядро каже:   sha256:");
        for (unsigned i = 0; i < k.d.digest_size; i++) printf("%02x", k.d.digest[i]);
        printf("\n%s\n", (k.d.digest_size == HASH &&
                          memcmp(k.d.digest, mine, HASH) == 0)
                         ? "збіглося" : "РОЗБІЖНІСТЬ");
    } else if (errno == ENODATA) {
        puts("перевірку на файлі ще не ввімкнено — ядру нема чого сказати");
    } else {
        perror("FS_IOC_MEASURE_VERITY");
    }
    close(fd);
    return 0;
}
