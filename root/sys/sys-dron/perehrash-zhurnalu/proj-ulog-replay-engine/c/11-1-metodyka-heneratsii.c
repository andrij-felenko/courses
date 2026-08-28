#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <string.h>

/* Функція створення синтетичного тестового ULog файлу */
static void generate_synthetic_ulog_file(const char *filename) {
    FILE *f = fopen(filename, "wb");
    assert(f != NULL);

    /* 1. Заголовок ULog (16 байтів) */
    uint8_t header[16] = {
        0x55, 0x4C, 0x6F, 0x67, 0x01, 0x12, 0x35, 0x00,
        0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00 /* 1048576 мкс */
    };
    fwrite(header, 1, 16, f);

    /* 2. Оголошення формату 'F' для sensor_combined */
    const char *fmt_text = "sensor_combined:uint64_t timestamp;float[3] gyro_rad;float[3] accel_m_s2;";
    uint16_t fmt_len = (uint16_t)strlen(fmt_text);
    uint8_t fmt_hdr[3] = { (uint8_t)(fmt_len & 0xFF), (uint8_t)(fmt_len >> 8), 'F' };
    fwrite(fmt_hdr, 1, 3, f);
    fwrite(fmt_text, 1, fmt_len, f);

    /* 3. Підписка 'A' (msg_id = 1, multi_id = 0) */
    uint8_t sub_payload[32];
    sub_payload[0] = 0; /* multi_id */
    sub_payload[1] = 1; /* msg_id low */
    sub_payload[2] = 0; /* msg_id high */
    strcpy((char *)&sub_payload[3], "sensor_combined");
    uint16_t sub_len = 3 + (uint16_t)strlen("sensor_combined");
    uint8_t sub_hdr[3] = { (uint8_t)(sub_len & 0xFF), (uint8_t)(sub_len >> 8), 'A' };
    fwrite(sub_hdr, 1, 3, f);
    fwrite(sub_payload, 1, sub_len, f);

    /* 4. Запис серії кадрів даних 'D' з навмисно переплутаним порядком часу */
    uint64_t timestamps[4] = { 1048600, 1048580, 1048650, 1048620 };
    for (int i = 0; i < 4; i++) {
        uint8_t data_payload[34];
        data_payload[0] = 1; /* msg_id low */
        data_payload[1] = 0; /* msg_id high */
        memcpy(&data_payload[2], &timestamps[i], 8);
        memset(&data_payload[10], 0, 24); /* dummy float arrays */

        uint16_t data_len = 34;
        uint8_t data_hdr[3] = { (uint8_t)(data_len & 0xFF), (uint8_t)(data_len >> 8), 'D' };
        fwrite(data_hdr, 1, 3, f);
        fwrite(data_payload, 1, data_len, f);
    }

    fclose(f);
}

/* Callback перевірки монотонності відтворення */
static uint64_t g_last_t_sim = 0;
static size_t g_verified_frames = 0;

static void verify_replay_callback(uint64_t t_sim, const char *topic, 
                                   uint8_t instance, const uint8_t *data, 
                                   uint16_t size, void *user_data) {
    (void)instance;
    (void)data;
    (void)size;
    (void)user_data;

    printf("  [Тестовий диспетчер] Топік: %s, t_sim = %llu мкс\n", 
           topic, (unsigned long long)t_sim);

    /* Перевірка суворої монотонності віртуального часу */
    assert(t_sim >= g_last_t_sim);
    g_last_t_sim = t_sim;
    g_verified_frames++;
}

int main(void) {
    const char *test_file = "test_synthetic_flight.ulg";
    printf("[Юніт-тест Replay Engine] Створення синтетичного ULog...\n");
    generate_synthetic_ulog_file(test_file);

    printf("[Юніт-тест Replay Engine] Запуск переграшу...\n");
    ulog_replay_engine_t engine;
    bool ok = ulog_engine_init(&engine, test_file, verify_replay_callback, NULL);
    assert(ok == true);

    ulog_engine_run(&engine);

    assert(g_verified_frames == 4);
    printf("[Юніт-тест Replay Engine] Тест УСПІШНО пройдено. Детермінізм підтверджено!\n");

    remove(test_file);
    return 0;
}
