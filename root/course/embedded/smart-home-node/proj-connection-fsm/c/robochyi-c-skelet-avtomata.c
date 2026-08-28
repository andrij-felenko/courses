#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include "esp_random.h"       // esp_random(): апаратний ГВЧ ESP32
#include "mqtt_client.h"      // ESP-MQTT: esp_mqtt_client_*

// --- Стани мережевого шару. Рівно один активний будь-якої миті. ---
typedef enum {
    NET_OFFLINE = 0,   // зв'язку нема, зараз не шукаємо
    NET_CONNECTING,    // наказали з'єднатися, чекаємо вердикту
    NET_ONLINE,        // зв'язок є — звітуємо й слухаємо
    NET_BACKOFF,       // щойно не вийшло — тримаємо паузу до наступної спроби
} net_state_t;

// --- Параметри відкату (у мілісекундах) ---
#define BACKOFF_BASE_MS    1000u      // перша стеля після невдачі: 1 с
#define BACKOFF_MAX_MS    60000u      // дах: далі стеля не росте
#define CONNECT_TIMEOUT_MS 8000u      // скільки ждемо CONNACK, поки не визнати невдачу

// --- Усе, чим живе автомат ---
static net_state_t g_net_state   = NET_OFFLINE;
static uint32_t    g_backoff_ceil = BACKOFF_BASE_MS;  // поточна СТЕЛЯ відкату: 1·2·4·8… с, росте до BACKOFF_MAX_MS
static uint32_t    g_backoff_wait = 0;                // фактична пауза ЦЬОГО відкату (повний джитер 0..стеля), кинута РАЗ на вході
static uint32_t    t_state_enter  = 0;                // коли увійшли в поточний стан, мс
static esp_mqtt_client_handle_t g_client = NULL;

// --- ЄДИНЕ джерело правди про зв'язок для решти прошивки ---
static bool g_net_up = false;                         // == (g_net_state == NET_ONLINE)
