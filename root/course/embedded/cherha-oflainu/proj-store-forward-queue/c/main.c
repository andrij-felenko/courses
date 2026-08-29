/* main.c — заняття на моделі NOR: чотири сцени життя черги.
 *
 *   1. Чистий кристал і перший старт.
 *   2. Зв'язку немає: кільце заповнюється, низький пріоритет
 *      відкидається, високий витісняє найстаріший сектор.
 *   3. Живлення зникає посеред запису кадру; після подачі напруги
 *      черга сама знаходить голову, хвіст і наступний номер.
 *   4. Зв'язок повернувся: свіжі кадри летять живою колією, історія
 *      вивантажується пачками, хвіст рухається лише по квитанціях.
 */
#include <stdio.h>
#include <string.h>

#include "sf_flash_sim.h"
#include "sf_queue.h"

#define SECTORS     16u
#define SECTOR_SIZE 4096u
#define PAGE_SIZE   256u
#define FLASH_SIZE  (SECTORS * SECTOR_SIZE)

static uint8_t        g_flash[FLASH_SIZE];
static sf_flash_sim_t g_sim;
static sf_flash_dev_t g_dev;
static sf_queue_t     g_queue;

/* Годинник вузла. */
static uint64_t g_now_ms = 1000u;

static uint64_t tick(uint32_t ms)
{
    g_now_ms += ms;
    return g_now_ms;
}

/* Замок-сторож: на хості потоку один, тож він нічого не блокує, зате
 * ловить вкладений вхід — тобто помилку, через яку на живій RTOS черга
 * колись прочитала б кадр посеред власного запису. На платі сюди
 * підставляють xSemaphoreTake / taskENTER_CRITICAL. */
static int g_lock_depth = 0;

static void lock_enter(void *ctx)
{
    (void)ctx;
    if (g_lock_depth++ != 0) {
        printf("!! повторний вхід у чергу: замок не тримає\n");
    }
}

static void lock_exit(void *ctx)
{
    (void)ctx;
    g_lock_depth--;
}

/* Радіоканал: детермінована псевдовипадковість замість справжніх втрат. */
static uint32_t g_rng = 0x2A3B4C5Du;

static uint32_t rnd(void)
{
    g_rng = g_rng * 1664525u + 1013904223u;
    return g_rng >> 16;
}

static bool link_deliver(void)
{
    return (rnd() % 100u) < 85u; /* 15% кадрів не доїжджає */
}

static uint16_t make_sample(char *buf, size_t cap, uint32_t n)
{
    const int len = snprintf(buf, cap, "t=%llu vbat=%umV temp=%d.%dC n=%u",
                             (unsigned long long)g_now_ms,
                             3600u + (n % 40u),
                             20 + (int)(n % 7u), (int)(n % 10u), n);
    return (uint16_t)len;
}

static void print_state(const char *label)
{
    printf("  %-22s голова %2u:%-5u хвіст %2u:%-5u курсор %2u:%-5u  наступний seq %u  у черзі %u Б\n",
           label, g_queue.head_sector, g_queue.head_offset,
           g_queue.tail_sector, g_queue.tail_offset,
           g_queue.drain_sector, g_queue.drain_offset,
           g_queue.next_seq, sf_queue_bytes_pending(&g_queue));
}

static void print_stats(void)
{
    const sf_stats_t *s = sf_queue_stats(&g_queue);

    printf("  записано %u кадрів (%u Б) · стерто секторів %u · витіснено %u\n",
           s->records_written, s->bytes_written, s->sectors_erased, s->sectors_evicted);
    printf("  відмовлено низькому пріоритету %u · битих кадрів %u · відновлено %u\n",
           s->dropped_full, s->corrupt_records, s->recovered_records);
    printf("  помилок носія %u · історія пропустила квитоване живцем %u · діапазонів втрачено %u\n",
           s->flash_errors, s->skipped_live_acked, g_queue.ack.dropped);
}

/* -------------------------------------------------------------------- сцени */

static void scene_offline(void)
{
    char payload[96];
    uint32_t n = 0;
    uint32_t refused = 0;
    uint32_t stored = 0;

    printf("\n== 2. Зв'язку немає: пишемо, поки є куди ==\n");

    /* 50 Гц телеметрії, раз на секунду статус, зрідка аварія. */
    for (uint32_t i = 0; i < 4000u && refused < 40u; i++) {
        uint8_t       type = SF_TYPE_TELEMETRY;
        sf_priority_t prio = SF_PRIORITY_LOW;

        if (i % 50u == 0u) {
            type = SF_TYPE_STATUS;
            prio = SF_PRIORITY_NORM;
        }
        if (i % 613u == 0u) {
            type = SF_TYPE_ALARM;
            prio = SF_PRIORITY_HIGH;
        }

        const uint16_t len = make_sample(payload, sizeof(payload), n++);
        const sf_err_t err = sf_queue_push(&g_queue, type, prio, tick(20), payload, len, NULL);

        if (err == SF_OK) {
            stored++;
        } else if (err == SF_E_FULL) {
            refused++;
        } else {
            printf("  носій відмовив: код %d\n", (int)err);
            break;
        }
    }

    printf("  збережено %u кадрів, відкинуто низькопріоритетних %u\n", stored, refused);
    print_state("кільце повне");
}

static void scene_power_loss(void)
{
    char payload[96];

    printf("\n== 3. Знеструмлення посеред кадру ==\n");

    /* Аварійний кадр піде у флеш, але напруга просяде після 24 байтів:
     * заголовок ляже, навантаження й CRC — ні. */
    const uint16_t len = make_sample(payload, sizeof(payload), 99999u);
    sf_flash_sim_cut_power_after(&g_sim, 24u);

    const sf_err_t err = sf_queue_push(&g_queue, SF_TYPE_ALARM, SF_PRIORITY_HIGH,
                                       tick(20), payload, len, NULL);
    printf("  push під час просідання напруги -> код %d (очікуємо %d)\n", (int)err, (int)SF_E_IO);

    const uint32_t seq_before = g_queue.next_seq;

    sf_flash_sim_power_up(&g_sim);
    printf("  живлення подано, вузол перезавантажився\n");

    const sf_lock_t lock = { lock_enter, lock_exit, NULL };
    if (sf_queue_init(&g_queue, &g_dev, 0, SECTORS, &lock) != SF_OK) {
        printf("  !! черга не піднялася\n");
        return;
    }

    print_state("після відновлення");
    printf("  номер до аварії %u, після сканування %u (обірваний кадр номера не з'їв)\n",
           seq_before, g_queue.next_seq);
}

static void scene_link_back(void)
{
    static sf_batch_t batch; /* 1 КіБ арени — на стеку задачі йому не місце */
    char payload[96];
    uint32_t fresh = 0;
    uint32_t live_acked = 0;
    uint32_t history_sent = 0;
    uint32_t rounds = 0;

    printf("\n== 4. Зв'язок повернувся: дві колії ==\n");

    while (rounds++ < 400u) {
        /* Жива колія: свіжий кадр лягає у флеш і одразу йде в ефір. */
        if (rounds % 2u == 0u) {
            const uint16_t len = make_sample(payload, sizeof(payload), 500000u + fresh);
            uint32_t seq = 0;

            if (sf_queue_push(&g_queue, SF_TYPE_TELEMETRY, SF_PRIORITY_NORM,
                              tick(20), payload, len, &seq) == SF_OK) {
                fresh++;
                if (link_deliver()) {
                    sf_queue_ack_live(&g_queue, seq);
                    live_acked++;
                }
                /* Квитанція не прийшла — кадр нікуди не дівся: історія
                 * дійде до нього сама й відправить удруге. */
            }
        }

        /* Колія історії: пачка старих кадрів від курсора вивантаження. */
        if (sf_queue_drain_batch(&g_queue, &batch) != SF_OK) {
            if (sf_queue_is_empty(&g_queue)) {
                break;
            }
            continue;
        }

        if (link_deliver()) {
            history_sent += batch.count;
            sf_queue_commit_ack(&g_queue, batch.last_seq);
        } else {
            /* Пачка загубилась — курсор назад на хвіст, поїде знову. */
            sf_queue_drain_rewind(&g_queue);
        }

        if (rounds % 40u == 0u) {
            printf("  раунд %3u: пачка %u кадрів [%u..%u], у черзі %u Б\n",
                   rounds, batch.count, batch.first_seq, batch.last_seq,
                   sf_queue_bytes_pending(&g_queue));
        }
    }

    printf("  свіжих кадрів %u (з них квитовано живцем %u), історією віддано %u\n",
           fresh, live_acked, history_sent);
    print_state("після вивантаження");
}

int main(void)
{
    const sf_lock_t lock = { lock_enter, lock_exit, NULL };

    printf("== 1. Чистий кристал ==\n");
    memset(g_flash, 0x00, sizeof(g_flash)); /* навмисно НЕ 0xFF: кристал із коробки */
    sf_flash_sim_init(&g_sim, g_flash, FLASH_SIZE, SECTOR_SIZE, PAGE_SIZE, &g_dev);
    sf_flash_sim_bulk_erase(&g_sim);

    if (sf_queue_init(&g_queue, &g_dev, 0, SECTORS, &lock) != SF_OK) {
        printf("черга не піднялася\n");
        return 1;
    }
    print_state("порожня черга");

    scene_offline();
    scene_power_loss();
    scene_link_back();

    printf("\n== Підсумок ==\n");
    print_stats();
    printf("  модель носія: стирань %u, операцій програмування %u\n",
           g_sim.erase_count, g_sim.program_count);
    return 0;
}
