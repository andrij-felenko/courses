#include <mavlink.h>

// Стендова перевірка одного мотора: крутнути на малому газі й дати
// команді САМІЙ зупинити його за таймаутом.
// УВАГА: ТІЛЬКИ БЕЗ ПРОПЕЛЕРІВ. Мотор крутнеться фізично.
void motor_test(int serial_fd, uint8_t motor_num,
                float throttle_percent, float seconds)
{
    mavlink_message_t msg;
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];

    mavlink_msg_command_long_pack(
        255, 0,                      // хто шле: наземна станція
        &msg,
        1, 1,                        // кому: система 1, автопілот
        MAV_CMD_DO_MOTOR_TEST,
        0,                           // не повтор
        (float)motor_num,            // param1: номер мотора (1..N)
        0,                           // param2: тип газу 0 = відсоток
        throttle_percent,            // param3: значення газу (%)
        seconds,                     // param4: таймаут, с — САМ зупинить
        0,                           // param5: один мотор
        0, 0);                       // param6..7 не потрібні

    int len = mavlink_msg_to_send_buffer(buf, &msg);
    write(serial_fd, buf, len);
}

// виклик: мотор 1, 10% газу, 3 секунди, тоді автостоп
motor_test(fd, 1, 10.0f, 3.0f);
