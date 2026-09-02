#ifndef ESC_DEADLINE_H
#define ESC_DEADLINE_H

#include <stdint.h>

/* Стеля очікування: довше тримати сцену немає сенсу — вона застаріває */
#define ESC_DEADLINE_MAX_MS  15000u
/* Скільки чекаємо, коли апарат уже стоїть */
#define ESC_DEADLINE_IDLE_MS 15000u

/* Час до точки неповернення, мілісекунди.
   0 означає «питати нікого вже нема коли — гальмувати негайно». */
uint32_t esc_deadline_ms(float distance_to_obstacle_m,
                         float current_speed_mps,
                         float max_braking_decel_mps2,
                         float safety_margin_m,
                         uint32_t sensor_lag_ms);

#endif /* ESC_DEADLINE_H */
