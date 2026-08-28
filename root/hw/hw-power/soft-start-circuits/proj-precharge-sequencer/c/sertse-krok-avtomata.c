typedef enum { ST_IDLE = 0, ST_PRECHARGE, ST_RUN, ST_FAULT } pc_state_t;
typedef enum { FLT_NONE = 0, FLT_TIMEOUT, FLT_BUS_LOST, FLT_SENSOR } pc_fault_t;

static pc_state_t    g_state = ST_IDLE;
static pc_fault_t    g_fault = FLT_NONE;
static uint32_t      g_t_enter;      // час входу в стан
static uint32_t      g_t_main;       // час замикання головного
static bool          g_main_closed;  // головний уже замкнено (у PRECHARGE)
static volatile bool g_start_req;    // команда «пуск» (ставить інший контекст)

static uint32_t threshold_mV(void)
{
    return (uint32_t)((uint64_t)VBUS_NOMINAL_mV * PRECHARGE_TARGET_pct / 100u);
}

static void enter_fault(pc_fault_t code, uint32_t now)
{
    hw_relay_main(false);           // ПЕРШЕ — зняти обидва ключі
    hw_relay_precharge(false);
    g_fault   = code;
    g_state   = ST_FAULT;
    g_t_enter = now;
    hw_fault_report((uint8_t)code);
}

// Викликати рівно кожні TICK_ms.
void precharge_tick(void)
{
    uint32_t now  = hw_millis();
    uint32_t vbus = filter_push(adc_to_bus_mV(hw_adc_read_bus()));

    // З будь-якого стану: неможливе значення -> аварія давача.
    if (vbus > VBUS_MAX_PLAUSIBLE_mV && g_state != ST_FAULT) {
        enter_fault(FLT_SENSOR, now);
        return;
    }

    switch (g_state) {
    case ST_IDLE:
        hw_relay_precharge(false);
        hw_relay_main(false);
        g_main_closed = false;
        if (g_start_req) {
            g_start_req = false;
            hw_relay_precharge(true);        // 1) замкнути передзарядне реле
            g_state   = ST_PRECHARGE;
            g_t_enter = now;
        }
        break;

    case ST_PRECHARGE:
        if (!g_main_closed) {
            if (vbus >= threshold_mV()) {
                hw_relay_main(true);         // 2) заряджено -> замкнути головний
                g_main_closed = true;
                g_t_main = now;
            } else if (now - g_t_enter >= PRECHARGE_TIMEOUT_ms) {
                enter_fault(FLT_TIMEOUT, now);   // шина не зарядилась -> коротке/обрив
            }
        } else if (now - g_t_main >= CONTACTOR_SETTLE_ms) {
            hw_relay_precharge(false);       // 3) контакти зійшлися -> зняти передзаряд
            g_state   = ST_RUN;
            g_t_enter = now;
        }
        break;

    case ST_RUN:
        // головний тримає шину; стежимо, що напруга не впала.
        if (vbus < VBUS_NOMINAL_mV / 2u) {
            enter_fault(FLT_BUS_LOST, now);
        }
        break;

    case ST_FAULT:
        hw_relay_precharge(false);
        hw_relay_main(false);
        break;
    }
}

// ── Керування ззовні ──────────────────────────────────────────────────
void precharge_start(void) { g_start_req = true; }   // «пуск»

void precharge_stop(void)                            // «стоп»
{
    hw_relay_main(false);
    hw_relay_precharge(false);
    g_main_closed = false;
    g_state = ST_IDLE;
}

bool precharge_reset(void)                           // скид аварії (лише з FAULT)
{
    if (g_state != ST_FAULT) return false;
    g_fault = FLT_NONE;
    g_main_closed = false;
    g_state = ST_IDLE;
    return true;
}

pc_state_t precharge_state(void) { return g_state; }
