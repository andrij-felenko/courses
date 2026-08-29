/*
 * main.c — головний цикл: черга подій і автомат.
 *
 * Прошивка складається з двох частин, які майже не знають одна про одну.
 * Переривання лише кладуть сигнали в чергу і негайно завершуються;
 * головний цикл забирає події по одній і віддає автоматові, який обробляє
 * кожну до кінця (run-to-completion). Ніде немає жодного delay().
 *
 * На хості справжніх переривань немає, тому їх роль грає sim_isr_tick():
 * на кожному такті вона вирішує, що «сталося» в залізі.
 */
#include "device_hal.h"
#include "device_ui.h"
#include "qequeue.h"
#include "qhsm.h"

#include <stdio.h>
#include <stdlib.h>

#define TICK_MS        10U   /* один такт системного таймера */
#define IDLE_TICKS     50U   /* бездіяльність до згасання екрана */
#define QUEUE_CAPACITY 16U
#define SIM_TICKS      130U

static QEvt l_queueStorage[QUEUE_CAPACITY];
static QEQueue l_queue;
static DeviceUI l_ui;

/* Скільки тактів минуло від останнього натискання. Пишуть і читають цю
 * змінну обидві половини програми, тож на справжньому МК вона мусить бути
 * volatile і оновлюватися лише в перериванні таймера. */
static volatile uint32_t l_ticksIdle = 0U;

/* --- Джерела подій (на платі — обробники переривань) ------------------- */

/* Сценарій натискань: такт -> сигнал. Замінює зчитувач клавіатури. */
typedef struct {
    uint32_t tick;
    QSignal sig;
} SimInput;

static const SimInput l_script[] = {
    {  5U, BTN_ENTER_SIG },  /* прокидаємось: ScreenSaver -> Active -> MainMenu */
    { 10U, BTN_DOWN_SIG  },  /* виділяємо «Налаштування» */
    { 15U, BTN_ENTER_SIG },  /* MainMenu -> Settings */
    { 20U, BTN_UP_SIG    },  /* яскравіше */
    { 25U, SENSOR_FAULT_SIG },/* аварію ловить Active, а не Settings */
    { 30U, BTN_ENTER_SIG },  /* Settings -> Calibration */
    { 35U, BTN_ENTER_SIG },  /* результат прийнято, назад у Settings */
    { 40U, BTN_ENTER_SIG },  /* знову в Calibration — і більше ні звуку */
    /* такт 90: спрацює таймаут бездіяльності й розкрутить усю гілку */
    {100U, BTN_BACK_SIG  }   /* прокидаємось удруге */
};

/* Переривання клавіатури: кладе подію і скидає лічильник бездіяльності. */
static void isr_keypad(QSignal sig) {
    l_ticksIdle = 0U;
    if (!QEQueue_post(&l_queue, sig, 0U)) {
        printf("  [ISR ] чергу переповнено, натискання втрачено\n");
    }
}

/* Переривання давача: аварія приходить асинхронно й бездіяльності не скасовує. */
static void isr_sensor_fault(void) {
    if (!QEQueue_post(&l_queue, SENSOR_FAULT_SIG, 0U)) {
        printf("  [ISR ] чергу переповнено, аварію втрачено\n");
    }
}

/* Переривання системного таймера: рахує бездіяльність і сам породжує подію. */
static void isr_systick(void) {
    ++l_ticksIdle;
    if (l_ticksIdle >= IDLE_TICKS) {
        l_ticksIdle = 0U;
        (void)QEQueue_post(&l_queue, TIMEOUT_IDLE_SIG, 0U);
    }
}

static void sim_isr_tick(uint32_t tick) {
    size_t i;
    for (i = 0U; i < sizeof(l_script) / sizeof(l_script[0]); ++i) {
        if (l_script[i].tick == tick) {
            if (l_script[i].sig == SENSOR_FAULT_SIG) {
                isr_sensor_fault();
            } else {
                isr_keypad(l_script[i].sig);
            }
        }
    }
    isr_systick();
}

/* --- Контракт рушія --------------------------------------------------- */

Q_NORETURN void Q_onAssert(const char *module, int line) {
    fprintf(stderr, "ФАТАЛЬНО: порушено контракт HSM у %s:%d\n", module, line);
    /* На платі тут був би запис причини в резервний регістр і апаратне
     * перезавантаження: працювати далі з невідомим станом небезпечніше,
     * ніж перезапуститися. */
    abort();
}

/* --- Головний цикл ----------------------------------------------------- */

int main(void) {
    uint32_t tick;
    uint32_t sleepTicks = 0U;

    DeviceUI_ctor(&l_ui);
    QEQueue_init(&l_queue, l_queueStorage, QUEUE_CAPACITY);

    printf("== початковий перехід ==\n");
    QHsm_init(DeviceUI_hsm(&l_ui), NULL);

    for (tick = 0U; tick < SIM_TICKS; ++tick) {
        QEvt e;

        sim_isr_tick(tick);

        /* Черга спорожняється повністю: кожна подія обробляється до кінця,
         * і лише потім береться наступна. Саме це й означає «неблокуючий
         * цикл» — жодного очікування всередині обробки. */
        while (QEQueue_get(&l_queue, &e)) {
            printf("== %lu мс: сигнал %u ==\n",
                   (unsigned long)tick * TICK_MS, (unsigned)e.sig);
            QHsm_dispatch(DeviceUI_hsm(&l_ui), &e);
        }

        /* Черга порожня. Прошивка на платі викликала б тут __WFI() і чекала
         * на наступне переривання; коли автомат у заставці, ядро при цьому
         * ще й скидає тактову частоту. Хостова модель просто рахує такти. */
        if (DeviceUI_isAsleep(&l_ui)) {
            ++sleepTicks;
        }
    }

    printf("\n== підсумок ==\n");
    printf("максимальна зайнятість черги: %u з %u\n",
           (unsigned)QEQueue_maxUsed(&l_queue), (unsigned)QUEUE_CAPACITY);
    printf("втрачено подій: %u\n", (unsigned)QEQueue_dropped(&l_queue));
    printf("тактів у мікроспоживанні: %lu з %lu\n",
           (unsigned long)sleepTicks, (unsigned long)SIM_TICKS);
    return 0;
}
