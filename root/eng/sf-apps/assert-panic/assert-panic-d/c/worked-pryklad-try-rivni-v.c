#include "esp_log.h"
#include <assert.h>
static const char *TAG = "cmd_handler";

typedef void (*cmd_fn_t)(const uint8_t *payload, size_t len);
static cmd_fn_t s_handlers[CMD_COUNT];          // заповнюється при старті

typedef struct {
    uint32_t magic;
    uint32_t value;
    uint32_t crc;
} critical_state_t;
extern critical_state_t g_state;                // у RAM

esp_err_t handle_command(uint8_t cmd_id, const uint8_t *payload, size_t len) {
    // Рівень 1 — ОЧІКУВАНЕ: невідома команда ззовні (вхід із поля)
    if (cmd_id >= CMD_COUNT) {
        ESP_LOGW(TAG, "unknown cmd 0x%02x", cmd_id);
        return ESP_ERR_NOT_SUPPORTED;           // код повернення — вирішує викликач
    }

    // Рівень 2 — ПОРУШЕНЕ ПРИПУЩЕННЯ: обробник мусить бути заповнений
    assert(s_handlers[cmd_id] != NULL);         // NULL → баг ініціалізації

    // Рівень 3 — НЕВІДНОВНИЙ СТАН: критична структура в RAM зіпсована
    uint32_t expected = crc32_calc(&g_state, offsetof(critical_state_t, crc));
    if (g_state.crc != expected || g_state.magic != STATE_MAGIC) {
        ESP_LOGE(TAG, "state corrupt! crc=0x%08lx exp=0x%08lx", g_state.crc, expected);
        esp_system_abort("state corrupt");      // паніка → reset
    }

    s_handlers[cmd_id](payload, len);
    return ESP_OK;
}
