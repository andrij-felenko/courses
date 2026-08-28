#include "esp_spp_api.h"

static char     line[64];      // буфер для одного рядка-команди
static uint8_t  len = 0;       // скільки символів уже зібрано
static uint32_t spp_handle;    // ідентифікатор відкритого з'єднання

// 1. Згодовуємо збирачу рівно стільки байтів, скільки принесла подія
static void feed(const uint8_t *buf, int n)
{
    for (int i = 0; i < n; i++) {
        char c = (char) buf[i];

        if (c == '\n' || c == '\r') {          // кінець рядка → команда готова
            if (len > 0) {
                line[len] = '\0';              // завершити С-рядок
                handle_command(line);          // розібрати її
                len = 0;                       // і почати збирати наступну
            }
        } else if (len < sizeof(line) - 1) {   // звичайний символ — у буфер
            line[len++] = c;
        } else {
            len = 0;                           // переповнення: скинути сміття
        }
    }
}

// 2. Дані приходять подією, тож ніякий цикл тут узагалі не чекає
static void spp_cb(esp_spp_cb_event_t event, esp_spp_cb_param_t *param)
{
    if (event == ESP_SPP_SRV_OPEN_EVT)
        spp_handle = param->srv_open.handle;
    else if (event == ESP_SPP_DATA_IND_EVT)
        feed(param->data_ind.data, param->data_ind.len);
}
