/* Прогін бортової VM на настільній машині: замість польотного контуру
   підставлено найпростішу кінематику, замість давачів — її стан. Цього
   досить, щоб побачити роботу циклів, умов і сторожів у трасі. */

#include <math.h>
#include <stdio.h>

#include "geo.h"
#include "mission_vm.h"

#define TICK_MS 20u   /* 50 Гц — типовий такт диспетчера місії */

static const geo_point_t HOME = { 504501000, 305234000, 0.0f };

/* ---------- модель апарата ---------- */

typedef struct {
    geo_point_t home;
    float east_m, north_m, alt_m;
    float yaw_deg;
    float soc_pct;
    float pack_v;
    float t_s;
} sim_t;

static void sim_init(sim_t *s, geo_point_t home)
{
    s->home    = home;
    s->east_m  = 0.0f;
    s->north_m = 0.0f;
    s->alt_m   = 0.0f;
    s->yaw_deg = 0.0f;
    s->soc_pct = 100.0f;
    s->pack_v  = 17.0f;
    s->t_s     = 0.0f;
}

static geo_point_t sim_position(const sim_t *s)
{
    geo_point_t p = geo_shift(s->home, s->east_m, s->north_m);
    p.alt_m = s->alt_m;
    return p;
}

static void sim_step(sim_t *s, const vm_outputs_t *out, float dt, float drain_pct_s)
{
    const geo_point_t pos = sim_position(s);
    const geo_offset_t d  = geo_offset(pos, out->target);
    const float dist = sqrtf(d.east_m * d.east_m + d.north_m * d.north_m);

    const float step = out->speed_mps * dt;
    if (dist > 0.01f) {
        const float k = (step < dist) ? step / dist : 1.0f;
        s->east_m  += d.east_m * k;
        s->north_m += d.north_m * k;
    }

    const float dz = out->target.alt_m - s->alt_m;
    const float vz = 2.5f * dt;
    s->alt_m += (fabsf(dz) < vz) ? dz : copysignf(vz, dz);
    if (s->alt_m < 0.0f) {
        s->alt_m = 0.0f;
    }

    /* Курс: або нав'язаний CONDITION_YAW, або просто на ціль. */
    const float want = (out->yaw_setpoint_deg >= 0.0f)
                     ? out->yaw_setpoint_deg
                     : geo_bearing_deg(pos, out->target);
    const float err  = geo_wrap_deg(want - s->yaw_deg);
    const float slew = 90.0f * dt;
    s->yaw_deg = geo_norm_heading_deg(
        s->yaw_deg + ((fabsf(err) < slew) ? err : copysignf(slew, err)));

    s->t_s += dt;
    s->soc_pct -= drain_pct_s * dt;
    if (s->soc_pct < 0.0f) {
        s->soc_pct = 0.0f;
    }

    /* 4S: 17.0 В на повній, 14.0 В на порожній. Плюс періодичне
       просідання під ривками тяги — саме воно й ламає перевірку
       за сирою напругою. */
    const float sag = (dist > 1.0f) ? 0.9f * (0.5f + 0.5f * sinf(s->t_s * 3.0f)) : 0.0f;
    s->pack_v = 14.0f + 0.030f * s->soc_pct - sag;
}

/* ---------- складання байткоду ---------- */

static mission_instr_t nav_wp(float east_m, float north_m, float alt_m,
                              int16_t hold_s, int16_t radius_m, bool autocontinue)
{
    const geo_point_t p = geo_shift(HOME, east_m, north_m);
    mission_instr_t in = { 0 };
    in.opcode = OP_NAV_WAYPOINT;
    in.flags  = autocontinue ? ITEM_FLAG_AUTOCONTINUE : 0u;
    in.p1     = hold_s;
    in.p2     = radius_m;
    in.lat_e7 = p.lat_e7;
    in.lon_e7 = p.lon_e7;
    in.alt_m  = alt_m;
    return in;
}

static mission_instr_t nav_simple(uint8_t opcode, float alt_m, int16_t radius_m)
{
    mission_instr_t in = { 0 };
    in.opcode = opcode;
    in.flags  = ITEM_FLAG_AUTOCONTINUE;
    in.p2     = radius_m;
    in.alt_m  = alt_m;   /* координати нульові — «тут же, де апарат» */
    return in;
}

static mission_instr_t op2(uint8_t opcode, int16_t p1, int16_t p2)
{
    mission_instr_t in = { 0 };
    in.opcode = opcode;
    in.flags  = ITEM_FLAG_AUTOCONTINUE;
    in.p1     = p1;
    in.p2     = p2;
    return in;
}

/* ---------- прогін ---------- */

static void run_mission(const char *title, const mission_instr_t *prog, uint16_t len,
                        float drain_pct_s, uint32_t limit_ms)
{
    printf("\n=== %s ===\n", title);

    mission_vm_t vm;
    const mission_load_err_t err = mission_vm_load(&vm, prog, len);
    if (err != LOAD_OK) {
        printf("  верифікатор відхилив місію: %s\n", mission_load_err_str(err));
        return;
    }

    sim_t s;
    sim_init(&s, HOME);
    mission_vm_start(&vm, HOME, 0u);

    uint16_t    last_nav    = 0xFFFFu;
    uint16_t    last_servo  = 0u;
    vm_status_t last_status = VM_IDLE;
    uint32_t    paused_at   = 0u;

    for (uint32_t now = 0u; now <= limit_ms; now += TICK_MS) {
        vm_telemetry_t t;
        t.now_ms          = now;
        t.position        = sim_position(&s);
        t.yaw_deg         = s.yaw_deg;
        t.battery_v       = s.pack_v;
        t.battery_soc_pct = s.soc_pct;
        t.gnss_ok         = true;
        t.link_ok         = true;

        mission_vm_tick(&vm, &t);

        if (vm.status != last_status) {
            printf("[%6.1f с] %s\n", now / 1000.0f, mission_vm_status_str(vm.status));
            if (vm.status == VM_PAUSED) {
                paused_at = now;
            }
            last_status = vm.status;
        }
        if (vm.nav_active && vm.nav_pc != last_nav) {
            printf("[%6.1f с] seq %2u  %-20s  SoC %3.0f%%  висота %5.1f м\n",
                   now / 1000.0f, vm.nav_pc,
                   mission_opcode_str(vm.code[vm.nav_pc].opcode),
                   s.soc_pct, s.alt_m);
            last_nav = vm.nav_pc;
        }
        if (vm.out.servo_pwm[0] != last_servo) {
            printf("[%6.1f с]          DO_SET_SERVO ch1 = %u мкс\n",
                   now / 1000.0f, vm.out.servo_pwm[0]);
            last_servo = vm.out.servo_pwm[0];
        }

        /* Наземна станція знімає покрокову паузу через 3 секунди. */
        if (vm.status == VM_PAUSED && (uint32_t)(now - paused_at) >= 3000u) {
            printf("[%6.1f с]          НСУ → MAV_CMD_MISSION_START\n", now / 1000.0f);
            mission_vm_resume(&vm);
        }

        if (mission_vm_stopped(&vm)) {
            return;
        }
        sim_step(&s, &vm.out, TICK_MS / 1000.0f, drain_pct_s);
    }
    printf("  ліміт часу симуляції вичерпано, стан: %s\n",
           mission_vm_status_str(vm.status));
}

int main(void)
{
    /* Місія з розділу про DO_JUMP: три точки й дворазовий повтор.
       Разом контур мусить пройти A, B, C тричі й сісти. */
    const mission_instr_t loop_mission[] = {
        nav_simple(OP_NAV_TAKEOFF, 30.0f, 0),              /* 0 */
        nav_wp(  0.0f, 120.0f, 30.0f, 0, 5, true),         /* 1: A */
        nav_wp(150.0f, 120.0f, 30.0f, 0, 5, true),         /* 2: B */
        nav_wp(150.0f,   0.0f, 30.0f, 0, 5, true),         /* 3: C */
        op2(OP_DO_JUMP, 1, 2),                             /* 4 */
        nav_simple(OP_NAV_LAND, 0.0f, 5)                   /* 5 */
    };
    run_mission("Цикл DO_JUMP(1, 2): три проходи A-B-C",
                loop_mission, (uint16_t)(sizeof(loop_mission) / sizeof(loop_mission[0])),
                0.05f, 300000u);

    /* Патрулювання без обмеження повторів: вихід дає не лічильник,
       а умова за станом батареї. Дорогою — умовне скидання вантажу
       й покрокова зупинка на другій точці. */
    const mission_instr_t patrol_mission[] = {
        nav_simple(OP_NAV_TAKEOFF, 40.0f, 0),              /* 0 */
        nav_wp(-200.0f, 300.0f, 40.0f, 0, 8, true),        /* 1: P1 */
        op2(OP_CONDITION_DISTANCE, 50, 0),                 /* 2 */
        op2(OP_DO_SET_SERVO, 1, 1900),                     /* 3 */
        nav_wp( 200.0f, 300.0f, 40.0f, 0, 8, false),       /* 4: P2, autocontinue = 0 */
        op2(OP_JUMP_IF_BAT_LOW, 30, 7),                    /* 5 */
        op2(OP_DO_JUMP, 1, -1),                            /* 6: нескінченний цикл */
        nav_simple(OP_NAV_RTL, 0.0f, 8)                    /* 7 */
    };
    run_mission("Патруль із виходом за станом батареї",
                patrol_mission, (uint16_t)(sizeof(patrol_mission) / sizeof(patrol_mission[0])),
                0.30f, 400000u);

    /* Те саме, але з биткою ціллю переходу: рівень 1 мусить відхилити
       місію ще при завантаженні, до MISSION_ACK. */
    const mission_instr_t broken_mission[] = {
        nav_simple(OP_NAV_TAKEOFF, 30.0f, 0),
        nav_wp(0.0f, 100.0f, 30.0f, 0, 5, true),
        op2(OP_DO_JUMP, 9, 1)
    };
    run_mission("Статичний верифікатор: DO_JUMP за межі місії",
                broken_mission, (uint16_t)(sizeof(broken_mission) / sizeof(broken_mission[0])),
                0.05f, 10000u);

    return 0;
}
