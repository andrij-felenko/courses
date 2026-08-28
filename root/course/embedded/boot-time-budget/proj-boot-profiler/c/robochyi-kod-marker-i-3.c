#include "esp_cpu.h"
#include "esp_clk_tree.h"   // дізнатися фактичну частоту ядра

// Скільки мікросекунд минуло від старту за лічильником тактів CPU.
// УВАГА: лічильник 32-бітний — на 240 МГц переповнюється за ~17.9 с,
// тож для довгого boot це наближення, для типового (сотні мс) — точне.
static int64_t cycles_to_us_since_reset(void)
{
    uint32_t cycles = esp_cpu_get_cycle_count();   // такти від старту ядра

    uint32_t cpu_hz = 0;
    esp_clk_tree_src_get_freq_hz(
        SOC_MOD_CLK_CPU, ESP_CLK_TREE_SRC_FREQ_PRECISION_CACHED, &cpu_hz);
    if (cpu_hz == 0) cpu_hz = 160000000u;   // запобіжник: типові 160 МГц

    return (int64_t)cycles * 1000000 / cpu_hz;
}
