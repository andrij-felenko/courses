#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"

#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAIL_BIT      BIT1
#define WARM_FAIL_LIMIT    3      // стільки теплих провалів поспіль — і викидаємо кеш

static EventGroupHandle_t s_wifi_events;
static bool   s_tried_warm   = false;   // цей сеанс почали з кешу?
static int    s_retry        = 0;       // лічильник спроб у межах сеансу
#define MAX_RETRY 5

// Нарахувати провал теплого старту в NVS (читаємо-нарощуємо-пишемо).
static void bump_fail_streak(void)
{
    fastconn_t st;
    if (!fastconn_load(&st)) return;       // нема блоба — нема чого нарощувати
    if (st.fail_streak < 0xFFFF) st.fail_streak++;
    if (st.fail_streak >= WARM_FAIL_LIMIT) {
        // Заготовка стабільно шкідлива — стираємо її, далі ходимо холодним.
        nvs_handle_t h;
        if (nvs_open(NVS_NS, NVS_READWRITE, &h) == ESP_OK) {
            nvs_erase_key(h, NVS_KEY);
            nvs_commit(h);
            nvs_close(h);
            ESP_LOGW(TAG, "warm failed %u times — blob dropped", st.fail_streak);
            return;
        }
    }
    fastconn_save(&st);
}

// Єдина, незалежна від причини відповідь на провал теплого старту: нарахувати
// провал у NVS, скинути канал-підказку в нуль (далі — повний скан) і почати
// холодну фазу зі свіжим бюджетом спроб. Спрацьовує рівно раз за сеанс — щойно
// s_tried_warm гасне, повторно сюди вже не потрапляємо.
static void warm_to_cold_fallback(void)
{
    bump_fail_streak();
    apply_sta_config(NULL);      // NULL → channel = 0
    s_tried_warm = false;        // теплого більше немає — далі холодний шлях
    s_retry      = 0;            // холодній фазі — свій бюджет спроб
}

static void wifi_event_handler(void *arg, esp_event_base_t base,
                               int32_t id, void *data)
{
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();                 // перший запит на з'єднання
        return;
    }

    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        wifi_event_sta_disconnected_t *e =
            (wifi_event_sta_disconnected_t *)data;
        ESP_LOGW(TAG, "disconnected, reason=%d", e->reason);

        // Канал-підказка не спрацювала (точку переставили / немає поряд):
        // скидаємо канал у 0 і далі вже пробуємо повним сканом.
        if (s_tried_warm && e->reason == WIFI_REASON_NO_AP_FOUND) {
            ESP_LOGW(TAG, "channel hint missed — falling back to full scan");
            warm_to_cold_fallback();
        }
        // Провал третій — «теплий не злетів, причина будь-яка»: спроби на
        // теплому вичерпано, а ми досі теплі, тож причина була НЕ NO_AP_FOUND
        // (auth, таймаут рукостискання — каналом їх не полікуєш). Відповідь та
        // сама — покинути теплий і дати холодному один повний скан.
        else if (s_tried_warm && s_retry >= MAX_RETRY) {
            ESP_LOGW(TAG, "warm exhausted (reason=%d) — one cold attempt", e->reason);
            warm_to_cold_fallback();
        }

        if (s_retry < MAX_RETRY) {
            s_retry++;
            esp_wifi_connect();             // повторюємо (уже, можливо, з каналом 0)
        } else {
            // Спроби вичерпано вже й на холодному — чесна відмова, а не
            // наслідок нашої оптимізації.
            xEventGroupSetBits(s_wifi_events, WIFI_FAIL_BIT);
        }
        return;
    }
}

static void ip_event_handler(void *arg, esp_event_base_t base,
                             int32_t id, void *data)
{
    if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t *e = (ip_event_got_ip_t *)data;
        s_retry = 0;
        capture_and_save(&e->ip_info);      // зберігаємо свіжі заготовки
        xEventGroupSetBits(s_wifi_events, WIFI_CONNECTED_BIT);
    }
}
