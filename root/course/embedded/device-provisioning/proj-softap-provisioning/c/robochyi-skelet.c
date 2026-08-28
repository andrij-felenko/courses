#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "nvs.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"

typedef enum {
    ST_BOOT,          // щойно ввімкнулись або скинуті
    ST_PROVISION_AP,  // портал піднято, чекаємо облікові дані
    ST_RECEIVED,      // форму прийнято й провалідовано (кандидати на руках)
    ST_PROVING,       // APSTA: реально пробуємо STA-підключення з тайм-аутом
    ST_CONNECTED,     // STA довело себе — дістали IP; далі живемо тут
} prov_state_t;

static prov_state_t   g_state;
static EventGroupHandle_t g_wifi_events;

// Біти в групі подій: що прилетіло від Wi-Fi-драйвера
#define BIT_GOT_IP        BIT0   // дістали IP у STA — доказ підключення
#define BIT_STA_FAILED    BIT1   // STA відвалилось (нема мережі / хибний пароль)

// Кандидати, які ще НЕ довели себе. Живуть тут, поки PROVING не винесе вирок.
static char g_ssid[33];
static char g_pass[65];

// Причина останньої невдачі — щоб показати користувачеві щось людське
static uint8_t g_last_fail_reason;
