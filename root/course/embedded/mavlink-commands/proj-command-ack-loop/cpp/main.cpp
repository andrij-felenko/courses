#include <stdint.h>
#include "mavlink.h"

// Прочитати з лінка наявні байти, згодувати їх парсеру MAVLink і,
// якщо зібрався COMMAND_ACK саме на очікувану команду, віддати його.
// Повертає true один раз — коли такий ACK з'явився.
bool poll_command_ack(uint16_t want_cmd, mavlink_command_ack_t *out);

// Зібрати й відіслати один кадр COMMAND_LONG.
static void send_command(uint16_t cmd, uint8_t confirmation,
                         float p1, float p2, float p3,
                         float p4, float p5, float p6, float p7) {
    mavlink_message_t m;
    mavlink_msg_command_long_pack(MY_SYSID, MY_COMPID, &m,
        TARGET_SYS, TARGET_COMP, cmd, confirmation,
        p1, p2, p3, p4, p5, p6, p7);
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    int n = mavlink_msg_to_send_buffer(buf, &m);
    serial_write(buf, n);
}

// Надіслати команду й дочекатися результату.
// Повертає код MAV_RESULT, або -1, якщо ACK так і не прийшов за всі спроби.
int send_command_blocking(uint16_t cmd,
                          float p1, float p2 = 0, float p3 = 0, float p4 = 0,
                          float p5 = 0, float p6 = 0, float p7 = 0,
                          uint32_t ack_timeout_ms = 1000,
                          uint8_t max_tries = 4) {
    for (uint8_t attempt = 0; attempt < max_tries; ++attempt) {
        send_command(cmd, attempt, p1, p2, p3, p4, p5, p6, p7);  // confirmation = № спроби
        uint32_t deadline = millis() + ack_timeout_ms;
        while ((int32_t)(deadline - millis()) > 0) {
            mavlink_command_ack_t ack;
            if (poll_command_ack(cmd, &ack)) {
                if (ack.result == MAV_RESULT_IN_PROGRESS) {
                    deadline = millis() + 5000;   // довга дія: відсунути таймаут, чекати далі
                    continue;
                }
                return ack.result;                // ACCEPTED / DENIED / FAILED / UNSUPPORTED…
            }
            // тут-таки крутимо приймання телеметрії, щоб не «оглухнути» на час очікування
        }
        // таймаут вийшов — наступна ітерація перешле ту саму команду з confirmation+1
    }
    return -1;   // апарат мовчить: лінк мертвий або апарат не відповідає
}

// Виклик: озброїти апарат.
int r = send_command_blocking(MAV_CMD_COMPONENT_ARM_DISARM, /*param1=*/1.0f);
if (r == MAV_RESULT_ACCEPTED)      { /* мотори озброєно */ }
else if (r == MAV_RESULT_DENIED)   { /* не пройшли передпольотні перевірки */ }
else if (r == -1)                  { /* зв'язку немає — у безпечний стан */ }
