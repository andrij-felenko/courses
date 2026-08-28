/* Legacy C code: hub_telemetry.h / hub_telemetry.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Офіційний доменний тип легасі-системи */
typedef struct {
    int device_id;
    float raw_temperature;
    int status_flags;
} telemetry_packet_t;

/* Вказівник на функцію відправки сповіщень — це і є наш ШОВ (Seam).
   У продакшні він вказує на реальну мережу, у тесті — на заглушку. */
typedef void (*notification_sink_t)(int device_id, const char* message);

static void default_network_sink(int device_id, const char* message) {
    /* Реальна відправка в мережевий сокет */
    printf("[NET-SEND] Device %d: %s\n", device_id, message);
}

/* Глобальний або контекстний шов */
notification_sink_t g_notification_seam = default_network_sink;

/* Легасі-функція з невідомими інваріантами */
int process_device_telemetry(const telemetry_packet_t* pkt) {
    if (!pkt) return -1;

    /* Заплутана легасі-логіка перевірки порогів */
    if (pkt->raw_temperature > 85.0f && (pkt->status_flags & 0x01)) {
        g_notification_seam(pkt->device_id, "CRITICAL_OVERHEAT");
        return 2; /* Критичний стан */
    } else if (pkt->raw_temperature < -20.0f) {
        g_notification_seam(pkt->device_id, "SENSOR_FREEZE");
        return 1; /* Попередження */
    }

    return 0; /* Норма */
}
