#include <stdint.h>

// команда осі −1..+1  →  ширина 1000..2000 мкс, з реверсом і тримом
uint16_t axis_to_us(float cmd, int reverse, int trim_us) {
    if (reverse) cmd = -cmd;                 // серво стоїть дзеркально
    if (cmd < -1.0f) cmd = -1.0f;            // затиск у межі команди
    if (cmd >  1.0f) cmd =  1.0f;
    int us = 1500 + trim_us + (int)(cmd * 500.0f);  // ±500 мкс = повний хід
    if (us < 1000) us = 1000;                // жорсткі межі серво
    if (us > 2000) us = 2000;
    return (uint16_t)us;
}

void plane_outputs(float roll, float pitch, float yaw,
                   uint16_t *ail_us, uint16_t *ele_us, uint16_t *rud_us) {
    *ail_us = axis_to_us(roll,  1,  0);      // елерон: реверс, триму нема
    *ele_us = axis_to_us(pitch, 0, +4);      // руль висоти: трим +4 мкс
    *rud_us = axis_to_us(yaw,   0,  0);      // руль напряму
}
