#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t  active_pilot_gcs_id;
    uint32_t token_nonce;
    uint32_t lease_deadline_ms;
    bool     commander_locked;
} flight_arbiter_t;

static flight_arbiter_t g_flight_arbiter;

/* Швидкий фільтр вхідних 50 Гц пакетів ручного керування */
bool is_manual_control_packet_valid(uint8_t src_gcs_id, uint32_t nonce, uint32_t now_ms) {
    if (g_flight_arbiter.commander_locked) {
        return false; /* Заблоковано командиром */
    }
    if (now_ms > g_flight_arbiter.lease_deadline_ms) {
        return false; /* Оренда прострочена */
    }
    if (src_gcs_id != g_flight_arbiter.active_pilot_gcs_id) {
        return false; /* Джерело не є активним пілотом */
    }
    if (nonce != g_flight_arbiter.token_nonce) {
        return false; /* Недійсний або застарілий токен */
    }
    return true;
}
