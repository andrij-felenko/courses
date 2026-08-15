# ⚙️ Проба монтування: програма, що міряє контракт замість вірити довідці

Довідка `nfs(5)` каже, що атрибути каталогу клієнт тримає в кеші від 30 до 60 секунд, а `mount.cifs` — що під орендою застарілості не буває взагалі. Обидва твердження правдиві щодо клієнта і майже нічого не кажуть про **ваше** монтування: між вами й довідкою стоять версія протоколу, опції експорту на сервері, реалізація серверної сторони (Linux `nfsd`, FreeBSD, Windows, коробка NAS із власною прошивкою) та кілька десятків важелів у `fstab`. Ця програма з'ясовує, що з усього цього вийшло насправді: шість дослідів, кожен повертає або число в секундах, або чітке «так/ні».

## Шість питань, на які потрібні числа

Кожне питання ловить одне конкретне припущення — з тих, які програми роблять мовчки, ніде не записують і від яких ламаються, щойно припущення не справджується.

1. **За скільки секунд** файл, створений на машині A, з'являється в `ls` на машині B — і чи однаковий цей час для `stat()` по імені та для `readdir()` цілого каталогу.
2. **Чи видно дописане**, поки письменник тримає файл відкритим, і скільки триває застарілість — окремо для розміру файлу й окремо для самих байтів.
3. **Куди насправді йдуть байти** при записі: скільки часу з'їдає `write()`, скільки `fsync()`, а скільки `close()`.
4. **Чи виключають одне одного замки** між машинами — `flock` проти `flock`, `fcntl` проти `fcntl` і, найцікавіше, `flock` проти `fcntl`.
5. **Що лишається після `unlink`** файлу, який тримають відкритим, — і що бачить у каталозі друга машина.
6. **Чи атомарне створення з `O_EXCL`**, коли дві машини змагаються за одне ім'я.

## Ідея: жодного спільного годинника

Перше, у що впирається будь-яка спроба поміряти таке, — час. Спокуслива схема виглядає так: машина A створює файл і записує в звіт свій `CLOCK_REALTIME`, машина B помічає появу файлу й записує свій, різниця й буде відповіддю. Схема не працює, і не через дрібну неточність. Годинники двох машин розходяться на десятки мілісекунд навіть під NTP, а без нього — на секунди й хвилини; на віртуальних машинах після міграції або призупинки стрибок буває миттєвим. Відповіді ж, які ми шукаємо, лежать у діапазоні від нуля до хвилини. Похибка того самого порядку, що й вимірюване, перетворює число на прикрасу.

Виходу з цього два, і другий кращий. Можна синхронізувати годинники як слід — але тоді проба міряє якість вашого NTP не менше, ніж контракт монтування. Або можна побудувати дослід так, щоб **обидва відліки часу бралися на одному годиннику**. Тоді розходження просто нікуди не входить: воно скорочується разом із самим поняттям «час на іншій машині».

Це вимагає єдиної речі: машина B мусить знати, **коли саме** A закінчила свою дію, — і знати це не через спільний каталог, бо саме спільний каталог ми й досліджуємо. Отже, поруч із файловою системою потрібен другий канал: пряме TCP-з'єднання між двома примірниками програми, яким летять команди й підтвердження, і ніколи — самі дані. Читач посилає команду «створи файл», чекає відповіді «створив», у мить її отримання бере `CLOCK_MONOTONIC` — це нуль. Далі опитує каталог, і коли файл нарешті видно, бере `CLOCK_MONOTONIC` ще раз. Різниця цих двох відліків і є результатом.

Годинник машини A в обчисленні не бере участі взагалі. Монотонний годинник до того ж не стрибає від переведення часу, від NTP-корекції й від переходу на літній час — він рахує від довільної точки в минулому й лише вперед, тому для вимірювання **відрізків** годиться, а для позначення моменту — ні (звідки він береться й чим відрізняється від інших джерел часу — [час у ядрі](book:unix-linux/kernel-timekeeping)).

![Дві панелі. Верхня: три прямокутники — машина A «письменник» ліворуч, «сервер, спільний каталог» посередині, машина B «читач» праворуч; стрілка від A до сервера підписана «створює файл», стрілка від сервера до B — «читає каталог»; знизу окремою зеленою пунктирною лінією з двома стрілками показано керувальний канал, що з'єднує A і B напряму в обхід сервера, з підписом «пряме TCP-з'єднання, тут ідуть команди, а не дані». Нижня панель: горизонтальна вісь часу читача, синя позначка t нуль у місці, де прийшла відповідь «файл створено», далі низка дрібних рисок із дужкою й підписом «stat кожні 50 мс — усе ще ENOENT», зелена позначка t один у місці, де stat повернув нуль, і під віссю двонаправлена стрілка від t нуль до t один із підписом «дельта — єдине число, що є результатом проби», а нижче зауваження, що годинник машини A в обчисленні не бере участі](/reference/unix-linux/files/network-filesystems/img/one-clock.svg)

*Керувальний канал навмисно не проходить через те, що ми міряємо. Обидва відліки — на годиннику читача, тож розходження годинників у результат не входить.*

Похибка в такій схемі лишається одна: файл на сервері з'явився приблизно на пів оберту керувального каналу раніше, ніж підтвердження дійшло до читача. Знак похибки відомий — проба **недооцінює** затримку, — а величина в локальній мережі становить десяті частки мілісекунди проти секунд, які ми міряємо.

Звідси випливає й розподіл ролей. Письменник не знає нічого про самі досліди: він — рука, що виконує елементарні дії над файлами й доповідає результат. Уся логіка живе в читачі. Так додати сьому пробу означає дописати одну функцію на одному боці, а не змінювати протокол.

## Каркас: канал, секундомір і віддалена рука

Далі — один файл `mountprobe.c`, поданий частинами в тому порядку, у якому вони в ньому стоять. Збирається без жодних залежностей.

:::tabs
```c
/* mountprobe.c — вимірює справжній контракт конкретного монтування.
 *   cc -O2 -Wall -Wextra -o mountprobe mountprobe.c
 * на машині A:  ./mountprobe writer /mnt/share 7411
 * на машині B:  ./mountprobe reader /mnt/share hostA 7411
 * шляхи до спільного каталогу на двох машинах МОЖУТЬ бути різні —
 * кожна сторона отримує свій.                                        */
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/file.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

static int  ctl = -1;            /* керувальний сокет */
static char share[PATH_MAX];     /* спільний каталог, як він видний ТУТ */

static double mono(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double) ts.tv_sec + (double) ts.tv_nsec * 1e-9;
}

static void nap_ms(long ms)
{
    struct timespec t = { ms / 1000, (ms % 1000) * 1000000L };
    nanosleep(&t, NULL);
}

/* один статичний буфер — не вживати двічі в одному виразі */
static const char *at(const char *name)
{
    static char p[PATH_MAX];
    snprintf(p, sizeof p, "%s/%s", share, name);
    return p;
}

static const char *secs(double v)      /* -1 означає «не дочекалися» */
{
    static char b[32];
    if (v < 0) snprintf(b, sizeof b, "  > 180");
    else       snprintf(b, sizeof b, "%7.2f", v);
    return b;
}
```
```cpp
// mountprobe.cpp — вимірює справжній контракт конкретного монтування (C++20/C++23)
#include <array>
#include <cerrno>
#include <chrono>
#include <filesystem>
#include <format>
#include <iostream>
#include <memory>
#include <span>
#include <string>
#include <string_view>
#include <thread>
#include <vector>

#include <dirent.h>
#include <fcntl.h>
#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/file.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <unistd.h>

namespace fs = std::filesystem;

static int ctl = -1;
static fs::path share_dir;

static double mono() {
    auto now = std::chrono::steady_clock::now();
    auto duration = now.time_since_epoch();
    return std::chrono::duration<double>(duration).count();
}

static void nap_ms(long ms) {
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

static fs::path at(std::string_view name) {
    return share_dir / name;
}

static std::string secs(double v) {
    if (v < 0) return "  > 180";
    return std::format("{:7.2f}", v);
}
```
:::

Керувальний канал — рядки, розділені переводом. Читання по одному байту виглядає марнотратним, але тут воно не коштує нічого (десятки повідомлень за весь прогін), зате знімає цілий клас помилок: жоден буфер не переживає межу між повідомленнями, тож відповідь на попередню команду ніяк не може потрапити в наступну.

:::tabs
```c
static int send_line(const char *s)
{
    char   buf[2048];
    size_t len = strlen(s), off = 0;

    if (len + 1 > sizeof buf) return -1;
    memcpy(buf, s, len);
    buf[len++] = '\n';
    while (off < len) {
        ssize_t n = write(ctl, buf + off, len - off);
        if (n < 0) { if (errno == EINTR) continue; return -1; }
        off += (size_t) n;
    }
    return 0;
}

static int recv_line(char *out, size_t cap)
{
    size_t i = 0;
    for (;;) {
        char    c;
        ssize_t n = read(ctl, &c, 1);
        if (n < 0) { if (errno == EINTR) continue; return -1; }
        if (n == 0) return -1;                       /* другий бік пішов */
        if (c == '\n') { out[i] = '\0'; return 0; }
        if (i + 1 < cap) out[i++] = c;
    }
}

static int tcp_accept(const char *port)
{
    struct addrinfo hints, *res = NULL;
    int srv = -1, cli = -1, on = 1;

    memset(&hints, 0, sizeof hints);
    hints.ai_family   = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags    = AI_PASSIVE;
    if (getaddrinfo(NULL, port, &hints, &res) != 0) return -1;

    srv = socket(res->ai_family, res->ai_socktype, 0);
    if (srv >= 0) {
        setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &on, sizeof on);
        if (bind(srv, res->ai_addr, res->ai_addrlen) == 0 && listen(srv, 1) == 0)
            cli = accept(srv, NULL, NULL);
        close(srv);
    }
    freeaddrinfo(res);
    /* без TCP_NODELAY алгоритм Нейгла міг би підмішати в наші відліки
       десятки мілісекунд затримки, яких у файловій системі немає  */
    if (cli >= 0) setsockopt(cli, IPPROTO_TCP, TCP_NODELAY, &on, sizeof on);
    return cli;
}

static int tcp_connect(const char *host, const char *port)
{
    struct addrinfo hints, *res = NULL, *ai;
    int s = -1, on = 1;

    memset(&hints, 0, sizeof hints);
    hints.ai_family   = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    if (getaddrinfo(host, port, &hints, &res) != 0) return -1;

    for (ai = res; ai; ai = ai->ai_next) {
        s = socket(ai->ai_family, ai->ai_socktype, 0);
        if (s < 0) continue;
        if (connect(s, ai->ai_addr, ai->ai_addrlen) == 0) break;
        close(s);
        s = -1;
    }
    freeaddrinfo(res);
    if (s >= 0) setsockopt(s, IPPROTO_TCP, TCP_NODELAY, &on, sizeof on);
    return s;
}
```
```cpp
static int send_line(std::string_view s) {
    std::string buf(s);
    buf.push_back('\n');
    size_t off = 0;
    while (off < buf.size()) {
        ssize_t n = ::write(ctl, buf.data() + off, buf.size() - off);
        if (n < 0) { if (errno == EINTR) continue; return -1; }
        off += static_cast<size_t>(n);
    }
    return 0;
}

static int recv_line(std::string& out) {
    out.clear();
    for (;;) {
        char c;
        ssize_t n = ::read(ctl, &c, 1);
        if (n < 0) { if (errno == EINTR) continue; return -1; }
        if (n == 0) return -1;
        if (c == '\n') return 0;
        out.push_back(c);
    }
}

static int tcp_accept(std::string_view port) {
    struct addrinfo hints{}, *res = nullptr;
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;
    if (::getaddrinfo(nullptr, port.data(), &hints, &res) != 0) return -1;

    int srv = ::socket(res->ai_family, res->ai_socktype, 0);
    int cli = -1, on = 1;
    if (srv >= 0) {
        ::setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));
        if (::bind(srv, res->ai_addr, res->ai_addrlen) == 0 && ::listen(srv, 1) == 0)
            cli = ::accept(srv, nullptr, nullptr);
        ::close(srv);
    }
    ::freeaddrinfo(res);
    if (cli >= 0) ::setsockopt(cli, IPPROTO_TCP, TCP_NODELAY, &on, sizeof(on));
    return cli;
}

static int tcp_connect(std::string_view host, std::string_view port) {
    struct addrinfo hints{}, *res = nullptr;
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    if (::getaddrinfo(host.data(), port.data(), &hints, &res) != 0) return -1;

    int s = -1, on = 1;
    for (auto ai = res; ai; ai = ai->ai_next) {
        s = ::socket(ai->ai_family, ai->ai_socktype, 0);
        if (s < 0) continue;
        if (::connect(s, ai->ai_addr, ai->ai_addrlen) == 0) break;
        ::close(s);
        s = -1;
    }
    ::freeaddrinfo(res);
    if (s >= 0) ::setsockopt(s, IPPROTO_TCP, TCP_NODELAY, &on, sizeof(on));
    return s;
}
```
:::

Далі — сторона письменника. Її словник навмисно складається з примітивів, а не з дослідів: `OPEN`, `WRITE`, `FSYNC`, `PREAD`, `CLOSE`, замки, `UNLINK`, підрахунок імен за префіксом. Дескриптори живуть у чотирьох комірках, щоб читач міг тримати відкритими кілька файлів одночасно. Відповідь — завжди `OK <число>` або `ERR <errno>`; єдиний виняток описаний у шостій пробі.

:::tabs
```c
#define SLOTS 4
static int slot[SLOTS];

static void ok(long v)  { char b[64]; snprintf(b, sizeof b, "OK %ld",  v);     send_line(b); }
static void err(void)   { char b[64]; snprintf(b, sizeof b, "ERR %d", errno);  send_line(b); }
static int  sl(long i)  { return (i >= 0 && i < SLOTS) ? slot[i] : -1; }

static int mode_flags(const char *m)
{
    if (!strcmp(m, "r"))  return O_RDONLY;
    if (!strcmp(m, "rw")) return O_RDWR   | O_CREAT;
    if (!strcmp(m, "w"))  return O_WRONLY | O_CREAT | O_TRUNC;
    if (!strcmp(m, "wx")) return O_WRONLY | O_CREAT | O_EXCL;
    return -1;
}

static long count_prefix(const char *dir, const char *prefix)
{
    DIR           *d = opendir(dir);
    struct dirent *e;
    size_t         plen = strlen(prefix);
    long           k = 0;

    if (!d) return -1;
    while ((e = readdir(d)) != NULL)
        if (strncmp(e->d_name, prefix, plen) == 0) k++;
    closedir(d);
    return k;
}

static void race(const char *prefix, int rounds, char *bits)
{
    int i;
    for (i = 0; i < rounds; i++) {
        char name[600];
        int  fd;
        snprintf(name, sizeof name, "%s-%d", prefix, i);
        fd = open(at(name), O_WRONLY | O_CREAT | O_EXCL, 0644);
        if (fd >= 0) { bits[i] = '1'; close(fd); }
        else           bits[i] = '0';
    }
    bits[rounds] = '\0';
}

static void serve(void)
{
    char cmd[2048], a[64], b[512];
    long i, n, off;

    for (i = 0; i < SLOTS; i++) slot[i] = -1;

    while (recv_line(cmd, sizeof cmd) == 0) {

        if (sscanf(cmd, "OPEN %ld %63s %511s", &i, a, b) == 3
            && i >= 0 && i < SLOTS) {
            int fl = mode_flags(a);
            slot[i] = (fl < 0) ? -1 : open(at(b), fl, 0644);
            if (slot[i] < 0) err(); else ok(0);
        }
        else if (sscanf(cmd, "WRITE %ld %ld", &i, &n) == 2) {
            char   *buf = malloc((size_t) n);
            ssize_t w = -1;
            if (buf) { memset(buf, 'x', (size_t) n); w = write(sl(i), buf, (size_t) n); }
            free(buf);
            if (w != (ssize_t) n) err(); else ok(n);
        }
        else if (sscanf(cmd, "FSYNC %ld", &i) == 1) {
            if (fsync(sl(i)) < 0) err(); else ok(0);
        }
        else if (sscanf(cmd, "PREAD %ld %ld %ld", &i, &off, &n) == 3) {
            char    buf[4096];
            ssize_t r;
            if (n > (long) sizeof buf) n = (long) sizeof buf;
            r = pread(sl(i), buf, (size_t) n, (off_t) off);
            if (r < 0) err(); else ok(r);
        }
        else if (sscanf(cmd, "CLOSE %ld", &i) == 1) {
            int rc = close(sl(i));              /* саме тут NFS віддає накопичене */
            if (i >= 0 && i < SLOTS) slot[i] = -1;
            if (rc < 0) err(); else ok(0);
        }
        else if (sscanf(cmd, "FLOCK %ld", &i) == 1) {
            if (flock(sl(i), LOCK_EX | LOCK_NB) < 0) err(); else ok(0);
        }
        else if (sscanf(cmd, "FCNTL %ld", &i) == 1) {
            struct flock fl;
            memset(&fl, 0, sizeof fl);          /* l_start = 0, l_len = 0 — увесь файл */
            fl.l_type = F_WRLCK;
            fl.l_whence = SEEK_SET;
            if (fcntl(sl(i), F_SETLK, &fl) < 0) err(); else ok(0);
        }
        else if (sscanf(cmd, "UNLINK %511s", b) == 1) {
            if (unlink(at(b)) < 0) err(); else ok(0);
        }
        else if (sscanf(cmd, "COUNT %511s", b) == 1) {
            ok(count_prefix(share, b));
        }
        else if (sscanf(cmd, "RACE %511s %ld", b, &n) == 2) {
            char *bits = malloc((size_t) n + 1);
            if (!bits) { err(); continue; }
            race(b, (int) n, bits);
            send_line(bits);                    /* відповідь — мапа, а не OK */
            free(bits);
        }
        else if (!strcmp(cmd, "BYE")) return;
        else send_line("ERR 22");               /* EINVAL: незрозуміла команда */
    }
}
```
```cpp
constexpr size_t SLOTS = 4;
static std::array<int, SLOTS> slot = {-1, -1, -1, -1};

static void ok(long v) { send_line(std::format("OK {}", v)); }
static void err() { send_line(std::format("ERR {}", errno)); }
static int sl(long i) { return (i >= 0 && static_cast<size_t>(i) < SLOTS) ? slot[i] : -1; }

static int mode_flags(std::string_view m) {
    if (m == "r")  return O_RDONLY;
    if (m == "rw") return O_RDWR   | O_CREAT;
    if (m == "w")  return O_WRONLY | O_CREAT | O_TRUNC;
    if (m == "wx") return O_WRONLY | O_CREAT | O_EXCL;
    return -1;
}

static long count_prefix(const fs::path& dir, std::string_view prefix) {
    long k = 0;
    std::error_code ec;
    for (const auto& entry : fs::directory_iterator(dir, ec)) {
        if (entry.path().filename().string().starts_with(prefix))
            k++;
    }
    return ec ? -1 : k;
}

static void race(std::string_view prefix, int rounds, std::string& bits) {
    bits.clear();
    for (int i = 0; i < rounds; ++i) {
        auto name = at(std::format("{}-{}", prefix, i));
        int fd = ::open(name.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0644);
        if (fd >= 0) { bits.push_back('1'); ::close(fd); }
        else { bits.push_back('0'); }
    }
}

static void serve() {
    std::string cmd;
    slot.fill(-1);

    while (recv_line(cmd) == 0) {
        long i = 0, n = 0, off = 0;
        char a_buf[64] = {}, b_buf[512] = {};

        if (::sscanf(cmd.c_str(), "OPEN %ld %63s %511s", &i, a_buf, b_buf) == 3 && i >= 0 && static_cast<size_t>(i) < SLOTS) {
            int fl = mode_flags(a_buf);
            slot[i] = (fl < 0) ? -1 : ::open(at(b_buf).c_str(), fl, 0644);
            if (slot[i] < 0) err(); else ok(0);
        }
        else if (::sscanf(cmd.c_str(), "WRITE %ld %ld", &i, &n) == 2) {
            std::vector<char> buf(static_cast<size_t>(n), 'x');
            ssize_t w = ::write(sl(i), buf.data(), buf.size());
            if (w != static_cast<ssize_t>(n)) err(); else ok(n);
        }
        else if (::sscanf(cmd.c_str(), "FSYNC %ld", &i) == 1) {
            if (::fsync(sl(i)) < 0) err(); else ok(0);
        }
        else if (::sscanf(cmd.c_str(), "PREAD %ld %ld %ld", &i, &off, &n) == 3) {
            std::vector<char> buf(4096);
            if (n > static_cast<long>(buf.size())) n = static_cast<long>(buf.size());
            ssize_t r = ::pread(sl(i), buf.data(), static_cast<size_t>(n), static_cast<off_t>(off));
            if (r < 0) err(); else ok(r);
        }
        else if (::sscanf(cmd.c_str(), "CLOSE %ld", &i) == 1) {
            int rc = ::close(sl(i));
            if (i >= 0 && static_cast<size_t>(i) < SLOTS) slot[i] = -1;
            if (rc < 0) err(); else ok(0);
        }
        else if (::sscanf(cmd.c_str(), "FLOCK %ld", &i) == 1) {
            if (::flock(sl(i), LOCK_EX | LOCK_NB) < 0) err(); else ok(0);
        }
        else if (::sscanf(cmd.c_str(), "FCNTL %ld", &i) == 1) {
            struct flock fl{};
            fl.l_type = F_WRLCK;
            fl.l_whence = SEEK_SET;
            if (::fcntl(sl(i), F_SETLK, &fl) < 0) err(); else ok(0);
        }
        else if (::sscanf(cmd.c_str(), "UNLINK %511s", b_buf) == 1) {
            std::error_code ec;
            fs::remove(at(b_buf), ec);
            if (ec) err(); else ok(0);
        }
        else if (::sscanf(cmd.c_str(), "COUNT %511s", b_buf) == 1) {
            ok(count_prefix(share_dir, b_buf));
        }
        else if (::sscanf(cmd.c_str(), "RACE %511s %ld", b_buf, &n) == 2) {
            std::string bits;
            race(b_buf, static_cast<int>(n), bits);
            send_line(bits);
        }
        else if (cmd == "BYE") return;
        else send_line("ERR 22");
    }
}
```
:::

На боці читача цій руці відповідає одна функція. Домовленість про знак робить код дослідів однорядковим: невід'ємне значення — те, що повернув виклик на іншій машині; від'ємне — мінус `errno`.

:::tabs
```c
static long rpc(const char *fmt, ...)
{
    char    req[2048], resp[2048];
    long    v;
    int     e;
    va_list ap;

    va_start(ap, fmt);
    vsnprintf(req, sizeof req, fmt, ap);
    va_end(ap);

    if (send_line(req) < 0 || recv_line(resp, sizeof resp) < 0) {
        fprintf(stderr, "керувальний канал обірвався на «%s»\n", req);
        exit(2);
    }
    if (sscanf(resp, "OK %ld",  &v) == 1) return v;
    if (sscanf(resp, "ERR %d",  &e) == 1) return -(long) e;
    fprintf(stderr, "незрозуміла відповідь: «%s»\n", resp);
    exit(2);
}
```
```cpp
static long rpc(std::string_view req) {
    if (send_line(req) < 0) {
        std::cerr << "керувальний канал обірвався\n";
        std::exit(2);
    }
    std::string resp;
    if (recv_line(resp) < 0) {
        std::cerr << "помилка читання відповіді\n";
        std::exit(2);
    }
    long v = 0;
    int e = 0;
    if (::sscanf(resp.c_str(), "OK %ld", &v) == 1) return v;
    if (::sscanf(resp.c_str(), "ERR %d", &e) == 1) return -static_cast<long>(e);
    std::cerr << "незрозуміла відповідь: " << resp << "\n";
    std::exit(2);
}
```
:::

## Проба 1: за скільки видно чужий файл

Найважливіший рядок цієї проби — не вимірювання, а підготовка. Перед тим як просити A створити файл, читач сам робить `stat()` по майбутньому імені й читає каталог цілком. Обидва звернення провалюються — і саме заради цього робляться: невдалий пошук лишає в кеші клієнта **негативний запис**, тобто твердження «такого імені тут немає», яке має свій термін придатності. Без цього кроку ми поміряли б випадкову величину: залишок чужого таймера, заведеного невідомо коли.

Опитуються два різні шляхи, бо вони спираються на різні кеші. `stat()` по повному імені перевіряє той самий негативний запис; `readdir()` віддає вміст каталогу, який клієнт тримає окремо ([каталог як таблиця імен](book:unix-linux/directory-as-mapping)). Числа збігаються не завжди, і розбіжність між ними сама по собі багато каже про клієнта.

:::tabs
```c
static double dir_ttl = -1;        /* результат цієї проби знадобиться далі */

static int in_listing(const char *dir, const char *name)
{
    DIR           *d = opendir(dir);
    struct dirent *e;
    int            found = 0;

    if (!d) return 0;
    while ((e = readdir(d)) != NULL)
        if (strcmp(e->d_name, name) == 0) { found = 1; break; }
    closedir(d);
    return found;
}

static void probe_visibility(void)
{
    char        name[64], path[PATH_MAX];
    struct stat st;
    double      t0, ts = -1, td = -1;

    snprintf(name, sizeof name, "vis-%ld", (long) getpid());
    snprintf(path, sizeof path, "%s/%s", share, name);

    if (stat(path, &st) == 0) { puts("1. ім'я вже зайняте"); return; }
    in_listing(share, name);             /* прогріваємо негативний запис */

    if (rpc("OPEN 0 wx %s", name) < 0) { puts("1. створити не вдалося"); return; }
    rpc("WRITE 0 64");
    rpc("FSYNC 0");
    rpc("CLOSE 0");

    t0 = mono();                         /* ← нуль нашого секундоміра */

    while (mono() - t0 < 180.0 && (ts < 0 || td < 0)) {
        if (ts < 0 && stat(path, &st) == 0)    ts = mono() - t0;
        if (td < 0 && in_listing(share, name)) td = mono() - t0;
        nap_ms(50);
    }

    printf("1a. stat() бачить новий файл через   %s с\n", secs(ts));
    printf("1b. readdir() бачить його через      %s с\n", secs(td));

    dir_ttl = (ts > td) ? ts : td;
    rpc("UNLINK %s", name);
}
```
```cpp
static double dir_ttl = -1;

static bool in_listing(const fs::path& dir, std::string_view name) {
    std::error_code ec;
    for (const auto& entry : fs::directory_iterator(dir, ec)) {
        if (entry.path().filename() == name) return true;
    }
    return false;
}

static void probe_visibility() {
    std::string name = std::format("vis-{}", ::getpid());
    auto path = at(name);

    std::error_code ec;
    if (fs::exists(path, ec)) { std::cout << "1. ім'я вже зайняте\n"; return; }
    in_listing(share_dir, name);

    if (rpc(std::format("OPEN 0 wx {}", name)) < 0) { std::cout << "1. створити не вдалося\n"; return; }
    rpc("WRITE 0 64");
    rpc("FSYNC 0");
    rpc("CLOSE 0");

    double t0 = mono(), ts = -1, td = -1;
    while (mono() - t0 < 180.0 && (ts < 0 || td < 0)) {
        if (ts < 0 && fs::exists(path, ec)) ts = mono() - t0;
        if (td < 0 && in_listing(share_dir, name)) td = mono() - t0;
        nap_ms(50);
    }

    std::cout << std::format("1a. stat() бачить новий файл через   {} с\n", secs(ts));
    std::cout << std::format("1b. readdir() бачить його через      {} с\n", secs(td));

    dir_ttl = std::max(ts, td);
    rpc(std::format("UNLINK {}", name));
}
```
:::

## Проба 2: чи видно дописане у відкритий файл

Тут перевіряється межа гарантії «від закриття до відкриття». Письменник створює файл, записує перший блок і синхронізує його — байти напевно на сервері. Тільки після цього читач відкриває файл: кешу цього файлу в нього ще немає, тож початковий вміст мусить бути видний одразу. Далі письменник дописує другий блок, **не закриваючи** файл, — і починається вимірювання трьох різних речей.

Розмір і дані живуть у різних кешах, тому й міряються окремо. `fstat()` віддає атрибути, які клієнт закешував при відкритті; `pread()` за старим кінцем файлу натрапляє або на нову сторінку, або на порожнечу. Третя доріжка — перевідкриття файлу в кожному колі; якщо контракт CTO працює, вона мусить дати майже нуль, і саме розрив між нею та двома першими показує, скільки коштує тримати файл відкритим.

:::tabs
```c
static void probe_open_file(void)
{
    char        name[64], path[PATH_MAX];
    struct stat st;
    off_t       base;
    double      t0, tsize = -1, tdata = -1, treopen = -1;
    int         fd;

    snprintf(name, sizeof name, "app-%ld", (long) getpid());
    snprintf(path, sizeof path, "%s/%s", share, name);

    rpc("UNLINK %s", name);                       /* байдуже, чи був */
    if (rpc("OPEN 0 w %s", name) < 0) { puts("2. створити не вдалося"); return; }
    rpc("WRITE 0 4096");
    rpc("FSYNC 0");

    fd = open(path, O_RDONLY);                    /* відкриваємо ПІСЛЯ — CTO має діяти */
    if (fd < 0) { perror("2. open"); return; }
    if (fstat(fd, &st) < 0) { close(fd); return; }
    base = st.st_size;

    rpc("WRITE 0 4096");                          /* дописано, файл лишається відкритим */
    rpc("FSYNC 0");
    t0 = mono();

    while (mono() - t0 < 180.0 && (tsize < 0 || tdata < 0 || treopen < 0)) {
        char c;
        int  g;
        if (tsize < 0 && fstat(fd, &st) == 0 && st.st_size > base)
            tsize = mono() - t0;
        if (tdata < 0 && pread(fd, &c, 1, base) == 1)
            tdata = mono() - t0;
        if (treopen < 0 && (g = open(path, O_RDONLY)) >= 0) {
            if (pread(g, &c, 1, base) == 1) treopen = mono() - t0;
            close(g);
        }
        nap_ms(50);
    }

    printf("2a. новий розмір видно через         %s с\n", secs(tsize));
    printf("2b. дописані байти читаються через   %s с\n", secs(tdata));
    printf("2c. те саме з перевідкриттям файлу:  %s с\n", secs(treopen));

    close(fd);
    rpc("CLOSE 0");
    rpc("UNLINK %s", name);
}
```
```cpp
static void probe_open_file() {
    std::string name = std::format("app-{}", ::getpid());
    auto path = at(name);

    rpc(std::format("UNLINK {}", name));
    if (rpc(std::format("OPEN 0 w {}", name)) < 0) { std::cout << "2. створити не вдалося\n"; return; }
    rpc("WRITE 0 4096");
    rpc("FSYNC 0");

    int fd = ::open(path.c_str(), O_RDONLY);
    if (fd < 0) { std::perror("2. open"); return; }
    
    struct stat st{};
    if (::fstat(fd, &st) < 0) { ::close(fd); return; }
    off_t base = st.st_size;

    rpc("WRITE 0 4096");
    rpc("FSYNC 0");
    double t0 = mono(), tsize = -1, tdata = -1, treopen = -1;

    while (mono() - t0 < 180.0 && (tsize < 0 || tdata < 0 || treopen < 0)) {
        char c;
        if (tsize < 0 && ::fstat(fd, &st) == 0 && st.st_size > base)
            tsize = mono() - t0;
        if (tdata < 0 && ::pread(fd, &c, 1, base) == 1)
            tdata = mono() - t0;
        if (treopen < 0) {
            int g = ::open(path.c_str(), O_RDONLY);
            if (g >= 0) {
                if (::pread(g, &c, 1, base) == 1) treopen = mono() - t0;
                ::close(g);
            }
        }
        nap_ms(50);
    }

    std::cout << std::format("2a. новий розмір видно через         {} с\n", secs(tsize));
    std::cout << std::format("2b. дописані байти читаються через   {} с\n", secs(tdata));
    std::cout << std::format("2c. те саме з перевідкриттям файлу:  {} с\n", secs(treopen));

    ::close(fd);
    rpc("CLOSE 0");
    rpc(std::format("UNLINK {}", name));
}
```
:::

## Проба 3: куди насправді йдуть байти

Ця проба обходиться без другої машини й тому найдешевша, а виявляє найважливіше. Записується 64 МіБ, і секундомір розділяє шлях на три відрізки: цикл `write()`, `fsync()` і `close()`. Розподіл часу між ними прямо показує, де стоїть та точка, у якій ваша програма дізнається правду про свій запис.

Читається результат так. Уся ціна в `write()` — дані йдуть на сервер одразу, тобто або монтування синхронне, або клієнтський кеш переповнився й почав витискати сторінки посеред циклу. Уся ціна в `close()` — накопичене віддається наприкінці, а отже, саме `close()` є тим місцем, де з'являться `ENOSPC`, `EDQUOT` чи `EIO`, і програма, яка його результату не перевіряє, втратить дані мовчки.

Окремо варто дивитися на останній рядок — сукупний темп. Якщо він вищий за фізичну стелю шляху (гігабітний канал — це близько 118 МіБ/с, і жоден трюк його не перевищить), то підтвердження приходять швидше, ніж байти встигають бути записаними. Найчастіша причина — опція `async` в експорті на сервері: за нею сервер відповідає на запит, ще не закріпивши зміни на носії. Довідка `exports(5)` називає це прямим порушенням протоколу NFS і попереджає, що аварійне перезавантаження сервера такі дані втратить або зіпсує. Ваш `fsync()` при цьому чесно повертає нуль — просто за цим нулем немає нічого ([що саме означає довговічність запису](book:unix-linux/page-cache-durability)). Сама проба цього не доводить, а лише дає підставу піти на сервер і подивитися `exportfs -v`.

:::tabs
```c
static void probe_write_path(void)
{
    enum { CHUNKS = 64 };
    const size_t CHUNK = 1u << 20;                /* 1 МіБ */
    char   name[64], path[PATH_MAX], *buf;
    double t0, t_write, t_fsync, t_close;
    int    fd, i, rc = 0;

    buf = malloc(CHUNK);
    if (!buf) return;
    memset(buf, 'z', CHUNK);
    snprintf(name, sizeof name, "flush-%ld", (long) getpid());
    snprintf(path, sizeof path, "%s/%s", share, name);

    fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) { perror("3. open"); free(buf); return; }

    t0 = mono();
    for (i = 0; i < CHUNKS; i++)
        if (write(fd, buf, CHUNK) != (ssize_t) CHUNK) { rc = -1; break; }
    t_write = mono() - t0;

    t0 = mono();
    if (fsync(fd) < 0) rc = -1;
    t_fsync = mono() - t0;

    t0 = mono();
    if (close(fd) < 0) rc = -1;                   /* ← результат close() перевіряємо ЗАВЖДИ */
    t_close = mono() - t0;

    printf("3.  %d МіБ:  write() %.2f с   fsync() %.2f с   close() %.2f с%s\n",
           (int) CHUNKS, t_write, t_fsync, t_close, rc < 0 ? "   ← ПОМИЛКА" : "");
    printf("    сукупний темп ≈ %.0f МіБ/с\n",
           CHUNKS / (t_write + t_fsync + t_close + 1e-9));

    free(buf);
    unlink(path);
}
```
```cpp
static void probe_write_path() {
    constexpr size_t CHUNKS = 64;
    constexpr size_t CHUNK = 1u << 20; // 1 МіБ
    std::string name = std::format("flush-{}", ::getpid());
    auto path = at(name);

    std::vector<char> buf(CHUNK, 'z');
    int fd = ::open(path.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) { std::perror("3. open"); return; }

    double t0 = mono();
    int rc = 0;
    for (size_t i = 0; i < CHUNKS; ++i) {
        if (::write(fd, buf.data(), CHUNK) != static_cast<ssize_t>(CHUNK)) { rc = -1; break; }
    }
    double t_write = mono() - t0;

    t0 = mono();
    if (::fsync(fd) < 0) rc = -1;
    double t_fsync = mono() - t0;

    t0 = mono();
    if (::close(fd) < 0) rc = -1;
    double t_close = mono() - t0;

    std::cout << std::format("3.  {} МіБ:  write() {:.2f} с   fsync() {:.2f} с   close() {:.2f} с{}\n",
                CHUNKS, t_write, t_fsync, t_close, rc < 0 ? "   ← ПОМИЛКА" : "");
    std::cout << std::format("    сукупний темп ≈ {:.0f} МіБ/с\n",
                CHUNKS / (t_write + t_fsync + t_close + 1e-9));

    std::error_code ec;
    fs::remove(path, ec);
}
```
:::

Побачити помилку від `close()` на власні очі проба сама не може — для цього потрібна відмова, якої на справному стенді немає. Влаштовується вона за півхвилини вручну: запустити проби, а між `write()` і `close()` розірвати шлях до сервера (`iptables -A OUTPUT -p tcp --dport 2049 -j DROP` на м'якому монтуванні). Прогалину в чужому коді шукають тим самим прийомом, тільки навпаки: якщо програма викликає `close()` без перевірки результату, вона на цьому стенді тихо втратить дані й нічого нікому не скаже.

## Проба 4: чи виключають замки одне одного між машинами

Три досліди, і найповчальніший — середній. Локально `flock` і `fcntl` — два незалежні механізми: замок одного виду нічого не знає про замок іншого, вони не конфліктують у принципі. Клієнт NFS у Linux, починаючи з версії ядра 2.6.12, реалізує `flock` **емуляцією** — як байтовий замок `fcntl` на весь файл. Наслідок прямо записаний у довідці `flock(2)`: через NFS ці два види замків уже взаємодіють. Отже, той самий код на локальному й на мережевому каталозі дає протилежні відповіді, і жодне повідомлення про це не з'явиться. Опція монтування `local_lock` (з ядра 2.6.37) дозволяє повернути кожному виду замків локальність — а разом із нею й тишу між машинами.

Перший і третій досліди перевіряють базове: чи взагалі замки долають межу машини. Порожня відповідь тут — не рідкість: `cifs` із опцією `nobrl` замки на сервер просто не надсилає, а NFS без запущеної служби блокування мовчки поводиться так само (загальна модель — [рекомендаційні замки](book:unix-linux/file-locking)).

:::tabs
```c
static void probe_locks(void)
{
    char         name[64], path[PATH_MAX];
    struct flock fl;
    int          fd, rc;

    snprintf(name, sizeof name, "lock-%ld", (long) getpid());
    snprintf(path, sizeof path, "%s/%s", share, name);

    if (rpc("OPEN 0 rw %s", name) < 0) { puts("4. створити не вдалося"); return; }
    if (rpc("FLOCK 0") < 0)            { puts("4. чужий flock не взявся"); return; }

    fd = open(path, O_RDWR);
    if (fd < 0) { perror("4. open"); return; }

    rc = flock(fd, LOCK_EX | LOCK_NB);
    printf("4a. flock проти чужого flock: %s\n",
           rc == 0 ? "НЕ виключає — замок не долає межі машини"
                   : "виключає, як і має бути");
    if (rc == 0) flock(fd, LOCK_UN);

    memset(&fl, 0, sizeof fl);
    fl.l_type = F_WRLCK;
    fl.l_whence = SEEK_SET;
    rc = fcntl(fd, F_SETLK, &fl);
    printf("4b. fcntl проти чужого flock: %s\n",
           rc == 0 ? "не виключає — як локально"
                   : "ВИКЛЮЧАЄ — flock зведено до POSIX-замка на весь файл");
    if (rc == 0) { fl.l_type = F_UNLCK; fcntl(fd, F_SETLK, &fl); }

    rpc("CLOSE 0");                                /* закриття зняло чужий flock */
    if (rpc("OPEN 0 rw %s", name) >= 0) {
        if (rpc("FCNTL 0") < 0) puts("4c. чужий fcntl-замок не взявся взагалі");
        else {
            memset(&fl, 0, sizeof fl);
            fl.l_type = F_WRLCK;
            fl.l_whence = SEEK_SET;
            rc = fcntl(fd, F_SETLK, &fl);
            printf("4c. fcntl проти чужого fcntl: %s\n",
                   rc == 0 ? "НЕ виключає — замки лишилися локальними"
                           : "виключає, як і має бути");
            if (rc == 0) { fl.l_type = F_UNLCK; fcntl(fd, F_SETLK, &fl); }
        }
        rpc("CLOSE 0");
    }

    close(fd);
    rpc("UNLINK %s", name);
}
```
```cpp
static void probe_locks() {
    std::string name = std::format("lock-{}", ::getpid());
    auto path = at(name);

    if (rpc(std::format("OPEN 0 rw {}", name)) < 0) { std::cout << "4. створити не вдалося\n"; return; }
    if (rpc("FLOCK 0") < 0) { std::cout << "4. чужий flock не взявся\n"; return; }

    int fd = ::open(path.c_str(), O_RDWR);
    if (fd < 0) { std::perror("4. open"); return; }

    int rc = ::flock(fd, LOCK_EX | LOCK_NB);
    std::cout << "4a. flock проти чужого flock: "
              << (rc == 0 ? "НЕ виключає — замок не долає межі машини"
                          : "виключає, як і має бути") << "\n";
    if (rc == 0) ::flock(fd, LOCK_UN);

    struct flock fl{};
    fl.l_type = F_WRLCK;
    fl.l_whence = SEEK_SET;
    rc = ::fcntl(fd, F_SETLK, &fl);
    std::cout << "4b. fcntl проти чужого flock: "
              << (rc == 0 ? "не виключає — як локально"
                          : "ВИКЛЮЧАЄ — flock зведено до POSIX-замка на весь файл") << "\n";
    if (rc == 0) { fl.l_type = F_UNLCK; ::fcntl(fd, F_SETLK, &fl); }

    rpc("CLOSE 0");
    if (rpc(std::format("OPEN 0 rw {}", name)) >= 0) {
        if (rpc("FCNTL 0") < 0) std::cout << "4c. чужий fcntl-замок не взявся взагалі\n";
        else {
            fl.l_type = F_WRLCK;
            fl.l_whence = SEEK_SET;
            rc = ::fcntl(fd, F_SETLK, &fl);
            std::cout << "4c. fcntl проти чужого fcntl: "
                      << (rc == 0 ? "НЕ виключає — замки лишилися локальними"
                                  : "виключає, як і має бути") << "\n";
            if (rc == 0) { fl.l_type = F_UNLCK; ::fcntl(fd, F_SETLK, &fl); }
        }
        rpc("CLOSE 0");
    }

    ::close(fd);
    rpc(std::format("UNLINK {}", name));
}
```
:::

## Проба 5: що лишається від видаленого відкритого файлу

Локально знімання імені з файлу, який хтось тримає відкритим, — рутина: [опис відкритого файлу](book:unix-linux/open-file-description) утримує об'єкт, доки не закриється останній дескриптор. У мережі це припущення розпадається на два різні випадки, і проба перевіряє обидва.

Спершу файл тримає **чужа** машина, а ім'я знімаємо ми. Порятунку тут не існує в принципі: клієнт, який робить `unlink`, нічого не знає про чужі дескриптори. Питання лише в тому, що дістанеться власникові — `ESTALE` від об'єкта, що зник, чи спокійне читання, бо сервер із власним знанням про відкриті файли (NFSv4, SMB) утримав його сам.

Потім та сама машина і тримає файл, і знімає ім'я. Ось тут клієнт NFS вмикає підміну: замість видалення перейменовує файл на `.nfs…` і прибирає його по-справжньому при останньому закритті. Ці рештки видно обом сторонам, і проба питає про них двічі — у письменника й у себе. Своя відповідь чекає на кеш каталогу, тривалість якого вже виміряно першою пробою: рідкісний випадок, коли результат одного досліду прямо витрачається в наступному.

:::tabs
```c
static void probe_open_unlink(void)
{
    char aname[64], bname[64], apath[PATH_MAX];
    long n;

    snprintf(aname, sizeof aname, "del-a-%ld", (long) getpid());
    snprintf(bname, sizeof bname, "del-b-%ld", (long) getpid());
    snprintf(apath, sizeof apath, "%s/%s", share, aname);

    /* (а) тримає ЧУЖА машина, ім'я знімаємо МИ */
    if (rpc("OPEN 0 rw %s", aname) < 0) { puts("5. створити не вдалося"); return; }
    rpc("WRITE 0 4096");
    rpc("FSYNC 0");
    if (unlink(apath) < 0) perror("5a. unlink");

    n = rpc("PREAD 0 0 16");
    printf("5a. чужий дескриптор після нашого unlink: %s\n",
           n >= 0        ? "читається далі — сервер утримав відкритий файл" :
           n == -ESTALE  ? "ESTALE — об'єкт зник просто під дескриптором"
                         : "інша помилка читання");
    rpc("CLOSE 0");

    /* (б) та сама машина і тримає, і знімає ім'я */
    if (rpc("OPEN 1 rw %s", bname) < 0) return;
    rpc("WRITE 1 4096");
    rpc("UNLINK %s", bname);
    printf("5b. з боку письменника імен «.nfs» у каталозі: %ld\n", rpc("COUNT .nfs"));

    if (dir_ttl > 0) nap_ms((long) (dir_ttl * 1000) + 1000);   /* чекаємо СВІЙ кеш */
    printf("    з нашого боку:                          %ld\n",
           count_prefix(share, ".nfs"));

    rpc("CLOSE 1");
    if (dir_ttl > 0) nap_ms((long) (dir_ttl * 1000) + 1000);
    printf("5c. після close() письменника лишилося:     %ld\n",
           count_prefix(share, ".nfs"));
}
```
```cpp
static void probe_open_unlink() {
    std::string aname = std::format("del-a-{}", ::getpid());
    std::string bname = std::format("del-b-{}", ::getpid());
    auto apath = at(aname);

    if (rpc(std::format("OPEN 0 rw {}", aname)) < 0) { std::cout << "5. створити не вдалося\n"; return; }
    rpc("WRITE 0 4096");
    rpc("FSYNC 0");
    std::error_code ec;
    fs::remove(apath, ec);

    long n = rpc("PREAD 0 0 16");
    std::cout << "5a. чужий дескриптор після нашого unlink: "
              << (n >= 0       ? "читається далі — сервер утримав відкритий файл" :
                  n == -ESTALE ? "ESTALE — об'єкт зник просто під дескриптором"
                               : "інша помилка читання") << "\n";
    rpc("CLOSE 0");

    if (rpc(std::format("OPEN 1 rw {}", bname)) < 0) return;
    rpc("WRITE 1 4096");
    rpc(std::format("UNLINK {}", bname));
    std::cout << "5b. з боку письменника імен «.nfs» у каталозі: " << rpc("COUNT .nfs") << "\n";

    if (dir_ttl > 0) nap_ms(static_cast<long>(dir_ttl * 1000) + 1000);
    std::cout << "    з нашого боку:                          " << count_prefix(share_dir, ".nfs") << "\n";

    rpc("CLOSE 1");
    if (dir_ttl > 0) nap_ms(static_cast<long>(dir_ttl * 1000) + 1000);
    std::cout << "5c. після close() письменника лишилося:     " << count_prefix(share_dir, ".nfs") << "\n";
}
```
:::

## Проба 6: чи атомарне створення з O_EXCL

Створення файлу з `O_CREAT | O_EXCL` — найпоширеніший спосіб узяти замок без жодних замків: хто створив, той і власник. Досліду тут потрібна справжня одночасність, і саме через це шоста проба ламає звичну схему «команда — відповідь». Читач надсилає `RACE`, **не чекаючи відповіді**, одразу починає власний забіг по тих самих іменах — і лише коли закінчить, забирає з каналу бітову мапу письменника. Це єдиний момент у всій програмі, де синхронний `rpc()` не годиться, і заради нього канал розділено на `send_line` та `recv_line`.

Подвійна перемога — той самий номер кола, який обидві сторони записали собі, — означає, що виключне створення на цьому монтуванні не атомарне між машинами. Розподіл перемог теж варто читати: приблизно рівний рахунок свідчить, що забіги справді перетнулися в часі, а рахунок «400 : 0» — що одна сторона встигла раніше й змагання не було, тож проба нічого не перевірила.

:::tabs
```c
static void probe_excl_race(void)
{
    enum { ROUNDS = 400 };
    char prefix[64], req[128], mine[ROUNDS + 1], theirs[ROUNDS + 8];
    int  i, mine_won = 0, their_won = 0, both = 0, none = 0;

    snprintf(prefix, sizeof prefix, "race-%ld", (long) getpid());
    snprintf(req, sizeof req, "RACE %s %d", prefix, (int) ROUNDS);
    if (send_line(req) < 0) return;               /* відповіді НЕ чекаємо */

    for (i = 0; i < ROUNDS; i++) {
        char name[PATH_MAX];
        int  fd;
        snprintf(name, sizeof name, "%s/%s-%d", share, prefix, i);
        fd = open(name, O_WRONLY | O_CREAT | O_EXCL, 0644);
        if (fd >= 0) { mine[i] = '1'; close(fd); }
        else           mine[i] = '0';
    }
    mine[ROUNDS] = '\0';

    if (recv_line(theirs, sizeof theirs) < 0) return;
    if (strlen(theirs) != (size_t) ROUNDS) { puts("6. мапа не тієї довжини"); return; }

    for (i = 0; i < ROUNDS; i++) {
        int m = (mine[i] == '1'), t = (theirs[i] == '1');
        mine_won += m;
        their_won += t;
        both += (m && t);
        none += (!m && !t);
    }

    printf("6.  O_EXCL, %d кіл: наших %d, чужих %d, ПОДВІЙНИХ %d, нічиїх %d\n",
           (int) ROUNDS, mine_won, their_won, both, none);
    if (both)
        puts("    подвійна перемога = створення НЕ атомарне між машинами");
    if (mine_won == 0 || their_won == 0)
        puts("    забіги не перетнулися в часі — проба нічого не перевірила");

    for (i = 0; i < ROUNDS; i++) {
        char name[PATH_MAX];
        snprintf(name, sizeof name, "%s/%s-%d", share, prefix, i);
        unlink(name);
    }
}

int main(int argc, char **argv)
{
    if (argc == 4 && strcmp(argv[1], "writer") == 0) {
        snprintf(share, sizeof share, "%s", argv[2]);
        ctl = tcp_accept(argv[3]);
        if (ctl < 0) { perror("accept"); return 1; }
        serve();
        return 0;
    }
    if (argc == 5 && strcmp(argv[1], "reader") == 0) {
        snprintf(share, sizeof share, "%s", argv[2]);
        ctl = tcp_connect(argv[3], argv[4]);
        if (ctl < 0) { perror("connect"); return 1; }
        probe_visibility();
        probe_open_file();
        probe_write_path();
        probe_locks();
        probe_open_unlink();
        probe_excl_race();
        send_line("BYE");
        return 0;
    }
    fprintf(stderr,
            "вжиток:\n"
            "  %s writer <спільний-каталог> <порт>\n"
            "  %s reader <спільний-каталог> <хост-письменника> <порт>\n",
            argv[0], argv[0]);
    return 1;
}
```
```cpp
static void probe_excl_race() {
    constexpr int ROUNDS = 400;
    std::string prefix = std::format("race-{}", ::getpid());
    std::string req = std::format("RACE {} {}", prefix, ROUNDS);
    if (send_line(req) < 0) return;

    std::string mine;
    mine.reserve(ROUNDS);
    for (int i = 0; i < ROUNDS; ++i) {
        auto name = at(std::format("{}-{}", prefix, i));
        int fd = ::open(name.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0644);
        if (fd >= 0) { mine.push_back('1'); ::close(fd); }
        else { mine.push_back('0'); }
    }

    std::string theirs;
    if (recv_line(theirs) < 0) return;
    if (theirs.size() != ROUNDS) { std::cout << "6. мапа не тієї довжини\n"; return; }

    int mine_won = 0, their_won = 0, both = 0, none = 0;
    for (int i = 0; i < ROUNDS; ++i) {
        bool m = (mine[i] == '1'), t = (theirs[i] == '1');
        mine_won += m;
        their_won += t;
        both += (m && t);
        none += (!m && !t);
    }

    std::cout << std::format("6.  O_EXCL, {} кіл: наших {}, чужих {}, ПОДВІЙНИХ {}, нічиїх {}\n",
                ROUNDS, mine_won, their_won, both, none);
    if (both) std::cout << "    подвійна перемога = створення НЕ атомарне між машинами\n";
    if (mine_won == 0 || their_won == 0) std::cout << "    забіги не перетнулися в часі — проба нічого не перевірила\n";

    std::error_code ec;
    for (int i = 0; i < ROUNDS; ++i) {
        fs::remove(at(std::format("{}-{}", prefix, i)), ec);
    }
}

int main(int argc, char **argv) {
    if (argc == 4 && std::string_view(argv[1]) == "writer") {
        share_dir = argv[2];
        ctl = tcp_accept(argv[3]);
        if (ctl < 0) { std::perror("accept"); return 1; }
        serve();
        return 0;
    }
    if (argc == 5 && std::string_view(argv[1]) == "reader") {
        share_dir = argv[2];
        ctl = tcp_connect(argv[3], argv[4]);
        if (ctl < 0) { std::perror("connect"); return 1; }
        probe_visibility();
        probe_open_file();
        probe_write_path();
        probe_locks();
        probe_open_unlink();
        probe_excl_race();
        send_line("BYE");
        return 0;
    }
    std::cerr << std::format("вжиток:\n  {} writer <спільний-каталог> <порт>\n  {} reader <спільний-каталог> <хост-письменника> <порт>\n",
                argv[0], argv[0]);
    return 1;
}
```
:::

Типовий вивід на NFSv3 у локальній мережі виглядає приблизно так — і кожен рядок тут вартий свого числа:

```
1a. stat() бачить новий файл через     28.35 с
1b. readdir() бачить його через        28.40 с
2a. новий розмір видно через            3.10 с
2b. дописані байти читаються через      3.15 с
2c. те саме з перевідкриттям файлу:     0.05 с
3.  64 МіБ:  write() 0.31 с   fsync() 0.02 с   close() 0.58 с
    сукупний темп ≈ 70 МіБ/с
4a. flock проти чужого flock: виключає, як і має бути
4b. fcntl проти чужого flock: ВИКЛЮЧАЄ — flock зведено до POSIX-замка на весь файл
4c. fcntl проти чужого fcntl: виключає, як і має бути
5a. чужий дескриптор після нашого unlink: ESTALE — об'єкт зник просто під дескриптором
5b. з боку письменника імен «.nfs» у каталозі: 1
    з нашого боку:                          1
5c. після close() письменника лишилося:     0
6.  O_EXCL, 400 кіл: наших 214, чужих 186, ПОДВІЙНИХ 0, нічиїх 0
```

## Пастки

**Годинники не звіряти ніколи.** Спокуса порівняти `st_mtime` файлу з власним `CLOCK_REALTIME` виникає майже одразу — і одразу ж отруює результат. Різниця в цій формулі складається з двох доданків: справжньої затримки та розходження годинників, і розділити їх неможливо. Проба вимірює лише те, що почалося й закінчилося на одному годиннику, і саме тому в ній є керувальний канал.

**Роздільність часу зміни ховає зміни.** Клієнт NFSv3 упізнає модифікацію файлу за `mtime` та розміром. Якщо файлова система на сервері зберігає час зміни з роздільністю в одну секунду (стара `ext3`, деякі NAS-прошивки), два записи в межах одного тика ззовні нерозрізненні: другий може лишитися невидимим, доки не станеться щось іще ([що саме про часи повертає `statx`](book:unix-linux/statx-extended-stat)). NFSv4 обходить це окремим атрибутом зміни — лічильником, не пов'язаним із годинником. Практичний наслідок для проби: досліди 1 і 2 пишуть по кілька кілобайтів і розділяють дії підтвердженнями по каналу, тому в один тик не потрапляють; коли ж робите свої досліди — стежте, щоб і вони не потрапляли.

**«Дійшло до сервера» — не те саме, що «закріплено».** Ці три стани легко зливаються в один, а це три різні рівні пам'яті, і на кожному дані можуть згоріти окремо:

```
у кеші клієнта       write() повернувся   згорить від падіння клієнта
у пам'яті сервера    COMMIT ще не був     згорить від падіння сервера
на носії сервера     COMMIT підтверджено  переживе все, крім відмови носія
```

Третій дослід міряє шлях між першим і другим станами. Про перехід до третього чесно доповідає лише `fsync()` — і лише якщо сервер не експортує каталог із `async`, за якої підтвердження надсилається раніше за запис.

**Кеш підлаштовується — одне вимірювання нічого не значить.** Проміжок довіри до атрибутів у клієнта NFS не сталий: файл, який при перевірці виявився незміненим, наступного разу перевіряється пізніше, і так до стелі (`acregmax`, `acdirmax` — типово 60 с); змінений файл повертає проміжок до підлоги (`acregmin` — 3 с, `acdirmin` — 30 с). Тому перший прогін проби на щойно змонтованому каталозі й десятий прогін поспіль дадуть різні числа, обидва правильні. Запускайте кілька разів і дивіться на розкид, а не на одне число.

**Проба вміє знайти ваду, а не довести її відсутність.** Це стосується насамперед шостого досліду: нуль подвійних перемог не означає, що `O_EXCL` атомарний, — він означає лише, що за 400 кіл ми не спіймали протилежного. Рядок про перетин забігів у часі додано саме для того, щоб відрізнити «перевірили й не знайшли» від «не перевірили».

**Проба пише, тому їй потрібен свій каталог.** Вона створює й видаляє близько чотирьохсот імен, лишає по собі сміття при аварійному завершенні й на кілька секунд навантажує сервер. Робочий спільний каталог для цього не годиться; заведіть окремий підкаталог і не бійтеся його втратити.

**На жорсткому монтуванні проба зависає разом із сервером.** Це не вада, а та сама поведінка, заради вивчення якої все й затіяно: процес у стані `D` не реагує на сигнали, крім вбивчих. Запускайте під `timeout 600 ./mountprobe …`, інакше зникнення сервера посеред досліду перетворить проби на процес, який ви не зможете зняти.

**Шляхи на двох машинах різні.** Одна й та сама спільна тека цілком може бути `/mnt/share` на машині A та `/srv/nfs/share` на машині B — тому кожна сторона отримує свій шлях аргументом, а не бере його від іншої. Найчастіша помилка при першому запуску — переконаність, що каталог «той самий, отже, і шлях той самий».
