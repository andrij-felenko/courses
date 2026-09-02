#include "arbiter.h"
#include "trace.h"

#include <math.h>

#define TILT_LIMIT        1.0f     /* повний хід кутових каналів */
#define SAFE_DESCENT_THR  0.25f    /* тяга керованого зниження, коли джерел не лишилось */
#define NOMINAL_DT_S      0.0025f  /* 400 Гц — крок за замовчуванням на першому такті */
#define MAX_DT_S          0.1f     /* довша пауза = цикл прострочив; лімітер не розганяємо */

static float clampf(float v, float lo, float hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

static void slot_defaults(source_slot_t *slot, uint32_t timeout_us)
{
    int i;

    slot->cfg.timeout_us          = timeout_us;
    slot->cfg.stick_deadband      = 0.08f;
    slot->cfg.stick_deadband_exit = 0.05f;
    slot->cfg.max_slew_rate[AX_ROLL]   = 6.0f;
    slot->cfg.max_slew_rate[AX_PITCH]  = 6.0f;
    slot->cfg.max_slew_rate[AX_YAW]    = 10.0f;
    slot->cfg.max_slew_rate[AX_THRUST] = 3.0f;  /* 0 → 100% за 330 мс */

    slot->sp.stamp_us  = 0;
    for (i = 0; i < AX_COUNT; ++i)
        slot->sp.ch[i] = 0.0f;
    slot->heartbeat_us = 0;
    slot->has_data     = false;
    slot->timed_out    = true;
}

void arbiter_init(arbiter_t *arb)
{
    int i;

    /* Таймаути різні, бо різні темпи джерел: пульт шле 150 Гц, комп'ютер зору
       40 Гц, місія з наземної станції — раз на секунду. Поріг беремо з запасом
       щонайменше на три періоди джерела: інакше джитер планувальника Linux на
       компаньйоні (сплеск завантаження, збирання сміття в Python/ROS 2) сипатиме
       хибними таймаутами й вимикатиме справне джерело. */
    slot_defaults(&arb->slots[SRC_FAILSAFE],    1000000u);
    slot_defaults(&arb->slots[SRC_RC_PILOT],     200000u);
    slot_defaults(&arb->slots[SRC_OFFBOARD],     100000u);
    slot_defaults(&arb->slots[SRC_GCS_MISSION], 2000000u);

    arb->active           = SRC_NONE;
    arb->previous         = SRC_NONE;
    arb->out.stamp_us     = 0;
    for (i = 0; i < AX_COUNT; ++i)
        arb->out.ch[i] = 0.0f;
    arb->out_valid        = false;
    arb->last_eval_us     = 0;
    arb->failsafe_latched = false;
    arb->override_latched = false;
    arb->deflection       = 0.0f;
    arb->switches         = 0;
    arb->rejects          = 0;
}

/* Кадр із NaN у каналі — не «дивне число», а вбитий процес джерела: у лімітері
   NaN за один такт отруїть вихід назавжди, бо порівняння з NaN хибні всі. */
static arb_status_t validate(const setpoint_t *sp)
{
    int i;

    for (i = 0; i < AX_COUNT; ++i) {
        if (!isfinite(sp->ch[i]))
            return ARB_ERR_NOT_FINITE;
    }
    for (i = AX_ROLL; i <= AX_YAW; ++i) {
        if (fabsf(sp->ch[i]) > TILT_LIMIT)
            return ARB_ERR_RANGE;
    }
    if (sp->ch[AX_THRUST] < 0.0f || sp->ch[AX_THRUST] > 1.0f)
        return ARB_ERR_RANGE;
    return ARB_OK;
}

arb_status_t arbiter_submit(arbiter_t *arb, source_id_t src,
                            const setpoint_t *sp, uint64_t now_us)
{
    source_slot_t *slot;
    arb_status_t   st;

    if (!arb || !sp || src >= SRC_COUNT)
        return ARB_ERR_SOURCE;

    st = validate(sp);
    if (st != ARB_OK) {
        arb->rejects++;
        return st;
    }

    slot = &arb->slots[src];

    /* Кадри йдуть різними каналами (UART, 4G) і легко переставляються місцями.
       Старіший за вже прийнятий повернув би стару уставку — відкидаємо. */
    if (slot->has_data && sp->stamp_us < slot->sp.stamp_us) {
        arb->rejects++;
        return ARB_ERR_STALE;
    }

    slot->sp = *sp;
    /* Серце б'ємо моментом ПРИЙОМУ, а не міткою відправника: годинники борту
       й наземної станції не синхронні, і чужий стрибок часу вимкнув би джерело. */
    slot->heartbeat_us = now_us;
    slot->has_data     = true;
    slot->timed_out    = false;
    return ARB_OK;
}

void arbiter_raise_failsafe(arbiter_t *arb, float descent_thrust, uint64_t now_us)
{
    source_slot_t *slot = &arb->slots[SRC_FAILSAFE];

    slot->sp.stamp_us       = now_us;
    slot->sp.ch[AX_ROLL]    = 0.0f;   /* горизонт */
    slot->sp.ch[AX_PITCH]   = 0.0f;
    slot->sp.ch[AX_YAW]     = 0.0f;
    slot->sp.ch[AX_THRUST]  = clampf(descent_thrust, 0.0f, 1.0f);
    slot->heartbeat_us      = now_us;
    slot->has_data          = true;
    slot->timed_out         = false;

    /* Засувка: аварія не має «розсмоктатися» від того, що монітор батареї
       замовк. Знімає її тільки явний виклик — після посадки й розброєння. */
    arb->failsafe_latched = true;
}

void arbiter_clear_failsafe(arbiter_t *arb)
{
    arb->failsafe_latched            = false;
    arb->slots[SRC_FAILSAFE].has_data = false;
    arb->slots[SRC_FAILSAFE].timed_out = true;
}

static void update_watchdog(arbiter_t *arb, uint64_t now_us)
{
    int i;

    for (i = 0; i < SRC_COUNT; ++i) {
        source_slot_t *slot = &arb->slots[i];
        uint64_t elapsed;

        if (!slot->has_data)
            continue;
        /* Годинник борту монотонний; якщо він усе-таки стрибнув назад,
           вважаємо кадр свіжим — краще зайвий такт довіри, ніж хибний таймаут. */
        elapsed = (now_us > slot->heartbeat_us) ? (now_us - slot->heartbeat_us) : 0u;
        /* Прапорець рахуємо щотакту наново: джерело, що ожило, повертається
           в гру наступним же кадром, без окремої процедури «розблокування». */
        slot->timed_out = (elapsed > slot->cfg.timeout_us);
    }
}

static bool slot_live(const source_slot_t *slot)
{
    return slot->has_data && !slot->timed_out;
}

/* Норма Чебишова: max(|roll|, |pitch|, |yaw|). Без sqrt — кілька тактів FPU
   (VABS.F32 + VMAXNM.F32), і чутливість кожної осі не залежить від сусідніх:
   8% ходу тангажа спрацьовують однаково при будь-якому крені. */
static float stick_deflection(const setpoint_t *sp)
{
    float d = fabsf(sp->ch[AX_ROLL]);
    float p = fabsf(sp->ch[AX_PITCH]);
    float y = fabsf(sp->ch[AX_YAW]);

    if (p > d) d = p;
    if (y > d) d = y;
    return d;
}

static source_id_t select_source(arbiter_t *arb)
{
    const source_slot_t *rc = &arb->slots[SRC_RC_PILOT];

    /* 1. Аварія — безумовно й поза чергою, стіки не питаємо. */
    if (arb->failsafe_latched && arb->slots[SRC_FAILSAFE].has_data)
        return SRC_FAILSAFE;

    /* 2. Пульт витісняє автономію лише тоді, коли пілот СПРАВДІ ворухнув ручку. */
    if (slot_live(rc)) {
        float threshold;
        bool  moved;

        arb->deflection = stick_deflection(&rc->sp);
        /* Гістерезис: увійшли на 0.08, тримаємося до 0.05. Без нього арбітр
           тремтів би на межі, перекидаючи авторитет туди-сюди щотакту. */
        threshold = arb->override_latched ? rc->cfg.stick_deadband_exit
                                          : rc->cfg.stick_deadband;
        moved = (arb->deflection > threshold);

        if (moved && !arb->override_latched)
            diag_pin_high();   /* фронт для аналізатора: намір пілота помічено */

        arb->override_latched = moved;
        if (moved)
            return SRC_RC_PILOT;
    } else {
        /* Пульт зник — засувку знімаємо, інакше після повернення зв'язку
           апарат лишився б у ручному режимі з невідомим положенням ручок. */
        arb->deflection       = 0.0f;
        arb->override_latched = false;
    }

    /* 3. Автономія за спаданням авторитету. */
    if (slot_live(&arb->slots[SRC_OFFBOARD]))
        return SRC_OFFBOARD;
    if (slot_live(&arb->slots[SRC_GCS_MISSION]))
        return SRC_GCS_MISSION;

    /* 4. Автономні джерела мовчать — пульт бере керування навіть із центрованими
          ручками: живий оператор кращий за порожній вихід. */
    if (slot_live(rc))
        return SRC_RC_PILOT;

    return SRC_NONE;
}

source_id_t arbiter_evaluate(arbiter_t *arb, uint64_t now_us, setpoint_t *out)
{
    source_id_t  selected;
    float        dt = NOMINAL_DT_S;
    float        target[AX_COUNT];
    const float *rate;
    int          i;

    update_watchdog(arb, now_us);
    selected = select_source(arb);

    if (selected != arb->active) {
        arb->previous = arb->active;
        arb->active   = selected;
        arb->switches++;
    }

    if (arb->last_eval_us != 0u && now_us > arb->last_eval_us) {
        dt = (float)(now_us - arb->last_eval_us) * 1e-6f;
        if (dt > MAX_DT_S)
            dt = MAX_DT_S;
    }
    arb->last_eval_us = now_us;

    if (selected != SRC_NONE) {
        for (i = 0; i < AX_COUNT; ++i)
            target[i] = arb->slots[selected].sp.ch[i];
        rate = arb->slots[selected].cfg.max_slew_rate;
        arb->out_valid = true;
    } else {
        /* Живих джерел не лишилося. Горизонтуємо апарат, а тягу ТІЛЬКИ
           зменшуємо до керованого зниження: обнулити її — вільне падіння,
           збільшити — розкрутити мотори на землі під час наладки. */
        target[AX_ROLL] = target[AX_PITCH] = target[AX_YAW] = 0.0f;
        target[AX_THRUST] = (arb->out.ch[AX_THRUST] < SAFE_DESCENT_THR)
                          ? arb->out.ch[AX_THRUST] : SAFE_DESCENT_THR;
        rate = arb->slots[SRC_FAILSAFE].cfg.max_slew_rate;
        arb->out_valid = false;
    }

    /* Лімітер похідної: |du| <= max_slew_rate * dt на кожному каналі. Саме він
       перетворює стрибок уставки при зміні джерела на плавний перехід і знімає
       ударний струм із мостів моторів та ривок із інтегральних ланок ПІД. */
    for (i = 0; i < AX_COUNT; ++i) {
        float max_delta = rate[i] * dt;
        float delta     = clampf(target[i] - arb->out.ch[i], -max_delta, max_delta);
        arb->out.ch[i] += delta;
    }
    arb->out.ch[AX_THRUST] = clampf(arb->out.ch[AX_THRUST], 0.0f, 1.0f);
    arb->out.stamp_us = now_us;

    if (out)
        *out = arb->out;
    return selected;
}

bool arbiter_output_valid(const arbiter_t *arb)
{
    return arb->out_valid;
}

bool arbiter_is_live(const arbiter_t *arb, source_id_t src)
{
    if (src >= SRC_COUNT)
        return false;
    return slot_live(&arb->slots[src]);
}

float arbiter_deflection(const arbiter_t *arb)
{
    return arb->deflection;
}

uint32_t arbiter_switch_count(const arbiter_t *arb)
{
    return arb->switches;
}

uint32_t arbiter_reject_count(const arbiter_t *arb)
{
    return arb->rejects;
}

const char *source_name(source_id_t src)
{
    switch (src) {
    case SRC_FAILSAFE:    return "FAILSAFE";
    case SRC_RC_PILOT:    return "RC";
    case SRC_OFFBOARD:    return "OFFBOARD";
    case SRC_GCS_MISSION: return "GCS";
    default:              return "немає";
    }
}

const char *arb_status_name(arb_status_t st)
{
    switch (st) {
    case ARB_OK:             return "прийнято";
    case ARB_ERR_SOURCE:     return "невідоме джерело";
    case ARB_ERR_NOT_FINITE: return "NaN у каналі";
    case ARB_ERR_RANGE:      return "поза межами апарата";
    case ARB_ERR_STALE:      return "кадр із минулого";
    default:                 return "?";
    }
}
