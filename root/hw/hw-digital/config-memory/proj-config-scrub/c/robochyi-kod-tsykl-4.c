// Лічильники для телеметрії: скільки й яких збоїв набігло.
typedef struct {
    uint32_t frames_scanned;   // скільки кадрів перевірено
    uint32_t sbe_fixed;        // виправлено однобітових
    uint32_t hard_fixed;       // перезалито з еталона
    uint32_t failed;           // не вдалося виправити — критично
    uint32_t full_passes;      // скільки разів обійшли ВСЮ пам'ять
} scrub_stats_t;

static scrub_stats_t stats;

extern void report_uncorrectable(uint32_t frame); // тривога назовні (журнал, прапор, скидання)
extern void yield_to_logic(void);                 // віддати трохи часу корисній роботі

// Головний фоновий цикл скрабера. Крутиться, доки живий пристрій.
void scrubber_run(void)
{
    uint32_t f = 0;
    uint32_t last_crc = cfg_global_crc();

    for (;;) {
        scrub_result_t r = scrub_one_frame(f);
        stats.frames_scanned++;

        switch (r) {
            case SCRUB_CLEAN:      break;
            case SCRUB_FIXED_SBE:  stats.sbe_fixed++;  break;
            case SCRUB_FIXED_HARD: stats.hard_fixed++; break;
            case SCRUB_FAILED:
                stats.failed++;
                report_uncorrectable(f);   // самі не впорались — хай вирішує система
                break;
        }

        if (++f >= FRAME_COUNT) {           // обійшли всю память — коло замкнулось
            f = 0;
            stats.full_passes++;

            // Дешева глобальна перевірка раз на коло: CRC змінився попри наші виправлення?
            // Значить, десь прослизнув збій, якого покадровий ECC не помітив, — варто
            // на наступному колі бути особливо уважним (або форсувати перезаливку).
            uint32_t crc = cfg_global_crc();
            (void)last_crc;                 // (порівняння/реакція — за політикою пристрою)
            last_crc = crc;
        }

        yield_to_logic();                   // не монополізуємо порт: даємо жити логіці
    }
}
