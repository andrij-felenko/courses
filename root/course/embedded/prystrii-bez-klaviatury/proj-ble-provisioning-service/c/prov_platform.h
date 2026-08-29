#ifndef PROV_PLATFORM_H
#define PROV_PLATFORM_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/*
 * Контракт порту: усе, чого диспетчер провізіонування вимагає від прошивки,
 * і все, що прошивка вимагає від диспетчера. Реалізації тут немає — її дає
 * конкретна платформа: крипто-бібліотека МК, BLE-стек, драйвер станції Wi-Fi,
 * енергонезалежна памʼять NVS. Диспетчер не знає жодного конкретного SDK,
 * і саме тому переноситься між ними.
 */

/* --- Апаратне джерело випадковості --- */
void plat_random_bytes(uint8_t *out, size_t len);

/* --- Криптографічні примітиви --- */

/* Публічний ключ із закритого: X25519(priv, базова точка 9). */
void plat_x25519_public(const uint8_t priv[32], uint8_t pub[32]);

/* Спільний секрет X25519. false — бібліотека сама відкинула вироджений результат. */
bool plat_x25519(const uint8_t priv[32], const uint8_t peer_pub[32], uint8_t shared[32]);

void plat_hmac_sha256(const uint8_t *key, size_t key_len,
                      const uint8_t *msg, size_t msg_len,
                      uint8_t out[32]);

void plat_hkdf_sha256(const uint8_t *salt, size_t salt_len,
                      const uint8_t *ikm, size_t ikm_len,
                      const uint8_t *info, size_t info_len,
                      uint8_t *okm, size_t okm_len);

/* Автентифіковане розшифрування AES-256-GCM. false — тег GMAC не зійшовся. */
bool plat_aes_gcm_decrypt(const uint8_t key[32], const uint8_t nonce[12],
                          const uint8_t tag[16],
                          const uint8_t *ciphertext, size_t len,
                          uint8_t *plaintext);

/* --- BLE-стек --- */
void plat_ble_notify(uint16_t char_uuid, const uint8_t *data, size_t len);
void plat_ble_advertise(void);
/* Вимкнути радіо й повернути RAM стека застосунку. Назад — лише через перезавантаження. */
void plat_ble_shutdown(void);

/* --- Станція Wi-Fi. Асинхронна: результат приходить у prov_on_wifi_event(). --- */
typedef enum {
    PLAT_WIFI_CONNECTED = 0,   /* асоціація + DHCP пройшли */
    PLAT_WIFI_AUTH_FAILED,     /* невірний пароль або AUTH_EXPIRED від точки доступу */
    PLAT_WIFI_NO_AP,           /* SSID не знайдено в ефірі */
    PLAT_WIFI_TIMEOUT          /* асоціація не завершилася вчасно */
} plat_wifi_event_t;

void plat_wifi_connect(const char *ssid, const char *passphrase);
void plat_wifi_stop(void);

/* --- Енергонезалежна памʼять --- */
bool plat_nvs_store_credentials(const char *ssid, const char *passphrase);
/* PoP пристрою: рядок із наліпки або QR-коду, зашитий на виробництві. */
size_t plat_pop_secret(const uint8_t **out);

/* --- Час і одноразовий таймер --- */
uint32_t plat_uptime_ms(void);
void plat_timer_once(uint32_t delay_ms, void (*callback)(void));

/* --- Зворотні виклики: їх кличе порт, реалізує диспетчер (main.c) --- */
void prov_service_start(void);
void prov_on_connect(void);
void prov_on_disconnect(uint8_t hci_reason);
uint16_t prov_on_mtu_exchange(uint16_t client_mtu);
void prov_on_gatt_write(uint16_t char_uuid, const uint8_t *data, size_t len);
uint16_t prov_on_gatt_read(uint16_t char_uuid, uint8_t *out, uint16_t max_len);
uint8_t prov_on_prepare_write(uint16_t char_uuid, uint16_t offset,
                              const uint8_t *value, size_t len);
uint8_t prov_on_execute_write(bool commit);
void prov_on_wifi_event(plat_wifi_event_t event, uint32_t ipv4);

#endif /* PROV_PLATFORM_H */
