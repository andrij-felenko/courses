/* modifier_inspect.c — декодування та аналіз 64-бітних модифікаторів DRM */
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <drm_fourcc.h>

/* Отримання назви виробника за 8-бітним ідентифікатором */
const char *drm_modifier_vendor_name(uint8_t vendor)
{
    switch (vendor) {
        case DRM_FORMAT_MOD_VENDOR_NONE:     return "Generic (Standard)";
        case DRM_FORMAT_MOD_VENDOR_INTEL:    return "Intel";
        case DRM_FORMAT_MOD_VENDOR_AMD:      return "AMD";
        case DRM_FORMAT_MOD_VENDOR_NVIDIA:   return "NVIDIA";
        case DRM_FORMAT_MOD_VENDOR_SAMSUNG:  return "Samsung";
        case DRM_FORMAT_MOD_VENDOR_QCOM:     return "Qualcomm";
        case DRM_FORMAT_MOD_VENDOR_VIVANTE:  return "Vivante";
        case DRM_FORMAT_MOD_VENDOR_BROADCOM: return "Broadcom";
        case DRM_FORMAT_MOD_VENDOR_ARM:      return "Arm (AFBC)";
        case DRM_FORMAT_MOD_VENDOR_ALLWINNER:return "Allwinner";
        case DRM_FORMAT_MOD_VENDOR_AMLOGIC:  return "Amlogic";
        default:                             return "Unknown Vendor";
    }
}

/* Декодування опису конкретного модифікатора */
void print_drm_modifier_info(uint64_t modifier)
{
    if (modifier == DRM_FORMAT_MOD_INVALID) {
        printf("Модифікатор: DRM_FORMAT_MOD_INVALID (Неявний вибір драйвером)\n");
        return;
    }

    if (modifier == DRM_FORMAT_MOD_LINEAR) {
        printf("Модифікатор: DRM_FORMAT_MOD_LINEAR (Суцільний растровий порядок рядків, CPU-сумісний)\n");
        return;
    }

    uint8_t vendor = fourcc_mod_get_vendor(modifier);
    uint64_t val = modifier & 0x00ffffffffffffffULL;

    printf("Модифікатор: 0x%016" PRIx64 "\n", modifier);
    printf("  Виробник: %s (ID: 0x%02x)\n", drm_modifier_vendor_name(vendor), vendor);
    printf("  Код конфігурації: 0x%014" PRIx64 "\n", val);

    if (vendor == DRM_FORMAT_MOD_VENDOR_INTEL) {
        switch (modifier) {
            case I915_FORMAT_MOD_X_TILED:
                printf("  Тип розкладки: Intel X-Tiled (Тайли 512x8 байтів, 4 КБ)\n");
                break;
            case I915_FORMAT_MOD_Y_TILED:
                printf("  Тип розкладки: Intel Y-Tiled (Тайли 128x32 байти, 4 КБ, 2D-локальність)\n");
                break;
            case I915_FORMAT_MOD_4_TILED:
                printf("  Тип розкладки: Intel Tile4 (Базовий тайлінг DG2 / Meteor Lake)\n");
                break;
            case I915_FORMAT_MOD_4_TILED_DG2_RC_CCS:
                printf("  Тип розкладки: Intel Tile4 + Render Decompression (Апаратне стиснення CCS)\n");
                break;
            default:
                printf("  Тип розкладки: Intel Специфічний тайлінг/стиснення\n");
                break;
        }
    } else if (vendor == DRM_FORMAT_MOD_VENDOR_ARM) {
        uint64_t block_size = val & 0x0f;
        printf("  Тип розкладки: Arm FrameBuffer Compression (AFBC)\n");
        if (block_size == 1) printf("  Розмір суперблока: 16x16 пікселів\n");
        else if (block_size == 2) printf("  Розмір суперблока: 32x8 пікселів\n");

        if (modifier & AFBC_FORMAT_MOD_YTR)
            printf("  Опція: YTR (Трансформація колірного простору RGB->YUV увімкнена)\n");
        if (modifier & AFBC_FORMAT_MOD_SPARSE)
            printf("  Опція: SPARSE (Підтримка розріджених порожніх блоків)\n");
    }
}
