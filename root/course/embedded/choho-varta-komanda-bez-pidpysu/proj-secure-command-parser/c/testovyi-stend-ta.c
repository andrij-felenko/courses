#include <stdio.h>

int main(void) {
    uint8_t secret_key[16] = "mcu_secret_key1";
    ReplayWindow window;
    replay_window_init(&window);

    uint8_t buffer[64];
    SecureFrameHeader *hdr = (SecureFrameHeader *)buffer;
    hdr->magic = SECURE_FRAME_MAGIC;
    hdr->msg_type = 0x01; /* Наприклад, SET_SERVO_ANGLE */
    hdr->reserved = 0x00;
    hdr->seq_num = 100;
    hdr->timestamp = 1700000000U;
    hdr->payload_len = 2;

    uint8_t payload[2] = {0x00, 0x5A}; /* 90 градусів */
    memcpy(buffer + sizeof(SecureFrameHeader), payload, 2);

    uint8_t tag[SECURE_TAG_SIZE];
    compute_hmac_sha256(secret_key, sizeof(secret_key), buffer, sizeof(SecureFrameHeader) + 2, tag);
    memcpy(buffer + sizeof(SecureFrameHeader) + 2, tag, SECURE_TAG_SIZE);

    size_t frame_len = sizeof(SecureFrameHeader) + 2 + SECURE_TAG_SIZE;

    uint8_t out_type;
    const uint8_t *out_data;
    uint16_t out_len;

    /* Тест 1: Перше надсилання */
    SecureStatus st = secure_frame_parse(buffer, frame_len, secret_key, sizeof(secret_key),
                                         1700000005U, 10, &window, &out_type, &out_data, &out_len);
    printf("Test 1 (Valid Frame): status = %d (expected 0)\n", st);

    /* Тест 2: Спроба повтору (Replay Attack) */
    st = secure_frame_parse(buffer, frame_len, secret_key, sizeof(secret_key),
                            1700000006U, 10, &window, &out_type, &out_data, &out_len);
    printf("Test 2 (Replay Attack): status = %d (expected %d)\n", st, SECURE_ERR_REPLAY_DETECTED);

    /* Тест 3: Підміна корисного навантаження */
    buffer[sizeof(SecureFrameHeader)] = 0xFF;
    hdr->seq_num = 101;
    st = secure_frame_parse(buffer, frame_len, secret_key, sizeof(secret_key),
                            1700000007U, 10, &window, &out_type, &out_data, &out_len);
    printf("Test 3 (Tampered Payload): status = %d (expected %d)\n", st, SECURE_ERR_AUTH_FAILED);

    return 0;
}
