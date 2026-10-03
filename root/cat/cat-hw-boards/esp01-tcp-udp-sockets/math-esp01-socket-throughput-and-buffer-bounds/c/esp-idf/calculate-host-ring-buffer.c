#include <stdint.h>
#include <stdbool.h>

/* Розрахунок мінімального розміру кільцевого буфера хоста */
uint32_t calculate_host_ring_buffer(uint32_t baud_rate, uint32_t max_isr_latency_us) {
    /* Фізична швидкість UART у байтах за секунду (8N1) */
    uint32_t bytes_per_sec = baud_rate / 10;
    
    /* Кількість байтів, що надійдуть за час максимальної затримки переривання */
    uint32_t latency_bytes = (bytes_per_sec * max_isr_latency_us) / 1000000UL;
    
    /* Апаратний FIFO буфер ESP8266 становить 128 байтів */
    const uint32_t esp8266_fifo_size = 128;
    
    /* Поріг спрацювання сигнатурного RTS (watermark) */
    uint32_t watermark = latency_bytes + 64;
    
    /* Підсумковий розмір буфера з урахуванням апаратного FIFO */
    uint32_t total_buffer_size = watermark + esp8266_fifo_size;
    
    return total_buffer_size;
}

/* Розрахунок таймауту FSM у мілісекундах для AT+CIPSEND */
uint32_t calculate_cipsend_timeout_ms(uint32_t baud_rate, uint32_t payload_len, uint32_t max_rtt_ms) {
    /* Тривалість передачі AT+CIPSEND префікса, даних та відповідей через UART */
    uint32_t total_uart_bytes = payload_len + 50;
    uint32_t uart_time_ms = (total_uart_bytes * 10 * 1000) / baud_rate;
    
    /* Час обробки у прошивці ESP-AT та захисний інтервал */
    const uint32_t esp_proc_ms = 100;
    const uint32_t safety_margin_ms = 500;
    
    return uart_time_ms + max_rtt_ms + esp_proc_ms + safety_margin_ms;
}
