/* Модель кільця секторів SPI NOR у RAM і три сценарії відновлення.
 *
 * Тут навмисно немає ані черги вивантаження, ані політики витіснення —
 * предмет цього прикладу один: що бачить прошивка на старті після того,
 * як живлення зникло посеред запису.
 */
#include <inttypes.h>
#include <stdio.h>
#include <string.h>

#include "sf_frame.h"
#include "sf_recover.h"

#define SECTOR_SIZE  4096u
#define SECTOR_COUNT 4u
#define AREA_SIZE    (SECTOR_SIZE * SECTOR_COUNT)

#define PAYLOAD_LEN 96u

static uint8_t  g_flash[AREA_SIZE];
static uint32_t g_valid_in_sector[SECTOR_COUNT]; /* очікуване, для звірки */

/* --- модель носія --------------------------------------------------- */

static int flash_read(void *ctx, uint32_t addr, void *dst, size_t len)
{
    (void)ctx;
    if (addr > AREA_SIZE || len > (size_t)(AREA_SIZE - addr)) {
        return -1;
    }
    memcpy(dst, g_flash + addr, len);
    return 0;
}

static void flash_erase(uint32_t sector)
{
    memset(g_flash + sector * SECTOR_SIZE, 0xFF, SECTOR_SIZE);
    g_valid_in_sector[sector] = 0;
}

/* Запис у NOR лише гасить біти (1 → 0); підняти біт може тільки стирання
 * цілого сектора. Модель тримає це правило, щоб обірваний кадр виглядав
 * так само, як на живому кристалі: заголовок є, а хвіст — суцільні 0xFF. */
static void flash_program(uint32_t addr, const uint8_t *src, size_t len)
{
    for (size_t i = 0; i < len; i++) {
        g_flash[addr + i] &= src[i];
    }
}

/* --- письменник черги ------------------------------------------------ */

typedef struct {
    uint32_t sector;
    uint32_t off;
    uint32_t seq;
    uint64_t ts_ms;
} writer_t;

/* cut_at — скільки байтів кадру встигло лягти на носій до знеструмлення;
 * SIZE_MAX означає нормальний, повністю записаний кадр. */
static bool append_frame(writer_t *w, uint8_t type, size_t cut_at)
{
    uint8_t payload[PAYLOAD_LEN];
    uint8_t frame[SF_MAX_FRAME];

    for (uint16_t i = 0; i < PAYLOAD_LEN; i++) {
        payload[i] = (uint8_t)(w->seq + i);
    }

    const sf_hdr_t hdr = {
        .seq   = w->seq,
        .ts_ms = w->ts_ms,
        .len   = PAYLOAD_LEN,
        .type  = type
    };

    const size_t total = sf_encode(frame, sizeof(frame), &hdr, payload);
    if (total == 0) {
        return false;
    }

    if (w->off + total > SECTOR_SIZE) {
        /* Кадр не ріжеться між секторами — переходимо на наступний.
         * Справжня черга стерла б його заздалегідь і лише переконавшись,
         * що це не сектор хвоста; тут витіснення нас не цікавить. */
        w->sector = (w->sector + 1) % SECTOR_COUNT;
        w->off = 0;
        flash_erase(w->sector);
    }

    const size_t written = (cut_at < total) ? cut_at : total;
    flash_program(w->sector * SECTOR_SIZE + w->off, frame, written);

    if (written == total) {
        g_valid_in_sector[w->sector]++;
    }

    w->off += (uint32_t)written;
    w->seq++;
    w->ts_ms += 20; /* 50 Гц */
    return true;
}

static void writer_init(writer_t *w)
{
    memset(w, 0, sizeof(*w));
    w->seq   = 1;
    w->ts_ms = 1735689600000ull; /* 2025-01-01T00:00:00Z */
}

/* --- звіт і звірка --------------------------------------------------- */

static int g_failures;

static void expect(bool cond, const char *what)
{
    if (!cond) {
        printf("    ПОМИЛКА: %s\n", what);
        g_failures++;
    }
}

static void report(const char *title, const sf_state_t *st)
{
    printf("%s\n", title);
    if (st->empty) {
        printf("    кільце порожнє, писати з сектора 0, seq = %" PRIu32 "\n",
               st->next_seq);
        return;
    }
    printf("    голова:  сектор %" PRIu32 ", зсув %" PRIu32
           ", наступний seq %" PRIu32 "\n",
           st->head_sector, st->head_offset, st->next_seq);
    printf("    хвіст:   сектор %" PRIu32 ", найстаріший seq %" PRIu32 "\n",
           st->tail_sector, st->tail_seq);
    printf("    кадрів:  %" PRIu32 ", пошкоджених секторів %" PRIu32
           ", обірваний запис: %s\n",
           st->valid_frames, st->damaged_sectors, st->torn_tail ? "так" : "ні");
}

static uint32_t expected_frames(void)
{
    uint32_t sum = 0;
    for (uint32_t i = 0; i < SECTOR_COUNT; i++) {
        sum += g_valid_in_sector[i];
    }
    return sum;
}

/* Заповнює кільце так, що воно робить повний оберт: голова опиняється
 * в секторі 0, а хвіст — у секторі 1. Останній кадр за бажанням рветься. */
static void fill_wrapped(writer_t *w, uint32_t frames, bool tear_last)
{
    writer_init(w);
    memset(g_flash, 0xFF, sizeof(g_flash));
    memset(g_valid_in_sector, 0, sizeof(g_valid_in_sector));

    for (uint32_t i = 0; i < frames; i++) {
        const bool last = (i + 1 == frames);
        const uint8_t type = (i % 50 == 0) ? SF_TYPE_STATUS : SF_TYPE_RAW;
        append_frame(w, type, (last && tear_last) ? SF_HDR_SIZE + 40u : (size_t)-1);
    }
}

int main(void)
{
    const sf_ring_t ring = {
        .read         = flash_read,
        .ctx          = NULL,
        .sector_size  = SECTOR_SIZE,
        .sector_count = SECTOR_COUNT
    };
    sf_state_t st;
    writer_t   w;

    /* 1. Знеструмлення посеред запису після обороту кільця. */
    fill_wrapped(&w, 150, true);
    if (sf_recover(&ring, &st) != 0) {
        printf("сканування не вдалося: збій читання\n");
        return 1;
    }
    report("Сценарій 1: живлення зникло посеред кадру seq 150", &st);
    expect(!st.empty, "кільце мало містити дані");
    expect(st.torn_tail, "обірваний кадр мав бути помічений");
    expect(st.head_sector == 0, "голова мала лишитись у секторі 0");
    expect(st.tail_sector == 1, "хвіст мав вказувати на сектор 1");
    expect(st.next_seq == 150, "наступний кадр мав дістати номер 150");
    expect(st.valid_frames == expected_frames(), "кількість кадрів не зійшлася");
    expect(st.head_offset % (SF_HDR_SIZE + PAYLOAD_LEN + SF_CRC_SIZE) == 0,
           "голова мала стати рівно за останнім валідним кадром");

    /* 2. Свіжий, повністю стертий носій. */
    memset(g_flash, 0xFF, sizeof(g_flash));
    memset(g_valid_in_sector, 0, sizeof(g_valid_in_sector));
    if (sf_recover(&ring, &st) != 0) {
        printf("сканування не вдалося: збій читання\n");
        return 1;
    }
    report("\nСценарій 2: перший старт, носій стертий", &st);
    expect(st.empty, "кільце мало виявитись порожнім");
    expect(st.next_seq == 1, "нумерація мала початися з одиниці");
    expect(st.valid_frames == 0, "кадрів не мало бути взагалі");

    /* 3. Деградована комірка посеред сектора. Кадр не проходить CRC, і
     *    все, що лежить у цьому секторі за ним, стає недосяжним: сканер
     *    не може відрізнити наступний запис від сміття минулого циклу. */
    fill_wrapped(&w, 150, false);
    {
        const uint32_t frame_len = SF_HDR_SIZE + PAYLOAD_LEN + SF_CRC_SIZE;
        const uint32_t victim = 2 * SECTOR_SIZE + 5 * frame_len + SF_HDR_SIZE + 8;
        g_flash[victim] &= 0xF0u; /* збій запису погасив чотири біти */
        g_valid_in_sector[2] = 5;
    }
    if (sf_recover(&ring, &st) != 0) {
        printf("сканування не вдалося: збій читання\n");
        return 1;
    }
    report("\nСценарій 3: биті комірки в шостому кадрі сектора 2", &st);
    expect(st.valid_frames == expected_frames(),
           "після битого кадру хвіст сектора мав стати недосяжним");
    expect(st.head_sector == 0, "голова не мала зрушити з сектора 0");
    expect(!st.torn_tail, "голова була ціла, обірваного запису тут немає");

    printf("\n%s\n", g_failures == 0 ? "усі перевірки пройдено"
                                     : "є розбіжності, див. вище");
    return g_failures == 0 ? 0 : 1;
}
