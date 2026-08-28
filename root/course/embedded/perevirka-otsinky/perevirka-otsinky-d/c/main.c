#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define LOG_BUFFER_CAPACITY 512

/* Двійковий пакет телеметрії фіксованого розміру */
typedef struct __attribute__((packed)) {
    uint32_t timestamp_us;   /* Системний час мікросекундного таймера */
    float gyro_z;            /* Сира кутова швидкість (рад/с) */
    float accel_x;           /* Сире прискорення (м/с²) */
    float accel_y;           /* Сире прискорення (м/с²) */
    float state_yaw;         /* Оцінений кут курсу (рад) */
    float state_bias;        /* Оцінений зсув нуля гіроскопа (рад/с) */
    float cov_p_yaw;         /* Діагональний елемент P[0][0] */
    float innov_yaw;         /* Нев'язка інновації y */
    float innov_cov_s;       /* Коваріація інновації S */
    float ground_truth_yaw;  /* Еталонний кут від зовнішнього енкодера */
} telemetry_frame_t;

typedef struct {
    telemetry_frame_t frames[LOG_BUFFER_CAPACITY];
    volatile uint16_t head;
    volatile uint16_t tail;
} log_ring_buffer_t;

static log_ring_buffer_t g_log_buf;

void log_buffer_init(void) {
    g_log_buf.head = 0;
    g_log_buf.tail = 0;
}

bool log_buffer_push(const telemetry_frame_t *frame) {
    uint16_t next_head = (g_log_buf.head + 1) % LOG_BUFFER_CAPACITY;
    if (next_head == g_log_buf.tail) {
        return false; /* Переповнення буфера: кадр втрачено */
    }
    g_log_buf.frames[g_log_buf.head] = *frame;
    g_log_buf.head = next_head;
    return true;
}

uint16_t log_buffer_pop_block(telemetry_frame_t *out_block, uint16_t max_count) {
    uint16_t count = 0;
    while (g_log_buf.tail != g_log_buf.head && count < max_count) {
        out_block[count++] = g_log_buf.frames[g_log_buf.tail];
        g_log_buf.tail = (g_log_buf.tail + 1) % LOG_BUFFER_CAPACITY;
    }
    return count;
}
