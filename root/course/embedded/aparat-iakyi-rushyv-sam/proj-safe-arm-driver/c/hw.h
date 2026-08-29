#ifndef HW_H
#define HW_H

#include <stdbool.h>
#include <stdint.h>

/*
 * Контракт платформного шару (BSP). Реалізація живе поруч із регістрами
 * конкретного мікроконтролера й до предмета цієї теми не належить: драйвер
 * безпеки навмисно не знає ні номерів виводів, ні адрес периферії.
 */

/* Вивід PIN_SAFETY_HEARTBEAT: рівень динамічного меандру помпи заряду.
 * Постійний рівень (байдуже, 0 чи 1) означає знеструмлення силового ключа. */
void hw_gpio_write_heartbeat(bool level);

/* Вивід PIN_MOTOR_PWM: коефіцієнт заповнення в тиках 0..PWM_MAX_DUTY. */
void hw_timer_set_pwm_duty(uint16_t duty);

/* Вільний лічильник мікросекунд. Переповнення дозволене: увесь драйвер
 * рахує тільки різниці в беззнаковій арифметиці. */
uint32_t hw_get_time_us(void);

/* Напруга силової батареї з вбудованого АЦП, мілівольти. */
uint16_t hw_read_supply_voltage_mv(void);

/* Лінія аварійної зупинки: true — кнопку натиснуто.
 * Та сама лінія паралельно рве живлення драйвера затворів апаратно. */
bool hw_read_estop_active(void);

/* Прапори захисту силового каскаду: термодавач ключів і компаратор струму. */
bool hw_read_overtemp_flag(void);
bool hw_read_overcurrent_flag(void);

/* Сторожовий таймер. Вікно задається один раз при старті. */
void hw_watchdog_start(uint16_t timeout_ms);
void hw_watchdog_feed(void);

#endif /* HW_H */
