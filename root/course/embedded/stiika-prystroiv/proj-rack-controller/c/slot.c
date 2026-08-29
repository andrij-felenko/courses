/* Сесія слота тестової стійки: flock, консоль, цикли живлення, реанімація. */
#include "slot.h"

#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/file.h>
#include <sys/select.h>
#include <sys/stat.h>
#include <termios.h>
#include <unistd.h>

#include "flash.h"

#define LOCK_DIR        "/tmp/dut-locks"
#define POWER_OFF_MS    250u /* стільки тримаємо VCC=0, щоб розрядилися ємності плати */
#define POWER_SETTLE_MS 30u  /* м'який старт ключа плюс POR мікроконтролера */
#define BOOTROM_MS      50u  /* поки фабричний завантажувач підніме SWD */
#define UART_CHUNK      512u
#define EMPTY_READS_MAX 8

/* ------------------------------------------------------------------ консоль */

static void write_all(int fd, const char *buf, size_t len)
{
    while (fd >= 0 && len > 0) {
        ssize_t n = write(fd, buf, len);
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            return; /* дзеркало — не критичний канал: лог у пам'яті лишається цілим */
        }
        buf += (size_t)n;
        len -= (size_t)n;
    }
}

static rack_status_t configure_raw(int fd, speed_t baud)
{
    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) {
        fprintf(stderr, "tcgetattr: %s\n", strerror(errno));
        return RACK_FAIL;
    }

    cfsetispeed(&tty, baud);
    cfsetospeed(&tty, baud);

    /* 8N1, приймач увімкнено, модемні лінії ігноруємо: DTR/RTS на налагоджувальній
       консолі часто заведені на скидання плати, і чекати на DCD немає сенсу. */
    tty.c_cflag = (tty.c_cflag & ~(tcflag_t)CSIZE) | CS8;
    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~(tcflag_t)(PARENB | PARODD | CSTOPB | CRTSCTS);

    /* Сирий режим: без рядкового буфера, без ехо, без сигналів від ^C у потоці. */
    tty.c_lflag &= ~(tcflag_t)(ICANON | ECHO | ECHOE | ECHONL | ISIG | IEXTEN);
    tty.c_iflag &= ~(tcflag_t)(IXON | IXOFF | IXANY | IGNBRK | BRKINT | PARMRK | ISTRIP |
                               INLCR | IGNCR | ICRNL);
    tty.c_oflag &= ~(tcflag_t)OPOST;

    /* VMIN=0, VTIME=0 — read() віддає що є й одразу повертається; чеканням
       керує select(), а не драйвер терміналу. */
    tty.c_cc[VMIN] = 0;
    tty.c_cc[VTIME] = 0;

    if (tcsetattr(fd, TCSANOW, &tty) != 0) {
        fprintf(stderr, "tcsetattr: %s\n", strerror(errno));
        return RACK_FAIL;
    }

    /* tcsetattr каже «добре», якщо застосував ХОЧ ЩОСЬ. Дешеві мости USB-UART
       мовчки підміняють нестандартну швидкість — перевіряємо, що вийшло. */
    struct termios check;
    if (tcgetattr(fd, &check) != 0 || cfgetospeed(&check) != baud) {
        fprintf(stderr, "порт не прийняв задану швидкість\n");
        return RACK_FAIL;
    }
    return RACK_OK;
}

static void append_log(rack_slot_t *s, const char *data, size_t len)
{
    const size_t cap = RACK_LOG_CAP - 1; /* один байт лишаємо під термінатор */

    if (len > cap) { /* один кусок більший за весь буфер — беремо його хвіст */
        data += len - cap;
        len = cap;
    }
    if (s->log_len + len > cap) {
        size_t drop = s->log_len + len - cap;
        memmove(s->log, s->log + drop, s->log_len - drop);
        s->log_len -= drop;
        s->scan_from = (s->scan_from > drop) ? s->scan_from - drop : 0;
        s->log_trimmed = true;
    }
    memcpy(s->log + s->log_len, data, len);
    s->log_len += len;
    s->log[s->log_len] = '\0';
}

/* Пошук по довжині, а не по strstr: у консольному потоці трапляються нульові
   байти (сміття на перехідних рівнях живлення), і рядок обірвався б на них. */
static bool log_contains(const rack_slot_t *s, const char *needle, size_t nlen)
{
    if (nlen == 0 || s->log_len < nlen || s->scan_from + nlen > s->log_len) {
        return false;
    }
    const char *hay = s->log + s->scan_from;
    size_t left = s->log_len - s->scan_from - nlen + 1;

    while (left > 0) {
        const char *p = memchr(hay, needle[0], left);
        if (p == NULL) {
            return false;
        }
        if (memcmp(p, needle, nlen) == 0) {
            return true;
        }
        left -= (size_t)(p - hay) + 1;
        hay = p + 1;
    }
    return false;
}

/* Один оберт: почекати на порт до slice_ms і забрати те, що прийшло. */
static rack_status_t pump_once(rack_slot_t *s, unsigned slice_ms)
{
    fd_set rfds;
    FD_ZERO(&rfds);
    FD_SET(s->uart_fd, &rfds);

    struct timeval tv = { .tv_sec = (time_t)(slice_ms / 1000u),
                          .tv_usec = (suseconds_t)(slice_ms % 1000u) * 1000 };

    int rc = select(s->uart_fd + 1, &rfds, NULL, NULL, &tv);
    if (rc < 0) {
        if (errno == EINTR) {
            return RACK_OK; /* сигнал: вирішувати про зупинку буде цикл вище */
        }
        fprintf(stderr, "select(uart): %s\n", strerror(errno));
        return RACK_FAIL;
    }
    if (rc == 0) {
        return RACK_OK; /* у порту тиша */
    }

    char chunk[UART_CHUNK];
    ssize_t n = read(s->uart_fd, chunk, sizeof chunk);
    if (n < 0) {
        if (errno == EAGAIN || errno == EINTR) {
            return RACK_OK;
        }
        fprintf(stderr, "read(uart): %s\n", strerror(errno));
        return RACK_FAIL;
    }
    if (n == 0) {
        /* select сказав «готовий», а даних нема. Один раз таке буває на межі
           кадру, але вперте повторення означає, що моста USB-UART від'єднали. */
        if (++s->empty_reads >= EMPTY_READS_MAX) {
            fprintf(stderr, "слот %02d: консоль зникла — від'єднали міст USB-UART?\n", s->id);
            return RACK_FAIL;
        }
        return RACK_OK;
    }

    s->empty_reads = 0;
    write_all(s->mirror_fd, chunk, (size_t)n); /* стрім наживо, ще до розбору */
    append_log(s, chunk, (size_t)n);
    return RACK_OK;
}

/* ------------------------------------------------------------- захоплення */

rack_status_t rack_slot_acquire(rack_slot_t *s, int slot_id, unsigned wait_ms)
{
    memset(s, 0, sizeof *s);
    s->id = slot_id;
    s->lock_fd = -1;
    s->uart_fd = -1;
    s->mirror_fd = -1;
    rack_power_init(&s->power);

    if (mkdir(LOCK_DIR, 0777) != 0 && errno != EEXIST) {
        fprintf(stderr, "не створюється %s: %s\n", LOCK_DIR, strerror(errno));
        return RACK_FAIL;
    }

    char path[64];
    snprintf(path, sizeof path, LOCK_DIR "/slot_%02d.lock", slot_id);

    s->lock_fd = open(path, O_CREAT | O_RDWR | O_CLOEXEC, 0666);
    if (s->lock_fd < 0) {
        fprintf(stderr, "не відкривається %s: %s\n", path, strerror(errno));
        return RACK_FAIL;
    }

    uint64_t deadline = rack_now_ms() + wait_ms;
    while (flock(s->lock_fd, LOCK_EX | LOCK_NB) != 0) {
        if (errno != EWOULDBLOCK) {
            fprintf(stderr, "flock(%s): %s\n", path, strerror(errno));
            close(s->lock_fd);
            s->lock_fd = -1;
            return RACK_FAIL;
        }
        if (rack_stop || rack_now_ms() >= deadline) {
            close(s->lock_fd);
            s->lock_fd = -1;
            return RACK_BUSY;
        }
        rack_sleep_ms(100);
    }

    /* Слід для людини, яка прийде дивитися, хто ж тримає слот. Дані суто
       діагностичні: право володіння дає flock, а не вміст файлу. */
    if (ftruncate(s->lock_fd, 0) == 0) {
        dprintf(s->lock_fd, "pid=%ld\n", (long)getpid());
    }
    return RACK_OK;
}

rack_status_t rack_slot_open_hw(rack_slot_t *s, int mirror_fd)
{
    s->mirror_fd = mirror_fd;

    /* КАНОНІЧНИЙ ПОРЯДОК. Спершу відкриваємо й налаштовуємо консоль — на це йде
       від 15 до 60 мс системних викликів до драйвера USB. Якби живлення вже було
       подане, ці десятки мілісекунд з'їли б початок банера завантажувача. */
    char path[64];
    snprintf(path, sizeof path, "/dev/dut-slot-%02d-uart", s->id);

    s->uart_fd = open(path, O_RDWR | O_NOCTTY | O_NONBLOCK | O_CLOEXEC);
    if (s->uart_fd < 0) {
        fprintf(stderr, "слот %02d: не відкривається %s: %s\n", s->id, path, strerror(errno));
        return RACK_FAIL;
    }
    if (configure_raw(s->uart_fd, B115200) != RACK_OK) {
        close(s->uart_fd);
        s->uart_fd = -1;
        return RACK_FAIL;
    }
    /* Викидаємо все, що осіло в черзі драйвера від попереднього прогону. */
    tcflush(s->uart_fd, TCIFLUSH);

    /* І лише тепер беремо силові лінії — запит уже кладе їх у нуль. */
    if (rack_power_open(&s->power, s->id) != RACK_OK) {
        close(s->uart_fd);
        s->uart_fd = -1;
        return RACK_FAIL;
    }
    return RACK_OK;
}

/* --------------------------------------------------------------- операції */

rack_status_t rack_slot_power_cycle(rack_slot_t *s, unsigned off_ms)
{
    if (rack_power_vcc(&s->power, false) != RACK_OK) {
        return RACK_FAIL;
    }
    rack_sleep_ms(off_ms);

    /* Поки плата знеструмлена, у черзі могло осісти сміття з перехідних рівнів
       на лінії RX. Чистимо саме тут — за мить до появи справжніх байтів. */
    tcflush(s->uart_fd, TCIFLUSH);

    if (rack_power_vcc(&s->power, true) != RACK_OK) {
        return RACK_FAIL;
    }
    /* Ніякої паузи «щоб плата встигла»: читання починається негайно, інакше
       ми знову втрачаємо перші рядки. */
    return RACK_OK;
}

rack_status_t rack_slot_expect(rack_slot_t *s, const char *pattern, unsigned timeout_ms)
{
    if (s->uart_fd < 0 || pattern == NULL) {
        return RACK_FAIL;
    }
    size_t nlen = strlen(pattern);
    if (nlen == 0) {
        fprintf(stderr, "порожній шаблон очікування\n");
        return RACK_FAIL;
    }

    /* Шукаємо тільки в тому, що прийде далі, плюс хвіст завдовжки з шаблон:
       так збіг не загубиться на межі кусків, а старе не дасть хибного попадання. */
    s->scan_from = (s->log_len >= nlen) ? s->log_len - (nlen - 1) : 0;

    uint64_t deadline = rack_now_ms() + timeout_ms;
    for (;;) {
        if (log_contains(s, pattern, nlen)) {
            return RACK_OK;
        }
        if (rack_stop) {
            return RACK_FAIL;
        }

        uint64_t now = rack_now_ms();
        if (now >= deadline) {
            return RACK_TIMEOUT;
        }

        unsigned slice = (unsigned)(deadline - now);
        if (slice > 50u) {
            slice = 50u; /* дрібний квант, щоб сигнал зупинки не чекав до кінця таймауту */
        }
        s->scan_from = (s->log_len >= nlen) ? s->log_len - (nlen - 1) : 0;
        if (pump_once(s, slice) != RACK_OK) {
            return RACK_FAIL;
        }
    }
}

rack_status_t rack_slot_drain(rack_slot_t *s, unsigned duration_ms)
{
    uint64_t deadline = rack_now_ms() + duration_ms;
    while (!rack_stop) {
        uint64_t now = rack_now_ms();
        if (now >= deadline) {
            return RACK_OK;
        }
        unsigned slice = (unsigned)(deadline - now);
        if (slice > 50u) {
            slice = 50u;
        }
        if (pump_once(s, slice) != RACK_OK) {
            return RACK_FAIL;
        }
    }
    return RACK_OK;
}

rack_status_t rack_slot_boot(rack_slot_t *s, const char *banner, unsigned timeout_ms)
{
    if (rack_slot_power_cycle(s, POWER_OFF_MS) != RACK_OK) {
        return RACK_FAIL;
    }
    return rack_slot_expect(s, banner, timeout_ms);
}

rack_status_t rack_slot_flash(rack_slot_t *s, const char *image_path)
{
    /* Прошиваємо зі свіжого старту: плата, що зависла в перериванні або тримає
       шину SWD, часто не дає налагоджувачу під'єднатися. */
    if (rack_slot_power_cycle(s, POWER_OFF_MS) != RACK_OK) {
        return RACK_FAIL;
    }
    rack_sleep_ms(POWER_SETTLE_MS);

    return rack_flash_program(s->id, image_path);
}

rack_status_t rack_slot_unbrick(rack_slot_t *s)
{
    /* 1. Зняти живлення: BOOT0 читається лише при старті. */
    if (rack_power_vcc(&s->power, false) != RACK_OK) {
        return RACK_FAIL;
    }
    rack_sleep_ms(POWER_OFF_MS);

    /* 2. Підняти BOOT0. */
    if (rack_power_boot0(&s->power, true) != RACK_OK) {
        return RACK_FAIL;
    }

    /* 3. Подати живлення — стартує фабричний завантажувач із ROM, а не збійний
       код користувача, тож ані петля сторожового таймера, ані переконфігурований
       SWD більше не заважають. */
    tcflush(s->uart_fd, TCIFLUSH);
    if (rack_power_vcc(&s->power, true) != RACK_OK) {
        (void)rack_power_boot0(&s->power, false);
        return RACK_FAIL;
    }
    rack_sleep_ms(POWER_SETTLE_MS + BOOTROM_MS);

    /* 4. Стерти пошкоджену прошивку. */
    rack_status_t st = rack_flash_mass_erase(s->id);

    /* 5. BOOT0 назад у нуль — обов'язково, навіть якщо стирання провалилося:
       інакше слот назавжди лишиться в завантажувачі й наступний прогін
       не зрозуміє, чому плата мовчить. */
    if (rack_power_boot0(&s->power, false) != RACK_OK) {
        st = RACK_FAIL;
    }

    /* 6. Холодний рестарт: після mass_erase і зняття RDP потрібен саме POR. */
    if (rack_slot_power_cycle(s, POWER_OFF_MS) != RACK_OK) {
        st = RACK_FAIL;
    }
    return st;
}

void rack_slot_release(rack_slot_t *s)
{
    /* Слот віддаємо знеструмленим: наступний прогін почне з чистого POR. */
    rack_power_close(&s->power);

    if (s->uart_fd >= 0) {
        close(s->uart_fd);
        s->uart_fd = -1;
    }
    if (s->lock_fd >= 0) {
        /* flock зняло б і саме закриття — знімаємо явно, щоб порядок був видимий.
           Саме тому слот не зависає і після SIGKILL: дескриптори закриває ядро. */
        flock(s->lock_fd, LOCK_UN);
        close(s->lock_fd);
        s->lock_fd = -1;
    }
}
