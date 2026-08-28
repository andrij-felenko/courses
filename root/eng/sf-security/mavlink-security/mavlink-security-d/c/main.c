#include <mavlink.h>
#include <string.h>

// 1. Спільний 256-бітний ключ
static const uint8_t g_secret_key[32] = {
    0x1A, 0x2B, 0x3C, 0x4D, 0x5E, 0x6F, 0x70, 0x81,
    0x92, 0xA3, 0xB4, 0xC5, 0xD6, 0xE7, 0xF8, 0x09,
    0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88,
    0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00
};

// 2. Формування та відправка підписаної команди
uint16_t send_signed_arm_command(uint8_t *send_buf, uint8_t channel) {
    mavlink_message_t msg;
    mavlink_command_long_t cmd = {0};

    cmd.target_system    = 1;
    cmd.target_component = 1;
    cmd.command          = MAV_CMD_COMPONENT_ARM_DISARM;
    cmd.confirmation     = 0;
    cmd.param1           = 1.0f; // 1.0 = Озброїти мотори (ARM)

    mavlink_msg_command_long_encode(255, 190, &msg, &cmd);

    // Налаштовуємо структуру підпису
    mavlink_status_t *status = mavlink_get_channel_status(channel);
    mavlink_signing_t signing_ctx = {0};
    mavlink_signing_streams_t streams = {0};

    signing_ctx.flags = MAVLINK_SIGNING_FLAG_SIGN_OUTGOING;
    signing_ctx.link_id = 0;
    signing_ctx.timestamp = 150000000ULL; // Монотонний час станції
    memcpy(signing_ctx.secret_key, g_secret_key, 32);
    signing_ctx.streams = &streams;

    status->signing = &signing_ctx;

    // Пакуємо підписане повідомлення у буфер
    return mavlink_msg_to_send_buffer(send_buf, &msg);
}
