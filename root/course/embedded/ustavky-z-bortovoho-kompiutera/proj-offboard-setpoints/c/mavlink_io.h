#ifndef MAVLINK_IO_H
#define MAVLINK_IO_H

#include <stdbool.h>
#include <stdint.h>

/* Усе, що ми знаємо про автопілот з його ж повідомлень.
 * Знімок оновлює mav_poll(), читає автомат станів генератора. */
typedef struct {
    bool     link_alive;         /* хоч один HEARTBEAT від FCU прийшов */
    uint64_t last_heartbeat_ms;
    bool     offboard;           /* FCU САМ повідомляє режим OFFBOARD */
    bool     armed;
    bool     mode_ack_seen;      /* прийшов COMMAND_ACK на DO_SET_MODE */
    bool     mode_ack_ok;        /* ...і його результат — «прийнято» */
    uint8_t  mode_ack_result;    /* сирий код MAV_RESULT для журналу */
    uint32_t rx_drops;           /* пакетів, зіпсованих на прийомі */
} fcu_status_t;

/* Кадр #84 SET_POSITION_TARGET_LOCAL_NED: швидкості у зв'язаній
 * системі NED плюс абсолютний курс. 0 / -1. */
int mav_send_setpoint(int fd, uint8_t sys_id, uint8_t comp_id,
                      float vx, float vy, float vz, float yaw);

/* MAV_CMD_DO_SET_MODE із запитом головного режиму PX4 OFFBOARD. */
int mav_send_offboard_request(int fd, uint8_t sys_id, uint8_t comp_id);

/* Власний HEARTBEAT: без нього FCU вважає супутній комп'ютер відсутнім. */
int mav_send_heartbeat(int fd, uint8_t sys_id, uint8_t comp_id);

/* Розбирає все, що встигло прийти, і оновлює знімок стану. Не блокується. */
void mav_poll(int fd, fcu_status_t *st, uint64_t now_ms);

#endif /* MAVLINK_IO_H */
