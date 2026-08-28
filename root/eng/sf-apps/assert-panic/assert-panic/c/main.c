#include "esp_log.h"
#include <assert.h>
static const char *TAG = "cmd_handler";

// Таблиця обробників — заповнюється при ініціалізації (не NULL!)
typedef void (*cmd_fn_t)(const uint8_t *payload, size_t len);
static cmd_fn_t s_handlers[CMD_COUNT];

// Критична структура зі своєю контрольною сумою
typedef struct {
    uint32_t magic;
    uint32_t value;
    uint32_t crc;
} critical_state_t;
extern critical_state_t g_state;  // у RAM

esp_err_t handle_command(uint8_t cmd_id, const uint8_t *payload, size_t len) {
    // Рівень 1: ОЧІКУВАНА ситуація — невідома команда від користувача
    if (cmd_id >= CMD_COUNT) {
        ESP_LOGW(TAG, "unknown cmd 0x%02x", cmd_id);
        return ESP_ERR_NOT_SUPPORTED;   // код повернення — викликач вирішить
    }

    // Рівень 2: ПОРУШЕННЯ ПРИПУЩЕННЯ — обробник мусить бути заповнений
    // (баг ініціалізації, якщо NULL)
    assert(s_handlers[cmd_id] != NULL);

    // Рівень 3: НЕВІДНОВНИЙ СТАН — структура в RAM зіпсована
    uint32_t expected_crc = crc32_calc(&g_state, offsetof(critical_state_t, crc));
    if (g_state.crc != expected_crc || g_state.magic != STATE_MAGIC) {
        ESP_LOGE(TAG, "state corrupt! crc=0x%08lx exp=0x%08lx", g_state.crc, expected_crc);
        esp_system_abort("state corrupt");   // паніка → reset
    }

    s_handlers[cmd_id](payload, len);
    return ESP_OK;
}
