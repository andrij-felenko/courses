/**
 * @file usb_cdc.c
 * @brief Ініціалізація та конфігурація нативного драйвера USB CDC для прийому й передачі даних через порт Type-C.
 *
 * ESP32-S3 має вбудований нативний периферичний USB Serial/JTAG контролер, який дозволяє
 * реалізувати віртуальний COM-порт безпосередньо через лінії D- (GPIO19) та D+ (GPIO20)
 * без зовнішніх мікросхем CP2102, CH340 чи FT232.
 */

#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_err.h"
#include "driver/usb_serial_jtag.h"

static const char *TAG = "USB_CDC";

#define USB_BUF_SIZE 1024

static bool s_usb_initialized = false;

/**
 * @brief Ініціалізація апаратного нативного контролера USB Serial/JTAG
 * @return ESP_OK у разі успіху або код помилки ESP-IDF
 */
esp_err_t usb_cdc_init(void)
{
    if (s_usb_initialized) {
        ESP_LOGW(TAG, "Драйвер USB CDC вже ініціалізовано");
        return ESP_OK;
    }

    // Налаштування буферів для нативного драйвера USB Serial/JTAG ESP32-S3
    usb_serial_jtag_driver_config_t usb_config = {
        .tx_buffer_size = USB_BUF_SIZE,
        .rx_buffer_size = USB_BUF_SIZE
    };

    esp_err_t err = usb_serial_jtag_driver_install(&usb_config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка встановлення драйвера USB Serial/JTAG: %s", esp_err_to_name(err));
        return err;
    }

    s_usb_initialized = true;
    ESP_LOGI(TAG, "Нативний драйвер USB CDC успішно ініціалізовано (Буфер RX/TX: %d байт)", USB_BUF_SIZE);
    return ESP_OK;
}

/**
 * @brief Перевірка стану підключення USB CDC
 * @return true, якщо USB готовий до обміну даними
 */
bool usb_cdc_is_connected(void)
{
    if (!s_usb_initialized) {
        return false;
    }
    // Перевірка готовності апаратного PHY контролера USB ESP32-S3
    return usb_serial_jtag_is_connected();
}

/**
 * @brief Читання даних з нативного USB CDC порта
 * @param buf Буфер для збереження отриманих байтів
 * @param max_len Максимальна кількість байтів для зчитування
 * @param timeout_ticks Час очікування в тиках FreeRTOS
 * @return Кількість фактично зчитаних байтів, або від'ємне значення при помилці
 */
int usb_cdc_read(uint8_t *buf, size_t max_len, TickType_t timeout_ticks)
{
    if (!s_usb_initialized || buf == NULL || max_len == 0) {
        return -1;
    }

    int bytes_read = usb_serial_jtag_read_bytes(buf, max_len, timeout_ticks);
    if (bytes_read > 0) {
        ESP_LOGD(TAG, "Зчитано %d байт з USB CDC", bytes_read);
    }
    return bytes_read;
}

/**
 * @brief Відправка даних через нативний USB CDC порт
 * @param buf Вказівник на буфер з даними для відправки
 * @param len Довжина даних у байтах
 * @param timeout_ticks Час очікування завершення передачі
 * @return Кількість фактично відправлених байтів, або від'ємне значення при помилці
 */
int usb_cdc_write(const uint8_t *buf, size_t len, TickType_t timeout_ticks)
{
    if (!s_usb_initialized || buf == NULL || len == 0) {
        return -1;
    }

    if (!usb_serial_jtag_is_connected()) {
        ESP_LOGD(TAG, "Пропущено відправку: USB порт не підключено до хоста");
        return 0;
    }

    int bytes_written = usb_serial_jtag_write_bytes(buf, len, timeout_ticks);
    if (bytes_written < 0) {
        ESP_LOGE(TAG, "Помилка записи в буфер USB CDC");
        return bytes_written;
    }

    // Примусове скидання буфера передачі для мінімізації затримок (flush)
    esp_err_t flush_err = usb_serial_jtag_wait_tx_done(timeout_ticks);
    if (flush_err != ESP_OK) {
        ESP_LOGW(TAG, "Затримка очищення буфера передачі USB: %s", esp_err_to_name(flush_err));
    }

    ESP_LOGD(TAG, "Передано %d байт через USB CDC", bytes_written);
    return bytes_written;
}
