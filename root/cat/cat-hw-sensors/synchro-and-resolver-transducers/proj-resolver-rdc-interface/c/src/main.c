#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include "ad2s1210.h"

/* Симуляційне середовище для тестування без фізичного заліза */
typedef struct {
    float current_angle_deg;
    float current_speed_rpm;
    bool  simulate_dos_fault;
    bool  simulate_lot_fault;
    ad2s1210_pin_state_t pin_sample;
    ad2s1210_pin_state_t pin_a0;
    ad2s1210_pin_state_t pin_a1;
    ad2s1210_pin_state_t pin_reset;
    ad2s1210_pin_state_t pin_cs;
    uint16_t latched_pos_code;
    int16_t  latched_vel_code;
} mock_hardware_t;

static mock_hardware_t g_hw = {
    .current_angle_deg = 45.0f,
    .current_speed_rpm = 1200.0f,
    .simulate_dos_fault = false,
    .simulate_lot_fault = false,
    .pin_sample = AD2S1210_PIN_HIGH,
    .pin_a0 = AD2S1210_PIN_LOW,
    .pin_a1 = AD2S1210_PIN_LOW,
    .pin_reset = AD2S1210_PIN_HIGH,
    .pin_cs = AD2S1210_PIN_HIGH
};

/* Зворотні виклики HAL */
static void mock_gpio_write(void *user_ctx, ad2s1210_pin_t pin, ad2s1210_pin_state_t state) {
    (void)user_ctx;
    switch (pin) {
        case AD2S1210_PIN_SAMPLE:
            if (g_hw.pin_sample == AD2S1210_PIN_HIGH && state == AD2S1210_PIN_LOW) {
                /* Западання SAMPLE замикає лічильник tracking loop у регістри фіксації */
                float norm_angle = fmodf(g_hw.current_angle_deg, 360.0f);
                if (norm_angle < 0.0f) norm_angle += 360.0f;
                g_hw.latched_pos_code = (uint16_t)lroundf((norm_angle / 360.0f) * 65536.0f);

                float rps = g_hw.current_speed_rpm / 60.0f;
                g_hw.latched_vel_code = (int16_t)lroundf((rps / 125.0f) * 32768.0f);
            }
            g_hw.pin_sample = state;
            break;
        case AD2S1210_PIN_A0:    g_hw.pin_a0 = state; break;
        case AD2S1210_PIN_A1:    g_hw.pin_a1 = state; break;
        case AD2S1210_PIN_RESET: g_hw.pin_reset = state; break;
        case AD2S1210_PIN_CS:    g_hw.pin_cs = state; break;
        default: break;
    }
}

static ad2s1210_pin_state_t mock_gpio_read(void *user_ctx, ad2s1210_pin_t pin) {
    (void)user_ctx;
    if (pin == AD2S1210_PIN_LOT) {
        return g_hw.simulate_lot_fault ? AD2S1210_PIN_LOW : AD2S1210_PIN_HIGH;
    }
    if (pin == AD2S1210_PIN_DOS) {
        return g_hw.simulate_dos_fault ? AD2S1210_PIN_LOW : AD2S1210_PIN_HIGH;
    }
    return AD2S1210_PIN_HIGH;
}

static void mock_delay_us(uint32_t us) {
    (void)us;
    /* У реальній системі тут буде виклик системної затримки */
}

static bool mock_spi_transfer(void *user_ctx, const uint8_t *tx_buf, uint8_t *rx_buf, size_t len) {
    (void)user_ctx;
    if (!tx_buf || !rx_buf || len == 0) return false;

    uint8_t mode = (g_hw.pin_a1 << 1) | g_hw.pin_a0;

    if (mode == AD2S1210_MODE_POSITION && len >= 2) {
        rx_buf[0] = (uint8_t)(g_hw.latched_pos_code >> 8);
        rx_buf[1] = (uint8_t)(g_hw.latched_pos_code & 0xFF);
    } else if (mode == AD2S1210_MODE_VELOCITY && len >= 2) {
        rx_buf[0] = (uint8_t)((uint16_t)g_hw.latched_vel_code >> 8);
        rx_buf[1] = (uint8_t)((uint16_t)g_hw.latched_vel_code & 0xFF);
    } else if (mode == AD2S1210_MODE_CONFIG) {
        uint8_t reg = tx_buf[0];
        if (reg == AD2S1210_REG_FAULT) {
            /* Байт помилок: 0 в біті означає активну помилку */
            uint8_t fault_byte = 0xFF;
            if (g_hw.simulate_dos_fault) {
                fault_byte &= ~(1 << 6); /* DOS/LOS fault */
            }
            if (g_hw.simulate_lot_fault) {
                fault_byte &= ~(1 << 5); /* LOT fault */
            }
            rx_buf[0] = fault_byte;
        } else {
            rx_buf[0] = 0x00;
        }
    }
    return true;
}

static void print_telemetry(size_t step, const ad2s1210_data_t *data, ad2s1210_status_t status) {
    printf("[%02zu] Кут: %6.2f deg (%5.3f rad) | Швидкість: %7.1f RPM (%6.2f rad/s) | Статус: %s\n",
           step,
           data->angle_degrees,
           data->angle_radians,
           data->velocity_rpm,
           data->velocity_rads,
           (status == AD2S1210_OK) ? "НОРМА" : "ПОМИЛКА ІНДУКТИВНОГО ЗВ'ЯЗКУ");

    if (status != AD2S1210_OK) {
        if (data->dos_pin_active) {
            printf("     [АПАРАТНИЙ ДІАГНОЗ]: Активовано лінію DOS (Degradation of Signal).\n");
        }
        if (data->lot_pin_active) {
            printf("     [АПАРАТНИЙ ДІАГНОЗ]: Активовано лінію LOT (Loss of Tracking).\n");
        }
        if (data->fault_flags.bits.dos_los_fault) {
            printf("      -> КРИТИЧНО: Обрив обмотки / втрата вхідного сигналу синус-косинус (DOS/LOS).\n");
        }
        if (data->fault_flags.bits.lot_fault) {
            printf("      -> КРИТИЧНО: Перевищення макс. швидкості стеження / втрати трекінгу (LOT).\n");
        }
    }
}

int main(void) {
    printf("====================================================================\n");
    printf("  Драйвер AD2S1210: Перетворювач резольвер-код (Resolver-to-Digital) \n");
    printf("====================================================================\n\n");

    /* Конфігурація драйвера */
    ad2s1210_config_t config = {
        .clk_in_hz = 8192000,
        .excitation_freq_hz = 10000,
        .resolution = AD2S1210_RES_16BIT,
        .enable_hysteresis = true,
        .enable_encoder_outputs = false,
        .gpio_write = mock_gpio_write,
        .gpio_read  = mock_gpio_read,
        .delay_us   = mock_delay_us,
        .spi_transfer = mock_spi_transfer,
        .user_ctx = NULL
    };

    ad2s1210_dev_t dev;
    ad2s1210_status_t status = ad2s1210_init(&dev, &config);

    if (status != AD2S1210_OK) {
        printf("Помилка ініціалізації AD2S1210: %s\n", ad2s1210_status_to_string(status));
        return EXIT_FAILURE;
    }

    printf("Ініціалізацію AD2S1210 успішно завершено (16 біт, f_exc = 10 кГц).\n\n");

    ad2s1210_data_t data;

    /* Цикл опитування валу електричної машини */
    for (size_t i = 1; i <= 10; ++i) {
        /* Симуляція обертання валу двигуна */
        g_hw.current_angle_deg += 36.0f;
        g_hw.current_speed_rpm = 1200.0f + (float)(i * 50);

        /* Сценарій штучного збою на кроці 6 (обрив лінії косинусної обмотки) */
        if (i == 6) {
            printf("\n>>> ШТУЧНА СИМУЛЯЦІЯ ОБРИВУ ОБМОТКИ РЕЗОЛЬВЕРА (DOS FAULT) <<<\n");
            g_hw.simulate_dos_fault = true;
        }

        /* Сценарій відновлення зв'язку на кроці 8 */
        if (i == 8) {
            printf("\n>>> ВІДНОВЛЕННЯ ІНДУКТИВНОГО ЗВ'ЯЗКУ РЕЗОЛЬВЕРА <<<\n");
            g_hw.simulate_dos_fault = false;
            ad2s1210_clear_faults(&dev);
        }

        status = ad2s1210_read_all(&dev, &data);
        print_telemetry(i, &data, status);
    }

    printf("\nДемонстрацію успішно завершено.\n");
    return EXIT_SUCCESS;
}
