# ⚙️ Обробка перерваних викликів і патерн повтору в системному коді

У класичних Unix-подібних операційних системах системний виклик, що очікує на дані з повільного джерела (сокета, каналу pipe, термінала або таймера), може бути перерваний надходженням асинхронного сигналу. Замість того щоб самостійно відновити операцію після завершення обробника сигналу, ядро перериває виконання, повертає значення `-1` і записує в глобальну змінну `errno` константу `EINTR` (англ. *Interrupted System Call* — перерваний системний виклик, числове значення `4` у заголовку `<errno.h>`).

Якщо прикладний код не перевіряє цей випадок, програма випадково скидає мережеві з'єднання або падає з фатальною помилкою вводу-виводу щоразу, коли процес отримує системний сигнал — наприклад, під час зміни розміру вікна термінала (`SIGWINCH`), спрацьовування таймера профілювання, приходу сигналу дочірнього процесу (`SIGCHLD`) або взаємодії з демонами керування конфігурацією (`SIGHUP`). Розберімо внутрішню механіку цього збою, крайові випадки часткового передавання даних, роботу з інтервальними таймерами, взаємодію з неблокуючим вводом-виводом (`O_NONBLOCK`), діагностику через `strace`, межі системних прапорців перезапуску, еволюцію системних викликів мультиплексування (`pselect`/`ppoll`/`signalfd`) та написання стійких типізованих обгорток у C та C++.

## Повільні та швидкі виклики: коли виникає блокування

Не кожен системний виклик піддається перериванню. Стандарт POSIX чітко розмежовує операції на дві принципово різні категорії за критерієм їхньої взаємодії з планувальником ядра:

1. **Швидкі системні виклики (fast syscalls)**. Це операції, які працюють виключно з оперативною пам'яттю ядра або локальними дисковими файлами через системний кеш сторінок (page cache). Приклади: `getpid()`, `gettimeofday()`, звичайне читання зі збереженого на локальному накопичувачі файлу. Навіть якщо диск виконує апаратне читання через контролер DMA, час очікування вважається детермінованим і коротким. Ядро виконує такий виклик неподільно (атомарно) щодо сигналів користувача: сигнал зберігається в черзі очікування процесу і доставляється лише після того, як виклик повністю завершив роботу та повернув результат у регістри процесора.
2. **Повільні системні виклики (slow syscalls)**. Це операції, які можуть заблокувати потік виконання на невизначений термін, очікуючи на зовнішню подію або дію іншого процесу чи мережевого вузла. До них належать:
   * Читання з каналу між процесами (`read()` з pipe або FIFO), коли в буфері немає готових байтів.
   * Очікування вхідних даних із мережевого сокета (`read()`, `recv()`, `recvfrom()`, `recvmsg()`).
   * Запис у заповнений сокет чи канал (`write()`, `send()`, `sendto()`), коли буфер передавання вичерпано.
   * Очікування відкриття каналу FIFO іншим процесом (`open()` у блокуючому режимі без прапорця `O_NONBLOCK`).
   * Очікування завершення дочірнього процесу (`wait()`, `waitpid()`, `waitid()`).
   * Очікування подій мультиплексованого вводу-виводу (`select()`, `poll()`, `epoll_wait()`, `epoll_pwait()`).
   * Операції з міжпроцесними блокуваннями, м'ютексами та чергами повідомлень (`sem_wait()`, `msgrcv()`, `msgsnd()`, блокуючі блокування файлів через `fcntl(F_SETLKW)`).
   * Системні паузи та інтервальні затримки (`pause()`, `sigsuspend()`, `nanosleep()`, `clock_nanosleep()`).

Коли потік блокується на повільному виклику, планувальник ядра переводить його зі стану виконання (state `TASK_RUNNING`) у стан сну з можливістю переривання (state `TASK_INTERRUPTIBLE`). Потік припиняє споживати процесорний час і додається до черги очікування на об'єкті драйвера.

## Анатомія переривання: шлях від сигналу до простору користувача

Розгляньмо покроково, що відбувається на рівні процесора та ядра операційної системи, коли сплячому процесу надходить сигнал (наприклад, `SIGUSR1` або `SIGALRM`):

```
+-------------------+      1. Сигнал      +--------------------+
|  Джерело сигналу  | ------------------> | Черга очікуваних   |
| (kill/таймер/HW)  |                     | сигналів у ядрі    |
+-------------------+                     +--------------------+
                                                     |
                                                     | 2. Пробудження потоку
                                                     v
+-------------------+      3. Повернення  +--------------------+
| Простір           | <------------------ | Переривання IO     |
| користувача       |    -1, EINTR        | Скидання контексту |
+-------------------+                     +--------------------+
         |
         | 4. Виклик signal_handler() на стеку користувача
         v
+-------------------+      5. sigreturn   +--------------------+
| Обробник сигналу  | ------------------> | Повернення в точку |
| завершено         |                     | виклику користувача|
+-------------------+                     +--------------------+
```

1. **Генерація сигналу**. Сигнал створюється апаратним перериванням (таймер), іншим процесом через виклик `kill()` або самим ядром. Ядро встановлює відповідний біт у бітовій масці очікуваних сигналів структури `task_struct` цільового процесу.
2. **Пробудження потоку**. Ядро виявляє, що потік перебуває у стані `TASK_INTERRUPTIBLE`. Планувальник вилучає потік із черги очікування драйвера пристрою і переводить його назад у чергу готових до виконання потоків (`TASK_RUNNING`).
3. **Вихід із ядра зі скиданням**. Потік отримує квант часу процесора. Замість того щоб тримати відкриту транзакцію в драйвері та зберігати вказівники на буфери, ядро встановлює повертане значення регістру результату процесора (регістр `RAX` на архітектурі x86-64) у `-EINTR` і завершує системний виклик.
4. **Формування користувацького кадру стека**. Перед поверненням у простір користувача ядро підміняє контекст виконання: воно записує на стек користувача структуру контексту (збережені регістри процесора) і налаштовує вказівник інструкцій процесора (регістр `RIP`) на адресу зареєстрованого обробника сигналу.
5. **Виконання обробника**. Потік починає виконувати код функції-обробника у просторі користувача.
6. **Системний виклик `sigreturn`**. Після виходу з обробника сигналу спеціальний системний виклик `sigreturn()` відновлює початковий стан процесора. Керування повертається в точку програми, де було викликано `read()`. На рівні мови C функція бібліотеки повертає `-1`, а глобальна змінна `errno` містить значення `EINTR`.

З погляду ядра такий підхід є бездоганно простим: ядро не підтримує складних машин стану, не розмотує стеки драйверів і не намагається вгадати, чи безпечно продовжувати ввід-вивід після довільного коду обробника сигналу. Вся складність скидається на того, хто викликав системну функцію.

## Крайовий випадок: повне переривання проти часткового передавання

Початківці часто припускаються критичної помилки, вважаючи, що сигнал завжди призводить до повернення `EINTR`. Це не так. Поведінка системи залежить від того, чи встигло ядро передати хоча б один байт до надходження сигналу.

Розгляньмо два сценарії:

### Сценарій 1: Сигнал надійшов ДО передавання даних

Процес викликав `read(fd, buf, 1024)`. Буфер каналу порожній. Процес заснув, не отримавши жодного байта. Через 50 мілісекунд надходить сигнал.
* Результат: `read()` повертає `-1`, а `errno` дорівнює `EINTR`.
* Дані не втрачені, позиція файлу чи сокета не змінилася. Виклик можна безпечно повторити з тим самим буфером і зміщенням.

### Сценарій 2: Сигнал надійшов ПІСЛЯ передавання частини даних

Процес викликав `write(sock_fd, buf, 1000000)` для запису 1 МБ даних. Ядро встигло записати в мережевий буфер 32 КБ (32768 байтів), після чого буфер заповнився, і потік заснув, очікуючи на звільнення місця. У цей момент надходить сигнал.
* Результат: `write()` повертає **`32768`** (кількість успішно записаних байтів), а `errno` **НЕ містить `EINTR`**!
* Ядро вважає операцію частково успішною.

Якщо розробник напише наївний цикл повтору, який у разі успішного повернення вважає операцію завершеною, програма втратить решту 968 КБ даних:

:::tabs
```c
#include <unistd.h>
#include <errno.h>

// НЕБЕЗПЕЧНИЙ КОД: втрачає дані під час часткового запису!
ssize_t broken_write_all(int fd, const void *buf, size_t count) {
    ssize_t written;
    do {
        // Якщо записано 32 КБ із 1 МБ, виклик поверне 32768 і вийде з циклу,
        // хоча 968 КБ залишилися незаписаними!
        written = write(fd, buf, count);
    } while (written == -1 && errno == EINTR);
    return written;
}
```
```cpp
#include <unistd.h>
#include <cerrno>
#include <span>
#include <expected>
#include <system_error>

// НЕБЕЗПЕЧНИЙ КОД: втрачає дані під час часткового запису!
std::expected<std::size_t, std::error_code> broken_write_all(int fd, std::span<const char> buf) {
    ssize_t written;
    do {
        // У разі запису лише частини даних повертається частковий розмір без дозапису
        written = ::write(fd, buf.data(), buf.size());
    } while (written == -1 && errno == EINTR);

    if (written == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return static_cast<std::size_t>(written);
}
```
:::

Правильний системний код зобов'язаний поєднувати перевірку `EINTR` із відстеженням накопичуваного зміщення (offset) та залишком непереданих байтів.

## Канонічний патерн: повне читання та запис без втрат

Ось еталонна реалізація функцій повного читання (`read_exact`) та повного запису (`write_exact`), які коректно витримують як шквал асинхронних сигналів, так і часткову передачу даних через фрагментацію буферів:

:::tabs
```c
#include <unistd.h>
#include <errno.h>
#include <stddef.h>

// Повне надійне читання: гарантує зчитування count байтів або повідомляє про EOF/помилку
ssize_t read_exact(int fd, void *buf, size_t count) {
    size_t total_read = 0;
    char *p = (char *)buf;

    while (total_read < count) {
        ssize_t res = read(fd, p + total_read, count - total_read);
        if (res == -1) {
            if (errno == EINTR) {
                // Перервано сигналом до передачі байтів у цій ітерації — повторюємо
                continue;
            }
            // Справжня фатальна помилка введення-виведення
            return -1;
        }
        if (res == 0) {
            // Несподіваний кінець потоку (EOF)
            break;
        }
        total_read += (size_t)res;
    }
    return (ssize_t)total_read;
}

// Повний надійний запис: гарантує надсилання всіх count байтів навіть при частинних передачах
ssize_t write_exact(int fd, const void *buf, size_t count) {
    size_t total_written = 0;
    const char *p = (const char *)buf;

    while (total_written < count) {
        ssize_t res = write(fd, p + total_written, count - total_written);
        if (res == -1) {
            if (errno == EINTR) {
                // Перервано сигналом — повторюємо спробу з поточної позиції
                continue;
            }
            // Справжня фатальна помилка
            return -1;
        }
        if (res == 0) {
            // Канал чи сокет не приймає дані
            break;
        }
        total_written += (size_t)res;
    }
    return (ssize_t)total_written;
}
```
```cpp
#include <unistd.h>
#include <cerrno>
#include <cstddef>
#include <span>
#include <expected>
#include <system_error>
#include <type_traits>

// Узагальнена обгортка над довільним системним викликом із захистом від EINTR
template <typename Syscall, typename... Args>
auto retry_on_eintr(Syscall&& call, Args&&... args) 
    -> std::invoke_result_t<Syscall, Args...> 
{
    using ResultType = std::invoke_result_t<Syscall, Args...>;
    ResultType res;
    do {
        res = call(std::forward<Args>(args)...);
    } while (res == static_cast<ResultType>(-1) && errno == EINTR);
    return res;
}

// Повне надійне читання з типізованим результатом
std::expected<std::size_t, std::error_code> read_exact(int fd, std::span<char> buf) {
    std::size_t total = 0;
    while (total < buf.size()) {
        ssize_t res = retry_on_eintr(::read, fd, buf.data() + total, buf.size() - total);
        if (res == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        if (res == 0) {
            break; // EOF
        }
        total += static_cast<std::size_t>(res);
    }
    return total;
}

// Повний надійний запис
std::expected<std::size_t, std::error_code> write_exact(int fd, std::span<const char> buf) {
    std::size_t total = 0;
    while (total < buf.size()) {
        ssize_t res = retry_on_eintr(::write, fd, buf.data() + total, buf.size() - total);
        if (res == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        if (res == 0) {
            break;
        }
        total += static_cast<std::size_t>(res);
    }
    return total;
}
```
:::

## Робота з інтервальними затримками: nanosleep та збереження залишку часу

Ще один критичний системний виклик, який постійно зазнає переривань — це `nanosleep()` (або більш сучасний `clock_nanosleep()`).

Коли процес викликає `nanosleep()`, запитуючи затримку на 100 мілісекунд, надходження сигналу через 20 мілісекунд призводить до негайного пробудження процесу, повернення значення `-1` та встановлення `errno = EINTR`. Якщо наївно викликати функцію знову з початковими 100 мс, сумарний час очікування складе 120 мс, що неприпустимо для систем реального часу.

Для коректного відновлення функція `nanosleep` приймає другий аргумент — вказівник на структуру `struct timespec rem`, куди ядро записує **залишок часу**, який потік не встиг проспати:

:::tabs
```c
#include <time.h>
#include <errno.h>

// Надійна затримка: досипає рівно залишок часу при перериванні
int sleep_exact_nanos(long sec, long nsec) {
    struct timespec req = { .tv_sec = sec, .tv_nsec = nsec };
    struct timespec rem = { 0, 0 };

    while (nanosleep(&req, &rem) == -1) {
        if (errno == EINTR) {
            // Оновлюємо запит залишком і продовжуємо сон
            req = rem;
            continue;
        }
        // Фатальна помилка (наприклад, некоректні параметри tv_nsec)
        return -1;
    }
    return 0;
}
```
```cpp
#include <chrono>
#include <ctime>
#include <cerrno>
#include <expected>
#include <system_error>

// Надійна затримка з використанням типів std::chrono
std::expected<void, std::error_code> sleep_exact(std::chrono::nanoseconds duration) {
    auto sec = std::chrono::duration_cast<std::chrono::seconds>(duration);
    auto nsec = duration - sec;

    struct timespec req{
        .tv_sec = static_cast<time_t>(sec.count()),
        .tv_nsec = static_cast<long>(nsec.count())
    };
    struct timespec rem{0, 0};

    while (::nanosleep(&req, &rem) == -1) {
        if (errno == EINTR) {
            req = rem; // Досипаємо залишок
            continue;
        }
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
```
:::

## Неблокуючий ввід-вивід: EAGAIN проти EINTR

У високопродуктивних мережевих серверах (наприклад, у веб-серверах Nginx або середовищах Node.js) дескриптори сокетів переводять у неблокуючий режим за допомогою системного виклику `fcntl(fd, F_SETFL, O_NONBLOCK)`.

У цьому режимі системні виклики `read()` та `write()` не засинають у ядрі, якщо буфер не готовий, а миттєво повертають `-1` зі значенням помилки `EAGAIN` (або еквівалентним `EWOULDBLOCK`).

Постає запитання: чи може неблокуючий сокет повернути `EINTR`?

Відповідь: **так, може**. Хоча ймовірність цього значно менша, ніж у блокуючому режимі, згідно зі стандартом POSIX та специфікацією ядра Linux, якщо сигнал надійшов у момент, коли потік щойно увійшов у системний виклик (до завершення перевірки структур сокета в ядрі), системний виклик завершується з помилкою `EINTR`.

Тому промисловий неблокуючий цикл обробки зобов'язаний розрізняти обидва випадки:

:::tabs
```c
#include <unistd.h>
#include <errno.h>
#include <stdio.h>

typedef enum {
    IO_SUCCESS,
    IO_WOULD_BLOCK,
    IO_CLOSED,
    IO_FATAL_ERROR
} IoStatus;

IoStatus handle_nonblocking_read(int fd, char *buf, size_t size, size_t *out_bytes) {
    while (1) {
        ssize_t n = read(fd, buf, size);
        if (n > 0) {
            *out_bytes = (size_t)n;
            return IO_SUCCESS;
        }
        if (n == 0) {
            return IO_CLOSED;
        }
        if (errno == EINTR) {
            // Сигнал перервав навіть неблокуючий виклик — негайний повтор
            continue;
        }
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            // Даних немає в буфері — повертаємося до циклу epoll
            return IO_WOULD_BLOCK;
        }
        // Усі інші коди — фатальний збій
        return IO_FATAL_ERROR;
    }
}
```
```cpp
#include <unistd.h>
#include <cerrno>
#include <span>
#include <expected>
#include <system_error>
#include <variant>

enum class NonBlockingStatus {
    WouldBlock,
    Closed
};

std::expected<std::size_t, std::variant<NonBlockingStatus, std::error_code>> 
handle_nonblocking_read(int fd, std::span<char> buf) {
    while (true) {
        ssize_t n = ::read(fd, buf.data(), buf.size());
        if (n > 0) {
            return static_cast<std::size_t>(n);
        }
        if (n == 0) {
            return std::unexpected(NonBlockingStatus::Closed);
        }
        if (errno == EINTR) {
            continue;
        }
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return std::unexpected(NonBlockingStatus::WouldBlock);
        }
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
}
```
:::

## Діагностика поведінки системних викликів за допомогою strace

Найкращим способом спостереження за перериванням системних викликів у реальному часі є системна утиліта трасування `strace`.

Якщо запустити програму, що виконує читання під потоком сигналів, за допомогою команди:

```bash
strace -e trace=read,write,kill,rt_sigaction,rt_sigreturn ./demo_app
```

В консолі з'явиться характерний протокол взаємодії ядра та процесу:

```
read(3, 0x7ffd9b8a3e00, 128)          = ? ERESTARTSYS (To be restarted if SA_RESTART)
--- SIGUSR1 {si_signo=SIGUSR1, si_code=SI_TKILL, si_pid=14205, si_uid=1000} ---
rt_sigreturn({mask=[]})                 = -1 EINTR (Interrupted system call)
read(3, "System Programming in Unix\n", 128) = 27
write(1, "[Головний потік] Успішно прочит"..., 45) = 45
```

У лозі чітко видно внутрішній стан ядра:
1. Виклик `read(3, ...)` повертає внутрішній код `ERESTARTSYS`.
2. Ядро вставляє кадр обробки сигналу `SIGUSR1`.
3. Виклик `rt_sigreturn()` відновлює стек і повертає користувачеві виправлене значення `-1 EINTR`.
4. Прикладний цикл повтору миттєво робить другий виклик `read(3, ...)`, який успішно читає 27 байтів.

## Макрос TEMP_FAILURE_RETRY та його C++ еквіваленти

У стандартній бібліотеці glibc операційної системи Linux існує макрос `TEMP_FAILURE_RETRY`. Він реалізований через розширення GCC/Clang (statement expressions `({ ... })`), яке повертає значення останнього виразу в блоці:

:::tabs
```c
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <errno.h>

// Використання стандартного макросу glibc для безпечного відкриття файлу
int open_file_safe(const char *path) {
    int fd = TEMP_FAILURE_RETRY(open(path, O_RDONLY | O_CLOEXEC));
    if (fd == -1) {
        perror("open failed");
        return -1;
    }
    return fd;
}
```
```cpp
#include <unistd.h>
#include <fcntl.h>
#include <cerrno>
#include <expected>
#include <system_error>

// Стандартний кросплатформний C++ еквівалент через лямбда-функцію без розширень GCC
template <typename F>
auto retry_expression(F&& f) -> decltype(f()) {
    decltype(f()) res;
    do {
        res = f();
    } while (res == -1 && errno == EINTR);
    return res;
}

std::expected<int, std::error_code> open_file_safe(const char *path) {
    int fd = retry_expression([&]() {
        return ::open(path, O_RDONLY | O_CLOEXEC);
    });
    if (fd == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return fd;
}
```
:::

## Детальний аналіз прапорця SA_RESTART

Функція встановлення обробника сигналу `sigaction()` дозволяє вказати прапорець `SA_RESTART`. Багато інженерів помилково вважають, що увімкнення `SA_RESTART` назавжди знімає проблему `EINTR`. Це небезпечна ілюзія.

У таблиці нижче наведено реальну поведінку ядра Linux для різних системних викликів у разі надходження сигналу:

| Системний виклик | Поведінка за замовчуванням (без `SA_RESTART`) | Поведінка з увімкненим `SA_RESTART` |
| :--- | :--- | :--- |
| `read()`, `write()` (канали, термінали, сокети) | Переривається (`-1`, `EINTR`) | **Автоматично перезапускається ядром** |
| `open()` (наприклад, блокуюче відкриття FIFO) | Переривається (`-1`, `EINTR`) | **Автоматично перезапускається ядром** |
| `wait()`, `waitpid()`, `waitid()` | Переривається (`-1`, `EINTR`) | **Автоматично перезапускається ядром** |
| `select()`, `pselect()` | Переривається (`-1`, `EINTR`) | **ЗАВЖДИ повертає `EINTR`** (не перезапускається) |
| `poll()`, `ppoll()`, `epoll_wait()`, `epoll_pwait()` | Переривається (`-1`, `EINTR`) | **ЗАВЖДИ повертає `EINTR`** (не перезапускається) |
| `sem_wait()`, `sem_timedwait()` | Переривається (`-1`, `EINTR`) | **ЗАВЖДИ повертає `EINTR`** (не перезапускається) |
| `nanosleep()`, `clock_nanosleep()` | Переривається (`-1`, `EINTR`) | **ЗАВЖДИ повертає `EINTR`** (повертає час залишку) |
| Сокети з таймаутом `SO_RCVTIMEO` / `SO_SNDTIMEO` | Переривається (`-1`, `EINTR`) | **ЗАВЖДИ повертає `EINTR`** (щоб не порушити таймаут) |

Чому такі виклики, як `epoll_wait()` чи `sem_wait()`, ніколи не перезапускаються автоматично? Тому що їхнє призначення — саме мультиплексування та синхронізація подій. Якщо програма очікує на події в циклі `epoll_wait()`, надходження сигналу (наприклад, запиту завершення `SIGTERM`) є законною підставою для негайного виходу з блокування, перевірки прапорця завершення програми та коректного очищення ресурсів.

## Еволюція до синхронних сигналів: signalfd та атомарні маски

Рішення скидати сигнали асинхронно прямо в стек потоку створило класичний стан гонитви (race condition). Уявімо серверний цикл:

```
1. if (g_terminate_requested) break;
2. // <-- Що, як сигнал SIGTERM надійде САМЕ ТУТ?
3. epoll_wait(epoll_fd, events, max_events, -1);
```

Якщо сигнал надійде між рядком 1 і рядком 3, обробник сигналу встановить прапорець `g_terminate_requested = 1`, після чого потік перейде в рядок 3 і **засне назавжди** в `epoll_wait()`, оскільки подій на дескрипторах немає, а сигнал уже минув!

Для подолання цієї вади операційні системи еволюціонували двома шляхами:

1. **Атомарне мультиплексування з маскою (`pselect`, `ppoll`, `epoll_pwait`)**. Ці виклики атомарно змінюють маску заблокованих сигналів процесу на час самого очікування і відновлюють її при виході.
2. **Перетворення сигналу на дескриптор (`signalfd` у Linux)**. Сигнали повністю блокуються для асинхронної доставки (`pthread_sigmask`), а замість цього створюється звичайний файловий дескриптор, з якого можна читати структури сигналів як байти через звичайний `epoll_wait()`.

Ось як виглядає надійна обробка сигналів через дескриптор `signalfd`:

Важлива архітектурна деталь: у багатопотокових застосунках для маскування сигналів слід використовувати виклик `pthread_sigmask()`, а не `sigprocmask()`. Згідно зі стандартом POSIX, кожен потік має власну маску заблокованих сигналів, і виклик `sigprocmask()` у багатопотоковому процесі має невизначену поведінку (undefined behavior). Функція `pthread_sigmask()` гарантовано змінює маску виключно для поточного потоку виконання, дозволяючи виділити один окремий керівний потік для синхронного зчитування подій із `signalfd`, тоді як усі робочі потоки (worker threads) залишаються захищеними від асинхронних переривань.

:::tabs
```c
#define _GNU_SOURCE
#include <sys/signalfd.h>
#include <signal.h>
#include <pthread.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

int create_signal_channel(void) {
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGTERM);

    // Блокуємо сигнали для поточного потоку
    if (pthread_sigmask(SIG_BLOCK, &mask, NULL) == -1) {
        perror("pthread_sigmask");
        return -1;
    }

    // Створюємо файловий дескриптор для читання сигналів
    int sfd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (sfd == -1) {
        perror("signalfd");
        return -1;
    }
    return sfd;
}
```
```cpp
#include <sys/signalfd.h>
#include <csignal>
#include <pthread.h>
#include <unistd.h>
#include <expected>
#include <system_error>

class SignalFileDescriptor {
public:
    static std::expected<int, std::error_code> create_for_termination() {
        sigset_t mask;
        sigemptyset(&mask);
        sigaddset(&mask, SIGINT);
        sigaddset(&mask, SIGTERM);

        // Блокуємо асинхронну доставку для поточного потоку
        if (::pthread_sigmask(SIG_BLOCK, &mask, nullptr) == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        int sfd = ::signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
        if (sfd == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return sfd;
    }
};
```
:::

Цей механізм повністю усуває `EINTR` із циклу обробки подій, перетворюючи сигнали на звичайний потік даних.

## Порівняння з моделлю Windows (Win32 API)

В операційних системах сімейства Windows NT філософія обробки асинхронних подій побудована на принципах, набагато ближчих до школи MIT, ніж до Unix:

* У Windows системні виклики введення-виведення (функція `ReadFile()`, `WriteFile()`) **ніколи не повертають аналога помилки `EINTR`**.
* Асинхронні переривання доставляються через так звані асинхронні виклики процедур (англ. *Asynchronous Procedure Calls*, APC).
* Потік користувача виконує функції APC виключно тоді, коли він явно переходить у стан тривожного очікування (alertable wait state) за допомогою функцій `SleepEx()`, `WaitForSingleObjectEx()` або `WaitForMultipleObjectsEx()` з параметром `bAlertable = TRUE`.
* У разі спрацьовування APC функція очікування повертає значення `WAIT_IO_COMPLETION`, а не помилку вводу-виводу.
* Для високопродуктивного масштабованого вводу-виводу Windows надає порти завершення вводу-виводу (IOCP / I/O Completion Ports), де операції виконуються ядром повністю у фоновому режимі, а прикладний код отримує пакети повідомлень про вже завершені операції.

Ця різниця наочно демонструє, як архітектурний вибір 1970-х років розділив дві провідні гілки операційних систем: Unix обрав простоту ядра та явний цикл повтору `EINTR`, тоді як Windows реалізувала складнішу підсистему асинхронного розмотування запитів введення-виведення на рівні драйверів пристроїв.

## Повний робочий проєкт: симуляція асинхронного переривання

Наведений нижче код демонструє роботу системного вводу-виводу в умовах агресивного потоку сигналів. Програма створює анонімний канал зв'язку (pipe), налаштовує обробник сигналу користувача `SIGUSR1`, запускає фоновий потік, який кожні 25 мілісекунд надсилає сигнал головному потоку, і виконує повільне читання.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <time.h>
#include <pthread.h>
#include <string.h>

static volatile sig_atomic_t g_signal_count = 0;

static void user_signal_handler(int signo) {
    (void)signo;
    g_signal_count++;
}

static void* signal_emitter_thread(void *arg) {
    pthread_t target = *(pthread_t*)arg;
    for (int i = 0; i < 6; ++i) {
        struct timespec ts = { .tv_sec = 0, .tv_nsec = 25000000 }; // 25 мс
        nanosleep(&ts, NULL);
        pthread_kill(target, SIGUSR1);
    }
    return NULL;
}

int main(void) {
    // 1. Реєструємо обробник сигналу БЕЗ SA_RESTART для демонстрації переривань
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = user_signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0; // Навмисно вимикаємо авто-перезапуск
    if (sigaction(SIGUSR1, &sa, NULL) == -1) {
        perror("sigaction");
        return 1;
    }

    int pipefds[2];
    if (pipe(pipefds) == -1) {
        perror("pipe");
        return 1;
    }

    pthread_t main_thread = pthread_self();
    pthread_t emitter;
    if (pthread_create(&emitter, NULL, signal_emitter_thread, &main_thread) != 0) {
        perror("pthread_create");
        return 1;
    }

    printf("[Головний потік] Очікування даних із каналу під час надходження сигналів...\n");

    // Запишемо тестове повідомлення в канал
    const char message[] = "System Programming in Unix\n";
    write(pipefds[1], message, sizeof(message));

    char buffer[128];
    size_t count = sizeof(message);
    size_t total_read = 0;
    int eintr_retries = 0;

    // Цикл стійкого читання з підрахунком подоланих EINTR
    while (total_read < count) {
        ssize_t res = read(pipefds[0], buffer + total_read, count - total_read);
        if (res == -1) {
            if (errno == EINTR) {
                eintr_retries++;
                printf("  -> [Перехоплено EINTR #%d] Системний виклик перервано, перезапуск...\n", eintr_retries);
                continue;
            }
            perror("read error");
            break;
        }
        if (res == 0) {
            printf("[Головний потік] Досягнуто кінця каналу (EOF)\n");
            break;
        }
        total_read += (size_t)res;
    }

    printf("[Головний потік] Успішно прочитано %zu байтів: %s", total_read, buffer);
    printf("[Підсумок] Отримано сигналів процесом: %d, виконано перезапусків виклику: %d\n", 
           (int)g_signal_count, eintr_retries);

    pthread_join(emitter, NULL);
    close(pipefds[0]);
    close(pipefds[1]);
    return 0;
}
```
```cpp
#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <csignal>
#include <unistd.h>
#include <cerrno>
#include <cstring>
#include <array>
#include <expected>
#include <system_error>

namespace {
    std::atomic<int> g_signal_counter{0};

    void signal_handler(int sig) noexcept {
        (void)sig;
        g_signal_counter.fetch_add(1, std::memory_order_relaxed);
    }
}

// RAII-обгортка для файлових дескрипторів
class FileDescriptor {
public:
    explicit FileDescriptor(int fd = -1) noexcept : fd_(fd) {}
    ~FileDescriptor() { reset(); }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    int get() const noexcept { return fd_; }
    void reset() noexcept {
        if (fd_ != -1) {
            ::close(fd_);
            fd_ = -1;
        }
    }

private:
    int fd_{-1};
};

struct Pipe {
    FileDescriptor reader;
    FileDescriptor writer;

    static std::expected<Pipe, std::error_code> create() {
        int fds[2];
        if (::pipe(fds) == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return Pipe{FileDescriptor(fds[0]), FileDescriptor(fds[1])};
    }
};

int main() {
    // Встановлюємо обробник сигналу SIGUSR1 без SA_RESTART
    struct sigaction sa{};
    sa.sa_handler = signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    if (::sigaction(SIGUSR1, &sa, nullptr) == -1) {
        std::cerr << "Помилка встановлення sigaction\n";
        return 1;
    }

    auto pipe_res = Pipe::create();
    if (!pipe_res) {
        std::cerr << "Помилка створення pipe: " << pipe_res.error().message() << "\n";
        return 1;
    }
    auto pipe = std::move(*pipe_res);

    // Фоновий потік надсилає сигнали
    std::thread spammer([]() {
        for (int i = 0; i < 6; ++i) {
            std::this_thread::sleep_for(std::chrono::milliseconds(25));
            ::kill(::getpid(), SIGUSR1);
        }
    });

    const char message[] = "System Programming in C++23\n";
    ::write(pipe.writer.get(), message, sizeof(message));

    std::array<char, 128> buffer{};
    std::size_t total_read = 0;
    std::size_t target_count = sizeof(message);
    int eintr_retries = 0;

    std::cout << "[Головний потік] Очікування читання з каналу під шквалом сигналів...\n";

    while (total_read < target_count) {
        ssize_t res = ::read(pipe.reader.get(), buffer.data() + total_read, target_count - total_read);
        if (res == -1) {
            if (errno == EINTR) {
                eintr_retries++;
                std::cout << "  -> [Перехоплено EINTR #" << eintr_retries << "] Перезапуск операції...\n";
                continue;
            }
            std::cerr << "Помилка читання: " << std::generic_category().message(errno) << "\n";
            break;
        }
        if (res == 0) {
            std::cout << "[Головний потік] Отримано EOF\n";
            break;
        }
        total_read += static_cast<std::size_t>(res);
    }

    std::cout << "[Головний потік] Прочитано " << total_read << " байтів: " << buffer.data();
    std::cout << "[Підсумок] Зафіксовано сигналів: " << g_signal_counter.load() 
              << ", виконано перезапусків: " << eintr_retries << "\n";

    spammer.join();
    return 0;
}
```
:::

## Кросплатформна альтернатива: патерн Self-Pipe

На платформах, де системний виклик `signalfd` відсутній (наприклад, у macOS, FreeBSD чи OpenBSD), класичним інженерним рішенням для усунення стану гонитви та перетворення асинхронного сигналу на звичайну подію дескриптора є так званий **трюк із власним каналом** (англ. *Self-Pipe Trick*).

Ідея полягає в наступному:
1. Процес створює неблокуючий анонімний канал pipe через `pipe()` і `fcntl(O_NONBLOCK)`.
2. Читальний кінець каналу реєструється в загальному циклі мультиплексування (`select`, `poll`, `kqueue`, `epoll`).
3. Обробник сигналу виконує рівно одну дію — записує один байт у записувальний кінець каналу за допомогою безпечного виклику `write()`.
4. Цикл обробки подій спокійно прокидається по дескриптору, вичитує байт і викликає високорівневу логіку реакції на сигнал у нормальному синхронному контексті, де дозволено виділяти пам'ять, користуватися м'ютексами та викликати будь-які функції.

Ось як реалізується цей патерн:

:::tabs
```c
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>

static int g_self_pipe_tx = -1;

static void self_pipe_signal_handler(int signo) {
    int saved_errno = errno;
    char sig_byte = (char)signo;
    // write() є async-signal-safe функцією за стандартом POSIX
    (void)write(g_self_pipe_tx, &sig_byte, 1);
    errno = saved_errno; // Відновлюємо errno для потоку, що був перерваний
}

int init_self_pipe(int *out_rx_fd) {
    int fds[2];
    if (pipe(fds) == -1) return -1;

    // Робимо обидва кінці неблокуючими та закриваємо при exec
    fcntl(fds[0], F_SETFL, O_NONBLOCK);
    fcntl(fds[1], F_SETFL, O_NONBLOCK);
    fcntl(fds[0], F_SETFD, FD_CLOEXEC);
    fcntl(fds[1], F_SETFD, FD_CLOEXEC);

    g_self_pipe_tx = fds[1];
    *out_rx_fd = fds[0];

    struct sigaction sa;
    sa.sa_handler = self_pipe_signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);
    return 0;
}
```
```cpp
#include <unistd.h>
#include <fcntl.h>
#include <csignal>
#include <cerrno>
#include <expected>
#include <system_error>

class SelfPipe {
public:
    static std::expected<int, std::error_code> initialize() {
        int fds[2];
        if (::pipe(fds) == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        ::fcntl(fds[0], F_SETFL, O_NONBLOCK);
        ::fcntl(fds[1], F_SETFL, O_NONBLOCK);
        ::fcntl(fds[0], F_SETFD, FD_CLOEXEC);
        ::fcntl(fds[1], F_SETFD, FD_CLOEXEC);

        tx_fd_ = fds[1];

        struct sigaction sa{};
        sa.sa_handler = &SelfPipe::signal_handler;
        sigemptyset(&sa.sa_mask);
        sa.sa_flags = SA_RESTART;
        ::sigaction(SIGINT, &sa, nullptr);
        ::sigaction(SIGTERM, &sa, nullptr);

        return fds[0]; // Повертаємо дескриптор для моніторингу в epoll/kqueue
    }

private:
    static inline int tx_fd_{-1};

    static void signal_handler(int signo) noexcept {
        int saved_errno = errno;
        char byte = static_cast<char>(signo);
        [[maybe_unused]] auto res = ::write(tx_fd_, &byte, 1);
        errno = saved_errno;
    }
};
```
:::

## Інженерний висновок

Управління перерваними системними викликами — це класичне втілення принципу «Worse is Better» у практиці системного програмування. Замість того щоб ускладнювати ядро монолітними абстракціями прозорого відновлення операцій, операційна система обрала примітивний контракт, який переклав відповідальність за відновлення на прикладний шар. Розуміння цієї моделі та використання правильних патернів повтору є обов'язковою вимогою для створення надійного, стійкого до збоїв промислового програмного забезпечення.
