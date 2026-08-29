/*
 * Стенд перевірки образу: той самий код, що в завантажувачі, зібраний під
 * хост. На пристрої замість читання файла буфер — це слот завантаження
 * у Flash, а замість argv ключ береться з захищеного сектора.
 *
 *   ./verify firmware-revB-v2.4.0.signed.bin root-pubkey.bin [лічильник]
 */
#include "image_verify.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Слот застосунку найбільшої з ревізій плюс заголовок. Статичний масив:
   динамічної пам'яті в завантажувачі немає, і _Alignas дає ту саму
   4-байтну межу, що її вимагає розбір заголовка. */
#define SLOT_CAPACITY (512u * 1024u)
static _Alignas(4) uint8_t g_download_slot[RELEASE_HEADER_SIZE + SLOT_CAPACITY];

static unsigned long g_kick_count = 0u;

/* На пристрої тут стоїть HAL_IWDG_Refresh(&hiwdg). */
static void watchdog_kick(void *user)
{
    (void)user;
    ++g_kick_count;
}

static size_t read_file(const char *path, uint8_t *buffer, size_t capacity)
{
    FILE *file = fopen(path, "rb");
    if (file == NULL) {
        fprintf(stderr, "не відкривається %s\n", path);
        return 0u;
    }

    size_t got = fread(buffer, 1u, capacity, file);
    /* Файл, що не влазить у слот, читати далі нема сенсу — але й мовчки
       обрізати його не можна: це виглядало б як обірваний образ. */
    int overflow = (got == capacity) && (fgetc(file) != EOF);
    fclose(file);

    if (overflow) {
        fprintf(stderr, "%s більший за слот завантаження (%zu Б)\n",
                path, capacity);
        return 0u;
    }
    if (got == 0u) {
        fprintf(stderr, "%s порожній\n", path);
    }
    return got;
}

int main(int argc, char **argv)
{
    if (argc < 3 || argc > 4) {
        fprintf(stderr,
                "вжиток: %s <образ.signed.bin> <root-pubkey.bin> [лічильник]\n",
                argv[0]);
        return 2;
    }

    uint32_t active_counter = 0u;
    if (argc == 4) {
        char *end = NULL;
        unsigned long value = strtoul(argv[3], &end, 10);
        if (end == argv[3] || *end != '\0' || value > 0xFFFFFFFFul) {
            fprintf(stderr, "лічильник '%s' не є числом\n", argv[3]);
            return 2;
        }
        active_counter = (uint32_t)value;
    }

    size_t image_len = read_file(argv[1], g_download_slot,
                                 sizeof g_download_slot);
    if (image_len == 0u) {
        return 1;
    }

    uint8_t pubkey[65];
    size_t key_len = read_file(argv[2], pubkey, sizeof pubkey);
    if (key_len != sizeof pubkey || pubkey[0] != 0x04u) {
        fprintf(stderr, "%s не є непакованою точкою P-256 (65 Б, 0x04)\n",
                argv[2]);
        return 1;
    }

    const release_verify_ctx_t ctx = {
        .root_pubkey = pubkey,
        .root_pubkey_len = key_len,
        .watchdog_kick = watchdog_kick,
        .watchdog_user = NULL,
    };

    const release_header_t *hdr = NULL;
    release_status_t status = release_verify_image(&ctx, g_download_slot,
                                                   image_len, active_counter,
                                                   SLOT_CAPACITY, &hdr);
    if (status != RELEASE_OK) {
        fprintf(stderr, "ОБРАЗ ВІДХИЛЕНО: %s\n", release_status_text(status));
        return 1;
    }

    uint8_t version[3];
    release_version_unpack(hdr->version_packed, version);
    printf("образ прийнято: v%u.%u.%u, тіло %u Б, лічильник %u, маска 0x%04X\n",
           version[0], version[1], version[2],
           hdr->payload_size, hdr->security_counter, hdr->hw_mask);
    printf("сторожовий таймер поглажено %lu разів\n", g_kick_count);
    return 0;
}
