#include "driver/uart.h"
#include "esp_log.h"

void app_main(void) {
  uart_config_t cfg = {
    .baud_rate = 9600,
    .data_bits = UART_DATA_8_BITS,        // 8 біт даних…
    .parity    = UART_PARITY_DISABLE,     // …без парності…
    .stop_bits = UART_STOP_BITS_1,        // …і 1 стоповий — це і є «8N1»
    .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
    .source_clk = UART_SCLK_DEFAULT,
  };
  uart_driver_install(UART_NUM_1, 1024, 0, 0, NULL, 0);
  uart_param_config(UART_NUM_1, &cfg);
  uart_set_pin(UART_NUM_1, 43, 44,        // TX=GPIO43, RX=GPIO44 — свої ноги
               UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);   // RTS/CTS не потрібні

  uint8_t b;
  while (1) {
    if (uart_read_bytes(UART_NUM_1, &b, 1, pdMS_TO_TICKS(20)) == 1)
      ESP_LOGI("uart", "прийшов байт 0x%02X", b);   // журнал іде в рідний USB
  }
}
