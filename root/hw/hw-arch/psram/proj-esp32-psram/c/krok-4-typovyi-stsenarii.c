#define FB_W 320
#define FB_H 240

uint16_t *fb = heap_caps_malloc(FB_W * FB_H * sizeof(uint16_t),
                                MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
if (fb == NULL) { ESP_LOGE(TAG, "немає місця під кадр"); return; }

// малюємо у кадр як у звичайний масив — обмін по QSPI прихований
for (int y = 0; y < FB_H; y++)
    for (int x = 0; x < FB_W; x++)
        fb[y * FB_W + x] = (x ^ y) & 1 ? 0xFFFF : 0x0000;  // проста шахівниця
