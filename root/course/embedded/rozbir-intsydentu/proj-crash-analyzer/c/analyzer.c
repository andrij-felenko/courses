#include "crashlog.h"

#include <math.h>
#include <string.h>

/* --- Пороги. Це фізика апарата, а не смак: числа взяті з розділу «Механізм». --- */

#define WINDOW_FRAMES       32       /* ~320 мс при 100 Гц — верх діапазону вікна */
#define WINDOW_SPAN_US      300000u  /* 300 мс: довша пам'ять уже не про подію */
#define MIN_FRAMES          30       /* коротший запис не дає вікна взагалі */

#define MOTOR_SAT_HIGH      0.98f    /* вихід уперся в стелю */
#define MOTOR_SAT_LOW       0.05f    /* протилежний мотор скинуто в нуль */
#define ROLL_ERR_DEG        20.0f
#define MOTOR_STREAK        15       /* ~150 мс стійкого насичення */
#define SHOCK_ALPHA_RADS2   150.0f   /* кутове прискорення, яке дає лише удар */
#define IMPACT_LEAD_US      20000u   /* 20 мс: сплеск гіро випередив насичення */

#define MAG_INNOV_LIMIT     0.45f
#define MAG_CURRENT_A       30.0f
#define MAG_CURRENT_STEP_A  8.0f     /* цікавить КРОК споживання, а не рівень */
#define YAW_ERR_DEG         15.0f
#define MAG_STREAK          20

#define SAG_VOLTAGE_V       13.2f    /* поріг стабілізатора для збірки 4S */
#define SAG_SLOPE_VPS       (-4.0f)  /* В/с: динамічний провал, а не вичерпання */
#define SAG_CURRENT_A       25.0f
#define SAG_MIN_SPAN_S      0.05f    /* коротше вікно дає шумну похідну */

#define FREEZE_FRAMES       25
#define MOTOR_FLYING_OUT    0.15f    /* вище холостого — апарат уже в динаміці */
#define IMU_HEALTHY_BIT     0x01u

/* --- Рухоме вікно: кільце на WINDOW_FRAMES кадрів --- */

typedef struct {
    TelemetryFrame buf[WINDOW_FRAMES];
    size_t n;     /* скільки кадрів реально лежить */
    size_t head;  /* куди писати наступний */
} Window;

static void window_push(Window *w, const TelemetryFrame *f)
{
    w->buf[w->head] = *f;
    w->head = (w->head + 1) % WINDOW_FRAMES;
    if (w->n < WINDOW_FRAMES) {
        w->n++;
    }
}

/* Індекс 0 — найстаріший кадр вікна, n-1 — щойно доданий. */
static const TelemetryFrame *window_at(const Window *w, size_t i)
{
    size_t start = (w->head + WINDOW_FRAMES - w->n) % WINDOW_FRAMES;
    return &w->buf[(start + i) % WINDOW_FRAMES];
}

static const TelemetryFrame *window_oldest(const Window *w)
{
    return window_at(w, 0);
}

/* --- Стан детекторів між кадрами --- */

typedef struct {
    size_t sat_streak;        /* кадрів поспіль із насиченням і зростанням помилки */
    uint64_t sat_start_us;
    float sat_start_err;
    float sat_prev_err;

    uint64_t shock_us;        /* остання мітка різкого сплеску гіроскопа */

    size_t mag_streak;
    uint64_t mag_start_us;

    size_t freeze_streak;
    uint64_t freeze_start_us;
} DetectorState;

/* --- Дрібні помічники --- */

/* Кутова помилка з коректним переходом через ±180°: інакше курс 359° проти 1°
 * дасть «розходження 358°» і кожен політ на північ читатиметься як відмова. */
static float angle_err_deg(float des, float act)
{
    float e = fmodf(des - act, 360.0f);
    if (e > 180.0f) {
        e -= 360.0f;
    } else if (e < -180.0f) {
        e += 360.0f;
    }
    return fabsf(e);
}

/* Реальний журнал не стерильний: у полі трапляється NaN (запис почався до
 * ініціалізації EKF), кадри дублюються, а після перезапуску оцінювача час
 * стрибає назад. Такий кадр не судимо — інакше похідні вибухнуть. */
static bool frame_is_sane(const TelemetryFrame *f)
{
    if (!isfinite(f->roll_des_deg) || !isfinite(f->roll_act_deg) ||
        !isfinite(f->yaw_des_deg) || !isfinite(f->yaw_act_deg) ||
        !isfinite(f->bat_voltage_v) || !isfinite(f->bat_current_a) ||
        !isfinite(f->ekf_mag_innov) || !isfinite(f->gyro_x_rads)) {
        return false;
    }
    for (int m = 0; m < MAX_MOTORS; m++) {
        if (!isfinite(f->motor_out[m])) {
            return false;
        }
    }
    return true;
}

const char *fault_name(FaultType fault)
{
    switch (fault) {
    case FAULT_NONE:                 return "FAULT_NONE";
    case FAULT_MOTOR_ESC_LOSS:       return "FAULT_MOTOR_ESC_LOSS";
    case FAULT_MAGNETIC_INTERFERENCE:return "FAULT_MAGNETIC_INTERFERENCE";
    case FAULT_BROWNOUT_VOLTAGE_SAG: return "FAULT_BROWNOUT_VOLTAGE_SAG";
    case FAULT_SENSOR_BUS_LOCKUP:    return "FAULT_SENSOR_BUS_LOCKUP";
    }
    return "FAULT_UNKNOWN";
}

/* --- 1. Відмова мотора або регулятора --- */

static bool detect_motor_loss(DetectorState *st, const TelemetryFrame *f, IncidentReport *rep)
{
    bool saturated = false;
    /* Діагональні пари квадрокоптера: виходи 1-2 і 3-4 нумерації ArduPilot.
     * Один уперся в стелю, протилежний скинуто в нуль — регулятор віддав
     * максимальний керівний момент, більше йому дати нічого. */
    for (int a = 0; a + 1 < MAX_MOTORS; a += 2) {
        int b = a + 1;
        if ((f->motor_out[a] > MOTOR_SAT_HIGH && f->motor_out[b] < MOTOR_SAT_LOW) ||
            (f->motor_out[b] > MOTOR_SAT_HIGH && f->motor_out[a] < MOTOR_SAT_LOW)) {
            saturated = true;
        }
    }

    float err = angle_err_deg(f->roll_des_deg, f->roll_act_deg);

    if (!saturated || err < ROLL_ERR_DEG) {
        st->sat_streak = 0;
        return false;
    }

    if (st->sat_streak == 0) {
        st->sat_streak = 1;
        st->sat_start_us = f->timestamp_us;
        st->sat_start_err = err;
        st->sat_prev_err = err;
        return false;
    }

    /* Помилка мусить рости монотонно. Якщо вона просідає — керування ще тягне
     * апарат назад, і насичення було просто різким маневром: серія рветься. */
    if (err + 0.5f < st->sat_prev_err) {
        st->sat_streak = 0;
        return false;
    }
    st->sat_prev_err = err;
    st->sat_streak++;

    if (st->sat_streak <= MOTOR_STREAK) {
        return false;
    }
    if (err <= st->sat_start_err) {
        return false; /* тримається на місці — росту за всю серію так і не було */
    }

    /* Крайовий випадок: удар об перешкоду теж насичує мотори. Відрізняємо
     * за ПОРЯДКОМ подій. При ударі різкий сплеск гіроскопа передує розкручуванню
     * моторів — спершу апарат кинуло, потім регулятор погнався. При відмові тяги
     * розходження й насичення народжуються разом, окремого поштовху немає. */
    if (st->shock_us != 0 && st->shock_us + IMPACT_LEAD_US < st->sat_start_us) {
        if (rep->impact_us == 0) {
            rep->impact_us = st->shock_us;
        }
        st->sat_streak = 0;
        return false;
    }

    rep->fault = FAULT_MOTOR_ESC_LOSS;
    rep->timestamp_us = st->sat_start_us;
    rep->confidence = 0.98f;
    rep->description = "Відмова мотора або ESC: насичення 100%/0% на діагоналі "
                       "при кутовій помилці, що монотонно зростає";
    return true;
}

/* --- 2. Магнітна завада силового струму --- */

static bool detect_mag_interference(DetectorState *st, const Window *w,
                                    const TelemetryFrame *f, IncidentReport *rep)
{
    float yaw_err = angle_err_deg(f->yaw_des_deg, f->yaw_act_deg);

    if (f->ekf_mag_innov <= MAG_INNOV_LIMIT || yaw_err < YAW_ERR_DEG) {
        st->mag_streak = 0;
        return false;
    }

    /* Базовий струм — мінімум по вікну: сигнатура це саме СТРИБОК споживання
     * (крок газу), а не високий рівень сам по собі. */
    float base = f->bat_current_a;
    for (size_t k = 0; k < w->n; k++) {
        float c = window_at(w, k)->bat_current_a;
        if (c < base) {
            base = c;
        }
    }

    bool current_step = f->bat_current_a > MAG_CURRENT_A &&
                        f->bat_current_a - base > MAG_CURRENT_STEP_A;

    if (!current_step) {
        /* Крайовий випадок: нев'язка компаса росте, а власний струм — ні.
         * Значить, поле спотворює залізо ПІД апаратом (міст, дах, арматура),
         * а не силовий джгут на борту. Це аномалія середовища, не дефект. */
        if (rep->env_anomaly_us == 0) {
            rep->env_anomaly_us = f->timestamp_us;
        }
        st->mag_streak = 0;
        return false;
    }

    if (st->mag_streak == 0) {
        st->mag_start_us = f->timestamp_us;
    }
    st->mag_streak++;
    if (st->mag_streak <= MAG_STREAK) {
        return false;
    }

    rep->fault = FAULT_MAGNETIC_INTERFERENCE;
    rep->timestamp_us = st->mag_start_us;
    rep->confidence = 0.92f;
    rep->description = "Розходження курсу від магнітного наведення силового "
                       "струму на компас: сплеск нев'язки збігся зі стрибком струму";
    return true;
}

/* --- 3. Динамічна просадка живлення --- */

static bool detect_brownout(const Window *w, const TelemetryFrame *f, IncidentReport *rep)
{
    if (w->n < 2) {
        return false;
    }
    const TelemetryFrame *old = window_oldest(w);
    float span_s = (float)(f->timestamp_us - old->timestamp_us) * 1e-6f;
    if (span_s < SAG_MIN_SPAN_S) {
        return false;
    }
    float slope = (f->bat_voltage_v - old->bat_voltage_v) / span_s;

    /* Крайовий випадок: наприкінці польоту напруга теж опускається під поріг,
     * але зі швидкістю в десяті вольта на секунду й із попередженням про заряд.
     * Це нормальне вичерпання — позначаємо як контекст і йдемо далі. */
    if (f->bat_voltage_v < SAG_VOLTAGE_V && slope > SAG_SLOPE_VPS) {
        if (rep->depletion_us == 0) {
            rep->depletion_us = f->timestamp_us;
        }
        return false;
    }

    if (slope >= SAG_SLOPE_VPS || f->bat_voltage_v >= SAG_VOLTAGE_V ||
        f->bat_current_a < SAG_CURRENT_A) {
        return false;
    }

    /* Мітка події — не мить перетину порогу, а останній кадр, на якому напруга
     * ще трималася: саме там почалося падіння. */
    uint64_t start = f->timestamp_us;
    for (size_t k = w->n; k-- > 0;) {
        const TelemetryFrame *p = window_at(w, k);
        if (p->bat_voltage_v >= SAG_VOLTAGE_V) {
            break;
        }
        start = p->timestamp_us;
    }

    rep->fault = FAULT_BROWNOUT_VOLTAGE_SAG;
    rep->timestamp_us = start;
    rep->confidence = 0.95f;
    rep->description = "Динамічна просадка живлення (brownout): dU/dt нижче "
                       "-4 В/с під струмовим кроком";
    return true;
}

/* --- 4. Зависання шини або мікросхеми давача --- */

static bool detect_sensor_freeze(DetectorState *st, const TelemetryFrame *f,
                                 const TelemetryFrame *prev, IncidentReport *rep)
{
    bool flying = false;
    for (int m = 0; m < MAX_MOTORS; m++) {
        if (f->motor_out[m] > MOTOR_FLYING_OUT) {
            flying = true;
        }
    }
    /* На землі до армінгу апарат нерухомий, і збіг показів нічого не доводить. */
    if (!flying) {
        st->freeze_streak = 0;
        return false;
    }

    /* Порівняння float на точну рівність тут НАВМИСНЕ. У динаміці тепловий шум
     * MEMS-структури ворушить молодші розряди АЦП на кожному опитуванні, тож
     * побітово однакові відліки поспіль означають застиглий вихідний регістр
     * або втрату тактування шини, а не «тишу». */
    if (f->gyro_x_rads != prev->gyro_x_rads) {
        st->freeze_streak = 0;
        return false;
    }

    if (st->freeze_streak == 0) {
        st->freeze_start_us = prev->timestamp_us;
    }
    st->freeze_streak++;
    if (st->freeze_streak < FREEZE_FRAMES) {
        return false;
    }

    rep->fault = FAULT_SENSOR_BUS_LOCKUP;
    rep->timestamp_us = st->freeze_start_us;
    rep->confidence = 0.90f;
    rep->description = "Застигання показів гіроскопа: 25 однакових відліків "
                       "поспіль у динамічному польоті";
    return true;
}

/* --- Скан запису --- */

IncidentReport analyze_incident(const TelemetryFrame *frames, size_t count)
{
    IncidentReport rep;
    memset(&rep, 0, sizeof rep);
    rep.description = "Інцидентів не виявлено: параметри в межах норми";

    if (frames == NULL || count < MIN_FRAMES) {
        rep.description = "Замало даних для формування вікна аналізу";
        return rep;
    }

    Window win;
    DetectorState st;
    memset(&win, 0, sizeof win);
    memset(&st, 0, sizeof st);

    TelemetryFrame prev;
    bool have_prev = false;

    for (size_t i = 0; i < count; i++) {
        const TelemetryFrame *f = &frames[i];

        if (!frame_is_sane(f) || (have_prev && f->timestamp_us <= prev.timestamp_us)) {
            rep.frames_skipped++;
            continue;
        }
        rep.frames_used++;
        window_push(&win, f);

        /* Прапорець здоров'я — це вже вирок самого драйвера: шина не відповіла.
         * Далі шукати нічого, решта каналів після цього недостовірна. */
        if ((f->sensor_status_mask & IMU_HEALTHY_BIT) == 0) {
            rep.fault = FAULT_SENSOR_BUS_LOCKUP;
            rep.timestamp_us = f->timestamp_us;
            rep.confidence = 1.0f;
            rep.description = "Апаратна відмова шини IMU: драйвер зняв прапорець "
                              "здоров'я (таймаут I2C/SPI)";
            return rep;
        }

        if (have_prev) {
            float dt = (float)(f->timestamp_us - prev.timestamp_us) * 1e-6f;
            float alpha = (f->gyro_x_rads - prev.gyro_x_rads) / dt;
            if (fabsf(alpha) > SHOCK_ALPHA_RADS2) {
                st.shock_us = f->timestamp_us;
            } else if (st.shock_us != 0 &&
                       f->timestamp_us - st.shock_us > WINDOW_SPAN_US) {
                st.shock_us = 0; /* пам'ять про удар живе рівно одне вікно */
            }
        }

        if (detect_brownout(&win, f, &rep) ||
            detect_motor_loss(&st, f, &rep) ||
            detect_mag_interference(&st, &win, f, &rep)) {
            return rep;
        }
        if (have_prev && detect_sensor_freeze(&st, f, &prev, &rep)) {
            return rep;
        }

        prev = *f;
        have_prev = true;
    }

    return rep;
}
