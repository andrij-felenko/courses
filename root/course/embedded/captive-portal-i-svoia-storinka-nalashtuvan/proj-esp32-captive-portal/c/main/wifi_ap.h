#pragma once

#include <stdint.h>
#include "esp_err.h"
#include "esp_wifi.h"

/* Адреса самої точки доступу; на неї ж указує DNS-перехоплювач. */
#define WIFI_AP_IP_ADDR "192.168.4.1"
#define WIFI_AP_NETMASK "255.255.255.0"

/* Пул DHCP: .2–.10. Десяти адрес вистачає з запасом — портал обслуговує
 * одного користувача, решта клієнтів це фонові служби його ж телефона. */
#define WIFI_AP_DHCP_POOL_START "192.168.4.2"
#define WIFI_AP_DHCP_POOL_END   "192.168.4.10"

/* Скільки мереж максимум віддаємо у відповіді на сканування. */
#define WIFI_SCAN_MAX_RECORDS 16

/*
 * Піднімає мережевий стек: створює віртуальні інтерфейси AP і STA,
 * ініціалізує драйвер і вмикає режим AP+STA. Режим саме комбінований,
 * бо сканувати ефір можна лише станційною частиною радіотракту.
 */
esp_err_t wifi_stack_init(void);

/*
 * Запускає точку доступу зі статичною адресою WIFI_AP_IP_ADDR, вимкненим
 * і переналаштованим сервером DHCP (пул адрес + видача себе як DNS-сервера).
 * password == NULL або порожній рядок → відкрита мережа.
 */
esp_err_t wifi_ap_start(const char *ssid, const char *password);

/* Підключення станційної частини до збереженої мережі. */
esp_err_t wifi_sta_connect(const char *ssid, const char *password);

/*
 * Синхронне сканування ефіру. out має вміщати щонайменше *count записів;
 * після повернення *count — скільки мереж справді знайдено.
 */
esp_err_t wifi_ap_scan(wifi_ap_record_t *out, uint16_t *count);

/* Назва режиму захисту для JSON-відповіді веб-інтерфейсу. */
const char *wifi_auth_name(wifi_auth_mode_t mode);
