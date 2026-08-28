/* tpm2_log_parser.c — Повнофункціональний парсер TCG Event Log мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#include <openssl/sha.h>

#define TPM2_ALG_SHA1   0x0004
#define TPM2_ALG_SHA256 0x000B
#define TPM2_ALG_SHA384 0x000C

#define SHA1_DIGEST_SIZE   20
#define SHA256_DIGEST_SIZE 32
#define SHA384_DIGEST_SIZE 48

#define EV_NO_ACTION 0x0003
#define EV_SEPARATOR 0x0004

typedef struct {
    uint32_t pcr_index;
    uint32_t event_type;
    uint8_t  digest[SHA1_DIGEST_SIZE];
    uint32_t event_size;
} __attribute__((packed)) tcg_pcr_event_hdr_t;

typedef struct {
    uint16_t alg_id;
    uint16_t digest_size;
} alg_size_entry_t;

static uint16_t get_digest_size(uint16_t alg_id, const alg_size_entry_t *alg_table, uint32_t table_count) {
    for (uint32_t i = 0; i < table_count; ++i) {
        if (alg_table[i].alg_id == alg_id) {
            return alg_table[i].digest_size;
        }
    }
    switch (alg_id) {
        case TPM2_ALG_SHA1:   return SHA1_DIGEST_SIZE;
        case TPM2_ALG_SHA256: return SHA256_DIGEST_SIZE;
        case TPM2_ALG_SHA384: return SHA384_DIGEST_SIZE;
        default: return 0;
    }
}

static const char* get_event_type_name(uint32_t type) {
    switch (type) {
        case 0x00000001: return "EV_POST_CODE";
        case 0x00000003: return "EV_NO_ACTION";
        case 0x00000004: return "EV_SEPARATOR";
        case 0x00000005: return "EV_ACTION";
        case 0x00000008: return "EV_S_CRTM_VERSION";
        case 0x00000009: return "EV_CPU_MICROCODE";
        case 0x0000000A: return "EV_PLATFORM_CONFIG_FLAGS";
        case 0x00008001: return "EV_EFI_VARIABLE_DRIVER_CONFIG";
        case 0x00008002: return "EV_EFI_BOOT_SERVICES_APPLICATION";
        case 0x00008003: return "EV_EFI_BOOT_SERVICES_DYNAMIC";
        case 0x0000800E: return "EV_EFI_VARIABLE_AUTHORITY";
        default: return "EV_UNKNOWN";
    }
}

void pcr_extend_sha256(uint8_t pcr[SHA256_DIGEST_SIZE], const uint8_t event_digest[SHA256_DIGEST_SIZE]) {
    uint8_t buffer[SHA256_DIGEST_SIZE * 2];
    memcpy(buffer, pcr, SHA256_DIGEST_SIZE);
    memcpy(buffer + SHA256_DIGEST_SIZE, event_digest, SHA256_DIGEST_SIZE);
    
    SHA256(buffer, sizeof(buffer), pcr);
}

void print_hex(const char *label, const uint8_t *data, size_t len) {
    printf("%s: ", label);
    for (size_t i = 0; i < len; ++i) {
        printf("%02x", data[i]);
    }
    printf("\n");
}

int main(int argc, char *argv[]) {
    const char *path = "/sys/kernel/security/tpm0/binary_bios_measurements";
    if (argc > 1) {
        path = argv[1];
    }

    FILE *f = fopen(path, "rb");
    if (!f) {
        fprintf(stderr, "Помилка відкриття логу (%s): %s\n", path, strerror(errno));
        return EXIT_FAILURE;
    }

    /* Читання першого заголовка TCG 1.2 Header */
    tcg_pcr_event_hdr_t header;
    if (fread(&header, sizeof(header), 1, f) != 1) {
        fprintf(stderr, "Помилка зчитування заголовка логу\n");
        fclose(f);
        return EXIT_FAILURE;
    }

    uint8_t *event_data = (uint8_t*)malloc(header.event_size);
    if (!event_data) {
        fclose(f);
        return EXIT_FAILURE;
    }

    if (fread(event_data, header.event_size, 1, f) != 1) {
        fprintf(stderr, "Помилка зчитування SpecIDEvent\n");
        free(event_data);
        fclose(f);
        return EXIT_FAILURE;
    }

    alg_size_entry_t alg_table[16];
    uint32_t num_algs = 0;

    if (header.event_size >= 0x1C) {
        uint32_t count = *(uint32_t*)(event_data + 0x18);
        if (count > 16) count = 16;
        num_algs = count;

        size_t offset = 0x1C;
        for (uint32_t i = 0; i < count; ++i) {
            if (offset + 4 > header.event_size) break;
            alg_table[i].alg_id = *(uint16_t*)(event_data + offset);
            alg_table[i].digest_size = *(uint16_t*)(event_data + offset + 2);
            offset += 4;
        }
    }
    free(event_data);

    uint8_t simulated_pcrs[8][SHA256_DIGEST_SIZE];
    memset(simulated_pcrs, 0, sizeof(simulated_pcrs));

    printf("Парсинг TCG 2.0 Agile Event Log (%s)...\n", path);

    size_t event_count_total = 0;
    while (!feof(f)) {
        uint32_t pcr_index, event_type, count;
        if (fread(&pcr_index, sizeof(pcr_index), 1, f) != 1) break;
        if (fread(&event_type, sizeof(event_type), 1, f) != 1) break;
        if (fread(&count, sizeof(count), 1, f) != 1) break;

        event_count_total++;

        for (uint32_t i = 0; i < count; ++i) {
            uint16_t alg_id;
            if (fread(&alg_id, sizeof(alg_id), 1, f) != 1) break;

            uint16_t digest_sz = get_digest_size(alg_id, alg_table, num_algs);
            if (digest_sz == 0) {
                fprintf(stderr, "Невідомий алгоритм: 0x%04x\n", alg_id);
                fclose(f);
                return EXIT_FAILURE;
            }

            uint8_t digest_buf[64];
            if (fread(digest_buf, digest_sz, 1, f) != 1) break;

            if (alg_id == TPM2_ALG_SHA256 && pcr_index < 8) {
                if (event_type != EV_NO_ACTION) {
                    pcr_extend_sha256(simulated_pcrs[pcr_index], digest_buf);
                }
            }
        }

        uint32_t event_size;
        if (fread(&event_size, sizeof(event_size), 1, f) != 1) break;
        fseek(f, event_size, SEEK_CUR);
    }

    fclose(f);

    printf("Успішно оброблено подій: %zu\n", event_count_total);
    for (int i = 0; i < 8; ++i) {
        char label[64];
        snprintf(label, sizeof(label), "Відтворений PCR %d (SHA-256)", i);
        print_hex(label, simulated_pcrs[i], SHA256_DIGEST_SIZE);
    }

    return EXIT_SUCCESS;
}
