#include <stdint.h>
#include <stdbool.h>

#define REG_RESET_CTRL        (0x06U)
#define BIT_SW_RESET          (1U << 7)
#define REG_STATUS            (0x07U)
#define BIT_STATUS_READY      (1U << 0)
#define SW_RESET_TIMEOUT_MS   (50U)

typedef enum {
    INIT_OK = 0,
    INIT_ERR_BUS,
    INIT_ERR_TIMEOUT,
    INIT_ERR_WRONG_ID
} init_result_t;

/* Безпечне виконання програмного скидання та очікування готовності */
init_result_t sensor_software_reset(uint8_t dev_addr) {
    /* 1. Відправляємо команду скидання */
    if (i2c_write_reg(dev_addr, REG_RESET_CTRL, BIT_SW_RESET) != 0) {
        return INIT_ERR_BUS;
    }

    /* 2. Обов'язкова апаратна пауза на перезавантаження внутрішнього ядра */
    delay_ms(5);

    /* 3. Цикл опитування готовності з таймаутом (Timeout Guard) */
    uint32_t start_time = platform_get_millis();
    while (true) {
        uint8_t reset_reg_val = 0;
        uint8_t status_val = 0;

        /* Перевіряємо, чи знявся біт скидання (самоочищення) */
        if (i2c_read_reg(dev_addr, REG_RESET_CTRL, &reset_reg_val) == 0 &&
            i2c_read_reg(dev_addr, REG_STATUS, &status_val) == 0) {
            
            bool reset_done = (reset_reg_val & BIT_SW_RESET) == 0;
            bool device_ready = (status_val & BIT_STATUS_READY) != 0;

            if (reset_done && device_ready) {
                return INIT_OK; /* Чип успішно перезавантажився і готовий */
            }
        }

        /* Захист від вічного зависання при фізичному пошкодженні кристала */
        if ((platform_get_millis() - start_time) >= SW_RESET_TIMEOUT_MS) {
            return INIT_ERR_TIMEOUT;
        }

        delay_ms(2); /* Інтервал між спробами опитування */
    }
}
