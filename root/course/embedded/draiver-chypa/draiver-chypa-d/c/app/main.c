/* app/main.c — прикладний рівень: два однакові чипи на різних шинах.
 *
 * Саме те, чого не вміє аматорський драйвер із глобальними змінними: два
 * незалежні дескриптори, кожен зі своєю шиною, адресою, тінню регістрів і
 * калібруванням. Плюс дві дисципліни збору — по готовності відліку та
 * пакетом із апаратного буфера.
 */
#define _POSIX_C_SOURCE 200809L

#include <signal.h>
#include <stdio.h>
#include <string.h>

#include "../chip_accel.h"
#include "../chip_fifo.h"
#include "../chip_status.h"
#include "../port/linux_i2c.h"

#define SENSOR_COUNT   2u
#define POLL_ROUNDS    20u
#define FIFO_WATERMARK 24u
#define FIFO_BATCH     32u

/* --- лінії SCL/SDA для аварійного скидання шини --------------------------
 *
 * На платі ці функції смикають справжні виводи мікроконтролера, переведені з
 * режиму периферії I2C у звичайний GPIO. У настільному прогоні справжніх
 * ліній немає, тож реалізація друкує послідовність тактів і моделює веденого,
 * який відпускає SDA після кількох тактів, — щоб алгоритм відновлення справді
 * виконувався й був видимий, а не мовчки повертав «нема ліній».
 */

typedef struct {
    unsigned clock_pulses;  /* скільки тактів SCL уже видано              */
    unsigned release_after; /* після якого такту ведений відпустить SDA   */
    bool     sda_level;     /* поточний рівень лінії даних                */
    bool     verbose;
} demo_gpio_t;

static void demo_gpio_init(demo_gpio_t *gpio, unsigned release_after, bool verbose)
{
    gpio->clock_pulses = 0u;
    gpio->release_after = release_after;
    gpio->sda_level = false; /* ведений тримає лінію в нулі — саме звідси й
                              * починається зависання шини */
    gpio->verbose = verbose;
}

static void demo_scl_set(void *user_ctx, bool level)
{
    demo_gpio_t *gpio = (demo_gpio_t *)user_ctx;
    if (level) {
        gpio->clock_pulses++;
        if (gpio->clock_pulses >= gpio->release_after) {
            /* Ведений виштовхнув останній біт і відпустив лінію даних. */
            gpio->sda_level = true;
        }
    }
    if (gpio->verbose) {
        printf("    SCL=%d (такт %u)\n", level ? 1 : 0, gpio->clock_pulses);
    }
}

static void demo_sda_set(void *user_ctx, bool level)
{
    demo_gpio_t *gpio = (demo_gpio_t *)user_ctx;
    /* Відкритий стік: нуль притискає лінію завжди, одиниця лише відпускає її
     * на резистор підтяжки — і лінія підніметься, тільки якщо її не тримає
     * ведений. */
    if (!level) {
        gpio->sda_level = false;
    } else if (gpio->clock_pulses >= gpio->release_after) {
        gpio->sda_level = true;
    }
    if (gpio->verbose) {
        printf("    SDA=%d\n", gpio->sda_level ? 1 : 0);
    }
}

static bool demo_sda_get(void *user_ctx)
{
    const demo_gpio_t *gpio = (const demo_gpio_t *)user_ctx;
    return gpio->sda_level;
}

static void demo_delay_us(uint32_t us)
{
    /* На платі тут стоїть калібрований цикл або таймер. У настільному
     * прогоні зволікати нема потреби: важлива послідовність, не тривалість. */
    (void)us;
}

static void demo_release(void *user_ctx)
{
    const demo_gpio_t *gpio = (const demo_gpio_t *)user_ctx;
    if (gpio->verbose) {
        printf("    лінії повернуто периферії I2C\n");
    }
}

static const chip_gpio_ops_t g_demo_gpio_ops = {
    .scl_set = demo_scl_set,
    .sda_set = demo_sda_set,
    .sda_get = demo_sda_get,
    .delay_us = demo_delay_us,
    .release = demo_release
};

/* --- давач на платі ------------------------------------------------------ */

typedef struct {
    const char     *bus_path;
    uint8_t         address;
    const char     *label;
    linux_i2c_bus_t bus;
    demo_gpio_t     gpio;
    chip_dev_t      dev;
    bool            online;
} sensor_t;

static volatile sig_atomic_t g_stop = 0;

static void on_sigint(int signo)
{
    (void)signo;
    g_stop = 1;
}

/* Ініціалізація з однією спробою аварійного скидання шини: якщо чип завис,
 * тримаючи SDA в нулі, жодна кількість повторів транзакції не допоможе —
 * лінію треба дотактувати вручну. */
static chip_status_t bring_up(sensor_t *sensor)
{
    chip_config_t cfg;
    memset(&cfg, 0, sizeof(cfg));
    cfg.bus_ops = linux_i2c_ops();
    cfg.gpio_ops = &g_demo_gpio_ops;
    cfg.user_ctx = &sensor->bus;
    cfg.gpio_ctx = &sensor->gpio;
    cfg.dev_addr = sensor->address;
    cfg.range = CHIP_RANGE_4G;
    cfg.odr = CHIP_ODR_100_HZ;
    cfg.resolution = CHIP_RES_16BIT;
    cfg.max_retries = 3u;
    cfg.retry_delay_ms = 1u;

    chip_status_t st = chip_init(&sensor->dev, &cfg);
    if (st != CHIP_ERR_COMM) {
        return st;
    }

    printf("  [%s] шина мовчить — пробуємо аварійне скидання\n", sensor->label);
    demo_gpio_init(&sensor->gpio, 4u, true);

    chip_status_t rc = chip_recover_bus(&sensor->dev);
    printf("  [%s] скидання шини: %s\n", sensor->label, chip_status_str(rc));
    if (rc != CHIP_OK) {
        return CHIP_ERR_COMM;
    }

    return chip_init(&sensor->dev, &cfg);
}

/* Калібрування конкретного екземпляра: зміщення нуля знімають на стенді,
 * поклавши плату на рівну поверхню, підсилення — на поворотному столі. */
static void apply_bench_calibration(sensor_t *sensor)
{
    chip_calib_t calib;
    memset(&calib, 0, sizeof(calib));
    calib.offset_raw[0] = -12;
    calib.offset_raw[1] = 8;
    calib.offset_raw[2] = -35;
    calib.gain[0] = 1.002f;
    calib.gain[1] = 0.998f;
    calib.gain[2] = 1.001f;

    chip_status_t st = chip_set_calibration(&sensor->dev, &calib);
    if (st != CHIP_OK) {
        printf("  [%s] калібрування не прийнято: %s\n", sensor->label, chip_status_str(st));
    }
}

/* Дисципліна 1: чекаємо готовності відліку з жорсткою стелею часу. На платі
 * замість очікування стоїть семафор, який виставляє обробник переривання
 * DRDY, — але сама транзакція так само робиться в контексті задачі. */
static void poll_loop(sensor_t *sensor)
{
    printf("\n[%s] збір по готовності відліку (%u кадрів)\n", sensor->label, POLL_ROUNDS);

    for (unsigned round = 0; round < POLL_ROUNDS && !g_stop; ++round) {
        chip_status_t st = chip_wait_data_ready(&sensor->dev, 50u);
        if (st == CHIP_ERR_TIMEOUT) {
            printf("  кадр %2u: датчик не віддав відліку за 50 мс\n", round);
            continue;
        }
        if (st != CHIP_OK) {
            printf("  кадр %2u: %s\n", round, chip_status_str(st));
            if (st == CHIP_ERR_COMM) {
                (void)chip_recover_bus(&sensor->dev);
            }
            continue;
        }

        /* Сирий відлік беремо РАЗ: читання очищає прапорець готовності, тож
         * друге звертання за тим самим кадром повернуло б CHIP_ERR_NO_DATA.
         * Усі три подання рахуються з однієї й тієї ж трійки кодів. */
        int16_t raw[3];
        st = chip_read_raw(&sensor->dev, raw);
        if (st != CHIP_OK) {
            printf("  кадр %2u: читання не вдалося (%s)\n", round, chip_status_str(st));
            continue;
        }

        chip_accel_si_t si;
        chip_accel_mg_t mg;
        chip_accel_mm_s2_t mm;
        chip_raw_to_si(&sensor->dev, raw, &si);
        chip_raw_to_accel_mg(&sensor->dev, raw, &mg);
        chip_raw_to_accel_mm_s2(&sensor->dev, raw, &mm);

        printf("  кадр %2u: %7.3f %7.3f %7.3f м/с²  |  %6d %6d %6d мг  |  "
               "%7d %7d %7d мм/с²\n",
               round, (double)si.x, (double)si.y, (double)si.z,
               mg.x, mg.y, mg.z, mm.x, mm.y, mm.z);
    }
}

/* Дисципліна 2: чип накопичує відліки сам, процесор спить і забирає пакет. */
static void fifo_loop(sensor_t *sensor)
{
    chip_fifo_config_t fifo_cfg;
    fifo_cfg.mode = CHIP_FIFO_STREAM;
    fifo_cfg.watermark = FIFO_WATERMARK;

    chip_status_t st = chip_fifo_configure(&sensor->dev, &fifo_cfg);
    if (st != CHIP_OK) {
        printf("\n[%s] буфер не налаштовано: %s\n", sensor->label, chip_status_str(st));
        return;
    }
    (void)chip_fifo_enable_watermark_interrupt(&sensor->dev, true);

    printf("\n[%s] кільцевий буфер, поріг %u вибірок\n", sensor->label, FIFO_WATERMARK);

    /* Поки чип набирає поріг при 100 Гц — приблизно чверть секунди сну. */
    for (unsigned attempt = 0; attempt < 5u && !g_stop; ++attempt) {
        uint8_t level = 0u;
        bool watermark_hit = false;
        bool overrun = false;

        st = chip_fifo_level(&sensor->dev, &level, &watermark_hit, &overrun);
        if (st != CHIP_OK) {
            printf("  стан буфера: %s\n", chip_status_str(st));
            break;
        }
        if (overrun) {
            printf("  УВАГА: буфер переповнено, частину відліків утрачено\n");
        }
        if (!watermark_hit) {
            sensor->dev.bus_ops->delay_ms(100u);
            continue;
        }

        chip_accel_si_t batch[FIFO_BATCH];
        size_t got = 0u;
        st = chip_fifo_read(&sensor->dev, batch, FIFO_BATCH, &got);
        if (got == 0u) {
            printf("  вичитування пакета: %s\n", chip_status_str(st));
            break;
        }
        if (st != CHIP_OK) {
            /* Пачка обірвалася посеред вичитування: те, що встигло приїхати,
             * лишається дійсним — BDU гарантує цілість кожної вибірки. */
            printf("  пакет обірвано (%s), забрано %zu вибірок\n", chip_status_str(st), got);
        }

        printf("  забрано %zu вибірок, перша Z = %.3f м/с², остання Z = %.3f м/с²\n",
               got, (double)batch[0].z, (double)batch[got - 1u].z);
        break;
    }

    fifo_cfg.mode = CHIP_FIFO_BYPASS;
    fifo_cfg.watermark = 0u;
    (void)chip_fifo_configure(&sensor->dev, &fifo_cfg);
    (void)chip_fifo_enable_watermark_interrupt(&sensor->dev, false);
}

int main(int argc, char **argv)
{
    sensor_t sensors[SENSOR_COUNT];
    memset(sensors, 0, sizeof(sensors));

    sensors[0].bus_path = (argc > 1) ? argv[1] : "/dev/i2c-1";
    sensors[0].address = 0x19u; /* вивід SA0 підтягнуто до живлення */
    sensors[0].label = "основний";

    sensors[1].bus_path = (argc > 2) ? argv[2] : "/dev/i2c-2";
    sensors[1].address = 0x18u; /* SA0 на землі — резервний канал   */
    sensors[1].label = "резервний";

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = on_sigint;
    sigaction(SIGINT, &sa, NULL);

    unsigned online = 0u;
    for (unsigned i = 0; i < SENSOR_COUNT; ++i) {
        sensor_t *s = &sensors[i];
        s->bus.fd = -1;
        demo_gpio_init(&s->gpio, 4u, false);

        int rc = linux_i2c_open(&s->bus, s->bus_path);
        if (rc != 0) {
            printf("[%s] %s не відкривається (errno %d)\n", s->label, s->bus_path, -rc);
            continue;
        }

        chip_status_t st = bring_up(s);
        if (st != CHIP_OK) {
            printf("[%s] %s @0x%02X: %s\n", s->label, s->bus_path, s->address,
                   chip_status_str(st));
            linux_i2c_close(&s->bus);
            continue;
        }

        apply_bench_calibration(s);
        s->online = true;
        online++;
        printf("[%s] %s @0x%02X: готовий, діапазон ±4g, 100 Гц\n",
               s->label, s->bus_path, s->address);
    }

    if (online == 0u) {
        printf("\nЖоден датчик не відповів. Перевірте живлення, підтяжки та адресу SA0.\n");
        return 1;
    }

    for (unsigned i = 0; i < SENSOR_COUNT && !g_stop; ++i) {
        if (!sensors[i].online) {
            continue;
        }
        poll_loop(&sensors[i]);
        fifo_loop(&sensors[i]);
    }

    for (unsigned i = 0; i < SENSOR_COUNT; ++i) {
        if (sensors[i].online) {
            (void)chip_shutdown(&sensors[i].dev);
            linux_i2c_close(&sensors[i].bus);
        }
    }

    printf("\nЗавершено. Активних датчиків: %u з %u.\n", online, SENSOR_COUNT);
    return 0;
}
