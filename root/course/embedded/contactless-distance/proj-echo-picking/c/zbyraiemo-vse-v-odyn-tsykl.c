#include <stdint.h>

#define N_PINGS       5
#define PING_GAP_MS   40        // пауза між пінгами: щоб луна попереднього згасла

extern void     delay_ms(uint32_t ms);
extern float    read_temperature_c(void);   // копійчаний давач температури

// Результат виміру: distance_m < 0 означає «цілі в діапазоні нема».
typedef struct { float distance_m; uint8_t valid; } range_t;

range_t measure(void) {
    uint32_t times[N_PINGS];
    int      got = 0;

    // 1) кілька пінгів, кожен — крізь усі внутрішні ворота
    for (int i = 0; i < N_PINGS; i++) {
        uint32_t t0   = send_ping();           // пуск + бланкування дзвону
        uint32_t echo = find_echo(t0);         // спадний поріг + тривалість + гістерезис
        if (echo > 0)
            times[got++] = echo;               // зберігаємо лише вдалі засічки
        delay_ms(PING_GAP_MS);                 // дати луні згаснути перед наступним
    }

    range_t r = { .distance_m = -1.0f, .valid = 0 };

    // 2) потрібна більшість вдалих засічок — інакше цілі надійно нема
    if (got < (N_PINGS / 2 + 1))
        return r;                              // забагато тиші/шуму → чесно кажемо «нема»

    // 3) медіана вцілілих часів — викидає поодинокі стрибки
    uint32_t t_med = median_us(times, got);

    // 4) час → метри з ЖИВОЮ швидкістю звуку (температурна поправка)
    r.distance_m = tof_to_distance_m(t_med, read_temperature_c());
    r.valid      = 1;
    return r;
}
