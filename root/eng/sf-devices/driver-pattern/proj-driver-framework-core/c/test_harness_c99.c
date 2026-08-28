/* ============================================================================
 * ФАЙЛ: test_harness_c99.c - Юніт-тестування каркаса драйвера на C99
 * ============================================================================ */
#include "driver_core.h"
#include <stdio.h>
#include <assert.h>

static hw_i2c_registers_t s_mock_hw;
static bool s_callback_called = false;
static driver_status_t s_cb_status = DRIVER_OK;

static void test_cb(driver_handle_t h, driver_status_t st, size_t bytes, void* arg) {
    (void)h; (void)bytes; (void)arg;
    s_callback_called = true;
    s_cb_status = st;
}

int main(void) {
    printf("=== Запуск тестування C99 драйвера ===\n");

    driver_config_t cfg = {
        .clock_hz = 100000,
        .default_timeout_ms = 50,
        .sda_pin = 4,
        .scl_pin = 5,
        .max_retries = 3
    };

    driver_handle_t h = driver_create(0, &s_mock_hw, &cfg);
    assert(h != NULL);
    assert(driver_init(h) == DRIVER_OK);

    /* Тест 1: Успішна асинхронна транзакція */
    uint8_t tx_buf[2] = {0x10, 0x55};
    driver_transaction_t trans1 = {
        .dev_addr = 0x3C,
        .op_type = DRIVER_OP_WRITE,
        .tx_buf = tx_buf,
        .tx_len = 2,
        .callback = test_cb
    };

    s_callback_called = false;
    assert(driver_submit_async(h, &trans1) == DRIVER_OK);

    /* Емуляція відповідей заліза в ISR */
    s_mock_hw.SR1 = SR1_SB;   driver_poll_isr(h); /* Start bit */
    s_mock_hw.SR1 = SR1_ADDR; driver_poll_isr(h); /* Address matched */
    s_mock_hw.SR1 = SR1_TXE;  driver_poll_isr(h); /* Byte 1 */
    s_mock_hw.SR1 = SR1_TXE | SR1_BTF; driver_poll_isr(h); /* Byte 2 complete */

    assert(s_callback_called == true);
    assert(s_cb_status == DRIVER_OK);

    /* Тест 2: Обробка NACK */
    s_callback_called = false;
    assert(driver_submit_async(h, &trans1) == DRIVER_OK);
    s_mock_hw.SR1 = SR1_AF; /* Симуляція NACK */
    driver_poll_isr(h);

    assert(s_callback_called == true);
    assert(s_cb_status == DRIVER_ERR_NACK);

    driver_stats_t stats;
    driver_get_stats(h, &stats);
    assert(stats.successful_transfers == 1);
    assert(stats.nack_errors == 1);

    printf("✓ Усі тести C99 драйвера пройдено успішно!\n");
    return 0;
}
