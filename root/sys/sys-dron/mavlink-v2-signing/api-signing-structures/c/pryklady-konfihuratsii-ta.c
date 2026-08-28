#include <mavlink.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>

static mavlink_signing_t g_signing_channel0;
static mavlink_signing_streams_t g_signing_streams_channel0;

// Функція безпечної конвертації POSIX часу в таймстемп MAVLink
static uint64_t get_system_mavlink_timestamp(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    uint64_t unix_us = (uint64_t)ts.tv_sec * 1000000ULL + (uint64_t)(ts.tv_nsec / 1000);
    uint64_t epoch_us = 1420070400000000ULL; // 2015-01-01 00:00:00 GMT
    
    if (unix_us < epoch_us) {
        return 1; // Захист від некоректного системного годинника
    }
    return (unix_us - epoch_us) / 10ULL;
}

// Колбек фільтрації непідписаного трафіку
static bool signing_filter_cb(const mavlink_status_t *status, uint32_t msgid) {
    (void)status;
    // Дозволяємо без підпису лише відкриту базову телеметрію
    if (msgid == MAVLINK_MSG_ID_HEARTBEAT || 
        msgid == MAVLINK_MSG_ID_ATTITUDE ||
        msgid == MAVLINK_MSG_ID_GLOBAL_POSITION_INT) {
        return true;
    }
    return false; // Усі команди вимагають валідного підпису
}

void setup_mavlink_signing_interface(uint8_t channel, const uint8_t raw_key[32], uint8_t link_id) {
    memset(&g_signing_channel0, 0, sizeof(g_signing_channel0));
    memset(&g_signing_streams_channel0, 0, sizeof(g_signing_streams_channel0));

    g_signing_channel0.flags = MAVLINK_SIGNING_FLAG_SIGN_OUTGOING;
    g_signing_channel0.link_id = link_id;
    g_signing_channel0.timestamp = get_system_mavlink_timestamp();
    memcpy(g_signing_channel0.secret_key, raw_key, 32);
    g_signing_channel0.streams = &g_signing_streams_channel0;
    g_signing_channel0.accept_unsigned_callback = signing_filter_cb;

    // Прив'язка до внутрішнього стану бібліотеки MAVLink
    mavlink_status_t *status = mavlink_get_channel_status(channel);
    status->signing = &g_signing_channel0;
    status->signing_streams = &g_signing_streams_channel0;
}
