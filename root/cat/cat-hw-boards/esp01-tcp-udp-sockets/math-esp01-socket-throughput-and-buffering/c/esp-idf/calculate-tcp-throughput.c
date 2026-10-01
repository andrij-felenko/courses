#include <stdio.h>
#include <stdint.h>

typedef struct {
    uint32_t baud_rate;
    uint16_t mss;
    float payload_efficiency;
    float net_throughput_kbps;
} socket_calc_t;

socket_calc_t calculate_tcp_throughput(uint32_t baud_rate, uint16_t mss) {
    socket_calc_t result;
    result.baud_rate = baud_rate;
    result.mss = mss;

    float raw_byte_rate = (float)baud_rate / 10.0f;
    result.payload_efficiency = (float)mss / (float)(mss + 40);
    result.net_throughput_kbps = (raw_byte_rate * result.payload_efficiency) / 1024.0f;

    return result;
}
