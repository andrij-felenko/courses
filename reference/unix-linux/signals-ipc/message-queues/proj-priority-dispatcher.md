# ⚙️ Диспетчер розпоряджень: служба з двома рангами

Це робоча служба на C — `drived`, невеликий демон, що приймає розпорядження від кількох незалежних програм через POSIX-чергу, виконує аварійні поперед рутинних, нічого не губить мовчки й після падіння не оживає з чужими намірами. Кожна з цих вимог коштує окремого рішення в коді: черга дає механізм, а політику — терміновість, живучість, поведінку на переповненні — доводиться дописувати самому.

Формат розпорядження тут найпростіший: рядок до 256 байтів, а важливість несе не тіло, а пріоритет повідомлення. Умовимось, що все з рангом від 9 і вище — термінове, решта — рутинне.

## Скільки слотів нам узагалі дадуть

Геометрію POSIX-черги фіксують один раз при створенні, і взяти «із запасом» не вийде: обидва числа впираються у стелі, причому в різні й з різними симптомами.

Перша стеля — `RLIMIT_MSGQUEUE`, сумарний обсяг усіх черг реального користувача ([ліміти ресурсів](book:unix-linux/resource-limits) — м'яка й тверда межа на процес, звідки береться типове значення й хто має право його підняти). Ядро рахує не самі байти даних, а й службовий запис на кожен слот; `getrlimit(2)` наводить формулу дослівно:

```
bytes = mq_maxmsg · sizeof(struct msg_msg)
      + min(mq_maxmsg, MQ_PRIO_MAX) · sizeof(struct posix_msg_tree_node)
      + mq_maxmsg · mq_msgsize
```

Друга стеля — `/proc/sys/fs/mqueue/msg_max`, типово **10**: непривілейований процес більшого `mq_maxmsg` не попросить узагалі, хай як багато місця лишає йому ліміт.

**Слот на 256 байтів за типових налаштувань.**

```
RLIMIT_MSGQUEUE (типово)   = 819200 байтів
службове на слот           ≈ sizeof(struct msg_msg)
                           + sizeof(struct posix_msg_tree_node)  ≈ 96 байтів (x86-64)

бюджет цій черзі (пів ліміту) = 409600
слотів за лімітом             = 409600 / (256 + 96) = 1163

/proc/sys/fs/mqueue/msg_max   = 10          ← спрацьовує перша
mq_maxmsg = min(1163, 10)     = 10
```

Ліміт зв'язує руки на товстих слотах, sysctl — на тонких. Помилки при цьому різні: завелике `mq_maxmsg` дає `EINVAL`, а невдалий облік за лімітом — `EMFILE`, той самий код, що й «забагато відкритих файлів». Хто цього не знає, шукає витік дескрипторів там, де насправді вперлися в обсяг черг.

Точні розміри тих двох структур — усередині ядра, вони залежать від архітектури й конфігурації, тому в коді ми беремо їх із запасом, а результат обрізаємо стелею з sysctl:

```c
/* drived.c — служба керування на POSIX-черзі. Збірка: cc -O2 -Wall drived.c -lrt */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <mqueue.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#define SLOT 256L        /* найдовше розпорядження плюс запас */

static long read_long(const char *path, long fallback)
{
    FILE *f = fopen(path, "r");
    long v;
    if (!f) return fallback;
    if (fscanf(f, "%ld", &v) != 1) v = fallback;
    fclose(f);
    return v;
}

static long slots_for(long msgsize)
{
    struct rlimit rl;
    long budget, n, ceiling;

    if (getrlimit(RLIMIT_MSGQUEUE, &rl) == -1) return 10;
    budget  = (rl.rlim_cur == RLIM_INFINITY) ? (1L << 20) : (long)(rl.rlim_cur / 2);
    n       = budget / (msgsize + 128);          /* 128 замість ≈96 — свідомий запас */
    ceiling = read_long("/proc/sys/fs/mqueue/msg_max", 10);
    if (n > ceiling) n = ceiling;
    return n < 1 ? 1 : n;
}
```

## Відкриття: черга могла нас пережити

Черга живе в ядрі окремо від процесів, тож наш демон майже ніколи не бачить чистого поля. Наївне `mq_open` з `O_CREAT` мовчки відкриє те, що лишилося з попереднього запуску, **проігнорувавши переданий `attr`** — і служба працюватиме зі вчорашньою геометрією, не підозрюючи про це. Тому створюємо з `O_EXCL`, ловимо `EEXIST` і після цього дивимося на дійсність через `mq_getattr`:

```c
#define Q_NAME "/drived.cmd"

static mqd_t open_queue(long maxmsg, long msgsize)
{
    struct mq_attr want = { .mq_maxmsg = maxmsg, .mq_msgsize = msgsize };
    struct mq_attr have;
    mqd_t q;

    q = mq_open(Q_NAME, O_RDONLY | O_CREAT | O_EXCL | O_NONBLOCK, 0620, &want);
    if (q != (mqd_t)-1) return q;                 /* поле чисте */
    if (errno != EEXIST) return (mqd_t)-1;        /* EINVAL: maxmsg > msg_max
                                                     EMFILE: не влізли в rlimit */

    q = mq_open(Q_NAME, O_RDONLY | O_NONBLOCK);   /* attr тут не діяв би однаково */
    if (q == (mqd_t)-1) return (mqd_t)-1;
    if (mq_getattr(q, &have) == -1) { mq_close(q); return (mqd_t)-1; }

    if (have.mq_msgsize >= msgsize) {             /* чужа геометрія нам підходить */
        fprintf(stderr, "черга вже є: %ld × %ld\n",
                (long)have.mq_maxmsg, (long)have.mq_msgsize);
        return q;
    }

    /* слот вужчий за наш формат: розпорядження діставали б EMSGSIZE ще на відправленні */
    fprintf(stderr, "слот %ld замалий — створюю чергу заново\n", (long)have.mq_msgsize);
    mq_close(q);
    mq_unlink(Q_NAME);                            /* знімаємо ІМ'Я, а не об'єкт */
    return mq_open(Q_NAME, O_RDONLY | O_CREAT | O_EXCL | O_NONBLOCK, 0620, &want);
}
```

Права `0620` — читання й запис власникові, лише запис групі: виробники кладуть, забирає служба. Як і в `open`, біти проходять крізь `umask`, тож демон із `umask 027` мовчки втратить право групи на запис і потім довго дивуватиметься на `EACCES` у виробників.

## Спадок попереднього запуску

Після `mq_unlink` старе ім'я звільнене, але сам об'єкт живе, доки хтось тримає на нього дескриптор: виробник, який відкрив чергу до перезапуску, і далі складатиме розпорядження — тепер уже в об'єкт-сироту, куди ніхто ніколи не загляне. Ліки не в коді служби, а в дисципліні виробників: відкривати чергу коротко, на час відправлення, або відкривати її наново після невдачі.

А коли геометрія збіглася й ми успадкували чергу з розпорядженнями, потрібна свідома політика. Ознака давності тут дається задарма: **усе, що лежить у черзі на момент старту, надійшло до цього запуску** — жодних міток часу вигадувати не треба. Далі вирішує сенс, якого ядро не знає: віддати виконавцеві аварійне «стоп» невідомо через скільки хвилин після аварії небезпечно, а рутинне «оновити налаштування» ідемпотентне й нешкідливе.

```c
/* Стартове вичерпування: термінові з минулого життя відкидаємо, рутинні переносимо
   на полицю (shelf_put — кільцевий буфер на вісім записів, його код нижче). */
static void carry_over(mqd_t q, char *buf, size_t cap)
{
    long dropped = 0, kept = 0, spilled = 0;

    for (;;) {
        unsigned prio;
        ssize_t n = mq_receive(q, buf, cap, &prio);
        if (n == -1) {
            if (errno == EINTR)  continue;
            if (errno == EAGAIN) break;                /* порожньо — усе розібрано */
            perror("mq_receive"); exit(1);
        }
        if (prio >= PRIO_URGENT)                                 dropped++;
        else if (shelf_put(&routine, prio, buf, (size_t)n))      kept++;
        else                                                     spilled++;
    }
    fprintf(stderr, "старт: відкинуто %ld термінових, %ld рутинних; перенесено %ld\n",
            dropped, spilled, kept);
}
```

## Дві межі: протитиск і справедливість

Тепер найцікавіше. Ядро завжди видає верхівку черги, і `mq_receive` не вміє попросити «щось інше» — отже, рівний потік термінових не залишить рутинним жодного шансу. Справедливість доводиться будувати в процесі: розібрати прочитане на дві полиці за рангом і видавати виконавцеві за власним правилом — чотири термінові, тоді одне рутинне поза чергою.

Тільки тут чигає пастка, у яку легко втрапити з розгону. Якщо перекладати чергу ядра в необмежений список у пам'яті процесу, черга завжди буде порожня — а разом із нею зникне єдине, що гальмувало виробників. Стеля `mq_maxmsg` була не прикрістю, а сигналом ([протитиск](book:algorithms/backpressure) — чому конструкція без зворотного гальмування рано чи пізно або губить дані, або роздувається до вичерпання пам'яті); осушивши чергу, ми той сигнал стерли й перенесли переповнення туди, де його вже ніхто не помітить.

Тому полиці **навмисно крихітні** — вісім записів на ранг. Їхня єдина робота — дати диспетчерові кілька записів на вибір; усе інше має лишатися в ядрі, де воно видиме виробникам.

![Виробники, черга ядра, дві невеликі полиці й диспетчер з квотою: протитиск лишається в ядрі, справедливість додає процес](/reference/unix-linux/signals-ipc/message-queues/img/dispatch-stages.svg)

*Ранг наступного повідомлення наперед невідомий, тому вичерпування спиняється, щойно заповнилася бодай одна полиця.*

```c
#define PRIO_URGENT  9u
#define STAGE        8            /* навмисно мало: протитиск має лишитися в ядрі */
#define URGENT_QUOTA 4

struct order { unsigned prio; size_t len; char body[SLOT]; };
struct shelf { struct order v[STAGE]; int head, n; };

static struct shelf urgent, routine;

/* власне робота служби; тут — заглушка, яка лише показує порядок видачі */
static void execute(const struct order *o)
{
    printf("%s prio %u: %.*s\n", o->prio >= PRIO_URGENT ? "ТЕРМІНОВО" : "рутина",
           o->prio, (int)o->len, o->body);
    fflush(stdout);
}

static int shelf_put(struct shelf *s, unsigned prio, const char *body, size_t len)
{
    struct order *o;
    if (s->n == STAGE) return 0;
    o = &s->v[(s->head + s->n) % STAGE];
    o->prio = prio; o->len = len; memcpy(o->body, body, len);
    s->n++;
    return 1;
}

static int shelf_take(struct shelf *s, struct order *out)
{
    if (s->n == 0) return 0;
    *out = s->v[s->head];
    s->head = (s->head + 1) % STAGE;
    s->n--;
    return 1;
}

/* Читаємо, доки є місце в ОБИДВОХ полицях: ранг наступного запису наперед невідомий. */
static void drain(mqd_t q, char *buf, size_t cap)
{
    for (;;) {
        unsigned prio;
        ssize_t n;

        if (urgent.n == STAGE || routine.n == STAGE) return;

        n = mq_receive(q, buf, cap, &prio);
        if (n == -1) {
            if (errno == EINTR)  continue;
            if (errno == EAGAIN) return;                 /* у ядрі порожньо */
            perror("mq_receive"); exit(1);
        }
        shelf_put(prio >= PRIO_URGENT ? &urgent : &routine, prio, buf, (size_t)n);
    }
}

static int dispatch_one(void)
{
    static int streak = 0;
    struct order o;

    if (urgent.n && streak < URGENT_QUOTA) { shelf_take(&urgent,  &o); streak++;   }
    else if (routine.n)                    { shelf_take(&routine, &o); streak = 0; }
    else if (urgent.n)                     { shelf_take(&urgent,  &o);             }
    else return 0;

    execute(&o);
    return 1;
}
```

## Головний цикл

Сповіщення `mq_notify` спрацьовує лише на краю «порожньо → непорожньо» й лише один раз, тож реєстрація мусить передувати вичерпуванню. Наш цикл робить за оберт рівно три речі: озброює сторожа, забирає з ядра все, що вміщається, і виконує **одне** розпорядження. Спати він має право тільки тоді, коли обидві полиці порожні — а це, за побудовою `drain`, можливо лише після зупинки на `EAGAIN`. Так безвихідний сон над непорожньою чергою просто не має де виникнути.

```c
static void on_notify(int sig) { (void)sig; }   /* тіло не потрібне: будить sigsuspend */

int main(void)
{
    long msgsize = SLOT, maxmsg = slots_for(SLOT);
    struct sigaction sa;
    struct sigevent sev;
    struct mq_attr attr;
    sigset_t block, awake;
    char *buf;
    mqd_t q;

    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_notify;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGRTMIN, &sa, NULL);             /* SIGRTMIN нічий: не збігається
                                                   ні з бібліотечним, ні з прикладним */
    sigemptyset(&block);
    sigaddset(&block, SIGRTMIN);
    sigprocmask(SIG_BLOCK, &block, &awake);     /* awake — стара маска, без SIGRTMIN */

    q = open_queue(maxmsg, msgsize);
    if (q == (mqd_t)-1) { perror("mq_open"); return 1; }

    /* Буфер мусить бути не менший за mq_msgsize — інакше EMSGSIZE навіть
       на восьмибайтовому «стоп». Розмір питаємо в самої черги: вона могла
       дістатися нам від попереднього запуску з іншим слотом. */
    mq_getattr(q, &attr);
    buf = malloc(attr.mq_msgsize);
    if (!buf) { perror("malloc"); return 1; }

    carry_over(q, buf, attr.mq_msgsize);

    memset(&sev, 0, sizeof sev);
    sev.sigev_notify = SIGEV_SIGNAL;
    sev.sigev_signo  = SIGRTMIN;

    for (;;) {
        if (mq_notify(q, &sev) == -1 && errno != EBUSY) { perror("mq_notify"); return 1; }

        drain(q, buf, attr.mq_msgsize);

        if (dispatch_one()) continue;           /* є робота — і назад по нову порцію */
        sigsuspend(&awake);                     /* сон лише з порожніми полицями */
    }
}
```

`EBUSY` тут не помилка, а звичайний стан: доки сповіщення не спрацювало, реєстрація ще діє, і повторний `mq_notify` просто каже про це. Зворотний випадок — сповіщення надійшло під час виконання розпорядження — дає одне зайве пробудження: сигнал лежить у стані очікування, `sigsuspend` віддає його негайно, `drain` бачить порожньо, цикл засинає знову. Нічого не ламається.

## Виробник: гальмувати, а не губити

На повній черзі `mq_send` блокується, а з `O_NONBLOCK` — повертає `EAGAIN`. Обидва варіанти правильні, неправильний лише третій: не подивитися на код повернення. Служба, яка «іноді не виконує розпоряджень», майже завжди виявляється саме цим.

```c
/* виробник відкрив чергу БЕЗ O_NONBLOCK: mq_timedsend має право почекати */
static int send_order(mqd_t q, const char *body, size_t len, unsigned prio)
{
    struct timespec deadline;
    clock_gettime(CLOCK_REALTIME, &deadline);   /* саме REALTIME: так вимагає POSIX */
    deadline.tv_sec += 2;

    for (;;) {
        if (mq_timedsend(q, body, len, prio, &deadline) == 0) return 0;
        if (errno == EINTR)     continue;       /* сигнал — просто повторюємо */
        if (errno == ETIMEDOUT) return -1;      /* приймач стоїть: це тривога, не тиша */
        return -1;                              /* EMSGSIZE — помилка нашого формату */
    }
}
```

`mq_timedsend` перетворює протитиск на обмежене чекання: дві секунди ми гальмуємо разом зі службою, а далі повідомляємо, що вона не встигає. Кому блокуватися не можна взагалі — обробникові кнопки, реальночасовому циклу — той бере `O_NONBLOCK` і на `EAGAIN` ухвалює рішення на місці: відкинути найменш важливе, злити на диск, підняти тривогу.

> 🔧 **Навіщо це.** Дві межі цієї служби — стеля черги й розмір полиці — насправді одна конструкція: місце, де швидкість виробників упирається в швидкість споживача. Пересунувши її вглиб процесу, ви не прискорите систему, а лише зробите переповнення невидимим — і воно проявиться як тихо втрачені розпорядження за кілька тижнів.

## Варіант через epoll

Щойно поряд із чергою з'явиться сокет чи таймер, сигнальна конструкція стає затісною: `sigsuspend` чекає на одну подію. На Linux `mqd_t` — звичайний файловий дескриптор, тож чергу можна покласти в `epoll` разом з усім іншим ([select, poll, epoll](book:unix-linux/select-poll-epoll) — очікування готовності багатьох джерел в одній точці програми):

```c
int ep = epoll_create1(EPOLL_CLOEXEC);
struct epoll_event want = { .events = EPOLLIN, .data.fd = (int)q };
epoll_ctl(ep, EPOLL_CTL_ADD, (int)q, &want);

for (;;) {
    struct epoll_event got[8];
    int n = epoll_wait(ep, got, 8, -1);
    if (n == -1) { if (errno == EINTR) continue; perror("epoll_wait"); return 1; }

    for (int i = 0; i < n; i++)
        if (got[i].data.fd == (int)q) {
            drain(q, buf, attr.mq_msgsize);
            while (dispatch_one()) ;
        }
}
```

Тут зникає вся морока з краєм: `epoll` за замовчуванням сповіщає за рівнем, тобто повторюватиме «є що читати», доки черга непорожня, і пропустити нічого не можна навіть помилившись із порядком. Заплачено за це портативністю — приведення `mqd_t` до `int` і чекання на дескриптор черги є розширенням Linux, якого стандарт не обіцяє: на FreeBSD чи Solaris лишається `mq_notify`.

## Де воно ламається

- **Буфер `mq_receive`.** Менший за `mq_msgsize` — `EMSGSIZE`, незалежно від того, що лежить у черзі. Розмір беруть у `mq_getattr`, а не з власних уявлень.
- **`attr` на наявній черзі.** Ігнорується без жодного натяку. Єдина надійна перевірка — `O_EXCL` плюс `mq_getattr`.
- **`EINTR`.** `mq_receive`, `mq_send` і їхні `timed`-варіанти перериваються сигналом, але, на відміну від `msgrcv`/`msgsnd` із System V, **перезапускаються** обробником із `SA_RESTART` ([EINTR](book:unix-linux/eintr-and-restart) — коли виклик повертає помилку лише через сигнал і що робить прапорець `SA_RESTART`). Покладатися на це в чужому коді не варто: цикл `if (errno == EINTR) continue;` коштує один рядок і працює скрізь.
- **Реєстрація `mq_notify`.** Одна на чергу в цілій системі (`EBUSY` другому), належить процесові, не успадковується через `fork` і зникає із закриттям дескриптора. Читач, що вже спить у `mq_receive`, забирає повідомлення поперед будь-якої реєстрації.
- **Обробник сигналу.** Наш порожній — і це не випадковість: у ньому не можна ні писати в полиці, ні викликати `printf` ([що можна в обробнику](book:unix-linux/async-signal-safety) — перелік async-signal-safe функцій і чому решта здатна зіпсувати стан у довільний спосіб).
- **Хто робить `mq_unlink`.** Наша служба не видаляє чергу при виході навмисно — саме тому розпорядження переживають перезапуск. Прибирає її або оператор (`rm /dev/mqueue/drived.cmd`, коли примонтовано `mqueue`), або юніт із `ExecStopPost`, коли політика вимагає чистого аркуша.
- **Ціна.** Один зайвий `mq_notify` на оберт циклу — кілька сотень наносекунд поряд із двома копіями й двома переходами в ядро на кожне повідомлення. Для потоку розпоряджень це не видно взагалі; було б видно, якби через чергу йшли кадри.
