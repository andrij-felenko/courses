#include "platform.h"

/* Кілька типових точок на шкалі «мікроконтролер — Linux SoC».
 * Пропускна здатність — практична, приблизно половина пікової. */
static const platform_t k_platforms[] = {
    { "ESP32-S3, PSRAM 8 MB (OctoSPI)",      55.0,    8.0 },
    { "STM32H7, AXI SRAM 0.5 MB",           800.0,    0.5 },
    { "STM32H7 + HyperRAM 32 MB (x8 DDR)",  180.0,   32.0 },
    { "SoC + DDR3-1066 x16, 128 MB",       1000.0,  128.0 },
    { "SoC + LPDDR4 x32, 512 MB",          6000.0,  512.0 },
};

const platform_t *platform_table(size_t *count)
{
    if (count != NULL)
        *count = sizeof(k_platforms) / sizeof(k_platforms[0]);
    return k_platforms;
}

platform_check_t platform_check(const platform_t *platform, const video_budget_t *budget)
{
    platform_check_t result;

    result.bus_load_percent = budget->dram_mbytes_s / platform->bus_mbytes_s * 100.0;
    result.ram_load_percent = budget->ram_pool_mb   / platform->ram_mb       * 100.0;

    /* Пам'ять судимо першою: коли буфери не вміщуються, розмова про шину
     * уже безпредметна — конвеєр не запуститься взагалі. */
    if (result.ram_load_percent > 100.0)
        result.verdict = FIT_NO_RAM;
    else if (result.bus_load_percent > 100.0)
        result.verdict = FIT_BUS_OVERLOAD;
    else if (result.bus_load_percent > BUS_SAFE_PERCENT)
        result.verdict = FIT_RISKY;
    else
        result.verdict = FIT_OK;

    return result;
}

const char *platform_fit_text(platform_fit_t fit)
{
    switch (fit) {
        case FIT_OK:            return "запас є";
        case FIT_RISKY:         return "на межі: понад 60 % шини, зриви FIFO на піках";
        case FIT_BUS_OVERLOAD:  return "шина не тягне";
        case FIT_NO_RAM:        return "бракує пам'яті під кадрові буфери";
    }
    return "?";
}
