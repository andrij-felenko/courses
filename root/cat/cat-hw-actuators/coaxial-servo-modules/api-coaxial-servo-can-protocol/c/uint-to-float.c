#include <stdint.h>
#include <math.h>

typedef struct {
    uint8_t motor_id;
    float position;  // рад
    float velocity;  // рад/с
    float torque;    // Н·м
    float temp_c;    // °C
    uint8_t error_code;
} servo_telemetry_t;

// Допоміжна функція декодування цілого у float
static float uint_to_float(uint16_t int_val, float min_val, float max_val, uint8_t bits) {
    uint32_t max_int = (1U << bits) - 1U;
    float span = max_val - min_val;
    return min_val + ((float)int_val / (float)max_int) * span;
}

// Розпакування кадру телеметрії (8 байт)
void unpack_servo_telemetry(const uint8_t payload[8], servo_telemetry_t* telemetry) {
    telemetry->motor_id = payload[0];

    uint16_t p_int = ((uint16_t)payload[1] << 8) | payload[2];
    uint16_t v_int = ((uint16_t)payload[3] << 4) | (payload[4] >> 4);
    uint16_t t_int = (((uint16_t)payload[4] & 0x0F) << 8) | payload[5];

    telemetry->position   = uint_to_float(p_int, -12.5f, 12.5f, 16);
    telemetry->velocity   = uint_to_float(v_int, -30.0f, 30.0f, 12);
    telemetry->torque     = uint_to_float(t_int, -12.0f, 12.0f, 12);
    telemetry->temp_c     = (float)payload[6]; // 1 LSB = 1 °C
    telemetry->error_code = payload[7];
}
