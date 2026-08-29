#include "arbiter.h"

#include <string.h>

typedef struct {
    station_table_t stations;

    uint8_t  pilot_gcs_id;         /* власник токена (0 — нічий) */
    uint8_t  pending_pilot_gcs_id; /* кандидат на зміну */
    uint8_t  commander_gcs_id;     /* хто тримає замок, якщо стан COMMANDER_LOCKED */

    uint32_t pilot_lease_deadline; /* мс: доти оренда чинна */
    uint32_t handover_deadline;    /* мс: доти вікно передачі відкрите */
    uint32_t neutral_since_ms;     /* коли стіки кандидата ввійшли в нейтраль */
    bool     neutral_latched;      /* нейтраль уже зафіксовано (діє ширший поріг) */

    uint32_t token_nonce;          /* міняється на КОЖНУ зміну власника */
    uint32_t rng_state;

    int16_t  current_thrust;       /* остання тяга з мікшера, 0..1000 */

    arbiter_state_t state;
    arbiter_state_t resume_state;  /* куди вернутися після LINK_LOST */
} arbiter_context_t;

/* Єдиний екземпляр, статичний. Купи в контурі керування немає взагалі. */
static arbiter_context_t g_arb;

/* --- дрібні помічники ------------------------------------------------- */

/* Час порівнюємо різницею, а не «більше»: лічильник мс переповнюється
 * приблизно на 49-й день, і наївне now >= deadline тоді відкриє все підряд. */
static bool time_reached(uint32_t now_ms, uint32_t deadline_ms)
{
    return (int32_t)(now_ms - deadline_ms) >= 0;
}

/* xorshift32 — швидкий і достатній: nonce ховає не таємницю, а вікно, у якому
 * старий пульт міг би вклинитися зі своїм застарілим токеном. Нуль заборонено:
 * ним позначаємо «недійсний». */
static uint32_t next_nonce(void)
{
    uint32_t x = g_arb.rng_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    g_arb.rng_state = x;
    return (x == 0u) ? 0xA5A5A5A5u : x;
}

static bool axis_within(int16_t value, int16_t limit)
{
    return (value >= (int16_t)-limit) && (value <= limit);
}

static void drop_handover(void)
{
    g_arb.pending_pilot_gcs_id = 0;
    g_arb.handover_deadline = 0;
    g_arb.neutral_since_ms = 0;
    g_arb.neutral_latched = false;
}

/* Запис нової сесії: власник і nonce мусять помінятися разом, інакше між
 * двома присвоєннями пролізе пакет старого пульта з новим власником. */
static uint32_t commit_owner(uint8_t new_owner, uint32_t now_ms, arbiter_state_t new_state)
{
    uint32_t nonce = next_nonce();

    ARB_CRITICAL_ENTER();
    g_arb.pilot_gcs_id = new_owner;
    g_arb.token_nonce = nonce;
    g_arb.pilot_lease_deadline = now_ms + ARB_HEARTBEAT_TIMEOUT_MS;
    g_arb.state = new_state;
    ARB_CRITICAL_EXIT();

    g_arb.resume_state = new_state;
    drop_handover();
    return nonce;
}

/* --- життєвий цикл ---------------------------------------------------- */

void arbiter_init(uint32_t seed, uint32_t now_ms)
{
    memset(&g_arb, 0, sizeof(g_arb));
    station_table_init(&g_arb.stations);
    g_arb.rng_state = (seed != 0u) ? seed : 0xDEADBEEFu;
    g_arb.token_nonce = next_nonce();
    g_arb.state = STATE_IDLE;
    g_arb.resume_state = STATE_IDLE;
    g_arb.pilot_lease_deadline = now_ms;
}

arb_err_t arbiter_process_heartbeat(uint8_t gcs_id, uint8_t roles, uint32_t now_ms)
{
    if (station_touch(&g_arb.stations, gcs_id, roles, now_ms) == NULL) {
        return ERR_TABLE_FULL;
    }

    if (gcs_id != g_arb.pilot_gcs_id || g_arb.pilot_gcs_id == 0u) {
        return ARB_OK; /* звичайна станція: оновили реєстр, і по всьому */
    }

    /* Власник токена мусить і далі мати роль, під якою його пустили.
     * Станція, що перезапустилася лише як монітор, оренду не продовжує. */
    uint8_t needed = (g_arb.state == STATE_COMMANDER_LOCKED) ? ROLE_COMMANDER : ROLE_PILOT;
    if ((roles & needed) == 0u) {
        return ERR_ROLE_DENIED;
    }

    g_arb.pilot_lease_deadline = now_ms + ARB_HEARTBEAT_TIMEOUT_MS;
    if (g_arb.state == STATE_LINK_LOST) {
        /* Звʼязок повернувся — токен той самий, nonce не міняємо:
         * пульт нічого не втрачав і перезапитувати його не мусить. */
        g_arb.state = g_arb.resume_state;
    }
    return ARB_OK;
}

arb_err_t arbiter_request_pilot_token(uint8_t gcs_id, uint32_t now_ms, uint32_t *out_nonce)
{
    if (g_arb.state == STATE_COMMANDER_LOCKED) {
        return ERR_LOCKED;
    }
    if (!station_has_role(&g_arb.stations, gcs_id, ROLE_PILOT, now_ms, ARB_HEARTBEAT_TIMEOUT_MS)) {
        return station_find(&g_arb.stations, gcs_id) ? ERR_ROLE_DENIED : ERR_UNKNOWN_STATION;
    }
    if (g_arb.state != STATE_IDLE && g_arb.state != STATE_LINK_LOST) {
        return ERR_BUSY;
    }
    /* Із LINK_LOST токен забирає будь-який пілот: старий власник мовчить
     * довше за оренду, і борт не має причин тримати його місце. */
    uint32_t nonce = commit_owner(gcs_id, now_ms, STATE_PILOT_ACTIVE);
    if (out_nonce != NULL) {
        *out_nonce = nonce;
    }
    return ARB_OK;
}

/* --- передача зміни --------------------------------------------------- */

arb_err_t arbiter_initiate_handover(uint8_t current_pilot_id, uint8_t target_gcs_id, uint32_t now_ms)
{
    if (g_arb.state == STATE_COMMANDER_LOCKED) {
        return ERR_LOCKED;
    }
    if (g_arb.state != STATE_PILOT_ACTIVE) {
        return ERR_WRONG_STATE;
    }
    if (current_pilot_id != g_arb.pilot_gcs_id) {
        return ERR_NOT_OWNER;
    }
    if (target_gcs_id == current_pilot_id) {
        return ERR_WRONG_STATE;
    }
    if (!station_has_role(&g_arb.stations, target_gcs_id, ROLE_PILOT, now_ms, ARB_HEARTBEAT_TIMEOUT_MS)) {
        return station_find(&g_arb.stations, target_gcs_id) ? ERR_ROLE_DENIED : ERR_UNKNOWN_STATION;
    }

    g_arb.pending_pilot_gcs_id = target_gcs_id;
    g_arb.handover_deadline = now_ms + ARB_HANDOVER_TIMEOUT_MS;
    g_arb.neutral_since_ms = 0;
    g_arb.neutral_latched = false;
    g_arb.state = STATE_HANDOVER_WAIT_STICK;
    g_arb.resume_state = STATE_HANDOVER_WAIT_STICK;
    return ARB_OK;
}

arb_err_t arbiter_confirm_handover_sticks(uint8_t candidate_id, const stick_axes_t *sticks,
                                          uint32_t now_ms, uint32_t *out_nonce)
{
    if (sticks == NULL) {
        return ERR_WRONG_STATE;
    }
    if (g_arb.state != STATE_HANDOVER_WAIT_STICK) {
        return ERR_WRONG_STATE;
    }
    if (candidate_id != g_arb.pending_pilot_gcs_id) {
        return ERR_NOT_OWNER;
    }
    if (time_reached(now_ms, g_arb.handover_deadline)) {
        g_arb.state = STATE_PILOT_ACTIVE;
        g_arb.resume_state = STATE_PILOT_ACTIVE;
        drop_handover();
        return ERR_HANDOVER_TIMEOUT;
    }
    /* Кандидат міг зникнути з ефіру просто під час перевірки. */
    if (!station_has_role(&g_arb.stations, candidate_id, ROLE_PILOT, now_ms, ARB_HEARTBEAT_TIMEOUT_MS)) {
        return ERR_UNKNOWN_STATION;
    }

    /* Гістерезис: поки нейтраль не зафіксована, поріг вузький; після фіксації
     * стіку дозволено трохи дрейфувати, не збиваючи витримку часу. */
    int16_t limit = g_arb.neutral_latched ? ARB_DEADBAND_EXIT : ARB_DEADBAND_ENTER;
    bool centered = axis_within(sticks->roll, limit) &&
                    axis_within(sticks->pitch, limit) &&
                    axis_within(sticks->yaw, limit);
    if (!centered) {
        g_arb.neutral_latched = false;
        g_arb.neutral_since_ms = 0;
        return ERR_STICK_NOT_NEUTRAL;
    }

    /* Газ у зависанні стоїть не в центрі, а десь на 45–60%. Порівнюємо його не
     * з нулем, а з поточною тягою: інакше в мить передачі мотори скинуть оберти. */
    int32_t diff = (int32_t)sticks->throttle - (int32_t)g_arb.current_thrust;
    if (diff < 0) {
        diff = -diff;
    }
    if (diff > ARB_THROTTLE_WINDOW) {
        g_arb.neutral_latched = false;
        g_arb.neutral_since_ms = 0;
        return ERR_THROTTLE_MISMATCH;
    }

    if (!g_arb.neutral_latched) {
        g_arb.neutral_latched = true;
        g_arb.neutral_since_ms = now_ms;
        return ERR_STICK_HOLD;
    }
    if ((uint32_t)(now_ms - g_arb.neutral_since_ms) < ARB_NEUTRAL_HOLD_MS) {
        return ERR_STICK_HOLD; /* одного вдалого кадру мало — тримай стіки */
    }

    uint32_t nonce = commit_owner(candidate_id, now_ms, STATE_PILOT_ACTIVE);
    if (out_nonce != NULL) {
        *out_nonce = nonce;
    }
    return ARB_OK;
}

arb_err_t arbiter_cancel_handover(uint8_t requester_id, uint32_t now_ms)
{
    (void)now_ms;
    if (g_arb.state != STATE_HANDOVER_WAIT_STICK) {
        return ERR_WRONG_STATE;
    }
    /* Скасувати може або чинний пілот, або сам кандидат. */
    if (requester_id != g_arb.pilot_gcs_id && requester_id != g_arb.pending_pilot_gcs_id) {
        return ERR_NOT_OWNER;
    }
    g_arb.state = STATE_PILOT_ACTIVE;
    g_arb.resume_state = STATE_PILOT_ACTIVE;
    drop_handover();
    return ARB_OK;
}

/* --- аварійне перехоплення -------------------------------------------- */

arb_err_t arbiter_commander_override(uint8_t commander_id, uint32_t now_ms, uint32_t *out_nonce)
{
    /* Єдина умова — роль командира за живою станцією. Ні стан машини, ні згода
     * чинного пілота тут не питаються: у цьому й сенс перехоплення. */
    if (!station_has_role(&g_arb.stations, commander_id, ROLE_COMMANDER, now_ms,
                          ARB_HEARTBEAT_TIMEOUT_MS)) {
        return station_find(&g_arb.stations, commander_id) ? ERR_ROLE_DENIED : ERR_UNKNOWN_STATION;
    }

    g_arb.commander_gcs_id = commander_id;
    uint32_t nonce = commit_owner(commander_id, now_ms, STATE_COMMANDER_LOCKED);
    if (out_nonce != NULL) {
        *out_nonce = nonce;
    }
    return ARB_OK;
}

arb_err_t arbiter_release_override(uint8_t commander_id, uint32_t now_ms)
{
    (void)now_ms;
    if (g_arb.state != STATE_COMMANDER_LOCKED) {
        return ERR_WRONG_STATE;
    }
    if (commander_id != g_arb.commander_gcs_id) {
        return ERR_NOT_OWNER;
    }
    ARB_CRITICAL_ENTER();
    g_arb.pilot_gcs_id = 0;
    g_arb.commander_gcs_id = 0;
    g_arb.token_nonce = next_nonce(); /* усі старі nonce протухають одразу */
    g_arb.state = STATE_IDLE;
    ARB_CRITICAL_EXIT();
    g_arb.resume_state = STATE_IDLE;
    drop_handover();
    return ARB_OK;
}

/* --- гарячий шлях ------------------------------------------------------ */

bool arbiter_is_flight_command_allowed(uint8_t src_gcs_id, uint32_t nonce)
{
    if (g_arb.state != STATE_PILOT_ACTIVE &&
        g_arb.state != STATE_HANDOVER_WAIT_STICK &&
        g_arb.state != STATE_COMMANDER_LOCKED) {
        return false; /* IDLE і LINK_LOST керування не пропускають */
    }
    /* Два цілочислові порівняння — рівно те, що можна дозволити собі на 50 Гц
     * у високопріоритетній задачі. Свіжість оренди стежить таймер. */
    return (src_gcs_id == g_arb.pilot_gcs_id) && (nonce == g_arb.token_nonce);
}

bool arbiter_is_payload_command_allowed(uint8_t src_gcs_id, uint32_t now_ms)
{
    /* Навмисно не дивимося ні на state, ні на токен пілота: оператор камери
     * працює навіть тоді, коли політ заблоковано. Розділення площин. */
    return station_has_role(&g_arb.stations, src_gcs_id, ROLE_PAYLOAD, now_ms,
                            ARB_HEARTBEAT_TIMEOUT_MS);
}

void arbiter_set_current_thrust(int16_t thrust)
{
    g_arb.current_thrust = thrust;
}

void arbiter_periodic_tick(uint32_t now_ms)
{
    station_expire(&g_arb.stations, now_ms);

    if (g_arb.state == STATE_PILOT_ACTIVE ||
        g_arb.state == STATE_HANDOVER_WAIT_STICK ||
        g_arb.state == STATE_COMMANDER_LOCKED) {
        if (time_reached(now_ms, g_arb.pilot_lease_deadline)) {
            /* Куди повертатися, коли пульт озветься: під замком командира
             * оренда протухла так само, як у звичайного пілота. */
            g_arb.resume_state = (g_arb.state == STATE_COMMANDER_LOCKED)
                                     ? STATE_COMMANDER_LOCKED
                                     : STATE_PILOT_ACTIVE;
            g_arb.state = STATE_LINK_LOST;
            drop_handover();
            return;
        }
    }

    if (g_arb.state == STATE_HANDOVER_WAIT_STICK && time_reached(now_ms, g_arb.handover_deadline)) {
        /* Кандидат не показав нейтралі — керування лишається в старого пілота. */
        g_arb.state = STATE_PILOT_ACTIVE;
        g_arb.resume_state = STATE_PILOT_ACTIVE;
        drop_handover();
    }
}

/* --- діагностика ------------------------------------------------------- */

arbiter_state_t arbiter_state(void)     { return g_arb.state; }
uint8_t         arbiter_active_pilot(void) { return g_arb.pilot_gcs_id; }
uint32_t        arbiter_current_nonce(void) { return g_arb.token_nonce; }

const char *arb_err_str(arb_err_t err)
{
    switch (err) {
    case ARB_OK:                return "OK";
    case ERR_UNKNOWN_STATION:   return "ERR_UNKNOWN_STATION";
    case ERR_ROLE_DENIED:       return "ERR_ROLE_DENIED";
    case ERR_BUSY:              return "ERR_BUSY";
    case ERR_WRONG_STATE:       return "ERR_WRONG_STATE";
    case ERR_NOT_OWNER:         return "ERR_NOT_OWNER";
    case ERR_STICK_NOT_NEUTRAL: return "ERR_STICK_NOT_NEUTRAL";
    case ERR_STICK_HOLD:        return "ERR_STICK_HOLD";
    case ERR_THROTTLE_MISMATCH: return "ERR_THROTTLE_MISMATCH";
    case ERR_HANDOVER_TIMEOUT:  return "ERR_HANDOVER_TIMEOUT";
    case ERR_LOCKED:            return "ERR_LOCKED";
    case ERR_TABLE_FULL:        return "ERR_TABLE_FULL";
    }
    return "ERR_?";
}

const char *arb_state_str(arbiter_state_t st)
{
    switch (st) {
    case STATE_IDLE:                return "IDLE";
    case STATE_PILOT_ACTIVE:        return "PILOT_ACTIVE";
    case STATE_HANDOVER_WAIT_STICK: return "HANDOVER_WAIT_STICK";
    case STATE_LINK_LOST:           return "LINK_LOST";
    case STATE_COMMANDER_LOCKED:    return "COMMANDER_LOCKED";
    }
    return "?";
}
