# Протокол Jobserver: координація паралелізму між процесами збірки

<preknowlist>
- [Граф залежностей і порядок робіт](root:sys-bsystem/dependency-graph) — топологічний порядок задач, критичний шлях та планування паралельного виконання.
- [Швидкість збірки](root:sys-bsystem/build-speed) — фактори затримок компіляції, утилізація процесорних ядер та вузькі місця введення-виведення.
- [pipe та FIFO](root:sys-unix/pipe-and-fifo) — передача байтів між процесами через системні буфери ядра та семантика дескрипторів.
- [Успадкування дескрипторів та close-on-exec](root:sys-unix/close-on-exec) — прапорець `O_CLOEXEC`, збереження та витік дескрипторів при виклику `execve()`.
- [Блокувальне та неблокувальне введення-виведення](root:sys-unix/blocking-and-nonblocking) — виклики `read()`/`write()`, неблокувальний режим `O_NONBLOCK` та готовність через `poll()` / `epoll()`.
</preknowlist>

Коли на шістнадцятиядерній робочій станції запускають збірку великого проєкту командою `make -j16`, система збірки розпаралелює компіляцію незалежних файлів рівно на шістнадцять потоків. Але якщо кореневий сценарій збірки містить виклики вкладених підпроєктів (`$(MAKE) -C subproject -j16`), кожен із дочірніх процесів Make заново запускає власні шістнадцять задач. За лічені мілісекунди в операційній системі виникає понад двісті п'ятдесят одночасних процесів компілятора, які намертво забивають чергу планувальника ядра, спустошують процесорні кеші та вичерпують гігабайти оперативної пам'яті до аварійного спрацьовування механізму аварійного завершення процесів (OOM Killer).

Щоб узгодити ліміт паралелізму між довільною кількістю незалежних процесів збірки без використання важких фонових демонів, інженери GNU розробили протокол **Jobserver** (англ. *job* — завдання, *server* — обслуговуючий вузол). Сьогодні цей протокол став загальновизнаним міжсистемним стандартом, який підтримують GNU Make, Ninja, Cargo (Rust), Meson, CMake та десятки сторонніх компіляторних інструментів на платформах Linux, macOS та Windows.

## Проблема рекурсивної перепідписки ядер (CPU Oversubscription)

У великих програмних комплексах дерево вихідного коду рідко буває однорідним. Воно містить ядро програми, сторонні бібліотеки, утиліти кодогенерації, підмодулі на мовах C, C++ та Rust, а також окремі компоненти, кожен із яких збирається власною системою збірки.

Традиційним підходом до організації таких проєктів є рекурсивний запуск підсистем (англ. *recursive make*). Кореневий сценарій запускає команду для кожного каталогу:

```makefile
SUBDIRS = core engine network renderer ui

all:
	for dir in $(SUBDIRS); do \
		$(MAKE) -C $$dir || exit 1; \
	done
```

Якщо користувач бажає прискорити збірку і передає прапорець `-j16` (англ. *jobs* — кількість паралельних задач), кореневий процес `make` може запустити всі підкаталоги одночасно. Проте всередині кожного каталогу `core/Makefile` чи `engine/Makefile` також прописано або передано через змінні середовища прапорець `-j16`.

```
Кореневий make -j16
 ├── Sub-Make core (-j16)      → 16 процесів g++
 ├── Sub-Make engine (-j16)    → 16 процесів g++
 ├── Sub-Make network (-j16)   → 16 процесів g++
 └── Sub-Make renderer (-j16)  → 16 процесів g++
... Сумарно: 16 × 16 = 256 паралельних процесів на 16 фізичних ядер CPU
```

Така ситуація називається перепідпискою процесора (англ. *CPU oversubscription*). Наслідки неконтрольованої перепідписки проявляються у чотирьох критичних деградаціях продуктивності:

1. **Вибух накладних витрат на перемикання контексту (Context Switch Overhead).** Замість того, щоб шістнадцять процесів безперервно виконували інструкції компілятора на шістнадцяти фізичних ядрах, планувальник операційної системи змушений щосекунди виконувати сотні тисяч перемикань між 256 процесами. Кожне перемикання скидає стан конвеєрів процесора, вимагає оновлення таблиць сторінок пам'яті та ініціює дорогі міжпроцесорні переривання (TLB shootdowns).
2. **Вимивання процесорних кешів (Cache Thrashing).** Компілятор під час синтаксичного аналізу активно використовує кеші інструкцій та даних першого (L1) та другого (L2) рівнів. Постійне витіснення робочих наборів даних різними процесами перетворює швидку роботу з кешем на безперервне очікування вибірки рядків із повільної оперативної пам'яті через насичену системну шину.
3. **Вичерпання оперативної пам'яті та OOM Killer.** Сучасні компілятори C++ (Clang, GCC) та Rust (`rustc`) при оптимізації важких шаблонів і макросів споживають від 1 до 3 ГБ оперативної пам'яті на одну одиницю трансляції. Одночасний запуск 256 процесів вимагає понад 400 ГБ пам'яті. Якщо фізичної пам'яті недостатньо, операційна система починає інтенсивний скид сторінок у файл підкачування (англ. *thrashing*), після чого підсистема Out-Of-Memory (OOM) примусово завершує процеси сигналом `SIGKILL`.
4. **Хибність статичного розподілу квот.** Спроба вирішити проблему шляхом статичного обмеження квот (наприклад, призначити кожному підкаталогу фіксований ліміт `-j2` або `-j4`) призводить до протилежної проблеми — простою обладнання (англ. *underutilization*). Якщо модуль `network` містить лише 2 файли, а модуль `renderer` — 500 важких файлів, то після компіляції мережевого коду більшість ядер процесора стоятимуть без діла, тоді як `renderer` повільно компілюватиметься лише двома потоками.

![Розподіл навантаження CPU: рекурсивний вибух проти пулу Jobserver](/root/sys/sys-bsystem/jobserver-protocol/img/oversubscription-tree.svg)
*Порівняння неконтрольованої рекурсивної збірки (256 процесів на 16 ядер) з централізованим пулом Jobserver, що підтримує суворо фіксовану кількість активних робітників.*

Вирішенням проблеми є глобальний динамічний пул токенів (англ. *token pool*), який діє на рівні всього дерева процесів незалежно від глибини вкладеності.

> 🔧 **Навіщо це.** Без узгодженого протоколу розподілу задач паралельна збірка великих монорепозиторіїв або проєктів із підмодулями (Linux Kernel, Chromium, Android AOSP, LLVM) або деградує вдесятеро за часом, або падає через нестачу пам'яті. Jobserver дозволяє тримати рівно `N` активних задач у масштабі всієї системи, миттєво віддаючи вільні ресурси тим гілкам графа, які мають готові задачі.

## Класичний протокол через POSIX-пайпи (GNU Make Pipe)

Ідею синхронізації паралельних екземплярів make через звичайний pipe у лютому 1999 року вперше запропонував Говард Чу (Howard Chu); у GNU Make 3.78 (вересень 1999 року) архітектуру Jobserver було реалізовано спільно групою розробників (Howard Chu, Roland McGrath, Paul Smith, Tim Magill). Головною вимогою була абсолютна простота, відсутність окремих фонових служб-демонів та здатність працювати виключно на стандартних системних викликах POSIX.

Механізм базується на концепції відерця з токенами (англ. *token bucket*), реалізованого через звичайний анонімний односпрямований канал — пайп (англ. *pipe*).

### Правило неявного токена (Implicit Token)

Ключовим фундаментальним правилом протоколу є концепція **неявного токена** (англ. *implicit token* або *internal token*):

> Кожен запущений процес системи збірки (кореневий `make` або будь-який дочірній `sub-make`) автоматично володіє рівно одним слотом виконання за фактом свого існування.

Це означає:
- Якщо користувач вказав загальний ліміт паралелізму `N` (наприклад, `-j4`), то кореневий процес `make` створює канал `pipe(fds)` і записує в нього рівно `N - 1` байтів-токенів (у нашому випадку — 3 байти, зазвичай символи `'+'` або пробіли).
- Першу задачу будь-який процес виконує на основі свого неявного токена, **не читаючи** нічого з каналу.
- Якщо процес бажає запустити *другу*, *третю* або *N-ну* паралельну задачу одночасно з першою, він зобов'язаний вилучити (прочитати) один байт із дескриптора читання каналу.
- Після завершення кожної додаткової задачі процес зобов'язаний повернути (записати) вилучений байт назад у дескриптор запису каналу.

```
Паралелізм: N = 4
├── Неявний токен (Implicit): 1 слот утримує сам процес make
└── Токени в пайпі: N - 1 = 3 байти ['+']['+']['+']
```

Якщо в пайпі не залишилося байтів (усі токени розібрані іншими паралельними процесами), системний виклик `read()` переводить процес у стан блокування в ядрі операційної системи. Щойно будь-який компілятор у системі завершує роботу і його батьківський процес повертає байт у пайп через `write()`, ядро миттєво будить один із заблокованих процесів.

![Життєвий цикл токена в POSIX Jobserver (GNU Make Pipe)](/root/sys/sys-bsystem/jobserver-protocol/img/pipe-token-exchange.svg)
*Життєвий цикл токена в POSIX Jobserver: кореневий процес створює дескриптори пайпа, записує N-1 байтів і передає їх дочірнім процесам через змінну MAKEFLAGS.*

### Передача параметрів через командний рядок та MAKEFLAGS

Щоб дочірні процеси знали, звідки читати та куди повертати токени, кореневий процес Make передає номери відкритих файлових дескрипторів через аргументи командного рядка та автоматичну змінну середовища `MAKEFLAGS`.

Історично формат прапорця змінювався:
- **GNU Make до версії 4.2:** використовувався прапорець `--jobserver-fds=R,W`, де `R` — номер файлового дескриптора для читання, а `W` — для запису (наприклад, `--jobserver-fds=3,4`).
- **GNU Make 4.2 та новіші версії:** прапорець перейменовано на `--jobserver-auth=R,W` (від англ. *authentication* — авторизація), щоб підкреслити передачу прав доступу до пулу.

При виклику вкладеного підпроцесу Make автоматично формує змінну середовища:

```bash
MAKEFLAGS="--jobserver-auth=3,4 -j16"
```

Коли дочірній процес `make` стартує, він розбирає `MAKEFLAGS`. Виявивши параметр `--jobserver-auth=3,4`, він розуміє, що не має права створювати новий власний пул токенів. Замість цього він підключається до вже відкритих дескрипторів 3 і 4 та стає клієнтом батьківського Jobserver.

## Підводні камені POSIX-пайпів: дескриптори, FIFO, eventfd і pidfd

Попри елегантність ідеї з байтами в пайпі, на практиці класичний підхід через передачу числових дескрипторів містить кілька серйозних вразливостей системного рівня.

### Проблема витоку та пошкодження дескрипторів

У стандартах POSIX відкриті файлові дескриптори за замовчуванням успадковуються дочірніми процесами при виклику `execve()`, якщо на них явно не встановлено прапорець `FD_CLOEXEC` (англ. *close-on-exec*).

Якщо дескриптори 3 і 4 залишаться відкритими, вони будуть успадковані кожним дочірнім процесом: компілятором `gcc`, компонувальником `ld`, утилітами `sed`, `awk`, оболонкою `sh` та довільними користувацькими скриптами. Це призводить до двох небезпечних ситуацій:

- Якщо довільний сторонній скрипт у рецепті випадково прочитає щось із дескриптора 3 (наприклад, очікуючи там вхідні дані), токен збірки зникне назавжди. Загальний ліміт паралелізму системи безповоротно зменшиться на одиницю.
- Якщо дочірня програма закриє дескриптор 4, наступна спроба системи збірки повернути токен викличе сигнал помилки зламаного каналу `SIGPIPE` (або помилку `EPIPE`), що призведе до аварійного падіння всієї збірки.

Щоб запобігти цьому, GNU Make використовує умовну логіку управління прапорцем `FD_CLOEXEC`:
1. За замовчуванням на дескриптори пайпа встановлюється прапорець `FD_CLOEXEC` за допомогою виклику `fcntl(fd, F_SETFD, FD_CLOEXEC)`. Усі звичайні команди рецептів (компілятори, утиліти) запускаються із закритими дескрипторами Jobserver.
2. Якщо Make виявляє, що рядок рецепта містить рекурсивний виклик (позначається символом `+` на початку рядка або містить посилання на змінні `$(MAKE)` чи `${MAKE}`), Make безпосередньо перед викликом `execve()` знімає прапорець `FD_CLOEXEC`, роблячи дескриптори доступними для вкладеного Make.

### Еволюція GNU Make 4.4+: іменовані канали (FIFO)

У складних інструментальних ланцюгах (де Make викликає CMake, CMake генерує виклики Python-скриптів, а ті викликають вкладений Make або Ninja) прапорці дескрипторів часто втрачаються або дескриптори закриваються проміжними бібліотеками.

У GNU Make 4.4 (випущеному наприкінці 2022 року) було представлено новий режим Jobserver на базі іменованих каналів — **FIFO** (лат. *primum intro, primum exit* — першим прийшов, першим пішов).

Замість анонімного пайпа кореневий процес створює тимчасовий FIFO-файл у файловій системі за допомогою системного виклику `mkfifo()` (наприклад, у каталозі `/tmp`):

```bash
--jobserver-auth=fifo:/tmp/GMfifo48912
```

Переваги схеми на базі FIFO:
- **Відсутність проблем з номерами дескрипторів.** Будь-який процес у дереві на будь-якому рівні вкладеності може самостійно відкрити зазначений файл викликом `open("/tmp/GMfifo48912", O_RDWR | O_CLOEXEC)`.
- **Безпека успадкування.** Кожен процес відкриває власний дескриптор із негайно встановленим `O_CLOEXEC`. Жодні дескриптори не передаються через `execve()`, що унеможливлює випадкове пошкодження пайпа сторонніми програмами.
- **Очищення ресурсів.** Кореневий процес видаляє точку монтування файлу викликом `unlink()`, але відкритий об'єкт у пам'яті ядра залишається доступним для всіх підключених процесів аж до закриття останнього дескриптора.

### Асинхронне опитування: eventfd, pidfd та неблокувальний ввід-вивід

Класичний блокувальний виклик `read(rfd, &token, 1)` створює проблему в архітектурі сучасних систем збірки з циклом обробки подій (англ. *event loop*). Якщо планувальник заблокується на читанні токена з пайпа, він не зможе вчасно реагувати на завершення дочірніх процесів або системні сигнали без переривання через `EINTR` та обробників `SIGCHLD`.

Сучасні клієнти Jobserver (наприклад, у системі збірки Ninja або компіляторі Rust) переводять дескриптор читання в неблокувальний режим:

:::tabs
```c
/* Налаштування неблокувального режиму дескриптора читання в C */
int make_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags < 0) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}
```
```cpp
// Налаштування неблокувального режиму дескриптора в C++
#include <fcntl.h>
#include <system_error>

std::error_code set_nonblocking(int fd) noexcept {
    const int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) {
        return std::error_code(errno, std::generic_category());
    }
    if (::fcntl(fd, F_SETFL, flags | O_NONBLOCK) < 0) {
        return std::error_code(errno, std::generic_category());
    }
    return {};
}
```
:::

Тепер замість сліпого зависання у виклику `read()`, планувальник використовує мультиплексування системних викликів `poll()`, `ppoll()` або `epoll()`:

1. У масив подій `struct pollfd` додається дескриптор читання Jobserver з прапорцем `POLLIN`.
2. Одночасно туди ж додаються дескриптори завершення процесів (у сучасному Linux — дескриптори `pidfd`, створені через `pidfd_open()`, або дескриптор сигналів `signalfd`).
3. Коли `poll()` повертає готовність дескриптора Jobserver, клієнт виконує неблокувальний `read()`. Якщо отримано токен — стартує новий компілятор. Якщо повертається `EAGAIN` чи `EWOULDBLOCK` (інший паралельний процес встиг перехопити токен раніше), планувальник просто повертається в цикл очікування.

## Реалізація Jobserver на Windows: іменовані семафори (Named Semaphores)

В операційній системі Windows архітектура процесів та файлових дескрипторів принципово відрізняється від POSIX. У Windows немає нативних числових дескрипторів файлів на рівні ядра — дескриптори (англ. *file descriptors*) є штучною надбудовою бібліотеки C Runtime (MSVCRT / UCRT). Спроба передати числові дескриптори через змінні середовища дочірнім процесам Windows призводить до збою, оскільки таблиця дескрипторів CRT є локальною для кожного процесу.

Крім того, механізм успадкування дескрипторів ядра Win32 (англ. *HANDLE inheritance*) через структуру `STARTUPINFOEX` вимагає складного ручного налаштування списків успадкування `LPPROC_THREAD_ATTRIBUTE_LIST`, який легко ламається при виклику проміжних командних інтерпретаторів на зразок `cmd.exe` або `powershell.exe`.

З цієї причини для платформи Windows було розроблено альтернативний протокол Jobserver на базі **іменованих семафорів ядра** (англ. *Win32 Named Semaphores*).

```
Ім'я об'єкта ядра: \BaseNamedObjects\jobserver_semaphore_PID_18420
Формат у MAKEFLAGS: --jobserver-auth=jobserver_semaphore_PID_18420
                 або --jobserver-auth=semaphore:jobserver_semaphore_PID_18420
```

### Принцип роботи з Win32 Named Semaphore

Семафор в операційній системі Windows є об'єктом синхронізації ядра, який зберігає цілочисельний лічильник у діапазоні від 0 до заданого максимуму. Стан семафора є «сигнальним» (англ. *signaled*), коли його лічильник строго більший за нуль, і «несигнальним» (англ. *nonsignaled*), коли лічильник дорівнює нулю.

:::tabs
```c
/* Win32 C API: створення та синхронізація семафора */
HANDLE create_jobserver_sem(const char *name, int max_jobs) {
    return CreateSemaphoreA(NULL, max_jobs - 1, max_jobs - 1, name);
}

HANDLE open_jobserver_sem(const char *name) {
    return OpenSemaphoreA(SYNCHRONIZE | SEMAPHORE_MODIFY_STATE, FALSE, name);
}

int acquire_sem_token(HANDLE hSem, DWORD timeout_ms) {
    return WaitForSingleObject(hSem, timeout_ms) == WAIT_OBJECT_0;
}

void release_sem_token(HANDLE hSem) {
    ReleaseSemaphore(hSem, 1, NULL);
}
```
```cpp
// Modern C++20 Win32 RAII обгортка семафора Jobserver
#include <windows.h>
#include <string_view>
#include <memory>

struct HandleDeleter {
    void operator()(HANDLE h) const noexcept {
        if (h && h != INVALID_HANDLE_VALUE) {
            ::CloseHandle(h);
        }
    }
};
using UniqueHandle = std::unique_ptr<void, HandleDeleter>;

class Win32SemaphoreJobserver {
public:
    static UniqueHandle create(std::string_view name, int max_jobs) noexcept {
        HANDLE h = ::CreateSemaphoreA(nullptr, max_jobs - 1, max_jobs - 1, name.data());
        return UniqueHandle(h);
    }

    static UniqueHandle open(std::string_view name) noexcept {
        HANDLE h = ::OpenSemaphoreA(SYNCHRONIZE | SEMAPHORE_MODIFY_STATE, FALSE, name.data());
        return UniqueHandle(h);
    }

    static bool try_acquire(HANDLE h, DWORD timeout_ms = 0) noexcept {
        return ::WaitForSingleObject(h, timeout_ms) == WAIT_OBJECT_0;
    }

    static void release(HANDLE h) noexcept {
        ::ReleaseSemaphore(h, 1, nullptr);
    }
};
```
:::

1. **Ініціалізація.** Кореневий процес створює семафор за допомогою виклику API Win32 `CreateSemaphoreA(NULL, N - 1, N - 1, semaphore_name)`.
2. **Підключення клієнта.** Дочірній процес збірки (Make, CMake, Cargo, Ninja) вичитує ім'я семафора з `MAKEFLAGS` і відкриває існуючий об'єкт викликом `OpenSemaphoreA`.
3. **Запит токена (Acquire).** Клієнт викликає функцію очікування `WaitForSingleObject(hSem, INFINITE)`. Ядро Windows атомарно зменшує лічильник семафора на одиницю. Якщо лічильник був рівний нулю, потік переходить у стан очікування без витрат процесорного часу.
4. **Повернення токена (Release).** Після завершення задачі процес збільшує лічильник семафора на одиницю викликом `ReleaseSemaphore(hSem, 1, NULL)`.

![Архітектура Windows Jobserver на основі Named Semaphore](/root/sys/sys-bsystem/jobserver-protocol/img/windows-named-semaphore.svg)
*Архітектура Windows Jobserver: використання системного об'єкта Named Semaphore для міжпроцесної координації та атомарного очікування через WaitForMultipleObjects.*

### Перевага Windows: атомарне очікування через WaitForMultipleObjects

У системі Windows реалізація Jobserver має суттєву перевагу над класичним пайпом POSIX завдяки системному виклику `WaitForMultipleObjects`.

Планувальник збірки на Windows формує єдиний масив дескрипторів:
- Перший елемент — дескриптор семафора `hSem`.
- Наступні елементи — дескриптори процесів запущених компіляторів `hProcess[0...K]`.

:::tabs
```c
/* Очікування або токена, або завершення робітника в C */
DWORD wait_jobserver_event(HANDLE hSem, HANDLE *procs, DWORD num_procs) {
    HANDLE handles[64];
    handles[0] = hSem;
    for (DWORD i = 0; i < num_procs && i < 63; ++i) {
        handles[i + 1] = procs[i];
    }
    return WaitForMultipleObjects(num_procs + 1, handles, FALSE, INFINITE);
}
```
```cpp
// Атомарне мультиплексування токена та процесів у C++
#include <windows.h>
#include <span>
#include <vector>

DWORD wait_for_job_or_process(HANDLE sem_handle, std::span<const HANDLE> process_handles) noexcept {
    std::vector<HANDLE> handles;
    handles.reserve(process_handles.size() + 1);
    handles.push_back(sem_handle);
    handles.insert(handles.end(), process_handles.begin(), process_handles.end());

    return ::WaitForMultipleObjects(
        static_cast<DWORD>(handles.size()),
        handles.data(),
        FALSE, // Прокинутися при сигналі БУДЬ-ЯКОГО об'єкта
        INFINITE
    );
}
```
:::

Цей виклик атомарно вирішує проблему синхронізації: потік пробуджується або коли звільнився токен (семафор став сигнальним), або коли будь-який із компіляторів завершив роботу (дескриптор процесу перейшов у сигнальний стан). Це повністю усуває гонитву станів (англ. *race condition*) між отриманням токенів і збором результатів виконання.

## Федерація інструментів: GNU Make, Ninja, Cargo, Meson і CMake

Jobserver перестав бути внутрішньою особливістю GNU Make і перетворився на стандартний протокол обміну лімітами паралелізму між гетерогенними інструментами розробки.

### Інтеграція в екосистему Cargo (Rust)

Пакетний менеджер і система збірки мови Rust — Cargo — використовує крейт `jobserver` (офіційно підтримуваний командою Rust).
- Коли `cargo build -j8` запускається з командного рядка самостійно, він створює власний Jobserver і передає токени численним екземплярам компілятора `rustc`, які виконують паралельну кодогенерацію (англ. *codegen units*).
- Коли Cargo викликається зсередини великого проєкту на C++ під керуванням GNU Make або CMake, Cargo виявляє змінні `MAKEFLAGS` або `CARGO_MAKEFLAGS`. Він не створює новий пул, а стає клієнтом батьківського Jobserver. Токени використовуються як для компіляції Rust-файлів, так і для запуску сторонніх C/C++ бібліотек у сценаріях `build.rs` (через крейт `cc-rs`).

### Інтеграція в Ninja

Система збірки Ninja від початку розроблялася для максимально швидкої роботи з пласким графом залежностей і довгий час не підтримувала Jobserver, запускаючи фіксовану кількість задач `-jN`. Проте при використанні Ninja у ролі підсистеми всередині інших систем збірки виникала та сама проблема перепідписки CPU.

Починаючи з версії Kitware Ninja та офіційних патчів Ninja v1.12+, Ninja підтримує роботу в режимі клієнта Jobserver (прапорець `-j` без аргументів або автоматичне зчитування `--jobserver-auth` із середовища). Ninja захоплює токени перед кожним викликом компілятора і повертає їх після завершення, забезпечуючи ідеальну інтеграцію у великі змішані збірки.

### Уникнення взаємних блокувань (Deadlock Avoidance)

Неправильна реалізація клієнта Jobserver може легко призвести до взаємного блокування (англ. *deadlock*), коли вся система збірки назавжди зависає.

Класичний сценарій взаємного блокування виникає при недотриманні правила утримання токенів (англ. *Hold and Wait*):

1. Нехай у системі є пул з 2 токенів (1 неявний + 1 у пайпі).
2. Процес `Make A` запускає вкладений `Make B` (використовуючи свій неявний токен).
3. Процес `Make A` вирішує запустити другу задачу `Make C`. Для цього `Make A` забирає 1 токен із пайпа. Пайп стає порожнім.
4. Тепер працюють `Make B` та `Make C`. Обидва використовують свої неявні токени.
5. Для завершення своєї першої фази `Make B` потребує запустити допоміжну утиліту (наприклад, кодогенератор). Але для другої задачі йому потрібен токен з пайпа. `Make B` блокується на виклику `read()`.
6. Одночасно `Make C` теж потребує запустити допоміжну утиліту і також блокується на читанні з порожнього пайпа.
7. `Make A` чекає завершення `Make B` та `Make C`, утримуючи токен. `Make B` і `Make C` чекають токена від `Make A`. Збірка зупинилася назавжди.

![Диспетчеризація токенів: цикл подій клієнта без дедлоків](/root/sys/sys-bsystem/jobserver-protocol/img/deadlock-avoidance-flow.svg)
*Алгоритм диспетчеризації токенів: перевірка неявного слота, неблокувальний запит токена з пайпа та своєчасне повернення ресурсів у чергу очікування.*

Щоб гарантувати відсутність взаємних блокувань, клієнти Jobserver повинні дотримуватися **золотих правил клієнта**:

1. **Не утримувати зайві токени під час сну.** Якщо процес збирається заснути в очікуванні завершення дочірніх процесів (`waitpid()`, `poll()`), він не має права тримати в руках жодного токена з пайпа, якщо для цього токена прямо зараз не виконується реальний активний процес.
2. **Своєчасне повернення.** Якщо процес захопив токен з пайпа, але через внутрішню помилку або зміну умов не зміг запустити дочірній процес, токен повинен бути негайно повернений назад у пайп або семафор.
3. **Строга відповідність символу токена.** При використанні пайпа бажано повертати рівно той самий байт, який було вичитано під час запиту (хоча GNU Make сприймає будь-які байти, деякі діагностичні розширення відстежують байти для профілювання черги).

## Практична реалізація клієнта Jobserver (C та C++)

Нижче наведено повноцінну, надійну реалізацію клієнта Jobserver, сумісну зі стандартами POSIX (пайпи дескрипторів та FIFO) і Windows (іменовані семафори). Клієнт підтримує розбір змінної `MAKEFLAGS`, неблокувальне отримання токенів та безпечне повернення ресурсів за допомогою ідіоми RAII в C++.

:::tabs
```c
/* jobserver_client.c — POSIX & Windows C Client */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#include <windows.h>
#else
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#endif

typedef enum {
    JS_MODE_NONE,
    JS_MODE_PIPE,
    JS_MODE_FIFO,
    JS_MODE_SEMAPHORE
} jobserver_mode_t;

typedef struct {
    jobserver_mode_t mode;
    int has_implicit_token;
#if defined(_WIN32)
    HANDLE sem_handle;
#else
    int read_fd;
    int write_fd;
#endif
} jobserver_client_t;

/* Розбір змінної MAKEFLAGS та ініціалізація клієнта */
int jobserver_init(jobserver_client_t *js) {
    js->mode = JS_MODE_NONE;
    js->has_implicit_token = 1; /* Власний слот виконання */

    const char *makeflags = getenv("MAKEFLAGS");
    if (!makeflags) {
        makeflags = getenv("MFLAGS");
    }
    if (!makeflags) {
        return 0; /* Працюємо в автономному режимі з 1 неявним слотом */
    }

    /* Пошук --jobserver-auth= або --jobserver-fds= */
    const char *auth = strstr(makeflags, "--jobserver-auth=");
    if (!auth) {
        auth = strstr(makeflags, "--jobserver-fds=");
    }
    if (!auth) {
        return 0;
    }

    const char *val = strchr(auth, '=') + 1;

#if defined(_WIN32)
    /* Windows Semaphore: --jobserver-auth=semaphore_name або fifo: / semaphore: */
    char sem_name[256];
    if (strncmp(val, "semaphore:", 10) == 0) {
        val += 10;
    }
    size_t len = strcspn(val, " \t\n");
    if (len >= sizeof(sem_name)) len = sizeof(sem_name) - 1;
    strncpy(sem_name, val, len);
    sem_name[len] = '\0';

    js->sem_handle = OpenSemaphoreA(SYNCHRONIZE | SEMAPHORE_MODIFY_STATE, FALSE, sem_name);
    if (js->sem_handle != NULL) {
        js->mode = JS_MODE_SEMAPHORE;
        return 1;
    }
#else
    /* POSIX FIFO: --jobserver-auth=fifo:/path/to/fifo */
    if (strncmp(val, "fifo:", 5) == 0) {
        const char *path_start = val + 5;
        char fifo_path[512];
        size_t len = strcspn(path_start, " \t\n");
        if (len >= sizeof(fifo_path)) len = sizeof(fifo_path) - 1;
        strncpy(fifo_path, path_start, len);
        fifo_path[len] = '\0';

        int fd = open(fifo_path, O_RDWR | O_CLOEXEC | O_NONBLOCK);
        if (fd >= 0) {
            js->read_fd = fd;
            js->write_fd = fd;
            js->mode = JS_MODE_FIFO;
            return 1;
        }
    } else {
        /* Класичні дескриптори: --jobserver-auth=R,W */
        int rfd = -1, wfd = -1;
        if (sscanf(val, "%d,%d", &rfd, &wfd) == 2) {
            /* Переведення дескриптора читання в неблокувальний режим */
            int flags = fcntl(rfd, F_GETFL, 0);
            if (flags >= 0) {
                fcntl(rfd, F_SETFL, flags | O_NONBLOCK);
                js->read_fd = rfd;
                js->write_fd = wfd;
                js->mode = JS_MODE_PIPE;
                return 1;
            }
        }
    }
#endif
    return 0;
}

/* Спроба отримати токен для запуску задачі (1 = успіх, 0 = немає доступних токенів) */
int jobserver_acquire(jobserver_client_t *js, char *out_token) {
    /* 1. Спершу використовуємо свій неявний слот */
    if (js->has_implicit_token) {
        js->has_implicit_token = 0;
        *out_token = '+';
        return 1;
    }

    /* 2. Якщо неявний слот зайнятий — запитуємо зовнішній токен */
    if (js->mode == JS_MODE_NONE) {
        return 0; /* Немає підключення до пулу, додаткові задачі заборонені */
    }

#if defined(_WIN32)
    if (js->mode == JS_MODE_SEMAPHORE) {
        /* Неблокувальне опитування семафора */
        DWORD res = WaitForSingleObject(js->sem_handle, 0);
        if (res == WAIT_OBJECT_0) {
            *out_token = '+';
            return 1;
        }
        return 0;
    }
#else
    if (js->mode == JS_MODE_PIPE || js->mode == JS_MODE_FIFO) {
        char buf = 0;
        ssize_t n = read(js->read_fd, &buf, 1);
        if (n == 1) {
            *out_token = buf;
            return 1;
        }
        if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
            return 0; /* Токенів немає в наявності */
        }
    }
#endif
    return 0;
}

/* Повернення токена після завершення задачі */
void jobserver_release(jobserver_client_t *js, char token) {
    /* Якщо неявний слот вільний — повертаємо його */
    if (!js->has_implicit_token) {
        js->has_implicit_token = 1;
        return;
    }

    if (js->mode == JS_MODE_NONE) {
        return;
    }

#if defined(_WIN32)
    if (js->mode == JS_MODE_SEMAPHORE) {
        ReleaseSemaphore(js->sem_handle, 1, NULL);
    }
#else
    if (js->mode == JS_MODE_PIPE || js->mode == JS_MODE_FIFO) {
        ssize_t written = 0;
        while (written <= 0) {
            written = write(js->write_fd, &token, 1);
            if (written < 0 && errno == EINTR) {
                continue; /* Повтор при перериванні сигналом */
            }
            break;
        }
    }
#endif
}

/* Закриття клієнта */
void jobserver_close(jobserver_client_t *js) {
#if defined(_WIN32)
    if (js->mode == JS_MODE_SEMAPHORE && js->sem_handle) {
        CloseHandle(js->sem_handle);
        js->sem_handle = NULL;
    }
#else
    if (js->mode == JS_MODE_FIFO && js->read_fd >= 0) {
        close(js->read_fd);
        js->read_fd = -1;
        js->write_fd = -1;
    }
#endif
    js->mode = JS_MODE_NONE;
}
```
```cpp
// jobserver_client.hpp — Modern C++20/C++23 RAII Client
#pragma once

#include <string>
#include <string_view>
#include <optional>
#include <memory>
#include <cstdlib>
#include <system_error>

#if defined(_WIN32)
#include <windows.h>
#else
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#endif

namespace build_system {

enum class JobserverMode {
    None,
    Pipe,
    Fifo,
    Semaphore
};

class JobserverClient {
public:
    // RAII охоронець для автоматичного повернення токена
    class TokenGuard {
    public:
        TokenGuard(JobserverClient& client, char token, bool is_implicit) noexcept
            : client_(&client), token_(token), is_implicit_(is_implicit) {}

        ~TokenGuard() {
            release();
        }

        TokenGuard(const TokenGuard&) = delete;
        TokenGuard& operator=(const TokenGuard&) = delete;

        TokenGuard(TokenGuard&& other) noexcept
            : client_(other.client_), token_(other.token_), is_implicit_(other.is_implicit_) {
            other.client_ = nullptr;
        }

        TokenGuard& operator=(TokenGuard&& other) noexcept {
            if (this != &other) {
                release();
                client_ = other.client_;
                token_ = other.token_;
                is_implicit_ = other.is_implicit_;
                other.client_ = nullptr;
            }
            return *this;
        }

        void release() noexcept {
            if (client_) {
                client_->release_token(token_, is_implicit_);
                client_ = nullptr;
            }
        }

        [[nodiscard]] char token() const noexcept { return token_; }
        [[nodiscard]] bool is_implicit() const noexcept { return is_implicit_; }

    private:
        JobserverClient* client_{nullptr};
        char token_{'+'};
        bool is_implicit_{false};
    };

    JobserverClient() {
        init_from_env();
    }

    ~JobserverClient() {
        close();
    }

    JobserverClient(const JobserverClient&) = delete;
    JobserverClient& operator=(const JobserverClient&) = delete;

    [[nodiscard]] JobserverMode mode() const noexcept { return mode_; }

    // Спроба захопити токен з поверненням RAII обгортки
    [[nodiscard]] std::optional<TokenGuard> try_acquire() {
        // 1. Неявний власний слот
        if (has_implicit_token_) {
            has_implicit_token_ = false;
            return TokenGuard(*this, '+', true);
        }

        if (mode_ == JobserverMode::None) {
            return std::nullopt;
        }

#if defined(_WIN32)
        if (mode_ == JobserverMode::Semaphore && sem_handle_) {
            DWORD res = WaitForSingleObject(sem_handle_, 0);
            if (res == WAIT_OBJECT_0) {
                return TokenGuard(*this, '+', false);
            }
        }
#else
        if ((mode_ == JobserverMode::Pipe || mode_ == JobserverMode::Fifo) && read_fd_ >= 0) {
            char buf = 0;
            ssize_t n = read(read_fd_, &buf, 1);
            if (n == 1) {
                return TokenGuard(*this, buf, false);
            }
        }
#endif
        return std::nullopt;
    }

private:
    void release_token(char token, bool is_implicit) noexcept {
        if (is_implicit) {
            has_implicit_token_ = true;
            return;
        }

        if (mode_ == JobserverMode::None) {
            return;
        }

#if defined(_WIN32)
        if (mode_ == JobserverMode::Semaphore && sem_handle_) {
            ReleaseSemaphore(sem_handle_, 1, nullptr);
        }
#else
        if ((mode_ == JobserverMode::Pipe || mode_ == JobserverMode::Fifo) && write_fd_ >= 0) {
            while (true) {
                ssize_t written = write(write_fd_, &token, 1);
                if (written < 0 && errno == EINTR) {
                    continue;
                }
                break;
            }
        }
#endif
    }

    void init_from_env() {
        const char* raw_flags = std::getenv("MAKEFLAGS");
        if (!raw_flags) {
            raw_flags = std::getenv("MFLAGS");
        }
        if (!raw_flags) {
            return;
        }

        std::string_view flags(raw_flags);
        auto auth_pos = flags.find("--jobserver-auth=");
        if (auth_pos == std::string_view::npos) {
            auth_pos = flags.find("--jobserver-fds=");
        }
        if (auth_pos == std::string_view::npos) {
            return;
        }

        auto eq_pos = flags.find('=', auth_pos);
        if (eq_pos == std::string_view::npos) {
            return;
        }

        std::string_view val = flags.substr(eq_pos + 1);
        auto end_pos = val.find_first_of(" \t\n");
        if (end_pos != std::string_view::npos) {
            val = val.substr(0, end_pos);
        }

#if defined(_WIN32)
        if (val.starts_with("semaphore:")) {
            val.remove_prefix(10);
        }
        std::string sem_name(val);
        sem_handle_ = OpenSemaphoreA(SYNCHRONIZE | SEMAPHORE_MODIFY_STATE, FALSE, sem_name.c_str());
        if (sem_handle_) {
            mode_ = JobserverMode::Semaphore;
        }
#else
        if (val.starts_with("fifo:")) {
            std::string fifo_path(val.substr(5));
            int fd = open(fifo_path.c_str(), O_RDWR | O_CLOEXEC | O_NONBLOCK);
            if (fd >= 0) {
                read_fd_ = fd;
                write_fd_ = fd;
                mode_ = JobserverMode::Fifo;
            }
        } else {
            int rfd = -1, wfd = -1;
            std::string str_val(val);
            if (sscanf(str_val.c_str(), "%d,%d", &rfd, &wfd) == 2) {
                int fl = fcntl(rfd, F_GETFL, 0);
                if (fl >= 0) {
                    fcntl(rfd, F_SETFL, fl | O_NONBLOCK);
                    read_fd_ = rfd;
                    write_fd_ = wfd;
                    mode_ = JobserverMode::Pipe;
                }
            }
        }
#endif
    }

    void close() noexcept {
#if defined(_WIN32)
        if (sem_handle_) {
            CloseHandle(sem_handle_);
            sem_handle_ = nullptr;
        }
#else
        if (mode_ == JobserverMode::Fifo && read_fd_ >= 0) {
            ::close(read_fd_);
            read_fd_ = -1;
            write_fd_ = -1;
        }
#endif
        mode_ = JobserverMode::None;
    }

    JobserverMode mode_{JobserverMode::None};
    bool has_implicit_token_{true};
#if defined(_WIN32)
    HANDLE sem_handle_{nullptr};
#else
    int read_fd_{-1};
    int write_fd_{-1};
#endif
};

} // namespace build_system
```
:::

## Зведення архітектурних рішень

Протокол Jobserver демонструє, як мінімалістичний дизайн системного рівня здатен масштабуватися від невеликих утиліт до гігантських розподілених монорепозиторіїв із сотнями тисяч файлів:

| Параметр | POSIX Classic (Make 3.81+) | POSIX Modern FIFO (Make 4.4+) | Windows Named Semaphore |
|---|---|---|---|
| **Механізм ядра** | Анонімний канал `pipe()` | Іменований канал `mkfifo()` | Об'єкт `Named Semaphore` |
| **Параметр MAKEFLAGS** | `--jobserver-auth=R,W` | `--jobserver-auth=fifo:PATH` | `--jobserver-auth=NAME` |
| **Успадкування** | Через дескриптори `execve()` | Відкриття файлу `open()` | Відкриття за ім'ям `OpenSemaphore` |
| **Безпека дескрипторів** | Потребує ручного керування `FD_CLOEXEC` | Повна ізоляція (`O_CLOEXEC`) | Повна ізоляція дескрипторів |
| **Синхронізація подій** | `poll()`, `signalfd`, `pidfd` | `poll()`, `epoll`, `pidfd` | `WaitForMultipleObjects` |
| **Підтримка в тулчейнах** | GNU Make, Ninja, Cargo, CMake | GNU Make 4.4+, Cargo, Ninja | GNU Make (Windows), MSVC, Cargo |

Завдяки протоколу Jobserver сучасні багатоядерні системи підтримують 100% утилізацію процесора без взаємних блокувань, вичерпання пам'яті та деградації кешів.
