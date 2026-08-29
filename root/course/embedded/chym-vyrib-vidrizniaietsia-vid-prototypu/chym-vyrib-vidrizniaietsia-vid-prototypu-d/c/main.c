/* main.c — порядок старту серійного виробу й нагляд за ним.
 *
 * Різниця з макетом видна вже в перших рядках main(): макет починає
 * з ініціалізації давача, виріб — зі знеструмлення силової частини
 * і з питання «а чому ми взагалі перезапустилися?». */
#include "console.h"
#include "crash_log.h"
#include "fault.h"
#include "mcu.h"
#include "safe_state.h"

#include <stdbool.h>
#include <stdint.h>

/* ---- Час -------------------------------------------------------------- */

#define CPU_HZ 168000000UL

static volatile uint32_t s_ms;

void SysTick_Handler(void)
{
    ++s_ms;
}

static uint32_t now_ms(void)
{
    return s_ms;
}

static void systick_init(void)
{
    SYST_RVR = (CPU_HZ / 1000UL) - 1UL;
    SYST_CVR = 0U;
    SYST_CSR = 0x7U; /* ENABLE | TICKINT | тактування від ядра */
}

/* ---- Монітор живлення (PVD) -------------------------------------------
 * Апаратний BOR виставляється ф'юзами й тримає ядро в скиданні нижче
 * свого порога. PVD — другий, програмний рубіж вище за BOR: він дає нам
 * кількасот мікросекунд, щоб добровільно погасити силову частину й не
 * почати запис у Flash перед самою смертю живлення. */

#define PVD_LEVEL_2V9 6U /* PLS = 110 -> ≈2.9 В */

static void power_monitor_init(void)
{
    RCC_APB1ENR |= RCC_APB1ENR_PWREN;
    mcu_dsb();

    uint32_t cr = PWR_CR;
    cr &= ~(7UL << PWR_CR_PLS_Pos);
    cr |= ((uint32_t)PVD_LEVEL_2V9 << PWR_CR_PLS_Pos);
    cr |= PWR_CR_PVDE;
    PWR_CR = cr;
}

static bool supply_is_sagging(void)
{
    return (PWR_CSR & PWR_CSR_PVDO) != 0U;
}

/* ---- Незалежний сторож із програмним вікном ---------------------------
 * IWDG тактується власним RC ≈32 кГц: він переживе і тріснутий кварц,
 * і зупинку основного тактування. Вікна в апаратурі F4 немає, тож
 * вікно робимо самі — і воно двобічне:
 *
 *   надто пізно  -> сторож перезапустить нас апаратно;
 *   надто рано   -> це ознака, що цикл провалився в порожнє коло
 *                   зі скиданням сторожа, і ми зупиняємося самі.
 *
 * До цього додається перекличка: сторожа годуємо лише тоді, коли за
 * період відзвітували ВСІ прикладні задачі. Інакше зависла одна задача
 * ховалася б за живою сусідкою. */

#define IWDG_TIMEOUT_MS 2048U
#define WINDOW_MIN_MS   200U

typedef enum {
    TASK_CONTROL = 0,
    TASK_TELEMETRY,
    TASK_COUNT
} task_id_t;

#define TASK_ALL_MASK ((1U << TASK_COUNT) - 1U)

static volatile uint32_t s_checkin_mask;
static uint32_t s_last_feed_ms;

static void watchdog_start(void)
{
    IWDG_KR = IWDG_KEY_UNLOCK;
    IWDG_PR = 4U;    /* дільник 64: 32000/64 = 500 Гц, крок 2 мс */
    IWDG_RLR = 1023U; /* 1024 кроки ≈ 2048 мс */
    while (IWDG_SR != 0U) {
        /* чекаємо, поки регістри перепишуться в домен сторожа */
    }
    IWDG_KR = IWDG_KEY_FEED;
    IWDG_KR = IWDG_KEY_START;
}

static void watchdog_checkin(task_id_t task)
{
    s_checkin_mask |= (1U << (unsigned)task);
}

static void watchdog_service(void)
{
    if ((s_checkin_mask & TASK_ALL_MASK) != TASK_ALL_MASK) {
        return; /* хтось не відзвітував — сторожа не годуємо */
    }

    const uint32_t elapsed = now_ms() - s_last_feed_ms;
    if (elapsed < WINDOW_MIN_MS) {
        /* Усі задачі відзвітували швидше, ніж фізично можливо: керуючий
         * цикл або крутиться порожнім колом, або зіпсовано лічильник
         * часу. Це аварія, а не привід годувати сторожа. */
        panic(PANIC_LOOP_TOO_FAST);
    }

    IWDG_KR = IWDG_KEY_FEED;
    s_last_feed_ms = now_ms();
    s_checkin_mask = 0U;
}

/* ---- Прикладна частина -------------------------------------------------
 * Давач вібрації віддає готовність рівнем на PA1 (DRDY). Макет чекав би
 * на нього нескінченним while; виріб чекає з таймаутом і має відповідь
 * на випадок «не дочекалися». */

#define PIN_SENSOR_DRDY   1U
#define SENSOR_TIMEOUT_MS 50U

static void sensor_input_init(void)
{
    RCC_AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    mcu_dsb();

    uint32_t moder = GPIOA_MODER;
    moder &= ~(3UL << (PIN_SENSOR_DRDY * 2U)); /* вхід */
    GPIOA_MODER = moder;

    uint32_t pupdr = GPIOA_PUPDR;
    pupdr &= ~(3UL << (PIN_SENSOR_DRDY * 2U));
    pupdr |= (2UL << (PIN_SENSOR_DRDY * 2U)); /* підтяжка до землі */
    GPIOA_PUPDR = pupdr;
}

/* Період силового ШІМ: 168 МГц / 8400 = 20 кГц — вище чутного діапазону
 * і нижче за межу комутаційних втрат мосту. */
static void pwm_init(void)
{
    TIM1_PSC = 0U;
    TIM1_ARR = 8399U;
    TIM1_CCR1 = 0U;
    /* OC1M = 110 (ШІМ-режим 1) плюс попереднє завантаження CCR1. */
    TIM1_CCMR1 = (TIM1_CCMR1 & ~0x7FUL) | (6UL << 4) | (1UL << 3);
}

static bool sensor_wait_ready(uint32_t timeout_ms)
{
    const uint32_t started = now_ms();
    while ((GPIOA_IDR & (1UL << PIN_SENSOR_DRDY)) == 0U) {
        if ((now_ms() - started) >= timeout_ms) {
            return false;
        }
    }
    return true;
}

static void control_step(void)
{
    if (!sensor_wait_ready(SENSOR_TIMEOUT_MS)) {
        /* Макет тут написав би printf і поїхав далі з торішніми даними.
         * Виріб не має права керувати приводом наосліп. */
        panic(PANIC_SENSOR_TIMEOUT);
    }

    /* Тут була б обробка вимірювання; для розмови про безпечний стан
     * досить того, що вона задає шпаруватість силового ШІМ. */
    const uint32_t duty = (TIM1_ARR / 4U);
    REQUIRE(duty <= TIM1_ARR); /* інваріант: шпаруватість у межах періоду */
    TIM1_CCR1 = duty;
}

/* ---- Перевірка силового каскаду на старті -----------------------------
 * Коротко подаємо живлення на міст із малою шпаруватістю й дивимося, чи
 * відповідає давач і чи не просідає шина під навантаженням. Гілок виходу
 * три, і кожна мусить погасити каскад. Класичний C-шаблон: єдина точка
 * прибирання під міткою out — і єдине місце, де про неї можна забути. */
static bool power_stage_self_test(void)
{
    bool ok = false;
    uint32_t started = 0U;

    if (!safe_state_enable_power()) {
        return false;
    }
    TIM1_CCR1 = TIM1_ARR / 10U;

    if (!sensor_wait_ready(SENSOR_TIMEOUT_MS)) {
        goto out;
    }

    started = now_ms();
    while ((now_ms() - started) < 5U) {
        if (supply_is_sagging()) {
            goto out; /* шина просіла під навантаженням — каскад слабкий */
        }
    }
    ok = true;

out:
    safe_state_disable_power();
    return ok;
}

/* ---- Старт ------------------------------------------------------------ */

/* Скільки поспіль аварій дозволяємо, перш ніж перестати заводити
 * силову частину зовсім. Пристрій, який після кожного рестарту знову
 * б'є приводом у механізм, небезпечніший за мовчазний. */
#define FAULT_LOCKOUT_THRESHOLD 3U

int main(void)
{
    /* 1. Механіка. До будь-чого іншого. */
    safe_state_arm_outputs();

    /* 2. Чому ми тут. Прапорці причини читаємо й гасимо одразу, поки
     *    ніхто їх не затер. */
    const reset_cause_t cause = crash_log_begin_boot();

    /* 3. Годинник, монітор живлення, діагностичний порт. */
    systick_init();
    power_monitor_init();
    console_init();
    sensor_input_init();
    pwm_init();

    char line[192];
    const size_t n = crash_log_render(line, sizeof(line));
    console_write_blocking(line, n);
    console_write_blocking("\r\n", 2U);

    const crash_log_t *log = crash_log_get();

    /* 4. Рішення про запуск силової частини. */
    bool allow_power = true;

    if (log->fault_count >= FAULT_LOCKOUT_THRESHOLD) {
        console_puts("LOCKOUT: забагато аварій поспіль, силова частина заблокована\r\n");
        allow_power = false;
    }
    if (cause == RESET_CAUSE_BROWN_OUT || supply_is_sagging()) {
        console_puts("HOLD: живлення нижче порога PVD, чекаємо відновлення\r\n");
        allow_power = false;
    }
    if (!crash_log_is_intact()) {
        console_puts("WARN: журнал не пройшов перевірку цілісності\r\n");
    }

    /* 5. Коротка перевірка силового каскаду під навантаженням. Макет
     *    цього не робить узагалі: там людина бачить прилад на столі. */
    if (allow_power && !power_stage_self_test()) {
        console_puts("SELFTEST: силовий каскад не пройшов перевірку\r\n");
        allow_power = false;
    }

    /* 6. Сторожа заводимо ПІСЛЯ ініціалізації, але ДО прикладного циклу:
     *    завислий старт теж мусить закінчитися рестартом. */
    s_last_feed_ms = now_ms();
    watchdog_start();

    s_checkin_mask = 0U;

    if (allow_power) {
        /* Виходимо з безпечного стану свідомо й один раз. */
        if (!safe_state_enable_power()) {
            console_puts("FAIL: силову частину зафіксовано в аварії\r\n");
            allow_power = false;
        }
    }

    uint32_t telemetry_due = now_ms() + 1000U;

    for (;;) {
        /* Живлення просіло під час роботи — гасимо силову частину
         * НЕГАЙНО, поки логіка ще детермінована, і не чекаємо, доки
         * ядро дійде до стану, в якому воно псує Flash. */
        if (supply_is_sagging()) {
            crash_log_note_uptime(now_ms());
            panic(PANIC_BROWN_OUT);
        }

        if (allow_power) {
            control_step();
        }
        /* Коли силову частину заблоковано, пристрій не вимикається
         * і не зациклюється мовчки: він далі годує сторожа й шле
         * телеметрію, щоб сервіс бачив живий вузол і причину блокування. */
        watchdog_checkin(TASK_CONTROL);

        if ((int32_t)(now_ms() - telemetry_due) >= 0) {
            const size_t len = crash_log_render(line, sizeof(line));
            console_write_blocking(line, len);
            console_write_blocking("\r\n", 2U);
            crash_log_note_uptime(now_ms());
            telemetry_due = now_ms() + 1000U;
        }
        watchdog_checkin(TASK_TELEMETRY);

        watchdog_service();
    }
}
