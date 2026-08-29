/* mission_test.c — прогін місій на настільній машині.
 *
 * Тут два різні предмети, і плутати їх не можна:
 *   · sim_* — груба модель апарата. Вона потрібна лише щоб було звідки взяти
 *     телеметрію: рівномірний рух до уставки, стала швидкість підйому, лінійне
 *     просідання батареї. Ніякої аеродинаміки, і не треба;
 *   · scenario_* — власне перевірки. Кожна ставить машині своє питання й
 *     стверджує відповідь.
 *
 * Складання: cc -std=c11 -O1 mission_vm.c mission_test.c -lm -o mission_test
 */
#include "mission_vm.h"

#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

#define SIM_DT_S          0.05f /* 20 Гц — типова частота задачі місії        */
#define SIM_DT_MS         50u
#define SIM_CLIMB_MPS     2.5f
#define SIM_DEFAULT_MPS   6.0f
#define SIM_METERS_PER_DEG 111320.0
#define SIM_DEG_TO_RAD    (3.14159265358979323846 / 180.0)

/* ------------------------------------------------------------- модель */

typedef struct {
    double lat_deg;
    double lon_deg;
    float  alt_m;         /* над домашньою точкою                            */
    float  yaw_deg;
    float  yaw_rate_dps;  /* апарат крутиться сам — треба для COND_YAW        */
    float  battery_pct;
    float  drain_pct_s;
    bool   gnss_ok;       /* вимикаємо, щоб побачити поведінку без позиції    */
    bool   gcs_link_ok;
} sim_t;

static void sim_init(sim_t *s, double home_lat, double home_lon)
{
    memset(s, 0, sizeof(*s));
    s->lat_deg     = home_lat;
    s->lon_deg     = home_lon;
    s->battery_pct = 100.0f;
    s->drain_pct_s = 0.02f;
    s->gnss_ok     = true;
    s->gcs_link_ok = true;
}

/* Плоска апроксимація: на масштабах кількох сотень метрів вона точніша, ніж
 * потрібно польотному завданню, і коштує два множення. */
static double sim_distance_m(const sim_t *s, double lat_deg, double lon_deg)
{
    double dy = (lat_deg - s->lat_deg) * SIM_METERS_PER_DEG;
    double dx = (lon_deg - s->lon_deg) * SIM_METERS_PER_DEG *
                cos(s->lat_deg * SIM_DEG_TO_RAD);
    return sqrt(dx * dx + dy * dy);
}

static void sim_update(sim_t *s, const vm_actuators_t *act, vm_telemetry_t *telem)
{
    double target_lat = (double)act->target_lat_1e7 * 1e-7;
    double target_lon = (double)act->target_lon_1e7 * 1e-7;
    double dist       = 0.0;

    if (act->nav_valid) {
        float speed = act->target_speed_mps > 0.0f ? act->target_speed_mps
                                                   : SIM_DEFAULT_MPS;
        dist = sim_distance_m(s, target_lat, target_lon);
        double stride = (double)speed * SIM_DT_S;
        if (dist > 1e-9) {
            double f = stride >= dist ? 1.0 : stride / dist;
            s->lat_deg += (target_lat - s->lat_deg) * f;
            s->lon_deg += (target_lon - s->lon_deg) * f;
        }

        float dalt = act->target_alt_m - s->alt_m;
        float climb = SIM_CLIMB_MPS * SIM_DT_S;
        s->alt_m += fabsf(dalt) <= climb ? dalt : (dalt > 0.0f ? climb : -climb);

        dist = sim_distance_m(s, target_lat, target_lon);
    }

    s->yaw_deg += s->yaw_rate_dps * SIM_DT_S;
    if (s->yaw_deg >= 360.0f) {
        s->yaw_deg -= 360.0f;
    }

    s->battery_pct -= s->drain_pct_s * SIM_DT_S;
    if (s->battery_pct < 0.0f) {
        s->battery_pct = 0.0f;
    }

    telem->lat_1e7         = (int32_t)lround(s->lat_deg * 1e7);
    telem->lon_1e7         = (int32_t)lround(s->lon_deg * 1e7);
    telem->alt_m           = s->alt_m;
    telem->yaw_deg         = s->yaw_deg;
    telem->battery_soc_pct = s->battery_pct;
    telem->gcs_link_ok     = s->gcs_link_ok;
    /* Без позиції навігатор не має ні відстані, ні права сказати «на місці».
     * Саме так це виглядає при відмові GNSS. */
    telem->dist_to_wp_m = s->gnss_ok ? (float)dist : NAN;
    telem->wp_reached   = s->gnss_ok && act->nav_valid && dist <= 2.0 &&
                        fabsf(act->target_alt_m - s->alt_m) <= 1.5f;
}

/* Прогін до зупинки машини або до вичерпання ліміту кроків. Повертає, скільки
 * разів виконано інструкцію під індексом watch_pc (нею рахуємо кола). */
static unsigned run_mission(mission_vm_t   *vm,
                            sim_t          *sim,
                            vm_actuators_t *act,
                            uint16_t        watch_pc,
                            unsigned        max_steps,
                            uint32_t       *out_ms)
{
    vm_telemetry_t telem;
    uint32_t       now_ms = 0;
    unsigned       hits   = 0;

    memset(&telem, 0, sizeof(telem));
    telem.dist_to_wp_m = NAN;

    for (unsigned i = 0; i < max_steps && mission_vm_is_active(vm->status); i++) {
        uint16_t pc_before = vm->pc;
        mission_vm_step(vm, &telem, act, now_ms);
        if (pc_before == watch_pc && vm->pc != pc_before) {
            hits++;
        }
        sim_update(sim, act, &telem);
        now_ms += SIM_DT_MS;
    }
    if (out_ms != NULL) {
        *out_ms = now_ms;
    }
    return hits;
}

/* -------------------------------------------------------- сценарій обльоту */

#define HOME_LAT_1E7 504500000
#define HOME_LON_1E7 305200000
#define PC_SERVO     4 /* індекс DO_SET_SERVO у програмі нижче               */

/* Обліт периметра ділянки: зліт, перевірка батареї, точка A, скидання маркера
 * за 30 метрів до неї, точка B, повторити тричі, повернення. Нумерація
 * інструкцій — це і є мітки стрибків, тому вона в коментарях. */
static const vm_instruction_t patrol_program[] = {
    /* 0 */ { .opcode = OP_NAV_TAKEOFF, .alt_m = 30.0f },
    /* 1 */ { .opcode = OP_JUMP_IF_BAT_LOW, .param1 = 25, .param2 = 7 },
    /* 2 */ { .opcode = OP_NAV_WAYPOINT, .flags = VM_FLAG_AUTO_CONTINUE,
              .lat_1e7 = 504507000, .lon_1e7 = 305212000, .alt_m = 30.0f },
    /* 3 */ { .opcode = OP_COND_DISTANCE, .param1 = 30 },
    /* 4 */ { .opcode = OP_DO_SET_SERVO, .param1 = 5, .param2 = 1900 },
    /* 5 */ { .opcode = OP_NAV_WAYPOINT, .lat_1e7 = 504512000,
              .lon_1e7 = 305224000, .alt_m = 30.0f },
    /* 6 */ { .opcode = OP_DO_JUMP, .param1 = 1, .param2 = 3 },
    /* 7 */ { .opcode = OP_NAV_RTL },
};

static void scenario_patrol(void)
{
    mission_vm_t   vm;
    sim_t          sim;
    vm_actuators_t act;
    uint32_t       elapsed_ms = 0;

    mission_vm_init(&vm);
    mission_vm_set_home(&vm, HOME_LAT_1E7, HOME_LON_1E7, 180.0f);
    memset(&act, 0, sizeof(act));
    sim_init(&sim, 50.45, 30.52);

    vm_load_result_t rc = mission_vm_load(&vm, patrol_program,
                                          (uint16_t)(sizeof patrol_program /
                                                     sizeof patrol_program[0]));
    assert(rc == VM_LOAD_OK);

    unsigned laps = run_mission(&vm, &sim, &act, PC_SERVO, 40000, &elapsed_ms);

    printf("обліт: %s, кіл %u, стрибків %u, кроків %u, час %.1f с\n",
           vm_status_name(vm.status), laps, vm.total_jumps, vm.steps_executed,
           elapsed_ms / 1000.0);

    assert(vm.status == VM_STATUS_COMPLETED);
    assert(act.rtl_triggered);
    assert(act.servo_pwm_us == 1900 && act.servo_channel == 5);
    /* Три стрибки DO_JUMP означають чотири проходи ділянки. Батарея жодного
     * разу не просіла, тож JUMP_IF_BAT_LOW не спрацював — усі переходи від
     * циклу. */
    assert(laps == 4);
    assert(vm.total_jumps == 3);
    assert(sim.battery_pct > 25.0f);
}

/* Та сама програма, але батарея сідає: перевірка на першій же інструкції кола
 * має відправити апарат додому, не дочекавшись трьох повторів. */
static void scenario_low_battery(void)
{
    mission_vm_t   vm;
    sim_t          sim;
    vm_actuators_t act;

    mission_vm_init(&vm);
    mission_vm_set_home(&vm, HOME_LAT_1E7, HOME_LON_1E7, 180.0f);
    memset(&act, 0, sizeof(act));
    sim_init(&sim, 50.45, 30.52);
    sim.drain_pct_s = 1.2f;
    sim.gcs_link_ok = false; /* зв'язок із наземною станцією втрачено */

    vm_load_result_t rc = mission_vm_load(&vm, patrol_program,
                                          (uint16_t)(sizeof patrol_program /
                                                     sizeof patrol_program[0]));
    assert(rc == VM_LOAD_OK);

    unsigned laps = run_mission(&vm, &sim, &act, PC_SERVO, 40000, NULL);

    printf("сіла батарея: %s, кіл %u, залишок %.1f%%\n",
           vm_status_name(vm.status), laps, sim.battery_pct);

    assert(vm.status == VM_STATUS_COMPLETED);
    assert(act.rtl_triggered);
    assert(laps < 4);                 /* до трьох повторів не дійшло          */
    assert(sim.battery_pct < 25.0f);
    /* Втрата зв'язку з оператором на автономну програму не вплинула жодним
     * чином: машина взагалі не дивиться на це поле. */
    assert(!sim.gcs_link_ok);
}

/* Дії й неблокуючі умови: зміна швидкості, витримка за часом, очікування
 * курсу, посадка. */
static const vm_instruction_t action_program[] = {
    /* 0 */ { .opcode = OP_DO_CHANGE_SPEED, .param2 = 250 }, /* 2,5 м/с */
    /* 1 */ { .opcode = OP_COND_DELAY, .param1 = 2 },
    /* 2 */ { .opcode = OP_COND_YAW, .param1 = 90 },
    /* 3 */ { .opcode = OP_NAV_LAND },
};

static void scenario_actions(void)
{
    mission_vm_t   vm;
    sim_t          sim;
    vm_actuators_t act;
    uint32_t       elapsed_ms = 0;

    mission_vm_init(&vm);
    mission_vm_set_home(&vm, HOME_LAT_1E7, HOME_LON_1E7, 180.0f);
    memset(&act, 0, sizeof(act));
    sim_init(&sim, 50.45, 30.52);
    sim.yaw_rate_dps = 10.0f; /* апарат повільно обертається: 90° за 9 с */

    vm_load_result_t rc = mission_vm_load(&vm, action_program,
                                          (uint16_t)(sizeof action_program /
                                                     sizeof action_program[0]));
    assert(rc == VM_LOAD_OK);
    run_mission(&vm, &sim, &act, 0xFFFFu, 4000, &elapsed_ms);

    printf("дії: %s, швидкість %.2f м/с, курс %.1f°, час %.1f с\n",
           vm_status_name(vm.status), act.target_speed_mps, sim.yaw_deg,
           elapsed_ms / 1000.0);

    assert(vm.status == VM_STATUS_COMPLETED);
    assert(act.land_triggered);
    assert(fabsf(act.target_speed_mps - 2.5f) < 1e-6f);
    /* Дві секунди витримки, а потім розворот до 85° (курс 90° із допуском 5°)
     * — разом близько восьми з половиною секунд, і жодного блокувального
     * очікування: самі лише повернення з WAITING_COND. */
    assert(elapsed_ms >= 8000u);
}

/* ----------------------------------------------------- аварійні випадки */

static void scenario_loop_guard(void)
{
    static const vm_instruction_t looping[] = {
        /* 0 */ { .opcode = OP_DO_JUMP, .param1 = 0, .param2 = 1000 },
        /* 1 */ { .opcode = OP_HALT },
    };
    mission_vm_t   vm;
    sim_t          sim;
    vm_actuators_t act;

    mission_vm_init(&vm);
    mission_vm_set_home(&vm, HOME_LAT_1E7, HOME_LON_1E7, 180.0f);
    memset(&act, 0, sizeof(act));
    sim_init(&sim, 50.45, 30.52);

    assert(mission_vm_load(&vm, looping, 2) == VM_LOAD_OK);
    run_mission(&vm, &sim, &act, 0xFFFFu, 5000, NULL);

    printf("сторож циклів: %s після %u стрибків, failsafe=%d\n",
           vm_status_name(vm.status), vm.total_jumps, (int)act.failsafe_request);

    assert(vm.status == VM_STATUS_ERROR_INFINITE_LOOP);
    assert(vm.total_jumps == VM_MAX_TOTAL_JUMPS);
    assert(act.failsafe_request);
    assert(!act.nav_valid);
}

static void expect_load(const vm_instruction_t *code, uint16_t len,
                        bool set_home, vm_load_result_t want)
{
    mission_vm_t vm;
    mission_vm_init(&vm);
    if (set_home) {
        mission_vm_set_home(&vm, HOME_LAT_1E7, HOME_LON_1E7, 180.0f);
    }
    vm_load_result_t got = mission_vm_load(&vm, code, len);
    printf("завантажувач: чекали %s, дістали %s\n",
           vm_load_result_name(want), vm_load_result_name(got));
    assert(got == want);
}

static void scenario_loader(void)
{
    static const vm_instruction_t bad_opcode[] = {
        { .opcode = 0x7F }, { .opcode = OP_HALT },
    };
    static const vm_instruction_t bad_jump[] = {
        { .opcode = OP_DO_JUMP, .param1 = 99, .param2 = 2 }, { .opcode = OP_HALT },
    };
    static const vm_instruction_t bad_servo[] = {
        { .opcode = OP_DO_SET_SERVO, .param1 = 5, .param2 = 5000 },
        { .opcode = OP_HALT },
    };
    static const vm_instruction_t no_end[] = {
        { .opcode = OP_DO_SET_SERVO, .param1 = 5, .param2 = 1500 },
    };
    static vm_instruction_t too_many_loops[VM_MAX_LOOP_SLOTS + 2];

    for (unsigned i = 0; i < VM_MAX_LOOP_SLOTS + 1; i++) {
        too_many_loops[i].opcode = OP_DO_JUMP;
        too_many_loops[i].param1 = 0;
        too_many_loops[i].param2 = 1;
    }
    too_many_loops[VM_MAX_LOOP_SLOTS + 1].opcode = OP_HALT;

    expect_load(patrol_program, 8, false, VM_LOAD_NO_HOME);
    expect_load(patrol_program, 0, true, VM_LOAD_EMPTY);
    expect_load(bad_opcode, 2, true, VM_LOAD_BAD_OPCODE);
    expect_load(bad_jump, 2, true, VM_LOAD_BAD_JUMP);
    expect_load(bad_servo, 2, true, VM_LOAD_BAD_PARAM);
    expect_load(no_end, 1, true, VM_LOAD_NO_TERMINATOR);
    expect_load(too_many_loops, VM_MAX_LOOP_SLOTS + 2, true, VM_LOAD_TOO_MANY_LOOPS);
}

/* Відмова GNSS: машина не має права ні летіти навмання, ні спинятися сама.
 * Вона просто лишається в очікуванні, а лічильник простою росте — і саме за
 * ним зовнішній супервізор колись вирішить сідати. */
static void scenario_no_position(void)
{
    static const vm_instruction_t program[] = {
        /* 0 */ { .opcode = OP_NAV_TAKEOFF, .alt_m = 10.0f },
        /* 1 */ { .opcode = OP_NAV_WAYPOINT, .lat_1e7 = 504507000,
                  .lon_1e7 = 305212000, .alt_m = 10.0f },
        /* 2 */ { .opcode = OP_NAV_RTL },
    };
    mission_vm_t   vm;
    sim_t          sim;
    vm_actuators_t act;
    vm_telemetry_t telem;
    uint32_t       now_ms = 0;

    mission_vm_init(&vm);
    mission_vm_set_home(&vm, HOME_LAT_1E7, HOME_LON_1E7, 180.0f);
    memset(&act, 0, sizeof(act));
    memset(&telem, 0, sizeof(telem));
    telem.dist_to_wp_m = NAN;
    sim_init(&sim, 50.45, 30.52);
    sim.gnss_ok = false; /* позиції немає від самого початку */

    for (unsigned i = 0; i < 400; i++) {
        mission_vm_step(&vm, &telem, &act, now_ms);
        sim_update(&sim, &act, &telem);
        now_ms += SIM_DT_MS;
    }

    uint32_t waiting_ms = mission_vm_wait_elapsed_ms(&vm, now_ms);
    printf("без GNSS: %s на інструкції %u, чекає %u мс\n",
           vm_status_name(vm.status), vm.pc, waiting_ms);

    /* Зліт вимагає лише висоти й тому відпрацював; політ у точку — ні. */
    assert(vm.pc == 1);
    assert(vm.status == VM_STATUS_WAITING_NAV);
    assert(waiting_ms > 5000u);
    assert(!act.failsafe_request); /* це не помилка машини, а стан світу */
}

int main(void)
{
    printf("розмір інструкції: %zu байтів\n", sizeof(vm_instruction_t));
    scenario_patrol();
    scenario_low_battery();
    scenario_actions();
    scenario_loop_guard();
    scenario_loader();
    scenario_no_position();
    printf("усі сценарії пройдено\n");
    return 0;
}
