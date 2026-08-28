#include <mavlink.h>
#include <string.h>

// 1. Ініціалізація спільного ключа
static const uint8_t g_secret_key[32] = {
    0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF,
    0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10,
    0x55, 0xAA, 0x55, 0xAA, 0x33, 0xCC, 0x33, 0xCC,
    0x0F, 0xF0, 0x0F, 0xF0, 0xAA, 0x55, 0xAA, 0x55
};

void send_signed_arm_command(uint8_t channel) {
    mavlink_message_t msg;
    mavlink_command_long_t cmd = {0};

    cmd.target_system    = 1;
    cmd.target_component = 1;
    cmd.command          = MAV_CMD_COMPONENT_ARM_DISARM;
    cmd.confirmation     = 0;
    cmd.param1           = 1.0f; // 1.0 = озброїти мотори (ARM)

    // Кодуємо повідомлення COMMAND_LONG (MSG ID 76)
    mavlink_msg_command_long_encode(255, 190, &msg, &cmd);

    // Налаштовуємо підпис у статусі каналу
    mavlink_status_t *status = mavlink_get_channel_status(channel);
    mavlink_signing_t signing_ctx = {0};
    mavlink_signing_streams_t streams = {0};

    signing_ctx.flags = MAVLINK_SIGNING_FLAG_SIGN_OUTGOING;
    signing_ctx.link_id = 0;
    signing_ctx.timestamp = 125000000ULL; // Поточний час (1250 с від епохи 2015)
    memcpy(signing_ctx.secret_key, g_secret_key, 32);
    signing_ctx.streams = &streams;

    status->signing = &signing_ctx;

    // Пакуємо кадр у буфер для відправки в UART
    uint8_t send_buf[MAVLINK_MAX_PACKET_LEN];
    uint16_t packet_len = mavlink_msg_to_send_buffer(send_buf, &msg);

    // Готовий кадр містить: Header(10) + Payload(33 після zero-trim) + CRC(2) + Signature(13) = 58 байтів
    // serial_write(send_buf, packet_len);
}
