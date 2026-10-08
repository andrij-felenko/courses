#include <stdint.h>
#include <math.h>

// Допоміжна функція квантування плаваючого числа у uint
static uint16_t float_to_uint(float val, float min_val, float max_val, uint8_t bits) {
    if (val < min_val) val = min_val;
    if (val > max_val) val = max_val;
    float span = max_val - min_val;
    float offset = min_val;
    uint32_t max_int = (1U << bits) - 1U;
    return (uint16_t)(((val - offset) / span) * (float)max_int);
}

// Упаковка параметрів PD-контуру у 8 байт CAN-пакета (MIT Protocol)
void pack_mit_command(uint8_t payload[8], float p_des, float v_des, 
                       float kp, float kd, float t_ff) {
    uint16_t p_int  = float_to_uint(p_des, -12.5f,  12.5f, 16);
    uint16_t v_int  = float_to_uint(v_des, -30.0f,  30.0f, 12);
    uint16_t kp_int = float_to_uint(kp,     0.0f,  500.0f, 12);
    uint16_t kd_int = float_to_uint(kd,     0.0f,    5.0f, 12);
    uint16_t t_int  = float_to_uint(t_ff,  -12.0f,  12.0f, 12);

    payload[0] = (uint8_t)(p_int >> 8);
    payload[1] = (uint8_t)(p_int & 0xFF);
    payload[2] = (uint8_t)(v_int >> 4);
    payload[3] = (uint8_t)(((v_int & 0x0F) << 4) | (kp_int >> 8));
    payload[4] = (uint8_t)(kp_int & 0xFF);
    payload[5] = (uint8_t)(kd_int >> 4);
    payload[6] = (uint8_t)(((kd_int & 0x0F) << 4) | (t_int >> 8));
    payload[7] = (uint8_t)(t_int & 0xFF);
}
