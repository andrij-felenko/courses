#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

#define ASSET_UNKNOWN           0
#define ASSET_FONT_TTF          1
#define ASSET_TFLITE_ML         2
#define ASSET_HIGH_ENTROPY_BLOB 3

typedef struct {
    uint32_t offset;
    uint32_t size;
    int asset_type;
    double entropy;
    uint8_t sha256_stub[32];
} asset_descriptor_t;

/* Обчислення ентропії Шеннона для блоку байтів */
double calculate_entropy(const uint8_t *data, size_t len) {
    if (len == 0) return 0.0;
    uint32_t counts[256] = {0};
    for (size_t i = 0; i < len; ++i) {
        counts[data[i]]++;
    }
    double entropy = 0.0;
    for (int i = 0; i < 256; ++i) {
        if (counts[i] > 0) {
            double p = (double)counts[i] / (double)len;
            entropy -= p * (log(p) / log(2.0));
        }
    }
    return entropy;
}

/* Сканування буфера на наявність сигнатур не-кодових активів */
int scan_firmware_buffer(const uint8_t *buf, size_t buf_size,
                         asset_descriptor_t *out_assets, size_t max_assets,
                         size_t *found_count) {
    if (!buf || !out_assets || !found_count) return -1;
    *found_count = 0;

    for (size_t i = 0; i + 16 < buf_size; ++i) {
        if (*found_count >= max_assets) break;

        /* Перевірка сигнатури TrueType / OpenType */
        if ((buf[i] == 0x00 && buf[i+1] == 0x01 && buf[i+2] == 0x00 && buf[i+3] == 0x00) ||
            (memcmp(&buf[i], "OTTO", 4) == 0) ||
            (memcmp(&buf[i], "ttcf", 4) == 0)) {
            
            asset_descriptor_t *asset = &out_assets[*found_count];
            asset->offset = (uint32_t)i;
            asset->size = 4096; /* Оцінка розміру за таблицею офсетів */
            asset->asset_type = ASSET_FONT_TTF;
            asset->entropy = calculate_entropy(&buf[i], 1024);
            (*found_count)++;
            i += 256; /* Пропуск заголовка */
            continue;
        }

        /* Перевірка сигнатури TFLite FlatBuffers: на зміщенні +4 стоїть TFL3 */
        if (memcmp(&buf[i+4], "TFL3", 4) == 0) {
            asset_descriptor_t *asset = &out_assets[*found_count];
            asset->offset = (uint32_t)i;
            asset->size = *(const uint32_t*)&buf[i]; /* Розмір буфера FlatBuffer */
            asset->asset_type = ASSET_TFLITE_ML;
            asset->entropy = calculate_entropy(&buf[i], 1024);
            (*found_count)++;
            i += 512;
            continue;
        }
    }
    return 0;
}
