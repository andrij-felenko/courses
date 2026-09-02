#include "ew_monitor.h"

#include "ew_detector.h"
#include "sx126x_rf.h"

#include "queue.h"

#define EW_MONITOR_PERIOD_MS    100u  /* класифікатор працює 10 разів на секунду */
#define EW_MONITOR_HOLD_MS      200u  /* вердикт мусить протриматися два цикли */
#define EW_MONITOR_QUEUE_LEN    8u
#define EW_MONITOR_STACK_WORDS  384u

/* Усе це реалізують інші рівні прошивки: радіо, навігація, мотори, телеметрія. */
extern void    rf_fhss_force_channel_hop(void);
extern void    rf_frontend_set_attenuator(bool on);
extern void    rf_set_fec_rate(uint8_t code_rate_denominator);
extern bool    nav_get_gnss_frame(ew_gnss_frame_t *out);
extern void    nav_use_gnss(bool allow);
extern uint8_t motors_throttle_pct(void);
extern void    telemetry_report_threat(ew_threat_t threat, uint32_t held_ms,
                                       const ew_rf_stats_t *stats, uint32_t dropped);

static ew_detector_t s_detector;

/* Статична черга й статичний потік: динамічної купи в польотній прошивці немає. */
static QueueHandle_t     s_queue;
static StaticQueue_t     s_queue_ctl;
static uint8_t           s_queue_storage[EW_MONITOR_QUEUE_LEN * sizeof(ew_rf_sample_t)];
static StaticTask_t      s_task_ctl;
static StackType_t       s_task_stack[EW_MONITOR_STACK_WORDS];
static volatile uint32_t s_dropped;

uint32_t ew_monitor_dropped(void)
{
    return s_dropped;
}

void ew_monitor_dio1_isr(void)
{
    ew_rf_sample_t sample;

    /* У перериванні дозволено рівно одне: короткий детермінований обмін по SPI
       (десяток байтів статусу, одиниці мікросекунд). Жодних обчислень тут
       немає — класифікація живе в потоці. */
    if (sx126x_read_sample(&sample) != SX126X_OK) {
        return;
    }
    sample.throttle_pct = motors_throttle_pct();

    BaseType_t woken = pdFALSE;
    /* Черга неблокуюча: якщо потік телеметрії відстав, вибірку свідомо
       втрачаємо, але радіотракт не зупиняємо ні на такт. */
    if (xQueueSendFromISR(s_queue, &sample, &woken) != pdTRUE) {
        s_dropped++;
    }
    portYIELD_FROM_ISR(woken);
}

static void ew_monitor_apply(ew_threat_t threat)
{
    switch (threat) {
        case EW_THREAT_SPOT_JAMMING:
            /* Прицільна б'є в одну частоту — тікаємо на інший канал. */
            rf_fhss_force_channel_hop();
            break;
        case EW_THREAT_BARRAGE_BLOCKING:
            /* Спершу виводимо LNA з насичення, інакше новий канал теж буде глухим. */
            rf_frontend_set_attenuator(true);
            rf_fhss_force_channel_hop();
            break;
        case EW_THREAT_PULSE_JAMMING:
            /* Проти рідких сплесків рятує надлишковість FEC. */
            rf_set_fec_rate(8u);
            break;
        case EW_THREAT_GNSS_SPOOFING:
            /* Координатам більше не віримо: далі — інерціальне числення. */
            nav_use_gnss(false);
            break;
        case EW_THREAT_WEAK_SIGNAL:
            /* Просто далеко: жодних дій, стрибок каналом тут лише зашкодить. */
            break;
        case EW_THREAT_NONE:
        default:
            /* Ефір очистився — знімаємо все, що вмикали. */
            rf_frontend_set_attenuator(false);
            rf_set_fec_rate(5u);
            nav_use_gnss(true);
            break;
    }
}

static void ew_monitor_task(void *arg)
{
    (void)arg;

    TickType_t   last_wake = xTaskGetTickCount();
    ew_threat_t  applied = EW_THREAT_NONE;

    for (;;) {
        vTaskDelayUntil(&last_wake, pdMS_TO_TICKS(EW_MONITOR_PERIOD_MS));

        const uint32_t now_ms = (uint32_t)(xTaskGetTickCount() * portTICK_PERIOD_MS);

        /* Забираємо все, що встигло накопати переривання. */
        ew_rf_sample_t sample;
        unsigned taken = 0;
        while (xQueueReceive(s_queue, &sample, 0) == pdTRUE) {
            ew_detector_push_rf(&s_detector, &sample);
            taken++;
        }

        if (taken == 0) {
            /* Тиша в ефірі — теж симптом. Під загороджувальною завадою пакетів
               немає, переривань немає, і вікно б «замерзло» на старих добрих
               вибірках. Тому знімаємо миттєвий RSSI самі: він і скаже, ефір
               порожній чи забитий по вінця. */
            if (sx126x_read_sample(&sample) == SX126X_OK) {
                sample.throttle_pct = motors_throttle_pct();
                ew_detector_push_rf(&s_detector, &sample);
            }
        }

        ew_gnss_frame_t gnss;
        const bool has_gnss = nav_get_gnss_frame(&gnss);

        const ew_threat_t threat = ew_detector_evaluate(&s_detector,
                                                        has_gnss ? &gnss : NULL,
                                                        now_ms);
        const uint32_t held_ms = ew_detector_threat_held_ms(&s_detector, now_ms);

        /* Реагуємо лише на вердикт, що протримався два цикли: одиничний
           провал у місті чи різкий крен не мусить перекидати канал. */
        if (threat != applied && held_ms >= EW_MONITOR_HOLD_MS) {
            ew_monitor_apply(threat);
            applied = threat;
        }

        ew_rf_stats_t stats;
        if (ew_detector_stats(&s_detector, &stats)) {
            telemetry_report_threat(threat, held_ms, &stats, s_dropped);
        }
    }
}

void ew_monitor_start(UBaseType_t priority)
{
    ew_detector_init(&s_detector);
    s_dropped = 0;

    s_queue = xQueueCreateStatic(EW_MONITOR_QUEUE_LEN, sizeof(ew_rf_sample_t),
                                 s_queue_storage, &s_queue_ctl);
    /* Статичне створення не вміє провалитися через брак пам'яті, але вміє
       через криво пораховані розміри — ловимо це на старті, а не в польоті. */
    configASSERT(s_queue != NULL);

    (void)xTaskCreateStatic(ew_monitor_task, "ew", EW_MONITOR_STACK_WORDS,
                            NULL, priority, s_task_stack, &s_task_ctl);
}
