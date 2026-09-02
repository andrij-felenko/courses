// Пульт: послідовність запуску й головна задача реального часу 1 кГц.
#include "hal.h"
#include "hud.h"
#include "link.h"
#include "power.h"
#include "sticks.h"
#include "sx1280.h"

#define TX_DEADLINE_US    700   // кадр 14 Б на 1.3 Мбіт/с іде близько 450 мкс
#define RX_WINDOW_US      260
#define WDT_TIMEOUT_MS    15
#define RADIO_FAULT_LIMIT 3
#define FAILSAFE_LOSSES   200   // 200 мс мовчання апарата — просимо аварійний режим

static volatile uint32_t g_tick;   // інкрементує переривання таймера
static uint32_t g_served;          // скільки тіків уже обробила задача
static uint32_t g_overruns;
static uint8_t  g_radio_faults;
static uint16_t g_lost_frames;
static link_stats_t g_stats;
static telemetry_t g_air;

// У перериванні — ЛИШЕ лічильник. Ні пакування, ні SPI, ні скидання
// сторожового таймера: watchdog, скинутий звідси, справно спрацьовував би й
// тоді, коли головна задача давно висить, і ховав би відмову.
static void timer_isr(void)
{
    g_tick++;
}

// Відмова до старту watchdog: миготимо вібромотором і не йдемо далі, бо
// відпускати апарат у ефір із несправним пультом гірше, ніж не злетіти.
static void fatal(uint8_t pulses)
{
    for (;;) {
        for (uint8_t i = 0; i < pulses; i++) {
            hal_haptic(200);
            hal_delay_us(120000);
            hal_haptic(0);
            hal_delay_us(180000);
        }
        hal_delay_us(800000);
    }
}

static bool radio_fault(void)
{
    if (++g_radio_faults >= RADIO_FAULT_LIMIT) {
        g_radio_faults = 0;
        // Спроба підняти трансивер займе кілька мілісекунд і зірве кілька
        // слотів — це свідомо: гірший варіант лише мовчазний ефір.
        sx1280_init(FRAME_LEN);
    }
    return false;   // watchdog не скидаємо: 15 відмов підряд перезапустять пульт
}

static bool run_slot(void)
{
    // 1. Осі. DMA поклав свіжі відліки повз кеш ядра — інвалідуємо рядки.
    hal_cache_invalidate(hal_adc_axes(), HAL_ADC_AXES * sizeof(uint16_t));
    const uint16_t *raw_gimbals = hal_adc_axes();

    uint16_t axes[HAL_ADC_AXES];
    for (uint8_t i = 0; i < HAL_ADC_AXES; i++) {
        axes[i] = sticks_process(i, raw_gimbals[i]);
    }

    const uint16_t switches = hal_switch_bits();
    const uint8_t faults = sticks_safety_check(axes, switches);
    const uint8_t aux = sticks_aux_update(switches);

    hud_state_t hud = {
        .pack_mv = power_battery_mv(),
        .batt_level = power_level(),
        .link_pct = g_stats.lq_pct,
        .lost_frames = g_lost_frames,
        .armed = (switches & SW_ARM) != 0,
        .safety_faults = faults,
        .air = g_air,
    };
    hud_set_state(&hud);

    if (faults) {
        // Блокування передачі: в ефір не йде нічого, поки оператор не поверне
        // газ у нуль і не зніме Arm. Вібро — короткими поштовхами раз на пів
        // секунди, щоб його чули крізь рукавицю, але воно не набридало.
        hal_haptic((g_served % 500u < 120u) ? 180 : 0);
        hud_service();
        return true;   // задача відпрацювала штатно, watchdog скидаємо
    }
    hal_haptic(0);

    uint8_t flags = 0;
    if (switches & SW_ARM) {
        flags |= FLAG_ARMED;
    }
    if (switches & SW_RATE_HIGH) {
        flags |= FLAG_RATE_HIGH;
    }
    if (switches & SW_PAYLOAD) {
        flags |= FLAG_PAYLOAD;
    }
    if (g_lost_frames > FAILSAFE_LOSSES) {
        flags |= FLAG_FAILSAFE;
    }

    // 2. Кадр і передача.
    uint8_t frame[FRAME_LEN];
    link_build_uplink(frame, axes, switches, flags, aux);
    if (!sx1280_transmit(frame, sizeof frame)) {
        return radio_fault();
    }

    // 3. PA в ефірі близько 450 мкс, шина SPI при цьому вільна — саме сюди
    //    лягає фонова графіка. Одна сторінка за виклик, вісім сторінок екрана.
    hud_service();

    if (!sx1280_wait_irq(SX1280_IRQ_TX_DONE, TX_DEADLINE_US, NULL)) {
        return radio_fault();
    }

    // 4. Перемикання TDD у прийом і друга порція графіки, поки чекаємо.
    if (!sx1280_listen(RX_WINDOW_US)) {
        return radio_fault();
    }
    hud_service();

    uint16_t irq = 0;
    const uint16_t rx_mask = SX1280_IRQ_RX_DONE | SX1280_IRQ_RX_TX_TIMEOUT |
                             SX1280_IRQ_CRC_ERROR;
    if (!sx1280_wait_irq(rx_mask, RX_WINDOW_US + 100u, &irq)) {
        // Чип не сказав навіть «таймаут» — це вже відмова трансивера, а не
        // втрачений пакет.
        return radio_fault();
    }

    bool got = false;
    if (irq & SX1280_IRQ_RX_DONE) {
        uint8_t buf[FRAME_LEN];
        size_t n = sx1280_read_packet(buf, sizeof buf);
        telemetry_t tlm;
        if (link_parse_downlink(buf, n, &tlm)) {   // сюди входить перевірка CRC
            g_air = tlm;
            got = true;
            g_lost_frames = 0;
        }
    }
    if (!got && g_lost_frames < 60000u) {
        g_lost_frames++;
    }
    link_stats_mark(&g_stats, got);
    g_radio_faults = 0;

    // 5. Вікно, у якому PA вже вимкнений, а наступна посилка ще не почалася.
    //    Тільки тут напруга батареї не просаджена стрибком струму на 95 мА.
    if ((g_served & 0x07u) == 0u) {
        power_sample_battery();
    }
    return true;
}

int main(void)
{
    hal_board_init();

    if (!power_hold_on()) {
        fatal(1);
    }
    if (!sx1280_init(FRAME_LEN)) {
        power_release();
        fatal(2);
    }

    // POST: двадцять мілісекунд живих відліків, щоб устоявся IIR, і аж тоді
    // маємо право судити про положення газу й справність осей.
    for (uint8_t i = 0; i < 20; i++) {
        hal_cache_invalidate(hal_adc_axes(), HAL_ADC_AXES * sizeof(uint16_t));
        const uint16_t *raw = hal_adc_axes();
        for (uint8_t ch = 0; ch < HAL_ADC_AXES; ch++) {
            (void)sticks_process(ch, raw[ch]);
        }
        power_sample_battery();
        hal_delay_us(1000);
    }
    if (power_level() == BATT_CRITICAL) {
        power_release();
        fatal(3);
    }

    hal_timer_start_1khz(timer_isr);
    hal_watchdog_start(WDT_TIMEOUT_MS);

    for (;;) {
        uint32_t tick = g_tick;
        if (tick == g_served) {
            continue;   // чекаємо строб таймера — слот починає він, не ми
        }
        if (tick - g_served > 1u) {
            g_overruns++;   // не вклалися в мілісекунду; лічильник видно в GDB
        }
        g_served = tick;

        if (run_slot()) {
            // Єдине місце в прошивці, де скидається watchdog: осі оцифровані,
            // кадр пішов у ефір, телеметрія перевірена за CRC.
            hal_watchdog_kick();
        }
    }
}
