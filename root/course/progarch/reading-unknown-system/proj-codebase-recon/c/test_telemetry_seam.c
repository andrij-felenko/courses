/* Characterization Test у C: test_telemetry_seam.c */
#include <assert.h>
#include <string.h>

static char g_last_log[128] = {0};
static int g_last_device = -1;

/* Тестовий шов — перехоплює виклики замість мережі */
static void test_capture_sink(int device_id, const char* message) {
    g_last_device = device_id;
    strncpy(g_last_log, message, sizeof(g_last_log) - 1);
}

void run_characterization_tests(void) {
    /* Підміняємо шов тестовим перехоплювачем */
    g_notification_seam = test_capture_sink;

    telemetry_packet_t pkt1 = { .device_id = 101, .raw_temperature = 90.0f, .status_flags = 0x01 };
    int res1 = process_device_telemetry(&pkt1);
    
    /* Фіксуємо поточну поведінку як незмінний факт */
    assert(res1 == 2);
    assert(g_last_device == 101);
    assert(strcmp(g_last_log, "CRITICAL_OVERHEAT") == 0);

    /* Тест на випадок, коли прапор 0x01 НЕ встановлено при високій температурі */
    telemetry_packet_t pkt2 = { .device_id = 102, .raw_temperature = 90.0f, .status_flags = 0x00 };
    int res2 = process_device_telemetry(&pkt2);
    
    /* Відкриття: без прапора 0x01 температура 90C вважається НОРМОЮ (res == 0)!
       Ми фіксуємо цю дивну поведінку тестом, щоб не зламати її випадково. */
    assert(res2 == 0);

    printf("Усі характеристичні тести пройдено успішно!\n");
}
