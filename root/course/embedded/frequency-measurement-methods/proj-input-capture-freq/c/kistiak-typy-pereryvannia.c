#include <stdint.h>
#include <stdbool.h>

// Таймер тактується від APB = 1 МГц (1 тик = 1 мкс). Підставте свою частоту.
#define TIMER_HZ        1000000u   // частота лічби таймера-захоплення, Гц
#define TIMER_ARR       0xFFFFu    // межа лічби 16-біт таймера (auto-reload)

// Оновлюються в перериваннях, читаються з головного циклу → volatile.
static volatile uint32_t g_ovf      = 0;  // лічильник переповнень таймера
static volatile uint64_t g_last_cap = 0;  // повна позиція попереднього фронту (48-біт)
static volatile uint64_t g_period   = 0;  // останній виміряний період у тиках
static volatile bool     g_primed   = false; // чи був уже хоч один фронт
static volatile uint32_t g_seq      = 0;  // лічильник готових вимірів (для свіжості)
