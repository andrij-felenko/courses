# Чому працює в терміналі й не працює службою

<preknowlist>
- [systemd: unit-файли та systemctl](root:sys-unix/systemd-systemctl-and-unit-files) — базовий синтаксис секцій [Unit], [Service], [Install] та життєвий цикл юнітів.
- [Демонізація: відхід у фон](root:sys-unix/daemonize) — створення сесій через setsid, подвійний fork та від'єднання керівного термінала.
- [Семантика виклику exec](root:sys-unix/exec-semantics) — як execve успадковує дескриптори, масив envp та поточний каталог.
- [Пісочниця служби](root:sys-unix/service-sandboxing) — простори назв (namespaces), обмеження файлової системи та системних викликів у systemd.
- [DynamicUser](root:sys-unix/dynamic-service-users) — динамічне виділення UID/GID, ізоляція /tmp та приватні каталоги служби.
</preknowlist>

Коли розробник запускає програму вручну в командній оболонці `./my-server --config config.yaml`, усе працює бездоганно: конфігураційні файли зчитуються, допоміжні утиліти викликаються, журнал подій у реальному часі виводиться на екран, а база даних SQLite створює необхідні таблиці. Але щойно той самий виконуваний файл прописують у юніт systemd (`ExecStart=/usr/local/bin/my-server`) або в розклад cron (`@reboot /usr/local/bin/my-server`), процес миттєво аварійно завершується з кодом помилки `1`, кодом systemd `203/EXEC`, зависає в нескінченному очікуванні, падає на системному виклику `open("config.yaml", O_RDONLY) = -1 ENOENT`, скаржиться на відсутність сторонніх бінарників (`sh: ffmpeg: command not found`) або перестає оновлювати логи в системному журналі.

Причина цієї розбіжності полягає в тому, що інтерактивний сеанс термінала надає процесу величезний невидимий каркас системного контексту, який розробник сприймає як належне. Під час інтерактивного входу оболонка автоматично завантажує файли ініціалізації (`/etc/profile`, `~/.bashrc`, `~/.zshrc`), наповнює масив змінних оточення сотнями записів (зокрема розширеним `$PATH`, шляхами `$HOME`, сесійними сокетами `$XDG_RUNTIME_DIR`), встановлює робочий каталог процесу в поточну теку проєкту, прив'язує стандартні потоки вводу/виводу до псевдотермінала (TTY) з автоматичною рядковою буферизацією і надає процесу повні права доступу користувача. 

Ініціалізаційний менеджер systemd (PID 1) або демон [cron](root:sys-unix/scheduled-jobs-cron-anacron) створюють для фонової служби принципово інше середовище — стерильний вакуум. Менеджер служб не запускає оболонку, не читає файли `.bashrc`, не виділяє термінал, встановлює робочий каталог у корінь файлової системи `/`, зрізає змінні оточення до мінімального базового набору, перемикає стандартні потоки вводу/виводу на блокову буферизацію та застосовує багатошарову пісочницю просторів назв (*namespaces*, простори імен) і лімітів контрольних груп (*cgroups*). Процес, що спирався на неявні припущення термінала, розбивається об ці чотири ізоляційні шари.

![Порівняння контексту виконання процесу у терміналі та під керуванням systemd](/root/course/unix/works-in-terminal-not-as-service/img/terminal-vs-service-execution-context.svg)

*Порівняння контексту виконання процесу у терміналі та під керуванням systemd.*

## Шар 1: Оточення та змінні середовища — зникнення неявного контексту

Кожен процес у Linux отримує змінні середовища через третій аргумент системного виклику `execve(const char *pathname, char *const argv[], char *const envp[])`. Коли програма стартує з термінала, її масив `envp` є прямим знімком пам'яті оболонки `bash` або `zsh`. Цей знімок формується в результаті виконання сценаріїв входу: туди потрапляють шляхи до віртуальних середовищ Python (`venv`), менеджери версій Node.js (`nvm`), менеджери пакетів Rust (`cargo`), локальні каталоги бінарників (`~/.local/bin`), конфігураційні змінні та секрети, експортовані користувачем.

Під час запуску системної служби systemd виконує виклик `fork()` безпосередньо з процесу PID 1 і передає у `execve` власноруч сформований стерильний масив змінних.

```
Термінальний сеанс (Bash):
envp = [
    "HOME=/home/developer",
    "USER=developer",
    "SHELL=/bin/bash",
    "PATH=/home/developer/.cargo/bin:/home/developer/.nvm/versions/node/v20/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "XDG_RUNTIME_DIR=/run/user/1000",
    "DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus",
    "DISPLAY=:0",
    "LANG=uk_UA.UTF-8",
    ... 80+ змінних оточення ...
]

Фонова служба systemd:
envp = [
    "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "LANG=C.UTF-8",
    "INVOCATION_ID=7a8b9c0d1e2f...",
    "JOURNAL_STREAM=8:123456"
]
```

Демон розкладу cron створює ще суворіше оточення: він запускає команди через оболонку `/bin/sh` (яка в дистрибутивах Debian та Ubuntu є мінімалістичною оболонкою Dash, а не Bash), очищає більшість змінних і встановлює `$PATH=/usr/bin:/bin`, `$SHELL=/bin/sh` та `$HOME` згідно із записом користувача в базі `/etc/passwd`. При цьому жодні файли профілю користувача (`~/.profile` або `~/.bashrc`) не виконуються. Крім того, синтаксис crontab має власну пастку: символ відсотка `%` інтерпретується cron як символ перенесення рядка, тому команди на кшталт `date +%Y-%m-%d` ламаються без екранування `\%`.

### Пастка мінімального $PATH та сторонніх інтерпретаторів

Найпоширеніша причина падіння служб, що використовують підпроцеси через системні виклики `system()`, `popen()` або `execvp()`, — це зміна значення змінної `$PATH` (*Path*, шлях пошуку бінарних файлів).

В інтерактивному сеансі розробника змінна `$PATH` містить шляхи до локальних інструментів. Якщо програма на Python чи Go викликає зовнішню команду `convert image.png image.webp` або виконує скрипт `ffmpeg`, пошук виконуваного файлу завершується успішно, оскільки бінарник лежить у `/home/developer/.local/bin` або `/opt/homebrew/bin`.

У службі systemd типовий `$PATH` містить лише `/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`. Якщо цільовий бінарник встановлено через ізольований пакетний менеджер або покладено в каталог користувача, функція пошуку `execvp` повертає помилку `-1` із кодом `ENOENT` (*No such file or directory*), а оболонка повертає код завершення `127`.

Окремою пасткою є директива `ExecStart=` у самому unit-файлі. Згідно зі специфікацією systemd, шлях до першого виконуваного файлу в `ExecStart=` **обов'язково має бути абсолютним** (наприклад, `/usr/bin/python3`, а не `python3`), якщо не увімкнено спеціальний префікс шляху. Якщо вказати `ExecStart=python3 main.py`, systemd поверне аварійний статус `203/EXEC` ще до спроби створення процесу.

### Відсутність $HOME та $USER

В інтерактивному сеансі змінні `$HOME` та `$USER` встановлюються підсистемою автентифікації PAM (*Pluggable Authentication Modules*, модулі вставної автентифікації) під час входу. Більшість високорівневих мов та бібліотек використовують ці змінні неявно:
1. `os.path.expanduser("~")` у Python або `std::env::var("HOME")` у Rust;
2. Бібліотеки конфігурації, що шукають файли за специфікацією XDG: `~/.config/myapp/config.toml` або кеш `~/.cache/`;
3. Драйвери баз даних та клієнти хмарних провайдерів (AWS SDK, Google Cloud SDK), які автоматично зчитують облікові ключі з `~/.aws/credentials` або `~/.kube/config`.

Якщо службу запущено від імені суперкористувача `root` без явної вказівки середовища, systemd не встановлює змінну `$HOME` автоматично (або встановлює її в `/root` лише за наявності директиви `User=`). Якщо ж служба використовує механізм динамічних користувачів `DynamicUser=yes`, каталогу `/home` у користувача взагалі не існує. У результаті виклик `getenv("HOME")` повертає нульовий покажчик `NULL`, що призводить до негайного падіння програми через розіменування нульового покажчика (*Segmentation fault*, порушення сегментації пам'яті, сигнал `SIGSEGV`), або програма намагається створити теку конфігурацій безпосередньо в кореневому каталозі `/` і розбивається об помилку `EACCES` (*Permission denied*, доступ заборонено).

### Відсутність графічного та сесійного контексту

Якщо програма взаємодіє з мультимедійними підсистемами (відтворює звук через PulseAudio / PipeWire, захоплює відео через апаратне прискорення GPU, надсилає системні сповіщення на робочий стіл або взаємодіє з шиною D-Bus), у терміналі вона автоматично підключається до сесійних сокетів завдяки змінним:
* `$XDG_RUNTIME_DIR` (вказує на `/run/user/1000/`);
* `$DBUS_SESSION_BUS_ADDRESS` (вказує на сокет сесійної шини D-Bus);
* `$DISPLAY` або `$WAYLAND_DISPLAY` (вказує на сервер відображення).

Фонова системна служба функціонує в загальносистемному контексті (*system context*), де немає доступу до графічного сеансу жодного користувача. Будь-яка спроба підключитися до сесійної шини D-Bus завершується помилкою `Connection refused`, а спроба ініціалізувати графічний бекенд OpenCV чи Qt аварійно зупиняє процес.

### Інженерне керування середовищем у systemd

Для вирішення проблем із [змінними середовища](root:unix/variable-did-not-reach-the-program) у unit-файлі застосовують директиви `Environment=` та `EnvironmentFile=`:

```ini
[Unit]
Description=Служба обробки медіафайлів
After=network.target

[Service]
Type=simple
User=mediaapp
Group=mediaapp

# Явне визначення шляхів та домашнього каталогу
Environment="PATH=/opt/mediaapp/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="HOME=/var/lib/mediaapp"
Environment="PYTHONUNBUFFERED=1"
Environment="APP_ENV=production"

# Завантаження зовнішнього конфігураційного файлу середовища
EnvironmentFile=-/etc/default/mediaapp

ExecStart=/opt/mediaapp/venv/bin/python3 /opt/mediaapp/src/main.py
Restart=on-failure
```

Знак мінуса `-/etc/default/mediaapp` вказує менеджерові systemd не вважати помилкою відсутність цього файлу на диску під час старту.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void audit_environment(void) {
    const char *path = getenv("PATH");
    const char *home = getenv("HOME");
    const char *user = getenv("USER");

    printf("[ENV AUDIT]\n");
    printf("  PATH: %s\n", path ? path : "(NOT SET - CRITICAL)");
    printf("  HOME: %s\n", home ? home : "(NOT SET - FALLBACK TO /)");
    printf("  USER: %s\n", user ? user : "(NOT SET)");

    if (!home) {
        /* Безпечний фолбек: не падати на розіменуванні NULL */
        setenv("HOME", "/tmp", 1);
    }
}
```
```cpp
#include <iostream>
#include <cstdlib>
#include <string_view>
#include <filesystem>

void audit_environment() {
    const char* path_raw = std::getenv("PATH");
    const char* home_raw = std::getenv("HOME");
    const char* user_raw = std::getenv("USER");

    std::string_view path = path_raw ? path_raw : "(NOT SET - CRITICAL)";
    std::string_view home = home_raw ? home_raw : "(NOT SET - FALLBACK TO /)";
    std::string_view user = user_raw ? user_raw : "(NOT SET)";

    std::cout << "[ENV AUDIT]\n"
              << "  PATH: " << path << "\n"
              << "  HOME: " << home << "\n"
              << "  USER: " << user << "\n";

    if (!home_raw) {
        setenv("HOME", "/tmp", 1);
    }
}
```
:::

## Шар 2: Робочий каталог (CWD) і пастка відносних шляхів

У ядрі Linux кожен процес описується структурою `struct task_struct` (файл `include/linux/sched.h`). Поточний робочий каталог процесу фіксується у внутрішній структурі файлової системи `task_struct->fs->pwd` (*Path Working Directory*, робочий каталог процесу). Коли процес виконує будь-який файловий системний виклик із відносним шляхом (`open("config.json", O_RDONLY)`, `stat("data/store.db", ...)`, `mkdir("logs", 0755)`), ядро перетворює цей відносний шлях на абсолютний, беручи за точку відліку саме значення покажчика `pwd`.

### Відносний шлях у терміналі проти служби

Коли розробник працює в консолі, термінальна сесія знаходиться в каталозі проєкту:
```
$ cd /home/developer/projects/analytics-service
$ ./bin/analytics-engine
```
У цьому разі `task_struct->fs->pwd` дорівнює `/home/developer/projects/analytics-service`. Виклик `open("config.json", O_RDONLY)` розв'язується ядром у відкриття `/home/developer/projects/analytics-service/config.json`.

Коли той самий виконуваний файл запускається службою systemd без явної вказівки робочого каталогу, systemd встановлює `task_struct->fs->pwd` у кореневий каталог системи `/`.

У результаті відбуваються наступні системні збої:
1. **Збій відкриття конфігурації:** виклик `open("config.json", O_RDONLY)` ядро інтерпретує як `open("/config.json", O_RDONLY)`. Оскільки в кореневому каталозі такого файлу немає, системний виклик негайно повертає помилку `-1 ENOENT` (*No such file or directory*), і програма завершує роботу;
2. **Збій створення баз даних та журналів:** виклик створення локальної бази даних SQLite `sqlite3_open("data.db", ...)` або створення файлу блокування `open("app.lock", O_CREAT|O_WRONLY, 0644)` призводить до спроби створити `/data.db` або `/app.lock`. Якщо служба працює не від імені суперкористувача, ядро блокує операцію з помилкою `EACCES` (*Permission denied*); якщо ж служба працює від `root`, кореневий розділ засмічується системними файлами програми.

### Інженерне вирішення через unit-файл та самовизначення бінарника

Для усунення проблеми відносних шляхів на рівні конфігурації служби використовують директиву `WorkingDirectory=`:

```ini
[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/analytics-service
ExecStart=/opt/analytics-service/bin/analytics-engine
```

Крім того, сучасні стандарти systemd надають [спеціалізовані керовані каталоги](root:sys-unix/service-directories):
* `ConfigurationDirectory=myapp` (створює `/etc/myapp` і передає шлях через змінну `$CONFIGURATION_DIRECTORY`);
* `StateDirectory=myapp` (створює робочу теку стану `/var/lib/myapp` з правами потрібного користувача і змінною `$STATE_DIRECTORY`);
* `RuntimeDirectory=myapp` (створює тимчасовий каталог сокетів та pid-файлів у пам'яті `/run/myapp` і змінну `$RUNTIME_DIRECTORY`);
* `LogsDirectory=myapp` (створює каталог `/var/log/myapp` і змінну `$LOGS_DIRECTORY`).

На рівні коду надійні програми не покладаються на `cwd`, а обчислюють абсолютний шлях до власних ресурсів відносно розташування самого виконуваного бінарника через спеціальне посилання віртуальної файлової системи `/proc/self/exe`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <limits.h>
#include <libgen.h>
#include <string.h>

int get_executable_dir(char *out_path, size_t max_len) {
    char exe_path[PATH_MAX];
    ssize_t len = readlink("/proc/self/exe", exe_path, sizeof(exe_path) - 1);
    if (len == -1) {
        return -1;
    }
    exe_path[len] = '\0';

    char *dir = dirname(exe_path);
    if (strlen(dir) >= max_len) {
        return -1;
    }
    strncpy(out_path, dir, max_len - 1);
    out_path[max_len - 1] = '\0';
    return 0;
}
```
```cpp
#include <iostream>
#include <filesystem>
#include <system_error>

namespace fs = std::filesystem;

fs::path get_executable_directory() {
    std::error_code ec;
    fs::path exe_path = fs::canonical("/proc/self/exe", ec);
    if (ec) {
        // Фолбек на поточний робочий каталог у разі помилки читання /proc
        return fs::current_path();
    }
    return exe_path.parent_path();
}
```
:::

## Шар 3: Фізика стандартних потоків вводу/виводу та термінала

Найменш очевидні для прикладного програміста збої виникають на стику між стандартними дескрипторами вводу/виводу (`stdin` 0, `stdout` 1, `stderr` 2), драйвером термінала та внутрішньою буферизацією [C-рантайму](root:sf-lang/c-runtime) (`glibc`).

### Відсутність керівного TTY та опитування isatty(0)

В інтерактивному сеансі файловий дескриптор `0` процесу вказує на пристрій псевдотермінала (наприклад, `/dev/pts/3`). У структурі ядра `task_struct->signal->tty` зберігається посилання на активний сесійний термінал. Коли програма виконує виклик `isatty(0)`, функція звертається до ядра через системний виклик `ioctl(0, TCGETS, ...)`: якщо дескриптор є терміналом, виклик повертає успіх `1`. Якщо дескриптор не є терміналом, ядро повертає помилку `ENOTTY` (*Inappropriate ioctl for device*, невідповідний виклик керування пристроєм), і `isatty` повертає `0`.

У фоновій службі systemd керівний термінал повністю відсутній (`task_struct->signal->tty == NULL`), а дескриптор стандартного вводу `stdin` (FD 0) перенаправляється на спеціальний пристрій `/dev/null`.

Це призводить до двох типових аварійних сценаріїв:
1. **Аварія на інтерактивних запитах:** якщо програма (або сторонній модуль автентифікації) намагається запитати підтвердження у користувача `scanf("%c", &confirm)`, зчитати пароль через `getpass("Password: ")` або викликати функцію бібліотеки `readline()`, зчитування з `/dev/null` повертає миттєвий символ кінця файлу `EOF` (0 байтів). Якщо код не перевіряє помилки, виникає нескінченний цикл споживання 100% процесора або викидається критичне виключення (наприклад, `EOFError` у Python), яке вбиває процес;
2. **Зависання на запитах безпеки:** деякі утиліти CLI під час виявлення `isatty(0) == 0` намагаються відкрити безпосередній керівний термінал через виклик `open("/dev/tty", O_RDWR)`. Оскільки у служби немає прив'язаного термінала, системний виклик повертає фатальну помилку `ENXIO` (*No such device or address*, пристрій або адреса відсутні).

### Зміна режиму буферизації стандартної бібліотеки C

Будь-яка програма, скомпільована з використанням бібліотеки C (`glibc`, `musl`) або написана мовами Python, Ruby чи C++, при роботі з потоками `stdout` / `stderr` спирається на буферизацію простору користувача (*I/O buffering*).

Стандарт POSIX та реалізація `glibc` визначають три режими буферизації файлових потоків `FILE*`:
1. `_IONBF` (*Unbuffered*, небуферизований режим): дані негайно передаються ядру системним викликом `write(2)` без затримки;
2. `_IOLBF` (*Line Buffered*, рядкова буферизація): дані накопичуються в буфері пам'яті до моменту, поки програма не виведе символ нового рядка `\n` (або поки буфер не переповниться);
3. `_IOFBF` (*Fully Buffered*, повна блокова буферизація): дані накопичуються великими блоками (за замовчуванням 4096 байтів) і скидаються системним викликом `write(2)` **лише тоді, коли весь буфер заповнено на 100%** або коли викликано функцію `fflush()`.

Коли процес стартує, бібліотека `glibc` під час ініціалізації викликає `isatty(fileno(stdout))`:
* Якщо дескриптор є терміналом (`isatty == 1`), `stdout` автоматично перемикається в режим **`_IOLBF`** (рядкова буферизація);
* Якщо дескриптор є файлом, конвеєром (*pipe*) або сокетом (`isatty == 0`), `stdout` автоматично перемикається в режим **`_IOFBF`** (повна блокова буферизація по 4 КБ).

![Режими буферизації стандартного потоку виводу у терміналі та службі](/root/course/unix/works-in-terminal-not-as-service/img/stdio-buffering-tty-vs-pipe.svg)

*Режими буферизації стандартного потоку виводу у терміналі та службі.*

### Чому зникають логи в journalctl

У фоновій службі systemd стандартні дескриптори виводу `stdout` (FD 1) та `stderr` (FD 2) підключаються до сокетів або конвеєрів, що ведуть до демона `systemd-journald`. Оскільки дескриптор `1` не є терміналом, стандартна бібліотека вмикає блоковий режим `_IOFBF`.

Це викликає два критичні ефекти:
1. **Затримка появи повідомлень:** якщо служба записує короткі рядки журналів (наприклад, `[INFO] Server started\n`, довжиною 25 байтів), системний виклик `write()` не викликається взагалі. Рядки накопичуються в оперативній пам'яті процесу. Журнал `journalctl -u myapp -f` залишається абсолютно порожнім, створюючи ілюзію того, що служба зависла під час старту;
2. **Повна втрата логів під час падіння:** якщо в процесі стається фатальна помилка пам'яті (`SIGSEGV`), сигнал примусового завершення від ядра (`SIGKILL` за перевищення пам'яті) або викликається аварійне завершення `abort()`, процес гине миттєво. Оскільки деструктори простору користувача не встигають викликати `fflush(stdout)`, усі нескинуті 4 КБ логів в оперативній пам'яті зникають назавжди. У журналі `journalctl` не залишається жодного запису про те, що саме відбувалося перед падінням.

### Інженерне керування буферизацією виводу

Щоб забезпечити надійне передавання [структурованих логів](root:sf-release/structured-logging) у системний журнал, використовують наступні підходи:
1. **На рівні коду C/C++:** примусове вимкнення буферизації або встановлення рядкового режиму через функцію `setvbuf()` під час старту функції `main()`;
2. **На рівні середовища Python:** передача змінної оточення `PYTHONUNBUFFERED=1` (або прапорця інтерпретатора `python3 -u`);
3. **На рівні unit-файлу:** директиви `StandardOutput=journal` та `StandardError=journal`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void setup_service_stdio(void) {
    /* Перевіряємо, чи ми працюємо не в інтерактивному терміналі */
    if (!isatty(fileno(stdout))) {
        /* Примусово вмикаємо рядкову буферизацію для stdout */
        setvbuf(stdout, NULL, _IOLBF, 0);
    }
    
    /* stderr завжди має бути небуферизованим */
    setvbuf(stderr, NULL, _IONBF, 0);

    /* Закриваємо або перенаправляємо stdin у разі потреби */
    if (!isatty(fileno(stdin))) {
        freopen("/dev/null", "r", stdin);
    }
}
```
```cpp
#include <iostream>
#include <cstdio>
#include <unistd.h>

void setup_service_stdio() {
    // Вимикаємо синхронізацію C++ iostream зі стандартними C-буферами для швидкості
    std::ios_base::sync_with_stdio(false);

    if (!isatty(fileno(stdout))) {
        // Вмикаємо рядковий режим буферизації для потоку C
        setvbuf(stdout, nullptr, _IOLBF, 0);
    }
    
    setvbuf(stderr, nullptr, _IONBF, 0);

    if (!isatty(fileno(stdin))) {
        std::freopen("/dev/null", "r", stdin);
    }
}
```
:::

## Шар 4: Обмеження безпеки, простори назв та пісочниця

Сучасні дистрибутиви Linux будують запуск служб за принципом найменших привілеїв (*Principle of Least Privilege*). В інтерактивному терміналі розробник зазвичай володіє повним доступом до домашнього каталогу, має право писати в глобальний `/tmp`, відкривати довільні сокети та користуватися відносно високими лімітами дескрипторів сесії. У системній службі за замовчуванням або за явною конфігурацією застосовується глибока [пісочниця](root:sys-unix/service-sandboxing).

![Чотири концентричні рівні ізоляції та обмежень служби systemd](/root/course/unix/works-in-terminal-not-as-service/img/systemd-isolation-layers.svg)

*Чотири концентричні рівні ізоляції та обмежень служби systemd.*

### Динамічні та непривілейовані користувачі

Запуск служби від імені суперкористувача `root` є серйозним ризиком безпеки. Тому в unit-файлах застосовують директиву `User=app` або сучасний механізм [DynamicUser=yes](root:sys-unix/dynamic-service-users).

Коли ввімкнено `DynamicUser=yes`:
1. systemd динамічно виділяє тимчасовий ідентифікатор користувача UID та групи GID із захищеного пулу `61184..65519`;
2. Цей обліковий запис не існує у файлі `/etc/passwd`, він створюється в пам'яті лише на час життя процесу;
3. Служба повністю позбавляється прав запису в будь-яку точку файлової системи, крім каталогів, явно створених директивами `RuntimeDirectory=`, `StateDirectory=` або `CacheDirectory=`.

Якщо програма розраховувала записати кеш у `/var/cache/app` або змінити власний виконуваний файл, виклик `open(..., O_WRONLY)` негайно зазнає невдачі з помилкою `EACCES`.

### Ізоляція файлової системи через простори назв (Namespaces)

Під час підготовки служби до запуску systemd використовує системний виклик `unshare(CLONE_NEWNS)` або `clone()`, створюючи для процесу власний відокремлений простір назв монтування файлової системи (*Mount Namespace*).

Основні директиви захисту та їхній вплив на виконання:

| Директива systemd | Механізм ядра Linux | Наслідок для програми |
|---|---|---|
| `PrivateTmp=yes` | Монтує приватний `tmpfs` у `/tmp` та `/var/tmp` для цього процесу | Сокети та файли, створені службою у `/tmp`, невидимі іншим процесам і терміналу; утиліти з термінала не можуть знайти сокет `/tmp/app.sock` |
| `ProtectSystem=strict` | Перемонтовує всю файлову систему (`/usr`, `/boot`, `/etc`, `/lib`) як `MS_RDONLY` | Спроба створити файл або змінити конфігурацію викликає аварію з помилкою `EROFS` (*Read-only file system*) |
| `ProtectHome=yes` | Монтує порожні каталоги `tmpfs` поверх `/home`, `/root` та `/run/user` | Спроба прочитати файли користувача або конфіги `~/.bashrc` викликає помилку `EACCES` або `ENOENT` |
| `NoNewPrivileges=yes` | Встановлює біт ядра `PR_SET_NO_NEW_PRIVS` | Забороняє зміну привілеїв через біти `setuid`/`setgid` (наприклад, утиліти `sudo`, `ping` чи `chfn` всередині підпроцесів припиняють працювати) |
| `ProtectKernelTunables=yes` | Робить точки `/proc/sys`, `/sys` доступними лише для читання | Спроби змінити мережеві параметри TCP або налаштування пам'яті ядра повертають помилку `EPERM` |

Найпідступнішою є помилка, пов'язана з `PrivateTmp=yes`: розробник запускає клієнтську утиліту в терміналі, яка намагається підключитися до UNIX-сокету `/tmp/engine.sock`, створеного службою. Клієнт падає з помилкою `ENOENT` (*File not found*), хоча служба звітує про успішне створення сокету, оскільки вони знаходяться в різних просторах назв монтування. Правильне інженерне рішення — використовувати для сокетів каталог `/run/myapp/` через директиву `RuntimeDirectory=myapp`.

### Ресурсні ліміти cgroups та ліміти дескрипторів файлів

В інтерактивному сеансі ліміти ресурсів процесу визначаються конфігурацією PAM-модуля `/etc/security/limits.conf`. Зазвичай користувачеві виділяється ліміт на кількість відкритих файлових дескрипторів `RLIMIT_NOFILE` у розмірі 1024 (м'який ліміт) або 524288 (жорсткий ліміт).

У systemd кожна служба запускається у власному зрізі контрольної групи (*cgroup slice*). Менеджер systemd встановлює ліміти явно:
1. **Ліміт файлових дескрипторів (`LimitNOFILE=`):** Якщо високонавантажений вебсервер або брокер повідомлень відкриває тисячі мережевих з'єднань одночасно, а в юніті не вказано `LimitNOFILE=65535`, виклики `accept(2)` або `socket(2)` починають масово повертати помилку `EMFILE` (*Too many open files*). Старий ліміт 1024 дескриптори на процес є критичною межею: функція `select(2)` у стандартній бібліотеці C жорстко обмежена макросом `FD_SETSIZE = 1024` і спричиняє переповнення буфера пам'яті при роботі з дескрипторами вище 1023, тому сучасні мережеві служби вимагають використання викликів `poll(2)` або `epoll(7)`;
2. **Жорсткий ліміт пам'яті (`MemoryMax=`):** Якщо служба споживає пам'ять понад значення, вказане в `MemoryMax=512M`, ядро Linux не викликає помилку `NULL` у функції `malloc()`. Замість цього ядерний механізм контрольних груп Cgroup OOM Killer негайно знищує процес сигналом `SIGKILL` (код `9`). Служба падає без запису стек-трейсу в логи, а команда `systemctl status` показує статус `status=9/KILL` або `exit-code, status=137`. Стан лімітів cgroup v2 можна перевірити безпосередньо у файловій системі контрольних груп `/sys/fs/cgroup/system.slice/myapp.service/memory.events`, де лічильник `oom_kill` показує точну кількість знищень процесу через брак пам'яті.

## Діагностичний стенд та еталонний unit-файл

Щоб точно локалізувати розбіжності між консоллю та службою, операційна система Linux надає утиліту `systemd-run`. Вона дозволяє виконати програму в ізольованому контексті тимчасової служби прямо з термінала:

```bash
# Запуск бінарника у стерильному середовищі з підключенням до термінала через пайп
systemd-run --user --pipe --wait -p WorkingDirectory=/tmp env
```

Ця команда наочно покаже зріз змінних середовища та обмежень, які отримає процес у реальних умовах запуску під керуванням systemd.

Якщо служба вже запущена і поводиться некоректно, повний стан її робочого оточення можна перевірити через віртуальну файлову систему `/proc`:

```bash
# Отримання PID служби
PID=$(systemctl show --property MainPID --value myapp.service)

# Перевірка реальних змінних оточення процесу
xargs -0 -L1 echo < /proc/$PID/environ

# Перевірка поточного робочого каталогу (CWD)
ls -ld /proc/$PID/cwd

# Перевірка відкритих файлових дескрипторів та точок перенаправлення
ls -l /proc/$PID/fd/

# Перевірка встановлених лімітів ресурсів
cat /proc/$PID/limits
```

Крім того, поведінку процесу під час старту можна простежити за допомогою утиліти `strace`:
```bash
# Трасування системних викликів служби під час ініціалізації
strace -f -e trace=openat,execve,ioctl,write,setvbuf -p $PID
```
Трасування миттєво покаже системні виклики `ioctl(0, TCGETS, ...)` із кодом `ENOTTY`, невдалі спроби `openat(AT_FDCWD, "config.yaml", O_RDONLY)` у каталозі `/`, а також відсутність системних викликів `write(1, ...)` через блокування в пам'яті glibc.

### Комплексна утиліта аудиту середовища

Для автономного тестування програми перед її пакуванням у службу доцільно впровадити внутрішній режим діагностичного аудиту:

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/resource.h>
#include <sys/stat.h>

void perform_full_system_audit(void) {
    printf("=== ДІАГНОСТИКА СЕРЕДОВИЩА ПРОЦЕСУ ===\n");

    /* 1. Перевірка TTY */
    int tty_in = isatty(fileno(stdin));
    int tty_out = isatty(fileno(stdout));
    printf("[TTY] stdin: %s, stdout: %s\n",
           tty_in ? "TTY (interactive)" : "PIPE/SOCKET (service)",
           tty_out ? "TTY (_IOLBF)" : "PIPE/SOCKET (_IOFBF)");

    /* 2. Перевірка CWD */
    char cwd[1024];
    if (getcwd(cwd, sizeof(cwd))) {
        printf("[CWD] Поточний каталог: %s\n", cwd);
        if (cwd[0] == '/' && cwd[1] == '\0') {
            printf("  [УВАГА] Процес запущено в корені /! Відносні шляхи будуть хибними.\n");
        }
    }

    /* 3. Перевірка критичних змінних */
    printf("[ENV] PATH: %s\n", getenv("PATH") ? getenv("PATH") : "(NULL)");
    printf("[ENV] HOME: %s\n", getenv("HOME") ? getenv("HOME") : "(NULL)");

    /* 4. Ліміти дескрипторів */
    struct rlimit rl;
    if (getrlimit(RLIMIT_NOFILE, &rl) == 0) {
        printf("[LIMITS] NOFILE soft: %lu, hard: %lu\n",
               (unsigned long)rl.rlim_cur, (unsigned long)rl.rlim_max);
    }

    /* 5. Тестовий запис у /tmp */
    FILE *tmp_test = fopen("/tmp/.audit_service_probe", "w");
    if (tmp_test) {
        printf("[FS] Запис у /tmp: УСПІХ\n");
        fclose(tmp_test);
        unlink("/tmp/.audit_service_probe");
    } else {
        perror("[FS] Помилка запису у /tmp");
    }
    printf("=========================================\n");
}
```
```cpp
#include <iostream>
#include <cstdlib>
#include <filesystem>
#include <unistd.h>
#include <sys/resource.h>
#include <fstream>

namespace fs = std::filesystem;

void perform_full_system_audit() {
    std::cout << "=== ДІАГНОСТИКА СЕРЕДОВИЩА ПРОЦЕСУ ===\n";

    // 1. Перевірка TTY
    bool tty_in = isatty(fileno(stdin));
    bool tty_out = isatty(fileno(stdout));
    std::cout << "[TTY] stdin: " << (tty_in ? "TTY (interactive)" : "PIPE/SOCKET (service)")
              << ", stdout: " << (tty_out ? "TTY (_IOLBF)" : "PIPE/SOCKET (_IOFBF)") << "\n";

    // 2. Перевірка CWD
    std::error_code ec;
    fs::path cwd = fs::current_path(ec);
    if (!ec) {
        std::cout << "[CWD] Поточний каталог: " << cwd.string() << "\n";
        if (cwd == "/") {
            std::cout << "  [УВАГА] Процес запущено в корені /! Відносні шляхи будуть хибними.\n";
        }
    }

    // 3. Перевірка критичних змінних
    const char* path = std::getenv("PATH");
    const char* home = std::getenv("HOME");
    std::cout << "[ENV] PATH: " << (path ? path : "(NULL)") << "\n"
              << "[ENV] HOME: " << (home ? home : "(NULL)") << "\n";

    // 4. Ліміти дескрипторів
    struct rlimit rl{};
    if (getrlimit(RLIMIT_NOFILE, &rl) == 0) {
        std::cout << "[LIMITS] NOFILE soft: " << rl.rlim_cur
                  << ", hard: " << rl.rlim_max << "\n";
    }

    // 5. Тестовий запис у /tmp
    std::ofstream tmp_test("/tmp/.audit_service_probe");
    if (tmp_test.is_open()) {
        std::cout << "[FS] Запис у /tmp: УСПІХ\n";
        tmp_test.close();
        std::filesystem::remove("/tmp/.audit_service_probe");
    } else {
        std::cout << "[FS] Помилка запису у /tmp (можливо увімкнено ProtectSystem/PrivateTmp)\n";
    }
    std::cout << "=========================================\n";
}
```
:::

### Еталонна конфігурація виробничої служби

Нижче наведено архітектурно надійний шаблон unit-файлу, який враховує всі чотири системні шари ізоляції, запобігає падінню через відсутність TTY, гарантує доставку логів і встановлює безпечні межі ресурсів:

```ini
[Unit]
Description=Еталонна фонова служба обробки даних
After=network-online.target
Wants=network-online.target
Documentation=https://docs.example.com/myapp

[Service]
Type=simple

# 1. Шар ідентичності та облікового запису
User=appservice
Group=appservice
# За потреби максимальної ізоляції: DynamicUser=yes

# 2. Шар робочого каталогу та керованих просторів
WorkingDirectory=/opt/appservice
RuntimeDirectory=appservice
RuntimeDirectoryMode=0755
StateDirectory=appservice
StateDirectoryMode=0700
ConfigurationDirectory=appservice

# 3. Шар змінних середовища
Environment="PATH=/opt/appservice/bin:/usr/local/bin:/usr/bin:/bin"
Environment="HOME=/var/lib/appservice"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=-/etc/default/appservice

# 4. Шар стандартних потоків вводу/виводу
StandardInput=null
StandardOutput=journal
StandardError=journal

# 5. Шар безпеки та пісочниці
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectKernelTunables=yes
ProtectControlGroups=yes
NoNewPrivileges=yes
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
RestrictRealtime=yes

# 6. Шар лімітів ресурсів cgroups
LimitNOFILE=65535
LimitNPROC=4096
MemoryMax=1G
TasksMax=512

# 7. Виконання та політика перезапуску
ExecStart=/opt/appservice/bin/app-engine --config /etc/appservice/config.yaml
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5s
TimeoutStopSec=30s

[Install]
WantedBy=multi-user.target
```

Коли програма розробляється з розумінням цих чотирьох системних кордонів, вона позбавляється прихованих залежностей від оточення користувача і працює у фоновій службі настільки ж детерміновано, надійно та передбачувано, як і під час ручного тестування в терміналі.
