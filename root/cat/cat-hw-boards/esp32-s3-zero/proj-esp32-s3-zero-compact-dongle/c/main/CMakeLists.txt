# Файл збирання компонента main для середовища ESP-IDF
# Реєстрація вихідних файлів проєкту ESP32-S3-Zero та підключення необхідних залежностей периферії

idf_component_register(
    SRCS
        "main.c"
        "usb_cdc.c"
        "ws2812_rmt.c"
        "net_relay.c"
    INCLUDE_DIRS
        "."
    REQUIRES
        driver
        esp_driver_usb_serial_jtag
        nvs_flash
        esp_wifi
        esp_event
        esp_netif
        bt
        freertos
        log
)
