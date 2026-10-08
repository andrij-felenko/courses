#include "driver/i2c.h"
#include "driver/uart.h"
#include "esp_log.h"

#define I2C_MASTER_SCL_IO    1        // Безпечний вивід SCL (не є страповим)
#define I2C_MASTER_SDA_IO    2        // Безпечний вивід SDA (не є страповим)
#define I2C_MASTER_NUM       I2C_NUM_0
#define I2C_MASTER_FREQ_HZ   400000

#define UART_PORT_NUM        UART_NUM_1
#define UART_TX_IO           43       // Апаратний вивід TX0
#define UART_RX_IO           44       // Апаратний вивід RX0

static const char *TAG = "HW_INIT";

esp_err_t init_safe_peripherals(void)
{
    // Налаштування конфігурації шини I2C
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = I2C_MASTER_SDA_IO,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_io_num = I2C_MASTER_SCL_IO,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = I2C_MASTER_FREQ_HZ,
    };
    
    esp_err_t err = i2c_param_config(I2C_MASTER_NUM, &conf);
    if (err != ESP_OK) return err;
    
    err = i2c_driver_install(I2C_MASTER_NUM, conf.mode, 0, 0, 0);
    if (err != ESP_OK) return err;
    
    // Налаштування конфігурації порту UART
    uart_config_t uart_config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };
    
    err = uart_param_config(UART_PORT_NUM, &uart_config);
    if (err != ESP_OK) return err;
    
    err = uart_set_pin(UART_PORT_NUM, UART_TX_IO, UART_RX_IO, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
    if (err != ESP_OK) return err;
    
    ESP_LOGI(TAG, "Периферійні шини I2C та UART успішно ініціалізовано на безпечних GPIO");
    return ESP_OK;
}
