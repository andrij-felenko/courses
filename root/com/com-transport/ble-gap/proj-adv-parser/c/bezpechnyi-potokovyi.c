#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/* Стандартні типи AD Data згідно з Bluetooth Assigned Numbers */
typedef enum {
    BLE_AD_TYPE_FLAGS                 = 0x01,
    BLE_AD_TYPE_UUID16_INCOMPLETE     = 0x02,
    BLE_AD_TYPE_UUID16_COMPLETE       = 0x03,
    BLE_AD_TYPE_UUID32_INCOMPLETE     = 0x04,
    BLE_AD_TYPE_UUID32_COMPLETE       = 0x05,
    BLE_AD_TYPE_UUID128_INCOMPLETE    = 0x06,
    BLE_AD_TYPE_UUID128_COMPLETE      = 0x07,
    BLE_AD_TYPE_SHORT_LOCAL_NAME      = 0x08,
    BLE_AD_TYPE_COMPLETE_LOCAL_NAME   = 0x09,
    BLE_AD_TYPE_TX_POWER_LEVEL        = 0x0A,
    BLE_AD_TYPE_SLAVE_CONN_INTERVAL   = 0x12,
    BLE_AD_TYPE_SERVICE_DATA_16       = 0x16,
    BLE_AD_TYPE_APPEARANCE            = 0x19,
    BLE_AD_TYPE_ADV_INTERVAL          = 0x1A,
    BLE_AD_TYPE_MANUFACTURER_SPECIFIC = 0xFF
} ble_ad_type_t;

/* Структура дескриптора знайденого блоку даних */
typedef struct {
    uint8_t        type;        /* Ідентифікатор AD Type */
    const uint8_t* data;        /* Вказівник на початок корисного навантаження блоку */
    uint8_t        data_len;    /* Довжина корисного навантаження (Length - 1) */
} ble_ad_element_t;

/* Сигнатура функції зворотного виклику. Повернення false зупиняє подальший обхід */
typedef bool (*ble_ad_iterator_cb)(const ble_ad_element_t* elem, void* user_ctx);

/**
 * @brief Безпечний потоковий розбір сирого масиву рекламних даних.
 * @param buffer Вказівник на сирий масив байтів AdvData або ScanRspData.
 * @param buffer_len Фактичний розмір буфера в байтах.
 * @param callback Функція обробки кожного знайденого елемента.
 * @param user_ctx Вказівник на довільний контекст користувача.
 * @return Кількість успішно розібраних блоків TLV.
 */
size_t ble_ad_parse(const uint8_t* buffer, size_t buffer_len, 
                    ble_ad_iterator_cb callback, void* user_ctx) 
{
    if (!buffer || buffer_len == 0 || !callback) {
        return 0;
    }

    size_t offset = 0;
    size_t elements_found = 0;

    while (offset < buffer_len) {
        uint8_t length = buffer[offset];

        /* Довжина 0 вказує на zero-padding або кінець корисного навантаження */
        if (length == 0) {
            break;
        }

        /* Перевірка на вихід за межі буфера: 1 байт поля Length + length байтів тіла */
        if (offset + 1 + length > buffer_len) {
            /* Пакет пошкоджений: заявлена довжина виходить за межі буфера */
            break;
        }

        /* Формуємо дескриптор знайденого елемента */
        ble_ad_element_t elem;
        elem.type     = buffer[offset + 1];
        elem.data     = &buffer[offset + 2];
        elem.data_len = (uint8_t)(length - 1);

        elements_found++;

        /* Викликаємо функцію обробки. Якщо вона повернула false — перериваємо пошук */
        if (!callback(&elem, user_ctx)) {
            break;
        }

        /* Зсуваємо вказівник на наступний блок */
        offset += (1 + length);
    }

    return elements_found;
}
