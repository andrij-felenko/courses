/* Демонстрація повного циклу: пробудження шини, перевірка блокування зон,
 * підпис зовнішнього дайджеста ключем зі слота, сон.
 *
 * Збірка:  cc -std=c11 -Wall -Wextra -O2 *.c -o atecc-sign
 * Запуск:  ./atecc-sign /dev/i2c-1 0 <64 шістнадцяткові символи дайджеста>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "atecc608.h"
#include "der_sig.h"
#include "i2c_linux.h"

static int hex_nibble(char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static bool parse_hex(const char *text, uint8_t *out, size_t len)
{
    if (strlen(text) != len * 2u) {
        return false;
    }
    for (size_t i = 0; i < len; i++) {
        int hi = hex_nibble(text[2 * i]);
        int lo = hex_nibble(text[2 * i + 1]);
        if (hi < 0 || lo < 0) {
            return false;
        }
        out[i] = (uint8_t)((hi << 4) | lo);
    }
    return true;
}

static void print_hex(const char *label, const uint8_t *data, size_t len)
{
    printf("%s", label);
    for (size_t i = 0; i < len; i++) {
        printf("%02x", data[i]);
    }
    printf("\n");
}

int main(int argc, char **argv)
{
    if (argc != 4) {
        fprintf(stderr, "вжиток: %s <шина> <слот 0..15> <дайджест-hex>\n", argv[0]);
        return 2;
    }

    char *end = NULL;
    long slot = strtol(argv[2], &end, 10);
    if (end == argv[2] || *end != '\0' || slot < 0 || slot > 15) {
        fprintf(stderr, "слот має бути числом від 0 до 15\n");
        return 2;
    }

    uint8_t digest[ATECC_DIGEST_LEN];
    if (!parse_hex(argv[3], digest, sizeof digest)) {
        fprintf(stderr, "дайджест має бути рівно 64 шістнадцятковими символами\n");
        return 2;
    }

    i2c_linux bus = { .fd = -1 };
    if (!i2c_linux_open(&bus, argv[1])) {
        return 1;
    }

    atecc_hal hal = i2c_linux_hal(&bus);
    atecc_dev dev;
    atecc_init(&dev, &hal, ATECC_ADDR_DEFAULT);

    int rc = 1;

    atecc_err err = atecc_wake(&dev);
    if (err != ATECC_OK) {
        fprintf(stderr, "пробудження: %s (%s)\n",
                atecc_strerror(err), atecc_status_str(dev.status));
        goto out;
    }
    printf("чип прокинувся\n");

    bool config_locked = false;
    bool data_locked = false;
    err = atecc_lock_state(&dev, &config_locked, &data_locked);
    if (err != ATECC_OK) {
        fprintf(stderr, "читання конфігурації: %s (%s)\n",
                atecc_strerror(err), atecc_status_str(dev.status));
        goto out;
    }
    printf("зона конфігурації: %s, зона даних: %s\n",
           config_locked ? "заблокована" : "відкрита",
           data_locked ? "заблокована" : "відкрита");

    if (!config_locked || !data_locked) {
        /* Незаблокований чип відхилить Sign — краще сказати це прямо,
         * ніж дати користувачеві розбирати код 0x0F. */
        fprintf(stderr, "%s: пройдіть фабричне блокування (Lock)\n",
                atecc_strerror(ATECC_ERR_NOT_LOCKED));
        goto out;
    }

    uint8_t signature[ATECC_SIGNATURE_LEN];
    err = atecc_sign_digest(&dev, (uint8_t)slot, digest, signature);
    if (err != ATECC_OK) {
        fprintf(stderr, "підпис: %s (%s)\n",
                atecc_strerror(err), atecc_status_str(dev.status));
        goto out;
    }

    print_hex("R = ", &signature[0], 32);
    print_hex("S = ", &signature[32], 32);

    uint8_t der[DER_SIG_MAX];
    size_t der_len = der_encode_signature(signature, der, sizeof der);
    if (der_len == 0) {
        fprintf(stderr, "не вдалося запакувати підпис у DER\n");
        goto out;
    }
    print_hex("DER = ", der, der_len);

    rc = 0;

out:
    /* Сон — не косметика: без нього чип тримає генератор до спрацювання
     * сторожового таймера й тягне мікроампери замість наноамперів. */
    atecc_sleep(&dev);
    i2c_linux_close(&bus);
    return rc;
}
