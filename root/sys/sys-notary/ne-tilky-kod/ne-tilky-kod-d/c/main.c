#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ASSET_TYPE_UNKNOWN 0
#define ASSET_TYPE_TTF_FONT 1
#define ASSET_TYPE_TFLITE_MODEL 2

typedef struct {
    uint32_t offset;
    uint32_t size;
    int type;
    char identifier[64];
} embedded_asset_t;

/* Сканування області пам'яті на наявність сигнатур шрифтів та нейромереж */
int find_embedded_assets(const uint8_t *rom_base, uint32_t rom_size,
                         embedded_asset_t *out_assets, int max_assets,
                         int *found_count) {
    if (!rom_base || !out_assets || !found_count) return -1;
    *found_count = 0;

    for (uint32_t i = 0; i + 16 < rom_size; ++i) {
        if (*found_count >= max_assets) break;

        /* Детекція TrueType/OpenType: версія 1.0 або тег OTTO */
        if ((rom_base[i] == 0x00 && rom_base[i+1] == 0x01 &&
             rom_base[i+2] == 0x00 && rom_base[i+3] == 0x00) ||
            (memcmp(&rom_base[i], "OTTO", 4) == 0)) {
            
            embedded_asset_t *a = &out_assets[*found_count];
            a->offset = i;
            a->type = ASSET_TYPE_TTF_FONT;
            snprintf(a->identifier, sizeof(a->identifier), "font-ttf-rom-0x%08X", i);
            a->size = 0; /* Визначається за таблицею numTables */
            (*found_count)++;
            i += 256;
            continue;
        }

        /* Детекція TensorFlow Lite Micro FlatBuffers */
        if (memcmp(&rom_base[i+4], "TFL3", 4) == 0) {
            embedded_asset_t *a = &out_assets[*found_count];
            a->offset = i;
            a->type = ASSET_TYPE_TFLITE_MODEL;
            a->size = *(const uint32_t*)&rom_base[i];
            snprintf(a->identifier, sizeof(a->identifier), "model-tflite-rom-0x%08X", i);
            (*found_count)++;
            i += 512;
            continue;
        }
    }
    return 0;
}
