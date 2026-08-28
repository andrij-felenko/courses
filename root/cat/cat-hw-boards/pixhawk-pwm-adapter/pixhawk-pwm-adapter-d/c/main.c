// Примусово задати ширину імпульсу на каналі серворульової машинки.
// УВАГА: команда обходить штатне змішування — на реальному апараті з
// увімкненими моторами так робити НЕ можна. Лише перевірка на столі.
mavlink_message_t msg;
uint8_t buf[MAVLINK_MAX_PACKET_LEN];

const uint8_t  servo_channel = 5;      // фізичний вихід (гребінка) № 5
const uint16_t pulse_us      = 1500;   // 1500 мкс = нейтраль серва

mavlink_msg_command_long_pack(
    255, 0,                            // хто шле: id наземної станції
    &msg,
    1, 1,                              // кому: система 1, автопілот
    MAV_CMD_DO_SET_SERVO,              // команда «задати вихід серва»
    0,                                 // не повтор
    servo_channel,                     // param1: номер каналу
    pulse_us,                          // param2: ширина імпульсу, мкс
    0, 0, 0, 0, 0);                    // решта параметрів не потрібні

int len = mavlink_msg_to_send_buffer(buf, &msg);
serial_write(buf, len);               // відправити в порт телеметрії
