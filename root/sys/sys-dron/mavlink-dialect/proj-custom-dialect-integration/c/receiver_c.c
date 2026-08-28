/* receiver_c.c — Побайтовий парсер та диспетчер команд на C */
#include <stdint.h>
#include "smart_multispectral/mavlink.h"

#define SENSOR_SYSID  1
#define SENSOR_COMPID 100

extern void uart_send_bytes(const uint8_t *data, uint16_t length);
extern void trigger_hardware_capture(uint32_t exposure_ms, uint8_t filter);

static void handle_command_long(const mavlink_message_t *msg)
{
    mavlink_command_long_t cmd;
    mavlink_msg_command_long_decode(msg, &cmd);

    /* Перевіряємо адресність: команда призначена нашому модулю? */
    if (cmd.target_system != SENSOR_SYSID && cmd.target_system != 0) return;
    if (cmd.target_component != SENSOR_COMPID && cmd.target_component != 0) return;

    uint8_t result = MAV_RESULT_UNSUPPORTED;

    if (cmd.command == 42050 /* MAV_CMD_DO_TRIGGER_SPECTRAL_CAPTURE */) {
        uint32_t exposure_ms = (uint32_t)cmd.param1;
        uint8_t filter_mode = (uint8_t)cmd.param2;

        /* Запуск апаратного процесу зйомки */
        trigger_hardware_capture(exposure_ms, filter_mode);
        result = MAV_RESULT_ACCEPTED;
    }

    /* Надсилаємо підтвердження виконання команди (COMMAND_ACK) */
    mavlink_message_t ack_msg;
    uint8_t tx_buf[MAVLINK_MAX_PACKET_LEN];

    mavlink_msg_command_ack_pack(
        SENSOR_SYSID,
        SENSOR_COMPID,
        &ack_msg,
        cmd.command,
        result,
        0,     /* progress */
        0,     /* result_param2 */
        msg->sysid,
        msg->compid
    );

    uint16_t len = mavlink_msg_to_send_buffer(tx_buf, &ack_msg);
    uart_send_bytes(tx_buf, len);
}

void process_incoming_byte(uint8_t byte)
{
    mavlink_message_t msg;
    mavlink_status_t status;

    /* Побайтовий скінченний автомат розбору кадру MAVLink */
    if (mavlink_parse_char(MAVLINK_COMM_0, byte, &msg, &status)) {
        switch (msg.msgid) {
            case MAVLINK_MSG_ID_COMMAND_LONG:
                handle_command_long(&msg);
                break;
            default:
                break;
        }
    }
}
