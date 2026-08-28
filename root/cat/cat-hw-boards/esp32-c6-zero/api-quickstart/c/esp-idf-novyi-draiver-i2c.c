#include "driver/i2c_master.h"

#define I2C_SDA   6
#define I2C_SCL   7
#define DEV_ADDR  0x68     // приклад: адреса давача на шині
#define REG_WHO   0x75     // реєстр «хто ти» (ідентифікатор)

static i2c_master_dev_handle_t dev;

static void i2c_init(void)
{
    i2c_master_bus_config_t bus_cfg = {
        .i2c_port = I2C_NUM_0,
        .sda_io_num = I2C_SDA,
        .scl_io_num = I2C_SCL,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = true,   // ввімкнути слабкі внутрішні підтяжки
    };
    i2c_master_bus_handle_t bus;
    ESP_ERROR_CHECK(i2c_new_master_bus(&bus_cfg, &bus));

    i2c_device_config_t dev_cfg = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = DEV_ADDR,
        .scl_speed_hz = 100000,    // 100 кГц — стандартна швидкість
    };
    ESP_ERROR_CHECK(i2c_master_bus_add_device(bus, &dev_cfg, &dev));
}

void app_main(void)
{
    i2c_init();

    uint8_t reg = REG_WHO;
    uint8_t who = 0;
    // атомарно: записати номер регістра, тоді прочитати 1 байт відповіді
    esp_err_t err = i2c_master_transmit_receive(dev, &reg, 1, &who, 1,
                                                pdMS_TO_TICKS(100));
    if (err == ESP_OK)
        printf("Давач відповів, WHO_AM_I = 0x%02X\n", who);
    else
        printf("Давач мовчить (err=%d): перевір адресу й підтяжки\n", err);

    while (1) vTaskDelay(pdMS_TO_TICKS(1000));
}
