#include "platform.h"

#include <string.h>

static uint32_t g_now_ms;

static uint8_t  g_flash[FLASH_SECTOR_COUNT][FLASH_SECTOR_SIZE];
static uint32_t g_erase_count[FLASH_SECTOR_COUNT];

static bool  g_sw_enable;        // дозвіл від прошивки
static bool  g_hw_enable;        // дозвіл від зовнішнього супервізора
static uint32_t g_last_pulse_ms;

static float g_pwm_throttle;
static float g_pwm_steering;
static bool  g_brake;
static bool  g_beacon;
static bool  g_low_power;

static bool     g_radio_up;
static uint32_t g_radio_bytes;

static float clampf(float v, float lo, float hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

void plat_init(void) {
    g_now_ms = 0U;
    memset(g_flash, 0xFF, sizeof g_flash);   // стерта комірка NOR — усі одиниці
    memset(g_erase_count, 0, sizeof g_erase_count);

    g_sw_enable = false;
    g_hw_enable = false;
    g_last_pulse_ms = 0U;

    g_pwm_throttle = 0.0f;
    g_pwm_steering = 0.0f;
    g_brake = true;
    g_beacon = false;
    g_low_power = false;

    g_radio_up = false;
    g_radio_bytes = 0U;
}

uint32_t plat_now_ms(void) { return g_now_ms; }

void plat_advance_ms(uint32_t dt_ms) { g_now_ms += dt_ms; }

void plat_set_power_enable(bool on) { g_sw_enable = on; }

bool plat_power_enabled(void) { return g_sw_enable && g_hw_enable; }

void plat_set_actuators(float throttle, float steering) {
    // У регістри ШІМ значення лягають завжди, але на затвори вони потраплять
    // лише тоді, коли обидва дозволи — програмний і апаратний — активні.
    g_pwm_throttle = clampf(throttle, -1.0f, 1.0f);
    g_pwm_steering = clampf(steering, -1.0f, 1.0f);
}

float plat_throttle_out(void) { return plat_power_enabled() ? g_pwm_throttle : 0.0f; }

float plat_steering_out(void) { return plat_power_enabled() ? g_pwm_steering : 0.0f; }

void plat_set_brake(bool on) { g_brake = on; }

bool plat_brake(void) { return g_brake; }

void plat_pulse_interlock(void) {
    // Імпульс перезаряджає накачувальний конденсатор супервізора.
    g_last_pulse_ms = g_now_ms;
    g_hw_enable = true;
}

void plat_interlock_service(void) {
    // Логіка зовнішньої мікросхеми: витримка минула без імпульсу — ENABLE у нуль.
    if ((uint32_t)(g_now_ms - g_last_pulse_ms) > INTERLOCK_HOLD_MS) {
        g_hw_enable = false;
    }
}

bool plat_interlock_enabled(void) { return g_hw_enable; }

void plat_set_beacon(bool on) { g_beacon = on; }

bool plat_beacon(void) { return g_beacon; }

void plat_set_low_power(bool on) { g_low_power = on; }

bool plat_low_power(void) { return g_low_power; }

flash_status_t plat_flash_erase(uint16_t sector) {
    if (sector >= FLASH_SECTOR_COUNT) return FLASH_ERR_RANGE;
    memset(g_flash[sector], 0xFF, FLASH_SECTOR_SIZE);
    g_erase_count[sector]++;
    return FLASH_OK;
}

flash_status_t plat_flash_write(uint16_t sector, uint16_t offset, const void *src, uint16_t len) {
    if (sector >= FLASH_SECTOR_COUNT) return FLASH_ERR_RANGE;
    if ((uint32_t)offset + len > FLASH_SECTOR_SIZE) return FLASH_ERR_RANGE;

    // NOR уміє лише гасити одиниці в нулі: запис поверх зайнятих байтів
    // мовчки зіпсував би сусідній запис, тому це помилка, а не «якось буде».
    for (uint16_t i = 0; i < len; i++) {
        if (g_flash[sector][offset + i] != 0xFFU) return FLASH_ERR_NOT_ERASED;
    }
    memcpy(&g_flash[sector][offset], src, len);
    return FLASH_OK;
}

flash_status_t plat_flash_read(uint16_t sector, uint16_t offset, void *dst, uint16_t len) {
    if (sector >= FLASH_SECTOR_COUNT) return FLASH_ERR_RANGE;
    if ((uint32_t)offset + len > FLASH_SECTOR_SIZE) return FLASH_ERR_RANGE;
    memcpy(dst, &g_flash[sector][offset], len);
    return FLASH_OK;
}

uint32_t plat_flash_erase_count(uint16_t sector) {
    return (sector < FLASH_SECTOR_COUNT) ? g_erase_count[sector] : 0U;
}

void plat_radio_set_up(bool up) { g_radio_up = up; }

size_t plat_radio_send(const void *data, size_t len) {
    (void)data;
    if (!g_radio_up) return 0U;                 // ефір мовчить — нічого не пішло
    size_t accepted = (len > RADIO_MTU) ? RADIO_MTU : len;
    g_radio_bytes += (uint32_t)accepted;
    return accepted;
}

uint32_t plat_radio_bytes_sent(void) { return g_radio_bytes; }
