/* Емуляція NOR Flash на хості й сценарії відмов.
 *
 * Модель кристала тримає дві фізичні властивості, на яких і стоїть увесь
 * формат: запис уміє лише гасити біти (побайтове AND), а стирання піднімає
 * весь сектор у 0xFF. Плюс керовані відмови — так перевіряється поведінка,
 * якої на столі не дочекаєшся: обрив живлення посеред кадру й сектор, що
 * перестав стиратися.
 *
 * Збірка: cc -std=c11 log_format.c flash_logger.c isr_stage.c test_recovery.c
 * (logger_rtos.c сюди не входить — він потребує FreeRTOS). */

#include <stdio.h>
#include <string.h>

#include "flash_logger.h"
#include "isr_stage.h"

#define FLASH_TOTAL (FLASH_SECTOR_SIZE * FLASH_SECTOR_COUNT)

typedef struct {
    uint8_t  mem[FLASH_TOTAL];
    uint32_t erase_fail_mask; /* сектори, які «розучилися» стиратися */
    uint32_t write_fail_mask; /* сектори, які відмовляють на записі */
    uint32_t erase_count[FLASH_SECTOR_COUNT];
} sim_flash_t;

static sim_flash_t g_sim;
static int g_failures;

/* ---------- модель кристала ---------- */

static bool sim_read(uint32_t addr, uint8_t *buf, size_t len, void *ctx)
{
    sim_flash_t *s = (sim_flash_t *)ctx;
    if (addr + len > FLASH_TOTAL) {
        return false;
    }
    memcpy(buf, &s->mem[addr], len);
    return true;
}

static bool sim_write(uint32_t addr, const uint8_t *buf, size_t len, void *ctx)
{
    sim_flash_t *s = (sim_flash_t *)ctx;
    if (addr + len > FLASH_TOTAL) {
        return false;
    }
    if ((s->write_fail_mask >> (addr / FLASH_SECTOR_SIZE)) & 1u) {
        return false;
    }
    for (size_t i = 0; i < len; ++i) {
        s->mem[addr + i] &= buf[i]; /* одиницю в нуль можна, назад — ні */
    }
    return true;
}

static bool sim_erase(uint32_t sector_addr, void *ctx)
{
    sim_flash_t *s = (sim_flash_t *)ctx;
    const uint32_t idx = sector_addr / FLASH_SECTOR_SIZE;
    if (idx >= FLASH_SECTOR_COUNT) {
        return false;
    }
    if ((s->erase_fail_mask >> idx) & 1u) {
        return false;
    }
    memset(&s->mem[idx * FLASH_SECTOR_SIZE], 0xFF, FLASH_SECTOR_SIZE);
    s->erase_count[idx] += 1;
    return true;
}

static void sim_reset(void)
{
    memset(&g_sim, 0, sizeof(g_sim));
    memset(g_sim.mem, 0xFF, sizeof(g_sim.mem));
}

static flash_hal_t sim_hal(void)
{
    flash_hal_t hal;
    hal.read = sim_read;
    hal.write = sim_write;
    hal.erase_sector = sim_erase;
    hal.ctx = &g_sim;
    return hal;
}

/* ---------- допоміжне ---------- */

static void check(bool ok, const char *what)
{
    printf("%s %s\n", ok ? "[ok]  " : "[ЗБІЙ]", what);
    if (!ok) {
        g_failures += 1;
    }
}

/* Скільки в усьому кристалі валідних кадрів із таким токеном; у out_payload
 * кладе перші 4 байти навантаження останнього знайденого. */
static uint32_t count_token(uint32_t token, uint32_t *out_payload)
{
    uint32_t found = 0;

    for (uint32_t sec = 0; sec < FLASH_SECTOR_COUNT; ++sec) {
        const uint8_t *base = &g_sim.mem[sec * FLASH_SECTOR_SIZE];
        sector_header_t sh;
        log_decode_sector_header(base, &sh);
        if (sh.magic != LOG_SECTOR_MAGIC) {
            continue;
        }

        uint32_t off = SECTOR_HEADER_SIZE;
        while (off + RECORD_HEADER_SIZE + RECORD_CRC_SIZE <= FLASH_SECTOR_SIZE) {
            record_header_t rh;
            const uint8_t *payload = NULL;
            uint8_t payload_len = 0;
            if (!log_decode_record(base + off, FLASH_SECTOR_SIZE - off, &rh, &payload, &payload_len)) {
                break;
            }
            if (rh.token_id == token) {
                found += 1;
                if (out_payload != NULL && payload_len >= 4) {
                    *out_payload = log_get_u32(payload);
                }
            }
            off += rh.length;
        }
    }
    return found;
}

static uint32_t sector_state_of(uint32_t idx)
{
    sector_header_t sh;
    log_decode_sector_header(&g_sim.mem[idx * FLASH_SECTOR_SIZE], &sh);
    return sh.state;
}

/* Пише кадри, доки логер не перейде в наступний сектор. */
static uint32_t fill_until_rotation(flash_logger_t *l, uint32_t *ts)
{
    const uint32_t start = l->active_sector;
    uint32_t written = 0;

    while (l->active_sector == start) {
        uint8_t payload[4];
        log_put_u32(payload, *ts);
        if (flash_logger_write(l, LOG_LEVEL_INFO, 7, *ts, 0x2000u, payload, sizeof(payload)) != LOG_OK) {
            break;
        }
        *ts += 1;
        written += 1;
    }
    return written;
}

/* ---------- сценарії ---------- */

static void scenario_fresh_start(void)
{
    printf("\n1. Чистий кристал: перший старт і перші записи\n");
    sim_reset();

    flash_hal_t hal = sim_hal();
    flash_logger_t logger;
    check(flash_logger_init(&logger, &hal, 0) == LOG_OK, "init на чистому кристалі");
    check(logger.active_sector == 0, "активний сектор — нульовий");
    check(logger.write_offset == SECTOR_HEADER_SIZE, "покажчик стоїть одразу за заголовком");
    check(sector_state_of(0) == SECTOR_STATE_ACTIVE, "сектор 0 позначено ACTIVE");

    uint32_t v = 120;
    uint8_t payload[4];
    log_put_u32(payload, v);
    check(flash_logger_write(&logger, LOG_LEVEL_INFO, 1, 1000, 0x1001u, payload, 4) == LOG_OK,
          "запис INFO");
    log_put_u32(payload, 404);
    check(flash_logger_write(&logger, LOG_LEVEL_WARN, 2, 1050, 0x1002u, payload, 4) == LOG_OK,
          "запис WARN");
    check(logger.write_offset == SECTOR_HEADER_SIZE + 2 * (RECORD_HEADER_SIZE + 4 + RECORD_CRC_SIZE),
          "покажчик просунувся на два кадри");
    check(count_token(0x1001u, NULL) == 1 && count_token(0x1002u, NULL) == 1,
          "обидва кадри читаються з валідною CRC");
}

static void scenario_power_cut(void)
{
    printf("\n2. Знеструмлення посеред кадру й відновлення на старті\n");
    sim_reset();

    flash_hal_t hal = sim_hal();
    flash_logger_t logger;
    (void)flash_logger_init(&logger, &hal, 0);

    uint8_t payload[4];
    log_put_u32(payload, 1);
    (void)flash_logger_write(&logger, LOG_LEVEL_INFO, 1, 1000, 0x1001u, payload, 4);
    log_put_u32(payload, 2);
    (void)flash_logger_write(&logger, LOG_LEVEL_WARN, 2, 1050, 0x1002u, payload, 4);

    const uint32_t cut_offset = logger.write_offset;

    /* Живлення зникає посеред Page Program: у Flash лягли перші 6 байтів
     * третього кадру — магічне число, довжина, рівень, модуль і початок мітки
     * часу. Ні тіла, ні CRC немає. Відтворюємо цей стан прямим записом. */
    record_header_t doomed;
    doomed.length = 0;
    doomed.level = LOG_LEVEL_ERROR;
    doomed.module_id = 3;
    doomed.timestamp_ms = 1100;
    doomed.token_id = 0x1003u;

    uint8_t frame[RECORD_MAX_SIZE];
    log_put_u32(payload, 3);
    const size_t total = log_encode_record(&doomed, payload, 4, frame, sizeof(frame));
    check(total == RECORD_HEADER_SIZE + 4 + RECORD_CRC_SIZE, "кадр зібрано");
    check(sim_write(cut_offset, frame, 6, &g_sim), "у Flash лягли лише 6 байтів кадру");

    /* Скидання мікроконтролера. */
    flash_logger_t rebooted;
    check(flash_logger_init(&rebooted, &hal, 0) == LOG_OK, "init після аварійного скидання");
    check(rebooted.active_sector == 0, "активним лишився той самий сектор");
    check(rebooted.write_offset == cut_offset, "покажчик став рівно перед битим кадром");
    check(count_token(0x1003u, NULL) == 0, "недописаний кадр не зарахований як валідний");

    /* Поверх обірваних байтів валідний кадр не ляже: NOR уміє лише гасити
     * біти. Логер побачить це на звірянні й піде в наступний сектор. */
    log_put_u32(payload, 4);
    check(flash_logger_write(&rebooted, LOG_LEVEL_INFO, 1, 1200, 0x1004u, payload, 4) == LOG_OK,
          "наступний запис пройшов");
    check(rebooted.active_sector == 1, "сектор із бітим хвостом закрито, запис пішов у наступний");
    check(sector_state_of(0) == SECTOR_STATE_FULL, "сектор 0 позначено FULL");
    check(count_token(0x1004u, NULL) == 1, "новий кадр читається");
}

static void scenario_rotation(void)
{
    printf("\n3. Заповнення сектора й ротація\n");
    sim_reset();

    flash_hal_t hal = sim_hal();
    flash_logger_t logger;
    (void)flash_logger_init(&logger, &hal, 0);

    uint32_t ts = 1;
    const uint32_t written = fill_until_rotation(&logger, &ts);
    const uint32_t record_size = RECORD_HEADER_SIZE + 4 + RECORD_CRC_SIZE;

    /* Останній із порахованих записів уже впав у новий сектор — саме він
     * і викликав ротацію, не помістившись у хвіст старого. */
    check(written == (FLASH_SECTOR_SIZE - SECTOR_HEADER_SIZE) / record_size + 1,
          "сектор набито до останнього кадру, що влазить");
    check(logger.active_sector == 1, "голова перейшла в сектор 1");
    check(sector_state_of(0) == SECTOR_STATE_FULL, "старий сектор закрито як FULL");
    check(sector_state_of(1) == SECTOR_STATE_ACTIVE, "новий сектор відкрито як ACTIVE");

    sector_header_t h0;
    sector_header_t h1;
    log_decode_sector_header(&g_sim.mem[0], &h0);
    log_decode_sector_header(&g_sim.mem[FLASH_SECTOR_SIZE], &h1);
    check(h1.seq_num == h0.seq_num + 1, "номер послідовності зріс на одиницю");
    check(h1.erase_count == 1, "лічильник стирань нового сектора став одиницею");
}

static void scenario_overrun(void)
{
    printf("\n4. Повний обіг кільця: хвіст витісняється\n");
    sim_reset();

    flash_hal_t hal = sim_hal();
    flash_logger_t logger;
    (void)flash_logger_init(&logger, &hal, 0);

    uint32_t ts = 1;
    check(logger.tail_sector == 0, "спочатку хвіст стоїть на нульовому секторі");

    /* Дев'ять ротацій — на один більше, ніж секторів у кільці. */
    for (uint32_t i = 0; i < FLASH_SECTOR_COUNT + 1; ++i) {
        (void)fill_until_rotation(&logger, &ts);
    }

    check(logger.tail_sector == (logger.active_sector + 1) % FLASH_SECTOR_COUNT,
          "хвіст стоїть одразу за головою — найстаріші дані затерто");
    check(logger.seq_num >= FLASH_SECTOR_COUNT, "номери послідовності монотонно зростали");

    /* Перезапуск: голову й хвіст логер мусить знайти самотужки. */
    const uint32_t head = logger.active_sector;
    const uint32_t tail = logger.tail_sector;
    flash_logger_t rebooted;
    (void)flash_logger_init(&rebooted, &hal, 0);
    check(rebooted.active_sector == head, "після скидання голова знайдена там само");
    check(rebooted.tail_sector == tail, "після скидання хвіст знайдений там само");
}

static void scenario_bad_sector(void)
{
    printf("\n5. Сектор перестав стиратися\n");
    sim_reset();
    g_sim.erase_fail_mask = 1u << 1; /* сектор 1 деградував */

    flash_hal_t hal = sim_hal();
    flash_logger_t logger;
    (void)flash_logger_init(&logger, &hal, 0);

    uint32_t ts = 1;
    (void)fill_until_rotation(&logger, &ts);

    check(logger.active_sector == 2, "дефектний сектор обійдено, голова стала в сектор 2");
    check((logger.bad_mask & (1u << 1)) != 0, "сектор 1 занесено в маску дефектних");

    uint32_t reported = 0xFFFFFFFFu;
    check(count_token(LOG_TOKEN_BAD_SECTOR, &reported) == 1,
          "у журналі з'явився службовий запис про дефект");
    check(reported == 1, "у навантаженні службового запису — номер битого сектора");

    /* Кільце працює далі, просто на сектор коротше. */
    (void)fill_until_rotation(&logger, &ts);
    check(logger.active_sector == 3, "після дефектного сектора ротація йде своїм ходом");
}

static void scenario_upload(void)
{
    printf("\n6. Вивантаження пачки й підтвердження від сервера\n");
    sim_reset();

    flash_hal_t hal = sim_hal();
    flash_logger_t logger;
    (void)flash_logger_init(&logger, &hal, 0);

    uint32_t ts = 1;
    (void)fill_until_rotation(&logger, &ts);

    static uint8_t batch[FLASH_SECTOR_SIZE];
    uint32_t sector = 0;
    size_t len = 0;
    uint32_t records = 0;

    check(flash_logger_read_batch(&logger, batch, sizeof(batch), &sector, &len, &records) == LOG_OK,
          "пачка вичитана");
    check(sector == 0, "віддано найстаріший заповнений сектор");
    check(records == (FLASH_SECTOR_SIZE - SECTOR_HEADER_SIZE) / (RECORD_HEADER_SIZE + 4 + RECORD_CRC_SIZE),
          "у пачці всі кадри сектора");

    /* Перевіряємо, що віддане справді розбирається — саме це робитиме сервер. */
    uint32_t parsed = 0;
    size_t off = 0;
    while (off < len) {
        record_header_t rh;
        if (!log_decode_record(batch + off, len - off, &rh, NULL, NULL)) {
            break;
        }
        off += rh.length;
        parsed += 1;
    }
    check(parsed == records, "усі кадри пачки проходять перевірку CRC");

    check(flash_logger_commit_tail(&logger, sector) == LOG_OK, "сервер підтвердив пачку");
    check(sector_state_of(0) == SECTOR_STATE_DIRTY, "сектор позначено DIRTY");
    check(logger.tail_sector == 1, "хвіст просунувся до наступного сектора");

    check(flash_logger_read_batch(&logger, batch, sizeof(batch), &sector, &len, &records) == LOG_ERR_EMPTY,
          "більше заповнених секторів немає — активний не віддається");
}

static void scenario_isr_queue(void)
{
    printf("\n7. Черга переривань і фонове перенесення у Flash\n");
    sim_reset();

    flash_hal_t hal = sim_hal();
    flash_logger_t logger;
    (void)flash_logger_init(&logger, &hal, 0);

    static isr_stage_t stage;
    isr_stage_init(&stage);

    for (uint16_t i = 0; i < 3; ++i) {
        isr_frame_t frame;
        frame.level = LOG_LEVEL_DEBUG;
        frame.module_id = 9;
        frame.arg16 = (uint16_t)(100 + i);
        frame.timestamp_ms = 2000u + i;
        frame.token_id = 0x3001u;
        check(isr_stage_push(&stage, &frame), "кадр покладено в чергу з переривання");
    }

    check(isr_stage_drain(&stage, &logger) == 3, "фонова задача перенесла всі три кадри");
    check(count_token(0x3001u, NULL) == 3, "кадри лежать у Flash");

    /* Переповнення: черга тримає ISR_STAGE_CAPACITY кадрів, решта гине. */
    for (uint32_t i = 0; i < ISR_STAGE_CAPACITY + 8u; ++i) {
        isr_frame_t frame;
        frame.level = LOG_LEVEL_TRACE;
        frame.module_id = 9;
        frame.arg16 = (uint16_t)i;
        frame.timestamp_ms = 3000u + i;
        frame.token_id = 0x3002u;
        (void)isr_stage_push(&stage, &frame);
    }

    check(isr_stage_drain(&stage, &logger) == ISR_STAGE_CAPACITY,
          "перенесено рівно стільки, скільки вмістила черга");

    uint32_t dropped = 0;
    check(count_token(LOG_TOKEN_ISR_DROPS, &dropped) == 1, "втрату кадрів визнано записом WARN");
    check(dropped == 8, "у записі стоїть точна кількість утрачених кадрів");
}

int main(void)
{
    scenario_fresh_start();
    scenario_power_cut();
    scenario_rotation();
    scenario_overrun();
    scenario_bad_sector();
    scenario_upload();
    scenario_isr_queue();

    printf("\nЗбоїв: %d\n", g_failures);
    return g_failures == 0 ? 0 : 1;
}
