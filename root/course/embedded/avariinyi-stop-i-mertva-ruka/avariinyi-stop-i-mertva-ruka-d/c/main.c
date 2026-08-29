/* Стенд контролера безпеки.
   Тут живе реалізація hal_* поверх моделі проводки: тестові виходи, контакти
   грибка, місця замикань, котушки контакторів із їхньою механічною затримкою
   та дзеркальні NC-контакти петлі EDM. Модель потрібна, щоб дефекти, заради
   яких написано діагностику, можна було внести навмисно — на живому верстаті
   міжканальне замикання не влаштовують. */

#include <stdio.h>
#include <string.h>

#include "safety.h"
#include "safety_hal.h"

#define CONTACTOR_DELAY_MS  15U   /* час відпускання якоря контактора */
#define TICK_US             1000U

typedef struct {
    uint32_t now_us;

    bool     test_out[2];
    bool     contact_closed[2];    /* контакти грибка: true — контур цілий */
    bool     short_to_supply[2];   /* лінія притиснута до +24 В */
    bool     cross_circuit;        /* лінії каналів зрощені між собою */

    bool     coil_on;
    uint32_t coil_since_ms;
    bool     mirror_closed;        /* петля EDM */
    bool     contactor_welded;     /* силовий контакт K1 приварився */

    bool     en_a, en_b, panic_nc; /* контакти 3-позиційної кнопки */
    bool     reset_btn, ack_btn, operator_active;
    bool     lamp, buzzer;
} bench_t;

static bench_t  bench;
static safety_t ctl;

/* ── реалізація контракту заліза ──────────────────────────────────────────── */

void hal_set_test_output(uint8_t ch, bool high)
{
    bench.test_out[ch] = high;
}

/* Чим лінія керується просто зараз. Розімкнений контакт лишає вхід
   висіти на підтяжці вниз, замкнений — під двотактним тестовим виходом. */
typedef enum { DRIVE_NONE = 0, DRIVE_LOW, DRIVE_HIGH } drive_t;

static drive_t line_drive(uint8_t ch)
{
    if (!bench.contact_closed[ch]) {
        return DRIVE_NONE;
    }
    return bench.test_out[ch] ? DRIVE_HIGH : DRIVE_LOW;
}

bool hal_read_estop_input(uint8_t ch)
{
    drive_t drive = line_drive(ch);

    if (bench.cross_circuit) {
        /* Зрощені лінії — один вузол. Двотактний вихід, що тягне вниз,
           перемагає: саме тому чужий тестовий імпульс видно на обох входах. */
        const drive_t other = line_drive((uint8_t)(ch ^ 1u));
        if (other == DRIVE_LOW) {
            drive = DRIVE_LOW;
        } else if (other == DRIVE_HIGH && drive == DRIVE_NONE) {
            drive = DRIVE_HIGH;
        }
        if (bench.short_to_supply[ch ^ 1u]) {
            return true;
        }
    }

    if (bench.short_to_supply[ch]) {
        return true;   /* стороннє живлення дужче за тестовий вихід */
    }
    return drive == DRIVE_HIGH;
}

bool hal_read_edm_loop(void)
{
    return bench.mirror_closed;
}

void hal_set_contactors(bool energize)
{
    if (bench.coil_on != energize) {
        bench.coil_on       = energize;
        bench.coil_since_ms = bench.now_us / 1000u;
    }
}

void hal_read_enabling_contacts(bool *circuit_a, bool *circuit_b, bool *panic_nc)
{
    *circuit_a = bench.en_a;
    *circuit_b = bench.en_b;
    *panic_nc  = bench.panic_nc;
}

bool hal_read_reset_button(void) { return bench.reset_btn; }
bool hal_read_ack_button(void)   { return bench.ack_btn; }
bool hal_operator_active(void)   { return bench.operator_active; }

void hal_set_lamp(bool on)   { bench.lamp = on; }
void hal_set_buzzer(bool on) { bench.buzzer = on; }

void hal_busy_wait_us(uint32_t us)
{
    bench.now_us += us;   /* тестовий імпульс з'їдає справжній час циклу */
}

uint32_t hal_now_ms(void)
{
    return bench.now_us / 1000u;
}

/* ── такт моделі ──────────────────────────────────────────────────────────── */

static void bench_tick(void)
{
    bench.now_us += TICK_US;
    const uint32_t now = bench.now_us / 1000u;

    /* Дзеркальні контакти йдуть слідом за котушкою, але не миттєво.
       Приварений силовий контакт тримає свій NC розімкненим назавжди. */
    if ((uint32_t)(now - bench.coil_since_ms) >= CONTACTOR_DELAY_MS) {
        bench.mirror_closed = !bench.coil_on && !bench.contactor_welded;
    }
}

/* ── друк подій ───────────────────────────────────────────────────────────── */

static uint32_t       t0_ms;
static safety_state_t last_state;
static bool           last_out, last_lamp, last_buzzer, fresh;

static void report(void)
{
    const safety_state_t st  = safety_state(&ctl);
    const bool           out = safety_outputs_on(&ctl);

    if (!fresh && st == last_state && out == last_out
        && bench.lamp == last_lamp && bench.buzzer == last_buzzer) {
        return;
    }

    printf("  %6u мс   K1/K2 %s   %s%s%s\n",
           hal_now_ms() - t0_ms,
           out ? "ON " : "off",
           safety_state_name(st),
           bench.lamp ? "   [лампа]" : "",
           bench.buzzer ? "   [зумер]" : "");

    last_state  = st;
    last_out    = out;
    last_lamp   = bench.lamp;
    last_buzzer = bench.buzzer;
    fresh       = false;
}

static void step(uint32_t ms)
{
    for (uint32_t i = 0; i < ms; i++) {
        bench_tick();
        safety_process(&ctl);
        report();
    }
}

/* ── дії оператора ────────────────────────────────────────────────────────── */

static void grip_enable(void)   { bench.en_a = bench.en_b = true;  bench.panic_nc = true;  }
static void grip_release(void)  { bench.en_a = bench.en_b = false; bench.panic_nc = true;  }
static void grip_panic(void)    { bench.en_a = bench.en_b = false; bench.panic_nc = false; }

static void press_reset(void)
{
    bench.reset_btn = true;  step(10);
    bench.reset_btn = false; step(10);
}

static void hit_mushroom(void)     { bench.contact_closed[0] = bench.contact_closed[1] = false; }
static void release_mushroom(void) { bench.contact_closed[0] = bench.contact_closed[1] = true;  }

/* Справний стенд: грибок витягнуто, кнопка дозволу відпущена, контактори
   знеструмлені, петля EDM замкнена. Годинник не скидаємо — він наскрізний. */
static void bench_reset(const char *title)
{
    const uint32_t keep = bench.now_us;
    memset(&bench, 0, sizeof bench);
    bench.now_us = keep;

    bench.test_out[0] = bench.test_out[1] = true;
    release_mushroom();
    grip_release();
    bench.mirror_closed = true;

    safety_init(&ctl);

    t0_ms = hal_now_ms();
    fresh = true;
    printf("\n=== %s ===\n", title);
    report();
}

/* ── сценарії ─────────────────────────────────────────────────────────────── */

static void scenario_normal_cycle(void)
{
    bench_reset("Штатний пуск, удар по грибку, повторний пуск");
    grip_enable();
    step(30);
    press_reset();          /* контур цілий, петля EDM замкнена → пуск */
    step(100);

    hit_mushroom();         /* Категорія 0 */
    step(150);

    release_mushroom();
    step(30);
    press_reset();
    step(100);
}

static void scenario_discordance(void)
{
    bench_reset("Розбіжність каналів: перекіс контактного блока");
    grip_enable();
    step(30);
    press_reset();
    step(100);

    bench.contact_closed[0] = false;   /* розімкнувся лише канал A */
    step(300);                         /* негайний стоп, далі — залипла помилка */
}

static void scenario_short_to_supply(void)
{
    bench_reset("Замикання лінії каналу A на шину +24 В");
    grip_enable();
    step(30);
    press_reset();
    step(50);

    bench.short_to_supply[0] = true;   /* перетерта ізоляція в кабель-каналі */
    step(100);                         /* тестовий провал не доходить до входу */
}

static void scenario_cross_circuit(void)
{
    bench_reset("Міжканальне замикання лінії A на лінію B");
    grip_enable();
    step(30);
    press_reset();
    step(50);

    bench.cross_circuit = true;
    step(100);   /* чужий імпульс з'являється на сусідньому каналі */
}

static void scenario_welded_contactor(void)
{
    bench_reset("Зварений силовий контакт K1: петля EDM не замикається");
    grip_enable();
    step(30);
    press_reset();
    step(50);

    bench.contactor_welded = true;   /* дуга зварила контакт під навантаженням */
    hit_mushroom();
    step(400);                       /* K2 розірвав живлення, EDM зафіксував K1 */

    release_mushroom();
    step(30);
    press_reset();                   /* повторний пуск заблоковано */
    step(50);
}

static void scenario_panic_release(void)
{
    bench_reset("Панічне стискання і зворотний хід крізь Позицію 2");
    grip_enable();
    step(30);
    press_reset();
    step(50);

    grip_panic();       /* Позиція 3: судомне стискання */
    step(50);

    grip_enable();      /* рука розтискається, кнопка проходить Позицію 2 */
    step(30);
    press_reset();      /* вмикання заборонено: блокування ще зведене */
    step(50);

    grip_release();     /* повне повернення в Позицію 1 знімає блокування */
    step(30);
    grip_enable();
    step(30);
    press_reset();
    step(50);
}

static void scenario_vigilance(void)
{
    bench_reset("Циклічний контроль пильності: лампа → зумер → зупинка");
    grip_enable();
    step(30);
    press_reset();
    step(50);

    bench.operator_active = true;    /* оператор працює джойстиком */
    step(20000);
    bench.operator_active = false;   /* і завмер */
    step(51000);                     /* 45 с спокою + 2.5 с + 2.5 с */

    grip_release();                  /* лише повне відпускання знімає блокування */
    step(30);
    grip_enable();
    step(30);
    press_reset();
    step(50);
}

int main(void)
{
    scenario_normal_cycle();
    scenario_discordance();
    scenario_short_to_supply();
    scenario_cross_circuit();
    scenario_welded_contactor();
    scenario_panic_release();
    scenario_vigilance();
    return 0;
}
