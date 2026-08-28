// Мінімальний запис події failsafe — те, без чого потім не розберешся.
typedef struct {
    uint32_t time_ms;     // монотонний час спрацювання (від старту)
    int32_t  lat_1e7;     // широта, у 1e-7 градуса (формат GPS ArduPilot)
    int32_t  lon_1e7;     // довгота, так само
    fs_state_t from;      // з якого стану
    fs_state_t to;        // у який перейшли
    uint8_t  reason;      // 0=uplink тиша, 1=downlink тиша
} fs_log_entry_t;

// Виклики, які реалізує платформа (маяк — GPIO/сирена; журнал — у Flash/FRAM).
extern void beacon_set(bool on);
extern void fs_log_write(const fs_log_entry_t *e);
extern void mav_get_position(int32_t *lat_1e7, int32_t *lon_1e7);
extern uint8_t fs_last_reason(void);   // що саме замовкло (uplink чи downlink)

// Записати перехід у журнал із поточними координатами й часом.
static void fs_log_transition(fs_state_t from, fs_state_t to, uint32_t now_ms)
{
    fs_log_entry_t e;
    e.time_ms = now_ms;
    e.from    = from;
    e.to      = to;
    e.reason  = fs_last_reason();
    mav_get_position(&e.lat_1e7, &e.lon_1e7);   // де ми зараз
    fs_log_write(&e);
}
