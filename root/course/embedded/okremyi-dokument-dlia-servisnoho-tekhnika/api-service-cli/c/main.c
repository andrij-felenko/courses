/* Структура безпечного керування навантаженням у сервісному режимі */
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    ACT_RELAY_1      = 0x01,
    ACT_RELAY_2      = 0x02,
    ACT_VALVE_PWM    = 0x03,
    ACT_FAN_OUT      = 0x04
} act_channel_t;

typedef struct {
    act_channel_t channel;
    uint16_t      duration_sec;  /* Максимальний тайм-аут увімкнення (1..60 с) */
    uint16_t      pwm_permille;  /* ШІМ: 0..1000 (0.0% .. 100.0%) */
    bool          force_override;/* Ігнорування аварійних сенсорів (потребує прав інженера) */
} act_command_t;

/* Функція виконання сервісної команди: автоматично знеструмлює канал при завершенні тайм-ауту */
int srv_actuate_channel(const act_command_t *cmd);
