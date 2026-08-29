/* Хостовий прогін верифікатора: пакет лежить звичайним файлом, Slot B
 * емульовано другим файлом із поведінкою NOR (стирання в 0xFF, запис
 * лише гасить біти), Ed25519 дає Monocypher 4.x. На платі замість цього
 * файла стоїть порт до FatFS, драйвера Flash і ROM-криптографії.
 *
 *   cc -std=c11 -O2 main.c upkg.c sha256.c -lmonocypher -o upkgtool
 *   ./upkgtool firmware.upkg slotb.bin [--resume]
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <monocypher.h>

#include "upkg.h"

/* Відкритий ключ випуску. На пристрої лежить у eFuse і не змінюється
 * ніколи — саме тому підробити заголовок у полі неможливо. */
static const uint8_t k_root_public_key[UPKG_PUBKEY_SIZE] = {
    0x3d, 0x40, 0x17, 0xc3, 0xe8, 0x43, 0x89, 0x5a,
    0x92, 0xb7, 0x0a, 0xa7, 0x4d, 0x1b, 0x7e, 0xbc,
    0x54, 0x94, 0xc9, 0x78, 0xc1, 0x67, 0x3b, 0xa5,
    0xa1, 0xc1, 0xc1, 0xd7, 0x93, 0xb1, 0x60, 0x1e
};

/* Ключ самого пристрою для підпису квитанції. У полі — захищений
 * елемент або OTP-область, звідки байти не вичитуються назовні. */
static const uint8_t k_device_secret[32] = {
    0x9d, 0x61, 0xb1, 0x9d, 0xef, 0xfd, 0x5a, 0x60,
    0xba, 0x84, 0x4a, 0xf4, 0x92, 0xec, 0x2c, 0xc4,
    0x44, 0x49, 0xc5, 0x69, 0x7b, 0x32, 0x69, 0x19,
    0x70, 0x3b, 0xac, 0x03, 0x1c, 0xae, 0x7f, 0x60
};

typedef struct {
    FILE *fp;
} file_dev_t;

static bool file_read(void *ctx, uint32_t offset, uint8_t *dst, uint32_t len) {
    FILE *fp = ((file_dev_t *)ctx)->fp;
    if (fseek(fp, (long)offset, SEEK_SET) != 0) {
        return false;
    }
    return fread(dst, 1, len, fp) == len;
}

static bool file_write(void *ctx, uint32_t offset, const uint8_t *src,
                       uint32_t len) {
    FILE *fp = ((file_dev_t *)ctx)->fp;
    if (fseek(fp, (long)offset, SEEK_SET) != 0) {
        return false;
    }
    if (fwrite(src, 1, len, fp) != len) {
        return false;
    }
    return fflush(fp) == 0;
}

/* Стирання NOR: сектор повертається у всі одиниці. */
static bool flash_erase(void *ctx, uint32_t offset, uint32_t len) {
    FILE *fp = ((file_dev_t *)ctx)->fp;
    uint8_t ones[256];
    memset(ones, 0xFF, sizeof(ones));
    if (fseek(fp, (long)offset, SEEK_SET) != 0) {
        return false;
    }
    while (len > 0) {
        uint32_t n = len < sizeof(ones) ? len : (uint32_t)sizeof(ones);
        if (fwrite(ones, 1, n, fp) != n) {
            return false;
        }
        len -= n;
    }
    return fflush(fp) == 0;
}

/* Програмування NOR уміє лише гасити біти. Якщо сектор не стертий,
 * реальна плата мовчки видала б суміш старого й нового — тут ми на
 * цьому чесно падаємо, щоб помилку було видно одразу. */
static bool flash_program(void *ctx, uint32_t offset, const uint8_t *src,
                          uint32_t len) {
    FILE *fp = ((file_dev_t *)ctx)->fp;
    for (uint32_t i = 0; i < len; ++i) {
        if (fseek(fp, (long)(offset + i), SEEK_SET) != 0) {
            return false;
        }
        int old = fgetc(fp);
        if (old == EOF) {
            old = 0xFF;  /* хвіст файла ще не існує — вважаємо стертим */
        }
        if ((uint8_t)(old & src[i]) != src[i]) {
            fprintf(stderr, "запис у нестертий байт 0x%08X\n", offset + i);
            return false;
        }
        if (fseek(fp, (long)(offset + i), SEEK_SET) != 0) {
            return false;
        }
        if (fputc(src[i], fp) == EOF) {
            return false;
        }
    }
    return fflush(fp) == 0;
}

static bool crypto_verify(const uint8_t sig[UPKG_SIG_SIZE],
                          const uint8_t pub[UPKG_PUBKEY_SIZE],
                          const uint8_t *msg, size_t len) {
    return crypto_eddsa_check(sig, pub, msg, len) == 0;
}

static bool crypto_sign(const uint8_t *msg, size_t len,
                        uint8_t sig[UPKG_SIG_SIZE]) {
    crypto_eddsa_sign(sig, k_device_secret, msg, len);
    return true;
}

/* NVS: на платі це окремий сектор конфігурації, тут — маленький файл. */
static bool nvs_store(void *ctx, const upkg_boot_state_t *state) {
    FILE *fp = fopen((const char *)ctx, "wb");
    if (fp == NULL) {
        return false;
    }
    bool ok = fwrite(state, sizeof(*state), 1, fp) == 1;
    return (fclose(fp) == 0) && ok;
}

static void print_hex(const char *label, const uint8_t *data, size_t len) {
    printf("%s", label);
    for (size_t i = 0; i < len; ++i) {
        printf("%02x", data[i]);
    }
    printf("\n");
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "вжиток: %s <пакет.upkg> <slotb.bin> [--resume]\n",
                argv[0]);
        return 2;
    }
    const bool resume = (argc > 3 && strcmp(argv[3], "--resume") == 0);

    file_dev_t pkg = {fopen(argv[1], "r+b")};
    if (pkg.fp == NULL) {
        perror("пакет");
        return 2;
    }
    /* Slot B: відкриваємо наявний образ, інакше заводимо порожній. */
    file_dev_t slot = {fopen(argv[2], "r+b")};
    if (slot.fp == NULL) {
        slot.fp = fopen(argv[2], "w+b");
    }
    if (slot.fp == NULL) {
        perror("slot B");
        fclose(pkg.fp);
        return 2;
    }

    /* 4 КБ буфера сектора всередині — тримаємо в .bss, а не на стеку:
     * у завантажувача стек буває на кілька сотень байтів. */
    static upkg_session_t s;
    s.policy.hw_id = 0x0217;        /* код моделі з OTP */
    s.policy.min_version = 13;      /* поріг із монотонних запобіжників */
    s.policy.device_serial = 0x00A31C07u;
    memcpy(s.policy.root_public_key, k_root_public_key, UPKG_PUBKEY_SIZE);

    s.media.read = file_read;
    s.media.write = file_write;
    s.media.ctx = &pkg;

    s.flash.erase = flash_erase;
    s.flash.write = flash_program;
    s.flash.read = file_read;
    s.flash.ctx = &slot;

    s.crypto.verify = crypto_verify;
    s.crypto.sign_receipt = crypto_sign;

    s.nvs_write_state = nvs_store;
    s.nvs_ctx = (void *)"bootstate.bin";

    upkg_receipt_t receipt;
    upkg_status_t st = upkg_install(&s, resume, &receipt);

    printf("результат: %s (код %d)\n", upkg_strstatus(st), (int)st);
    if (st == UPKG_OK) {
        printf("прошито версію %u, спроб завантаження %u\n",
               receipt.body.version, receipt.body.boot_retries);
        print_hex("хеш образу:  ", receipt.body.image_sha256, UPKG_HASH_SIZE);
        print_hex("підпис квитанції: ", receipt.signature, UPKG_SIG_SIZE);
    }

    fclose(slot.fp);
    fclose(pkg.fp);
    return st == UPKG_OK ? 0 : 1;
}
