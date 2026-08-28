#include "esp_system.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "esp_crc.h"
#include "nvs.h"
#include "nvs_flash.h"

#define RTC_MAGIC        0xB007C0DEu   // вартовий структури в RTC
#define BURST_WINDOW_S   30            // збої ближче 30 с — одна серія
#define FAULT_THRESHOLD  5             // щільних рестартів → ескалація

static const char *TAG = "reboot";

typedef struct {
    uint32_t magic;        // RTC_MAGIC, якщо структура жива
    uint32_t fail_cnt;     // патологічних рестартів у поточній серії
    uint32_t last_uptime;  // скільки секунд прожив перед попереднім збоєм
    uint32_t crc;          // CRC32 над попередніми полями
} boot_state_t;

RTC_NOINIT_ATTR static boot_state_t s_bs;

// CRC над усіма полями, крім самого crc (останні 4 байти структури)
static uint32_t bs_crc(const boot_state_t *b) {
    return esp_crc32_le(0, (const uint8_t *)b, sizeof(*b) - sizeof(b->crc));
}

static bool bs_valid(const boot_state_t *b) {
    return b->magic == RTC_MAGIC && b->crc == bs_crc(b);
}

static void bs_commit(boot_state_t *b) {   // перерахувати CRC після зміни полів
    b->magic = RTC_MAGIC;
    b->crc = bs_crc(b);
}
