#include <math.h>
#include <stdio.h>
#include <string.h>

#include "fallback.h"
#include "platform.h"

#define KEY              0x00C0FFEEu
#define SESSION_FIRST    0x000051E5u
#define SESSION_SECOND   0x00007A11u
#define FRAME_PERIOD_MS  40U
#define SIM_END_MS       95000U

// Годинник пульта попереду нашого на 3.2 с, а перед перепідключенням сервер
// сам підтягнувся по NTP назад на 1.5 с. Пристрій мусить пережити обидва
// зсуви, жодного разу не пустивши свій монотонний час назад.
static uint32_t server_clock(uint32_t t) { return (t < 70000U) ? t + 3200U : t + 1700U; }

// Ефір: коротке завмирання за стелажем і довгий обрив за бетонною стіною.
static bool air_up(uint32_t t) {
    if (t >= 3000U && t < 3300U) return false;
    if (t >= 6000U && t < 76000U) return false;
    return true;
}

static float pult_throttle(uint32_t t) { return (t < 2000U) ? 0.4f : 0.8f; }

static uint32_t rng = 2463534242u;
static float sensor_noise(void) {
    rng ^= rng << 13;
    rng ^= rng >> 17;
    rng ^= rng << 5;
    return ((float)(rng % 1000U) / 1000.0f - 0.5f) * 0.6f;
}

static const char *event_name(uint8_t ev) {
    switch (ev) {
    case FB_EV_LINK_LOST:  return "зв'язок зник";
    case FB_EV_PHASE2:     return "перехід у фазу 2";
    case FB_EV_SAFE_STATE: return "безпечний стан";
    case FB_EV_DR_LIMIT:   return "числення шляху обірвано";
    case FB_EV_RECONNECT:  return "рукостискання";
    case FB_EV_ONLINE:     return "контроль повернуто";
    case LOG_EV_SAMPLE:    return "пачка телеметрії";
    default:               return "?";
    }
}

static void report(uint32_t t, const fallback_t *fb, const char *why) {
    printf("%7.2f с | %-16s | %-20s | тяга %+5.2f | ШІМ %+5.2f | живлення %d | interlock %d | гальмо %d | лог %3u\n",
           t / 1000.0, why, fallback_state_name(fb->state), (double)fb->throttle,
           (double)plat_throttle_out(), plat_power_enabled() ? 1 : 0,
           plat_interlock_enabled() ? 1 : 0, plat_brake() ? 1 : 0,
           (unsigned)logstore_pending(&fb->log));
}

int main(void) {
    plat_init();

    fallback_t fb;
    fallback_init(&fb, plat_now_ms(), KEY);

    uint32_t session = SESSION_FIRST;
    uint32_t seq = 1U;
    bool handshaken = false;
    bool air_prev = false;
    fallback_state_t state_prev = fb.state;
    uint32_t next_frame_ms = 0U;
    uint32_t next_note_ms = 10000U;

    uint8_t stale_frame[LINK_FRAME_SIZE];
    bool stale_saved = false;
    bool stale_tried = false;

    report(0U, &fb, "старт");

    for (uint32_t t = 0U; t <= SIM_END_MS; t += FB_TICK_MS) {
        bool air = air_up(t);
        if (air != air_prev) {
            plat_radio_set_up(air);
            if (!air) {
                handshaken = false;
            } else if (t > 10000U) {
                session = SESSION_SECOND;   // після довгої тиші пульт відкриває нову сесію
            }
            air_prev = air;
            report(t, &fb, air ? "ефір є" : "ефір зник");
        }

        if (air && t >= next_frame_ms) {
            next_frame_ms = t + FRAME_PERIOD_MS;
            uint8_t frame[LINK_FRAME_SIZE];
            uint32_t st_ms = server_clock(t);

            if (!handshaken) {
                // Крок 1: спершу пульт виплюне команду, що чекала в його черзі
                // ще з часів до обриву. Пристрій зобов'язаний її відкинути.
                if (stale_saved && !stale_tried && t > 70000U) {
                    stale_tried = true;
                    link_status_t st = fallback_on_frame(&fb, stale_frame, sizeof stale_frame, t);
                    printf("%7.2f с | %-16s | застаріла команда з черги пульта: %s\n",
                           t / 1000.0, "реплей", link_status_name(st));
                }
                size_t n = link_encode_hello(frame, sizeof frame, KEY, session, st_ms);
                if (fallback_on_frame(&fb, frame, n, t) == LINK_OK) {
                    handshaken = true;
                    report(t, &fb, "рукостискання");
                }
            } else {
                size_t n = link_encode_command(frame, sizeof frame, KEY, session, seq++, st_ms,
                                               pult_throttle(t), 0.0f);
                fallback_on_frame(&fb, frame, n, t);
                if (!stale_saved && t >= 2000U) {
                    memcpy(stale_frame, frame, n);
                    stale_saved = true;
                }
            }
        }

        // Давач струму двигуна: те, що справді доїхало до обмоток, плюс шум.
        float current_a = fabsf(plat_throttle_out()) * 42.0f + sensor_noise();
        fallback_tick(&fb, t, current_a);

        if (fb.state != state_prev) {
            state_prev = fb.state;
            report(t, &fb, "зміна стану");
        }
        if (t >= next_note_ms) {
            next_note_ms += 10000U;
            report(t, &fb, "зріз");
        }

        plat_advance_ms(FB_TICK_MS);
    }

    printf("\n--- підсумок прогону ---\n");
    printf("стан наприкінці         : %s\n", fallback_state_name(fb.state));
    printf("кадрів прийнято         : %u\n", (unsigned)fb.link.accepted);
    printf("відкинуто               : CRC %u, автентифікація %u, сесія %u, повтор %u, застарілі %u\n",
           (unsigned)fb.link.rej_crc, (unsigned)fb.link.rej_auth, (unsigned)fb.link.rej_session,
           (unsigned)fb.link.rej_replay, (unsigned)fb.link.rej_stale);
    printf("спрацювань мертвої руки : %u\n", (unsigned)fb.dm.trips);
    printf("записів у Flash         : %u (затерто не злитих %u, втрачено %u, блокувальних стирань %u)\n",
           (unsigned)fb.log.written, (unsigned)fb.log.overwritten,
           (unsigned)fb.log.dropped, (unsigned)fb.log.blocking_erases);
    printf("у черзі на злив         : %u записів, в ефір пішло %u байтів\n",
           (unsigned)logstore_pending(&fb.log), (unsigned)plat_radio_bytes_sent());
    printf("поправка годинника      : %+d мс, лишилося підтягнути %+d мс\n",
           (int)fb.tb.offset_ms, (int)timebase_pending(&fb.tb));

    printf("стирань по секторах     :");
    for (uint16_t i = 0; i < FLASH_SECTOR_COUNT; i++) {
        printf(" %u", (unsigned)plat_flash_erase_count(i));
    }
    printf("\n");

    uint32_t bb = logstore_blackbox_count(&fb.log);
    printf("чорна скринька (%u записів):\n", (unsigned)bb);
    for (uint32_t i = 0; i < bb; i++) {
        log_record_t r;
        if (!logstore_blackbox_get(&fb.log, i, &r)) continue;
        printf("   t=%8.2f с  подія 0x%02X  %s\n", r.t_ms / 1000.0, r.event, event_name(r.event));
    }
    return 0;
}
