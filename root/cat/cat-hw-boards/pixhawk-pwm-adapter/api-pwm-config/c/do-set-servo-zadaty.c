#include <mavlink.h>

// Примусово задати ширину імпульсу на виході серворульової машинки.
// УВАГА: команда ОБХОДИТЬ штатне змішування. На реальному апараті з
// увімкненими (озброєними) моторами так робити НЕ можна — лише перевірка
// на столі, без пропелерів.
void servo_set_pwm(int serial_fd, uint8_t out_channel, uint16_t pulse_us)
{
    mavlink_message_t msg;
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];

    const uint8_t my_sysid  = 255;   // id нашої наземної станції
    const uint8_t my_compid = 0;
    const uint8_t target_sys  = 1;   // автопілот зазвичай має system id = 1
    const uint8_t target_comp = 1;   // MAV_COMP_ID_AUTOPILOT1

    mavlink_msg_command_long_pack(
        my_sysid, my_compid,
        &msg,
        target_sys, target_comp,
        MAV_CMD_DO_SET_SERVO,        // команда «задати вихід серва»
        0,                           // confirmation: 0 = не повтор
        (float)out_channel,          // param1: номер виходу (гребінки)
        (float)pulse_us,             // param2: ширина імпульсу, мкс
        0, 0, 0, 0, 0);              // param3..7 не потрібні

    int len = mavlink_msg_to_send_buffer(buf, &msg);
    write(serial_fd, buf, len);      // відправити в порт телеметрії
}

// виклик: серво на виході 5 — у нейтраль
servo_set_pwm(fd, 5, 1500);
