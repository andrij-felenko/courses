typedef enum {
    ESP_RST_UNKNOWN,    // причину визначити не вдалося
    ESP_RST_POWERON,    // подача живлення (холодний старт)
    ESP_RST_EXT,        // зовнішній пін скидання (не для класичного ESP32)
    ESP_RST_SW,         // програмний скид через esp_restart()
    ESP_RST_PANIC,      // виняток / паніка (напр. LoadProhibited)
    ESP_RST_INT_WDT,    // сторожовий таймер переривань
    ESP_RST_TASK_WDT,   // сторожовий таймер задач
    ESP_RST_WDT,        // інший сторожовий таймер
    ESP_RST_DEEPSLEEP,  // вихід із глибокого сну
    ESP_RST_BROWNOUT,   // brownout (апаратний АБО програмний — див. нижче)
    ESP_RST_SDIO,       // скид через SDIO
    // …ESP_RST_USB, ESP_RST_JTAG, ESP_RST_EFUSE, ESP_RST_PWR_GLITCH, ESP_RST_CPU_LOCKUP
} esp_reset_reason_t;
