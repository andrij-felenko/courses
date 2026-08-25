# ⚙️ Служба, що чесно каже «готова» і годує сторожовий таймер

Зберімо невелику робочу службу, яка сама повідомляє менеджеру про свою готовність і подає ознаку життя, — і напишімо протокол сповіщень голими руками, без бібліотеки `libsystemd`, бо тільки так видно, що весь він складається з одного текстового рядка в датаграмі.

## Задача

Служба слухає TCP-порт і відповідає на з'єднання. Від неї вимагають чотирьох речей, і кожна перетворюється на рядок юніта:

- оголосити готовність **рівно тоді**, коли сокет уже прив'язаний і слухається, — ані миттю раніше;
- поки живе, регулярно підтверджувати, що її головний цикл справді крутиться;
- показувати людині осмислений рядок у виводі `systemctl status`;
- на `SIGTERM` спокійно згорнутися й вийти з кодом нуль.

## Ідея: увесь протокол — це рядок у датаграмі

Менеджер кладе в оточення служби змінну `NOTIFY_SOCKET` з іменем [сокета домену Unix](topic:sys-unix/unix-domain-sockets), і спілкування зводиться до того, щоб надіслати туди датаграму з рядками виду `КЛЮЧ=значення`, розділеними переводом рядка. З'єднання немає, відповіді немає, підтвердження немає — надіслав і забув. Ніякого «клієнта» писати не треба.

Деталей, які мусить знати той, хто пише це вручну, рівно три.

**Ім'я може починатися з `@`.** Це позначка абстрактного простору імен — сокета, який не має запису у файловій системі. У структурі адреси цей символ треба замінити на нульовий байт, а довжину адреси рахувати **без** завершального нуля: для абстрактних імен довжина адреси і є довжиною імені, і зайвий нуль дав би інше ім'я.

**Датаграма несе облікові дані відправника.** Ядро додає їх само (`SCM_CREDENTIALS`), і саме за номером процесу звідти менеджер вирішує, чи має право це повідомлення. Підробити чужий номер процес не може.

**Відсутність змінної — не помилка.** Немає `NOTIFY_SOCKET` — служба запущена не менеджером, і сповіщати нема кого. Тоді функція просто мовчить, і той самий двійник однаково запускається і з-під systemd, і з рук на розробницькій машині.

## Служба

:::tabs
```c
/* notifyd.c — служба Type=notify без libsystemd: READY=1 після listen,
   WATCHDOG=1 з того самого циклу, що робить роботу. */
#define _GNU_SOURCE
#include <errno.h>
#include <netinet/in.h>
#include <poll.h>
#include <signal.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>

static volatile sig_atomic_t stop_requested = 0;

static void on_terminate(int sig) { (void) sig; stop_requested = 1; }

/* ── Увесь протокол sd_notify: одна датаграма з рядками КЛЮЧ=значення. ── */
static int notify(const char *msg)
{
    const char *path = getenv("NOTIFY_SOCKET");
    if (!path || !*path)
        return 0;                       /* запустили не менеджером — мовчимо */

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof addr);
    addr.sun_family = AF_UNIX;

    size_t len = strlen(path);
    if (len >= sizeof addr.sun_path) {
        errno = ENAMETOOLONG;
        return -1;
    }
    memcpy(addr.sun_path, path, len);

    socklen_t alen;
    if (addr.sun_path[0] == '@') {      /* абстрактний простір імен ядра */
        addr.sun_path[0] = '\0';
        alen = (socklen_t) (offsetof(struct sockaddr_un, sun_path) + len);
    } else {                            /* звичайний шлях у файловій системі */
        alen = (socklen_t) (offsetof(struct sockaddr_un, sun_path) + len + 1);
    }

    int fd = socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0)
        return -1;

    ssize_t n = sendto(fd, msg, strlen(msg), MSG_NOSIGNAL,
                       (struct sockaddr *) &addr, alen);
    int saved = errno;
    close(fd);
    errno = saved;
    return n < 0 ? -1 : 0;
}

/* Термін сторожового таймера в мікросекундах; 0 — сторожа немає.
   Змінна могла дістатися нам у спадок від предка — звіряємо номер процесу. */
static uint64_t watchdog_usec(void)
{
    const char *owner = getenv("WATCHDOG_PID");
    const char *usec  = getenv("WATCHDOG_USEC");

    if (owner && strtol(owner, NULL, 10) != (long) getpid())
        return 0;
    if (!usec)
        return 0;
    return strtoull(usec, NULL, 10);
}

static uint64_t now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);   /* монотонний: переведення годинника не збиває */
    return (uint64_t) ts.tv_sec * 1000 + (uint64_t) ts.tv_nsec / 1000000;
}

/* Корисна робота: прийняти з'єднання, відповісти, закрити. */
static int serve_one(int srv)
{
    int c = accept4(srv, NULL, NULL, SOCK_CLOEXEC);
    if (c < 0)
        return 0;

    char buf[256];
    ssize_t n = recv(c, buf, sizeof buf, 0);
    if (n > 0)
        send(c, buf, (size_t) n, MSG_NOSIGNAL);
    close(c);
    return 1;
}

int main(void)
{
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_terminate;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGTERM, &sa, NULL);   /* БЕЗ SA_RESTART: poll має повернутися з EINTR */
    sigaction(SIGINT,  &sa, NULL);
    signal(SIGPIPE, SIG_IGN);        /* інакше запис у закрите з'єднання вб'є службу */

    int srv = socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    int one = 1;
    setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);

    struct sockaddr_in a;
    memset(&a, 0, sizeof a);
    a.sin_family      = AF_INET;
    a.sin_port        = htons(9100);
    a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (bind(srv, (struct sockaddr *) &a, sizeof a) < 0 || listen(srv, 64) < 0) {
        perror("bind/listen");
        return 1;                    /* READY=1 не було — менеджер бачить невдалий старт */
    }

    /* Аж ТЕПЕР порт слухається: залежні юніти можуть стартувати. */
    if (notify("READY=1\nSTATUS=слухаю 127.0.0.1:9100\n") < 0)
        perror("notify");

    uint64_t period_ms = watchdog_usec() / 2000;   /* половина терміну, мкс → мс */
    uint64_t next_ping = now_ms() + period_ms;
    uint64_t served    = 0;

    while (!stop_requested) {
        int timeout = -1;
        if (period_ms) {
            uint64_t now = now_ms();
            timeout = now >= next_ping ? 0 : (int) (next_ping - now);
        }

        struct pollfd pfd = { .fd = srv, .events = POLLIN };
        int r = poll(&pfd, 1, timeout);
        if (r < 0 && errno != EINTR)
            break;
        if (r > 0 && (pfd.revents & POLLIN))
            served += serve_one(srv);

        /* Ознака життя йде ЗВІДСИ — з циклу, що робить роботу. */
        if (period_ms && now_ms() >= next_ping) {
            char buf[96];
            snprintf(buf, sizeof buf,
                     "WATCHDOG=1\nSTATUS=обслужено з'єднань: %llu\n",
                     (unsigned long long) served);
            notify(buf);
            next_ping = now_ms() + period_ms;
        }
    }

    notify("STOPPING=1\nSTATUS=закриваю сокет\n");
    close(srv);
    return 0;                        /* чистий вихід: перезапуску не буде */
}
```
```go
// notifyd.go — та сама служба ідіоматичним Go: без залежностей, той самий протокол.
package main

import (
	"fmt"
	"net"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"
)

// notify — увесь протокол: датаграма з рядками КЛЮЧ=значення.
// Позначку «@» для абстрактного імені стандартна бібліотека розуміє сама,
// тож замінювати її на нульовий байт вручну не треба — і НЕ МОЖНА.
func notify(msg string) {
	path := os.Getenv("NOTIFY_SOCKET")
	if path == "" {
		return // запустили не менеджером
	}
	conn, err := net.DialUnix("unixgram", nil, &net.UnixAddr{Name: path, Net: "unixgram"})
	if err != nil {
		return
	}
	defer conn.Close()
	conn.Write([]byte(msg))
}

// Половина сторожового терміну; 0 — сторожа немає.
func pingPeriod() time.Duration {
	if owner := os.Getenv("WATCHDOG_PID"); owner != "" && owner != strconv.Itoa(os.Getpid()) {
		return 0 // змінна дісталася в спадок від предка
	}
	usec, err := strconv.ParseInt(os.Getenv("WATCHDOG_USEC"), 10, 64)
	if err != nil || usec <= 0 {
		return 0
	}
	return time.Duration(usec) * time.Microsecond / 2
}

func serve(c net.Conn) {
	defer c.Close()
	c.SetDeadline(time.Now().Add(2 * time.Second))
	buf := make([]byte, 256)
	// Запис у закрите з'єднання поверне помилку: середовище виконання Go
	// саме ігнорує SIGPIPE для всього, крім стандартного виводу й помилок.
	if n, err := c.Read(buf); err == nil {
		c.Write(buf[:n])
	}
}

func main() {
	ln, err := net.Listen("tcp", "127.0.0.1:9100")
	if err != nil {
		fmt.Fprintln(os.Stderr, "listen:", err)
		os.Exit(1) // READY=1 не було — менеджер бачить невдалий старт
	}
	notify("READY=1\nSTATUS=слухаю 127.0.0.1:9100\n")

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGTERM, syscall.SIGINT)

	// Accept блокує, тому живе в окремій горутині — але вона лише ПРИНОСИТЬ
	// з'єднання; сама робота лишається в головному циклі, нижче.
	conns := make(chan net.Conn)
	go func() {
		defer close(conns)
		for {
			c, err := ln.Accept()
			if err != nil {
				return
			}
			conns <- c
		}
	}()

	var ping <-chan time.Time // nil-канал у select блокує назавжди
	if p := pingPeriod(); p > 0 {
		t := time.NewTicker(p)
		defer t.Stop()
		ping = t.C
	}

	served := 0
	for {
		select {
		case c, ok := <-conns:
			if !ok {
				return
			}
			serve(c) // робота — в ЦЬОМУ ж циклі
			served++
		case <-ping:
			notify(fmt.Sprintf("WATCHDOG=1\nSTATUS=обслужено з'єднань: %d\n", served))
		case <-stop:
			notify("STOPPING=1\nSTATUS=закриваю сокет\n")
			ln.Close()
			return // код виходу 0
		}
	}
}
```
:::

Обидві версії тримають одну властивість, заради якої все й робиться: **пінг стоїть у тій самій черзі, що й робота**. У C він виконується після `poll` у тілі циклу; зависне `serve_one` — пінг не станеться. У Go горутина приймання лише передає з'єднання в канал, а обробка йде в тілі `select`; зависне `serve` — гілка з тікером не виконається. Якби замість цього запустити `go func() { for range t.C { notify("WATCHDOG=1") } }()`, сторожовий пес пильнував би справність тікера — а тікер тікає завжди, навіть коли служба давно нічого не обслуговує.

## Юніт

```ini
[Unit]
Description=Демонстраційна служба з чесним оголошенням готовності
After=network.target

[Service]
Type=notify
NotifyAccess=main
ExecStart=/usr/local/bin/notifyd

WatchdogSec=30
TimeoutStartSec=20

Restart=on-failure
RestartSec=1
RestartSteps=5
RestartMaxDelaySec=32
RestartPreventExitStatus=78

DynamicUser=yes

[Install]
WantedBy=multi-user.target
```

`WatchdogSec=30` не лише вмикає нагляд, а й кладе в оточення `WATCHDOG_USEC=30000000` — саме звідти код бере період і саме тому число 30 не зашите у двійник: змінили юніт, перезапустили, служба сама підлаштувалася. Ділити цей термін навпіл — не забобон і не запас «про всяк випадок»: за такого періоду один пропущений пінг ще прощається. Служба, яка ходить на межі й пінгує раз на двадцять дев'ять секунд, помре від першого ж запиту, що затримався на дві секунди, — і в журналі це буде виглядати як зависання, якого не було.

Рядок `STATUS=` не має жодного впливу на рішення менеджера — це слово служби до людини. Коштує він майже нічого, а видно його там, куди дивляться першим ділом:

```
● notifyd.service - Демонстраційна служба з чесним оголошенням готовності
     Active: active (running) since Sat 2026-08-08 03:14:07 EEST; 6h ago
   Main PID: 8123 (notifyd)
     Status: "обслужено з'єднань: 41927"
      Tasks: 1 (limit: 4915)
```

`Restart=on-failure` ловить і мовчання сторожового таймера: прострочений пінг менеджер зараховує до невдач, тому окремий `on-watchdog` тут не потрібен. `RestartPreventExitStatus=78` — код `EX_CONFIG` із `sysexits.h`: якщо служба вийшла з ним, конфігурація зіпсована, і підіймати її марно.

Пара `RestartSteps=` з `RestartMaxDelaySec=` (з'явилася у версії 254) робить паузу між спробами зростаючою. Множник система рахує сама:

**Початкова пауза 1 с, стеля 32 с, 5 кроків росту:**

```
множник = (RestartMaxDelaySec / RestartSec) ^ (1 / RestartSteps)
        = (32 / 1) ^ (1/5) = 32^0.2 = 2

спроба 1 → пауза  1 с   (перезапуск на 1-й секунді)
спроба 2 → пауза  2 с   (на 3-й)
спроба 3 → пауза  4 с   (на 7-й)
спроба 4 → пауза  8 с   (на 15-й)
спроба 5 → пауза 16 с   (на 31-й)
далі     → пауза 32 с щоразу
```

І тут-таки перша неприємність, яку видно лише з арифметики. Типовий запобіжник — п'ять спроб за десять секунд. У найгустіші десять секунд цього ряду вміщається чотири спроби (0, 1, 3, 7). Отже, ліміт **не спрацює ніколи**, і служба з битою конфігурацією підійматиметься раз на пів хвилини роками. Зростаюча пауза не заміняє ліміт спроб — вона робить його недосяжним, тому, вмикаючи її, ліміт треба перебирати руками (звузити вікно або взагалі покластися на `RestartPreventExitStatus=`).

## Пастки

**Хто саме шле повідомлення.** Право слати менеджер перевіряє за номером процесу з облікових даних датаграми, а не за UID — тому скидання привілеїв само собою нічого не ламає. Ламає інше: `Type=notify` мовчки виставляє `NotifyAccess=main`, тож датаграма від будь-якого нащадка буде відкинута. Якщо служба відгалужує робітника, який робить `bind`, і `READY=1` шле саме він, старт зависне до `TimeoutStartSec` і закінчиться невдачею — при тому, що порт уже слухається. Ліки: слати з головного процесу, а якщо це справді неможливо — оголосити `NotifyAccess=exec` або `all`.

**Дорога до сокета мусить лишитися.** `NOTIFY_SOCKET` для системних служб — це шлях у файловій системі. Служба, яка сама заходить у [chroot](topic:sys-unix/chroot) або власний простір монтувань після старту, цього шляху вже не побачить, і `sendto` поверне `ENOENT`. Або відкривайте сокет **до** переходу й тримайте дескриптор відкритим, або віддайте ізоляцію менеджеру (`RootDirectory=`), який сам подбає про доступність сокета.

**`MAINPID` при відгалуженні.** Якщо служба таки відгалужується й головним стає нащадок, менеджера треба про це попередити рядком `MAINPID=<номер>` — інакше сторожовий таймер і вирок про вихід стосуватимуться не того процесу. Надіслати цей рядок має ще старий головний процес. Загалом же вибір «`Type=notify` з `MAINPID=`» кращий за «`Type=forking` з `PIDFile=`»: другий повертає в гру pid-файл із усіма його гонками.

**`SIGPIPE` вбиває тихо.** Смерть від `SIGTERM`, `SIGINT`, `SIGHUP` і `SIGPIPE` менеджер зараховує до **успішних** завершень. Отже, служба, яка не заглушила `SIGPIPE`, одного дня напише в з'єднання, яке клієнт щойно закрив, — і зникне без сліду: `Restart=on-failure` не спрацює, бо формально це чистий вихід. Тому в коді стоїть і `signal(SIGPIPE, SIG_IGN)`, і `MSG_NOSIGNAL` на кожному записі — заглушки дублюються навмисно, бо бібліотечний код може повернути обробник на місце.

**Сигнал між перевіркою й очікуванням.** Обробник `SIGTERM` ставить прапорець, але якщо сигнал прийде рівно між `while (!stop_requested)` і входом у `poll`, служба чекатиме до наступної події. Тут це нешкідливо (пінг розбудить цикл щонайпізніше за пів терміну), але правильна розв'язка — [читати сигнали дескриптором](topic:sys-unix/signal-mask-signalfd) і додати його до тих самих `poll`. З тієї ж причини обробник ставиться **без** `SA_RESTART`: інакше `poll` перезапустився б сам і прапорця ніхто б не побачив; у самому ж обробнику можна робити тільки [дуже небагато](topic:sys-unix/async-signal-safety) — присвоєння `sig_atomic_t` до цього небагато належить.

## Ціна

Сорок рядків на весь протокол і три системні виклики раз на пів терміну — на тлі роботи служби це не видно взагалі. Натомість зникає залежність від `libsystemd`, а разом з нею й половина мороки зі статичним складанням. Якщо термін довгий (хвилини), а служба вміє чесно довго стартувати, є ще рядок `EXTEND_TIMEOUT_USEC=`, яким вона просить продовжити таймаут, підтверджуючи цим, що рухається, а не зависла.

## Як перевірити, що воно справді працює

Готовність перевіряють залежним юнітом: підвісьте на нього `After=` і `Requires=`, вставте перед `notify("READY=1…")` затримку на кілька секунд — залежний юніт мусить чекати ці секунди, а не стартувати одразу.

Сторожовий таймер перевіряють штучним зависанням, і найдешевший спосіб — заморозити процес: `systemctl kill -s SIGSTOP` спиняє його, не вбиваючи. Пінги припиняються, менеджер витримує свої тридцять секунд і оголошує службу невдалою. Щоб побачити ще й [аварійний дамп](topic:sys-unix/core-dump) із зупиненими потоками (менеджер б'є `SIGABRT` саме заради нього), заморожування не годиться — сигнал висітиме нерозглянутим; тоді потрібне справжнє зависання в коді, наприклад тимчасовий `sleep` на подвійний термін усередині `serve_one`.

І остання перевірка, яку роблять найрідше, а шкодують найчастіше: зупиніть службу `systemctl stop` і подивіться на код виходу в `systemctl status`. Нуль означає, що `SIGTERM` дійшов до циклу й вихід був свій; будь-що інше — що службу довелося добивати, і ця секунда затримки при кожній зупинці одного дня перетвориться на хвилину при перезавантаженні машини.
