#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_PATH_LEN 1024
#define MAX_SIGNATURES 8

typedef enum {
    RISK_NONE = 0,
    RISK_PATENT_AVC,
    RISK_PATENT_HEVC,
    RISK_PATENT_AAC,
    RISK_PATENT_MPEG2
} PatentRiskCategory;

typedef struct {
    const char *signature;
    const char *codec_name;
    const char *pool_name;
    PatentRiskCategory category;
} CodecSignature;

static const CodecSignature KNOWN_SIGNATURES[MAX_SIGNATURES] = {
    {"libx264",     "H.264 / AVC",    "Via LA (MPEG LA)",      RISK_PATENT_AVC},
    {"libgstx264",  "H.264 / AVC",    "Via LA (MPEG LA)",      RISK_PATENT_AVC},
    {"libx265",     "H.265 / HEVC",   "Access Advance / Via",  RISK_PATENT_HEVC},
    {"libgstx265",  "H.265 / HEVC",   "Access Advance / Via",  RISK_PATENT_HEVC},
    {"libfaac",     "AAC Audio",      "Via LA (Via Licensing)", RISK_PATENT_AAC},
    {"libfdk_aac",  "AAC Audio",      "Via LA (Via Licensing)", RISK_PATENT_AAC},
    {"libmpeg2",    "MPEG-2 Video",   "MPEG LA (Expired in US)",RISK_PATENT_MPEG2},
    {"libgstaac",   "AAC Audio",      "Via LA (Via Licensing)", RISK_PATENT_AAC}
};

static void analyze_buffer(const unsigned char *buffer, size_t size, const char *filepath) {
    bool found_any = false;
    printf("[*] Аудит файлу: %s (%zu байтів)\n", filepath, size);

    for (int i = 0; i < MAX_SIGNATURES; ++i) {
        const char *sig = KNOWN_SIGNATURES[i].signature;
        size_t sig_len = strlen(sig);
        if (sig_len > size) continue;

        for (size_t pos = 0; pos <= size - sig_len; ++pos) {
            if (memcmp(buffer + pos, sig, sig_len) == 0) {
                printf("  [!] ВИЯВЛЕНО ПАТЕНТНИЙ РИЗИК:\n");
                printf("      - Сигнатура: %s\n", sig);
                printf("      - Технологія: %s\n", KNOWN_SIGNATURES[i].codec_name);
                printf("      - Патентний пул: %s\n", KNOWN_SIGNATURES[i].pool_name);
                found_any = true;
                break;
            }
        }
    }

    if (!found_any) {
        printf("  [+] Чисто: запатентованих кодеків не виявлено.\n");
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях до ELF-файлу>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *filepath = argv[1];
    FILE *f = fopen(filepath, "rb");
    if (!f) {
        perror("Помилка відкриття файлу");
        return EXIT_FAILURE;
    }

    fseek(f, 0, SEEK_END);
    long file_size = ftell(f);
    fseek(f, 0, SEEK_SET);

    if (file_size <= 0) {
        fclose(f);
        fprintf(stderr, "Помилка: порожній файл\n");
        return EXIT_FAILURE;
    }

    unsigned char *buffer = (unsigned char *)malloc((size_t)file_size);
    if (!buffer) {
        fclose(f);
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return EXIT_FAILURE;
    }

    size_t read_bytes = fread(buffer, 1, (size_t)file_size, f);
    fclose(f);

    if (read_bytes != (size_t)file_size) {
        free(buffer);
        fprintf(stderr, "Помилка читання даних файлу\n");
        return EXIT_FAILURE;
    }

    analyze_buffer(buffer, (size_t)file_size, filepath);
    free(buffer);
    return EXIT_SUCCESS;
}
