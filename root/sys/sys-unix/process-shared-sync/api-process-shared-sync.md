# 📋 Контракт процесних примітивів: підписи, атрибути, коди повернення

Довідка для звіряння: повний перелік викликів, якими синхронізують окремі процеси — спільний м'ютекс з умовною змінною та POSIX-семафори, — з усіма атрибутами, кодами відмови і **зобов'язанням, яке кожен із них накладає на код**. Потрібна тоді, коли обгортку вже написано й треба точно знати, що саме повернув виклик, чи тримаєте ви замок після цього і що зобов'язані зробити далі.

Родини дві, і різняться вони не лише набором імен. Різні в них навіть угоди про те, як повідомити відмову — і саме на цьому найчастіше розсипається обробка помилок.

## Дві угоди про відмову

| Родина | Успіх | Відмова | `errno` |
|---|---|---|---|
| `pthread_*` | `0` | **повертає** додатний номер помилки | не чіпає |
| `sem_*` | `0` (крім `sem_open`) | `-1` | ставить |
| `sem_open` | покажчик | `SEM_FAILED` | ставить |

Наслідків три, і всі три коштують налагодження. По-перше, `perror()` після `pthread_mutex_lock` друкує чужу помилку — ту, що лежала в `errno` від попереднього виклику; розбирати треба **повернене значення**, а текст брати `strerror(r)`. По-друге, звична згортка `if (r) goto fail;` тут хибна: `EOWNERDEAD` — це **успіх** із попередженням, і замок після нього ваш. По-третє, `sem_*` перериваються сигналом, а `pthread_*` — ні: жоден із викликів захоплення м'ютекса чи чекання на умові не повертає `EINTR` ніколи, тож цикл перезапуску потрібен рівно семафорам ([EINTR і перезапуск](root:sys-unix/eintr-and-restart)).

---

## Атрибути м'ютекса

```c
#include <pthread.h>          /* збірка: cc … -pthread */

int pthread_mutexattr_init   (pthread_mutexattr_t *attr);
int pthread_mutexattr_destroy(pthread_mutexattr_t *attr);

int pthread_mutexattr_setpshared    (pthread_mutexattr_t *attr, int pshared);
int pthread_mutexattr_setrobust     (pthread_mutexattr_t *attr, int robustness);
int pthread_mutexattr_setprotocol   (pthread_mutexattr_t *attr, int protocol);
int pthread_mutexattr_settype       (pthread_mutexattr_t *attr, int type);
int pthread_mutexattr_setprioceiling(pthread_mutexattr_t *attr, int ceiling);
```

Кожен `set` має двійника `get` із покажчиком на вихід замість значення. Усі `set` повертають `0` або `EINVAL` на нерозпізнане значення; `pthread_mutexattr_init` може ще й не дістати пам'яті — `ENOMEM`.

| Атрибут | Значення | Усталено | Що змінює |
|---|---|---|---|
| `pshared` | `PTHREAD_PROCESS_PRIVATE` (0) · `PTHREAD_PROCESS_SHARED` (1) | `PRIVATE` | ключ, за яким ядро шукає чергу очікувачів: від адреси або від самої сторінки |
| `robustness` | `PTHREAD_MUTEX_STALLED` (0) · `PTHREAD_MUTEX_ROBUST` (1) | `STALLED` | чи буде наступний захоплювач сповіщений про смерть власника |
| `protocol` | `PTHREAD_PRIO_NONE` · `PTHREAD_PRIO_INHERIT` · `PTHREAD_PRIO_PROTECT` | `NONE` | спадкування пріоритету або стеля пріоритету ([інверсія пріоритетів](root:sf-os/priority-inversion)) |
| `type` | `NORMAL` · `ERRORCHECK` · `RECURSIVE` · `DEFAULT` | `DEFAULT` (у glibc = `NORMAL`) | чи виявляються повторне захоплення й чуже звільнення |
| `prioceiling` | число зі шкали `SCHED_FIFO` | залежить від системи | стеля лише для `PRIO_PROTECT` |

Два практичні зауваження про сам об'єкт атрибутів. Він **не** мусить лежати у спільному сегменті: його читають рівно один раз, усередині `pthread_mutex_init`, і далі він не потрібен — звичайна змінна на стеку створювача. І `PTHREAD_MUTEX_INITIALIZER` тут не годиться в принципі: статичний ініціалізатор дає `PROCESS_PRIVATE` і `STALLED`, тобто рівно ті два усталені значення, від яких ми тікаємо.

`PRIO_INHERIT` діє лише на задачах із політиками реального часу; для звичайної `SCHED_OTHER` піднімати нема чого ([пріоритети, nice і реальний час](root:sys-unix/priority-nice-realtime)).

## Створення й знищення

```c
int pthread_mutex_init   (pthread_mutex_t *restrict mutex,
                          const pthread_mutexattr_t *restrict attr);
int pthread_mutex_destroy(pthread_mutex_t *mutex);
```

| Код | Виклик | Значення |
|---|---|---|
| `EAGAIN` | `init` | забракло внутрішніх ресурсів на ще один примітив |
| `ENOMEM` | `init` | забракло пам'яті |
| `EPERM` | `init` | немає прав на задані атрибути (типово — стеля пріоритету) |
| `ENOTSUP` | `init` | реалізація не тягне саме цю комбінацію атрибутів |
| `EBUSY` | `init`, `destroy` | `init` — над уже ініціалізованим; `destroy` — над захопленим або таким, на якому хтось чекає |
| `EINVAL` | обидва | зіпсовані атрибути або не м'ютекс |

`destroy` робить один учасник — той, хто створював, і лише після того, як решта припинили користуватися. Знищення захопленого чи очікуваного м'ютекса — невизначена поведінка навіть тоді, коли `EBUSY` не повернувся.

## Захоплення й звільнення

```c
int pthread_mutex_lock      (pthread_mutex_t *mutex);
int pthread_mutex_trylock   (pthread_mutex_t *mutex);
int pthread_mutex_timedlock (pthread_mutex_t *restrict mutex,
                             const struct timespec *restrict abstime);
int pthread_mutex_clocklock (pthread_mutex_t *restrict mutex, clockid_t clockid,
                             const struct timespec *restrict abstime);
int pthread_mutex_unlock    (pthread_mutex_t *mutex);
int pthread_mutex_consistent(pthread_mutex_t *mutex);
```

`abstime` — **абсолютна** мить, не тривалість. `timedlock` завжди міряє її за `CLOCK_REALTIME`, який можна перевести; `clocklock` бере годинник аргументом і приймає `CLOCK_REALTIME` або `CLOCK_MONOTONIC`, інший — `EINVAL` ([годинники ядра](root:sys-unix/kernel-timekeeping)). У glibc `pthread_mutex_clocklock` оголошено під `_GNU_SOURCE`; без макроса це помилка **компіляції**, а не поведінки.

Головна таблиця. Стовпець «замок» відповідає на єдине питання, від якого залежить увесь подальший код: ви всередині чи ні.

| Код | Замок | Зобов'язання коду |
|---|---|---|
| `0` | ваш | працювати й звільнити |
| `EOWNERDEAD` | **ваш** | стан під замком лишив по собі мрець. Полагодити → `pthread_mutex_consistent()` → `unlock`. Або `unlock` без підтвердження — і замок стає непридатним **назавжди** |
| `ENOTRECOVERABLE` | ні, і не буде | цілісність ніхто не підтвердив. Єдина дозволена дія — `pthread_mutex_destroy` і перестворення примітиву за згодою всіх учасників |
| `ETIMEDOUT` | ні | строк минув; входити не можна |
| `EBUSY` | ні | лише від `trylock`: зайнято зараз |
| `EAGAIN` | ні | вичерпано лічильник рекурсії в `RECURSIVE` |
| `EDEADLK` | ні | `ERRORCHECK`: цей м'ютекс уже ваш; або виявлено цикл очікування ([взаємне блокування](root:sf-tasks/deadlock)) |
| `EPERM` | не змінився | лише від `unlock`: віддаєте не свій. Помічається тільки на `ERRORCHECK`, `RECURSIVE` та живучих |
| `EINVAL` | ні | не м'ютекс · `abstime.tv_nsec` поза `[0, 999999999]` · невідомий `clockid` · пріоритет викликача вищий за стелю `PRIO_PROTECT` |

`pthread_mutex_consistent` повертає `EINVAL`, якщо м'ютекс не живучий або не позначений як лишений мерцем. Це другий бік того самого зобов'язання: підтверджувати цілісність можна рівно один раз і рівно тоді, коли її під сумнівом поставили.

## Умовна змінна

```c
int pthread_condattr_setpshared(pthread_condattr_t *attr, int pshared);
int pthread_condattr_setclock  (pthread_condattr_t *attr, clockid_t clock_id);

int pthread_cond_init     (pthread_cond_t *restrict cond,
                           const pthread_condattr_t *restrict attr);
int pthread_cond_destroy  (pthread_cond_t *cond);
int pthread_cond_wait     (pthread_cond_t *restrict cond,
                           pthread_mutex_t *restrict mutex);
int pthread_cond_timedwait(pthread_cond_t *restrict cond,
                           pthread_mutex_t *restrict mutex,
                           const struct timespec *restrict abstime);
int pthread_cond_clockwait(pthread_cond_t *restrict cond,
                           pthread_mutex_t *restrict mutex, clockid_t clockid,
                           const struct timespec *restrict abstime);
int pthread_cond_signal   (pthread_cond_t *cond);
int pthread_cond_broadcast(pthread_cond_t *cond);
```

`pshared` бере ті самі два значення, що й у м'ютекса, і його треба ставити окремо: спільний м'ютекс зі звичайною умовною змінною — та сама поломка, лише в другій половині пари.

`clock_id` приймає `CLOCK_REALTIME` (усталено) або `CLOCK_MONOTONIC`; годинник процесорного часу дає `EINVAL`. Тут є структурна відмінність від м'ютекса, яку легко проґавити: `pthread_cond_timedwait` міряє строк **за годинником умовної змінної**, заданим при створенні, а не жорстко за `CLOCK_REALTIME`. Тобто для умовної змінної монотонний строк доступний і без glibc 2.30 — через атрибут.

Коди чекання й те саме питання «чи ваш замок»:

| Код | М'ютекс після повернення | Зобов'язання |
|---|---|---|
| `0` | ваш | перевірити умову наново — пробудження бувають хибні |
| `ETIMEDOUT` | **ваш** | строк минув, але замок перезахоплено. Треба звільнити |
| `EOWNERDEAD` | **ваш** | власник помер, поки ви спали: лагодити, підтверджувати, звільняти |
| `ENOTRECOVERABLE` | ні | пару м'ютекс-умова треба перестворювати |
| `EPERM` | не ваш | ви не тримали м'ютекс, входячи в чекання |
| `EINVAL` | невизначено | на одну умовну змінну одночасно подано **різні** м'ютекси · зіпсований `abstime` · невідомий `clockid` |

Звідси правило: із чекання **не виходять по `if (r) return`**. Три з шести кодів лишають замок захопленим, і поспішний вихід або губить його назавжди, або лишає невідновлений стан.

`signal` і `broadcast` не вимагають тримати м'ютекс і не повертають `EOWNERDEAD` — вони нічого не захоплюють.

## Семафори

```c
#include <semaphore.h>

int    sem_init     (sem_t *sem, int pshared, unsigned int value);
int    sem_destroy  (sem_t *sem);
sem_t *sem_open     (const char *name, int oflag,
                     ... /* mode_t mode, unsigned int value */);
int    sem_close    (sem_t *sem);
int    sem_unlink   (const char *name);

int    sem_wait     (sem_t *sem);
int    sem_trywait  (sem_t *sem);
int    sem_timedwait(sem_t *restrict sem,
                     const struct timespec *restrict abs_timeout);
int    sem_clockwait(sem_t *restrict sem, clockid_t clockid,
                     const struct timespec *restrict abs_timeout);
int    sem_post     (sem_t *sem);
int    sem_getvalue (sem_t *restrict sem, int *restrict sval);
```

`pshared` у `sem_init` — не пара іменованих сталих, а просто «нуль чи ні»: ненульове означає «між процесами», і тоді сама структура `sem_t` мусить лежати у спільному відображенні ([спільна пам'ять POSIX](root:sys-unix/posix-shared-memory)). Ініціалізувати вже ініціалізований семафор — невизначена поведінка, тож правило «ініціалізує творець сегмента» тут таке саме, як для м'ютекса.

Іменований семафор спільної пам'яті не потребує зовсім. Ім'я — рядок вигляду `/ім'я`: початкова скісна риска, далі від одного до `NAME_MAX-4` (251) символів без скісних рисок; фізично це файл `sem.ім'я` у `/dev/shm`.

| `oflag` | Ім'я вже є | Імені немає |
|---|---|---|
| `0` | відкрити наявний | `ENOENT` |
| `O_CREAT` | відкрити наявний, `mode` і `value` **ігноруються** | створити зі значенням `value` |
| `O_CREAT \| O_EXCL` | `EEXIST` | створити |

`mode` задають як для `open(2)` і накладають `umask`; для двох програм від різних користувачів це означає `0666` плюс продумані права на теку, а не `0600`. `sem_close` закриває лише ваш доступ, `sem_unlink` прибирає ім'я — сам об'єкт зникає, коли його закрив останній користувач. Без `sem_unlink` семафор переживає всі процеси й доживає до перезавантаження, тож наступний запуск має шанс підхопити лічильник із чужим значенням.

Коди відмови (тут угода інша: `-1` і `errno`):

| Код | Де | Значення |
|---|---|---|
| `EINTR` | `wait`, `timedwait`, `clockwait` | чекання обірвав обробник сигналу. **Виклик перезапускають** — до того самого абсолютного строку |
| `EAGAIN` | `trywait` | лічильник зараз нуль |
| `ETIMEDOUT` | `timedwait`, `clockwait` | строк минув |
| `EOVERFLOW` | `post` | значення перевищило б `SEM_VALUE_MAX` |
| `ENOSYS` | `init` | `pshared` ненульовий, а система не вміє процесних семафорів |
| `EINVAL` | усі | не семафор · `value` більше за `SEM_VALUE_MAX` · `tv_nsec` поза `[0, 999999999]` · невідомий `clockid` · зіпсоване ім'я |
| `EEXIST`, `ENOENT`, `EACCES`, `ENAMETOOLONG`, `EMFILE`, `ENFILE`, `ENOMEM` | `open` | звичайні відмови іменованого об'єкта: уже є · немає · немає прав · задовге ім'я · вичерпано дескриптори · немає пам'яті |

`sem_timedwait` жорстко прив'язаний до `CLOCK_REALTIME`; вибір годинника дає лише `sem_clockwait`, і він приймає `CLOCK_REALTIME` або `CLOCK_MONOTONIC`.

`sem_getvalue` придатний тільки для діагностики: значення може змінитися ще до повернення з виклику. Коли на семафорі є сплячі, Linux кладе в `sval` нуль — POSIX дозволяє й від'ємне число з кількістю очікувачів, тож на знак покладатися непортабельно.

`sem_destroy` стосується лише семафорів від `sem_init`. Для іменованих пара інша — `sem_close` і `sem_unlink`; знищувати іменований через `sem_destroy` не можна.

Покажчик, який віддає `sem_open`, чинний **лише у вашому процесі**: це адреса відображення, зробленого саме цим викликом. Передати його сусідові неможливо — сусід відкриває той самий семафор своїм `sem_open` за тим самим іменем. Безіменний семафор передається протилежним способом: через пам'ять, тож після `fork()` дитина бачить його тоді й лише тоді, коли він лежить у спільному відображенні; у звичайній купі кожна половина після розгалуження працює з власною копією лічильника й жодної помилки при цьому не отримує.

І окремо: `sem_post` — єдина з усіх перелічених тут операцій, яку дозволено викликати з обробника сигналу ([що можна робити в обробнику сигналу](root:sys-unix/async-signal-safety)).

Три речі, яких у контракті немає взагалі, і шукати їх марно. Жодна функція обох родин не повідомляє **власника** — ні номера процесу, ні задачі; `EOWNERDEAD` каже «попередній помер», але не каже хто. У семафорів немає ані живучості, ані спадкування пріоритету — обидва механізми стоять на понятті власника, якого семафор не має. І `sem_getvalue` не є перевіркою «чи можна брати»: між ним і `sem_wait` немає жодної неподільності, тож пара з них — це готові перегони, а не `trywait`.

## Доступність

| Що | Відколи | Примітка |
|---|---|---|
| `pthread_mutexattr_setpshared`, `pthread_condattr_setpshared` | POSIX.1-2001, будь-яка glibc з NPTL | базовий рівень |
| `pthread_condattr_setclock` | POSIX.1-2001 | монотонний строк для умовної змінної без нових функцій |
| `pthread_mutexattr_setrobust_np`, `pthread_mutex_consistent_np` | glibc **2.4** | застарілі з glibc 2.34 |
| `pthread_mutexattr_setrobust`, `pthread_mutex_consistent` | glibc **2.12** | безсуфіксні імена з POSIX.1-2008 |
| `set_robust_list` у ядрі | Linux 2.6.17 | без нього живучість не працює; від 2.6.28 сповіщення охоплює й `execve` |
| PI-futex (`PTHREAD_PRIO_INHERIT`) | Linux 2.6.18 | потребує окремої розкладки слова стану |
| `pthread_mutex_clocklock`, `pthread_cond_clockwait`, `sem_clockwait` | glibc **2.30** | потребують `_GNU_SOURCE`; ухвалені в POSIX.1-2024 |

## Макроси перевірки можливостей

```c
#include <unistd.h>
```

| Макрос | Виклик `sysconf` | Про що |
|---|---|---|
| `_POSIX_THREAD_PROCESS_SHARED` | `_SC_THREAD_PROCESS_SHARED` | атрибут `pshared` узагалі підтримується |
| `_POSIX_THREAD_PRIO_INHERIT` | `_SC_THREAD_PRIO_INHERIT` | `PTHREAD_PRIO_INHERIT` підтримується |
| `_POSIX_THREAD_PRIO_PROTECT` | `_SC_THREAD_PRIO_PROTECT` | `PTHREAD_PRIO_PROTECT` і стеля пріоритету |
| `_POSIX_SEMAPHORES` | `_SC_SEMAPHORES` | родина `sem_*` є |

Читати їх треба за тризначною угодою POSIX, а не як звичайний `#ifdef`: макрос не визначено або він дорівнює `-1` — можливості немає; додатне число — є завжди; **нуль** — питати `sysconf()` під час виконання, бо відповідь залежить від конкретної системи.

На glibc з Linux усі чотири мають додатні значення, тож перевірка часу компіляції тут не відсіює нічого. Реальні перевірки інші: наявність живучих м'ютексів вирішує версія glibc з таблиці вище, наявність `clocklock`/`clockwait` — теж, а придатність процесних семафорів чесно перевіряється лише під час виконання, за `ENOSYS` від `sem_init`.

## Мінімальний робочий виклик

Обгортка нижче містить рівно ті три місця, де контракт живучого спільного м'ютекса порушують найчастіше: розбір **поверненого** значення замість `errno`, `EOWNERDEAD` як успіх і свідоме рішення в разі невдалого лагодження.

```c
#define _GNU_SOURCE
#include <errno.h>
#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

struct hdr { pthread_mutex_t lock; /* … далі дані, які захищає замок … */ };

int  repair(struct hdr *h);        /* привести стан до ладу; 0 — вдалося */
void work  (struct hdr *h);

/* 0 — усередині, стан цілий;  1 — усередині, стан треба лагодити;
  -1 — не ввійшли, причина в *err. */
static int robust_lock(pthread_mutex_t *m, long ms, int *err)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);           /* монотонний: перевід годинника не страшний */
    ts.tv_nsec += (ms % 1000) * 1000000L;
    ts.tv_sec  += ms / 1000 + ts.tv_nsec / 1000000000L;
    ts.tv_nsec %= 1000000000L;

    int r = pthread_mutex_clocklock(m, CLOCK_MONOTONIC, &ts);
    if (r == 0)          return 0;
    if (r == EOWNERDEAD) return 1;                 /* замок наш, дані під сумнівом */
    *err = r;            return -1;                /* ETIMEDOUT / ENOTRECOVERABLE / EINVAL */
}

int use_segment(struct hdr *h)
{
    int err = 0;
    int st  = robust_lock(&h->lock, 200, &err);

    if (st < 0) {
        fprintf(stderr, "не ввійшли: %s\n", strerror(err));  /* НЕ perror */
        return -1;
    }
    if (st == 1) {
        if (repair(h) != 0) {                  /* полагодити не вдалося */
            pthread_mutex_unlock(&h->lock);    /* далі всім — ENOTRECOVERABLE */
            return -1;
        }
        pthread_mutex_consistent(&h->lock);    /* знімаємо тавро */
    }

    work(h);
    pthread_mutex_unlock(&h->lock);
    return 0;
}
```

Семафорний бік має іншу форму саме через другу угоду про відмову — цикл навколо `EINTR`:

```c
#include <fcntl.h>          /* O_CREAT */
#include <semaphore.h>
#include <sys/stat.h>       /* права 0666 */

sem_t *s = sem_open("/frames", O_CREAT, 0666, 0);
if (s == SEM_FAILED) { perror("sem_open"); return 1; }   /* тут perror доречний */

struct timespec ts;
clock_gettime(CLOCK_MONOTONIC, &ts);
ts.tv_sec += 2;                                /* абсолютний строк, не тривалість */

int r;
while ((r = sem_clockwait(s, CLOCK_MONOTONIC, &ts)) == -1 && errno == EINTR)
    ;                                          /* строк той самий — цикл не подовжує чекання */

if (r == -1 && errno == ETIMEDOUT)
    fputs("порція роботи так і не з'явилася\n", stderr);
```

Строк обчислюють **до** циклу й не перераховують усередині: інакше кожен сигнал відсуватиме межу, і тайм-аут перестане бути тайм-аутом.
