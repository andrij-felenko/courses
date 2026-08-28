/* fscrypt-key.c — виведення ключів fscrypt у просторі користувача.
 * Збірка: cc -O2 -o fscrypt-key fscrypt-key.c -lcrypto
 * Виклик: ./fscrypt-key ФАЙЛ-ГОЛОВНОГО-КЛЮЧА ШЛЯХ
 * Потрібні заголовки ядра не старші за 5.7 (FS_IOC_GET_ENCRYPTION_NONCE). */
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <linux/fscrypt.h>
#include <openssl/hmac.h>

#define HASHLEN     64   /* довжина виходу SHA-512 */
#define NONCE_SIZE  16   /* FSCRYPT_FILE_NONCE_SIZE — у uapi його немає */

/* Номери контекстів HKDF. У заголовках простору користувача їх теж немає:
   вони лежать у fs/crypto/fscrypt_private.h. Але це частина формату на
   носії, тож user space їх просто переписує до себе. */
#define CTX_KEY_IDENTIFIER    1   /* info порожній        */
#define CTX_PER_FILE_ENC_KEY  2   /* info = nonce файлу   */

/* HKDF-Extract: солі немає, отже ключем HMAC служать HASHLEN нулів. */
static void hkdf_extract(const uint8_t *ikm, unsigned ikmlen, uint8_t prk[HASHLEN])
{
    static const uint8_t zero_salt[HASHLEN] = { 0 };
    unsigned int n = HASHLEN;

    HMAC(EVP_sha512(), zero_salt, HASHLEN, ikm, ikmlen, prk, &n);
}

/* HKDF-Expand: T(i) = HMAC(prk, T(i−1) ‖ "fscrypt\0" ‖ контекст ‖ info ‖ i).
   Буфер зібрано явно — саме його розкладка й є весь формат. */
static void hkdf_expand(const uint8_t prk[HASHLEN], uint8_t context,
                        const uint8_t *info, unsigned infolen,
                        uint8_t *okm, unsigned okmlen)
{
    uint8_t msg[HASHLEN + 8 + 1 + NONCE_SIZE + 1], tmp[HASHLEN];

    for (unsigned i = 0, counter = 1; i < okmlen; i += HASHLEN, counter++) {
        unsigned n = 0, take = okmlen - i < HASHLEN ? okmlen - i : HASHLEN;
        unsigned int outlen = HASHLEN;

        if (i) { memcpy(msg + n, okm + i - HASHLEN, HASHLEN); n += HASHLEN; }
        memcpy(msg + n, "fscrypt\0", 8);  n += 8;   /* сім літер І нульовий байт */
        msg[n++] = context;
        if (infolen) { memcpy(msg + n, info, infolen); n += infolen; }
        msg[n++] = (uint8_t)counter;

        HMAC(EVP_sha512(), prk, HASHLEN, msg, n, tmp, &outlen);
        memcpy(okm + i, tmp, take);
    }
    OPENSSL_cleanse(tmp, sizeof tmp);
}

static unsigned mode_keysize(unsigned mode)
{
    switch (mode) {
    case FSCRYPT_MODE_AES_256_XTS:   return 64;  /* 32 на дані + 32 на твік */
    case FSCRYPT_MODE_AES_256_CTS:   return 32;
    case FSCRYPT_MODE_AES_128_CBC:
    case FSCRYPT_MODE_AES_128_CTS:   return 16;
    case FSCRYPT_MODE_ADIANTUM:
    case FSCRYPT_MODE_AES_256_HCTR2: return 32;
    default:                         return 0;
    }
}

static void put_hex(const char *label, const uint8_t *p, unsigned n)
{
    printf("%s\n  ", label);
    for (unsigned i = 0; i < n; i++) {
        printf("%02x", p[i]);
        if ((i + 1) % 32 == 0 && i + 1 < n) printf("\n  ");
    }
    putchar('\n');
}

int main(int argc, char **argv)
{
    uint8_t master[65], nonce[NONCE_SIZE], prk[HASHLEN];
    uint8_t ident[FSCRYPT_KEY_IDENTIFIER_SIZE], filekey[64];
    struct fscrypt_get_policy_ex_arg arg;
    const struct fscrypt_policy_v2 *pol;
    struct stat st;

    if (argc != 3) {
        fprintf(stderr, "вжиток: %s ФАЙЛ-ГОЛОВНОГО-КЛЮЧА ШЛЯХ\n", argv[0]);
        return 2;
    }

    /* Головний ключ приходить ЗЗОВНІ: з ядра його не дістати ніяк. */
    int kfd = open(argv[1], O_RDONLY);
    if (kfd < 0) { perror(argv[1]); return 1; }
    ssize_t mlen = read(kfd, master, sizeof master);
    close(kfd);
    if (mlen < 16 || mlen > 64) {
        fprintf(stderr, "ключ мусить бути 16..64 байтів (прочитано %zd)\n", mlen);
        return 1;
    }

    int fd = open(argv[2], O_RDONLY);
    if (fd < 0) {
        if (errno == ENOKEY)
            fprintf(stderr, "%s: ключа у ФС немає, звичайний файл без нього "
                            "не відкрити (каталог — відкрити можна)\n", argv[2]);
        else
            perror(argv[2]);            /* EACCES — просто немає права читати */
        return 1;
    }
    if (fstat(fd, &st)) { perror("fstat"); return 1; }

    memset(&arg, 0, sizeof arg);
    arg.policy_size = sizeof arg.policy;      /* на вхід — скільки місця є */
    if (ioctl(fd, FS_IOC_GET_ENCRYPTION_POLICY_EX, &arg)) {
        if (errno == ENODATA)     fprintf(stderr, "%s: не зашифрований\n", argv[2]);
        else if (errno == ENOTTY) fprintf(stderr, "ця ФС не вміє fscrypt\n");
        else                      perror("FS_IOC_GET_ENCRYPTION_POLICY_EX");
        return 1;
    }
    if (arg.policy.version != FSCRYPT_POLICY_V2) {
        fprintf(stderr, "політика версії %u: ідентифікатора ключа в ній немає, "
                        "і ключі виводяться не HKDF\n", arg.policy.version);
        return 1;
    }

    pol = &arg.policy.v2;
    if (pol->flags & (FSCRYPT_POLICY_FLAG_DIRECT_KEY |
                      FSCRYPT_POLICY_FLAG_IV_INO_LBLK_64 |
                      FSCRYPT_POLICY_FLAG_IV_INO_LBLK_32)) {
        fprintf(stderr, "прапорці %#x: ключ спільний на режим, "
                        "окремого ключа inode тут немає\n", pol->flags);
        return 1;
    }

    if (ioctl(fd, FS_IOC_GET_ENCRYPTION_NONCE, nonce)) {
        perror("FS_IOC_GET_ENCRYPTION_NONCE");   /* ENOTTY — ядро старше за 5.7 */
        return 1;
    }

    hkdf_extract(master, (unsigned)mlen, prk);
    hkdf_expand(prk, CTX_KEY_IDENTIFIER, NULL, 0, ident, sizeof ident);

    put_hex("nonce файлу", nonce, sizeof nonce);
    put_hex("ідентифікатор у політиці", pol->master_key_identifier, sizeof ident);
    put_hex("виведений із ключа", ident, sizeof ident);

    if (memcmp(ident, pol->master_key_identifier, sizeof ident)) {
        puts("РОЗБІЖНІСТЬ: це не той головний ключ, якого просить файл");
        return 1;
    }
    puts("ідентифікатори збіглися — ключ той самий");

    /* Режим добирають ЗА ТИПОМ inode: вміст — для звичайного файлу,
       імена — для каталогу й символьного посилання. */
    unsigned mode = S_ISREG(st.st_mode) ? pol->contents_encryption_mode
                                        : pol->filenames_encryption_mode;
    unsigned keylen = mode_keysize(mode);
    if (!keylen) { fprintf(stderr, "невідомий режим %u\n", mode); return 1; }

    hkdf_expand(prk, CTX_PER_FILE_ENC_KEY, nonce, sizeof nonce, filekey, keylen);
    printf("режим %u, ключ inode %llu, %u Б\n", mode,
           (unsigned long long)st.st_ino, keylen);
    put_hex("", filekey, keylen);

    OPENSSL_cleanse(master, sizeof master);
    OPENSSL_cleanse(prk, sizeof prk);
    OPENSSL_cleanse(filekey, sizeof filekey);
    close(fd);
    return 0;
}
