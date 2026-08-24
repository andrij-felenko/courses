# Landlock LSM: безпривілейоване обмеження файлового доступу

<preknowlist>
- [Модель привілеїв POSIX та capabilities](book:unix-linux/capabilities) — розподіл привілеїв у Linux, успадкування прав та прапорець `PR_SET_NO_NEW_PRIVS`.
- [Фільтрація системних викликів Seccomp](book:unix-linux/seccomp-filtering) — обмеження системних викликів із користувацького простору та його межі щодо шляхів VFS.
- [Фреймворк Linux Security Modules](book:unix-linux/lsm-framework) — архітектура хуків LSM та контроль доступу в ядрі Linux.
</preknowlist>

Обробка недовірених даних у користувацькому просторі — таких як декодування мережевих пакетів, парсинг документів чи рендеринг веб-сторінок — несе постійний ризик виявлення вразливостей переповнення буфера чи довільного виконання коду. У класичній моделі прав Linux процес успадковує повні привілеї користувача, який його запустив. Якщо процес фонової обробки зображень від імені звичайного користувача піддається зламу, зловмисник отримує прямий доступ до файлів `~/.ssh/id_rsa`, `~/.gnupg` чи баз даних браузера. Традиційні механізми мандатного контролю доступу (SELinux, AppArmor) вимагають прав суперкористувача (root) для написання та завантаження політик безпеки, що унеможливлює створення самостійних пісочниць (self-sandboxing) у самому коді прикладних програм. Системний модуль Landlock розв'язує цю проблему, надаючи будь-якому безпривілейованому процесу можливість самостійно обмежувати власні права доступу до файлової системи та мережі на рівні ядра.

## 1. Механізми ізоляції та виклик безпривілейованого контролю

Еволюція безпеки в Linux тривалий час спиралася на розмежування прав за ідентифікаторами користувачів та груп. Однак зростання складності прикладного програмного забезпечення виявило фундаментальні межі класичних підходів.

### 1.1. Межі DAC та недостатність Seccomp для VFS

Традиційна модель вибіркового контролю доступу (DAC — Discretionary Access Control) оперує триплетами бітів прав (`rwx`) для власника, групи та інших користувачів, а також розширеними списками ACL. З точки зору ядра, будь-який процес, створений користувачем `alice`, володіє однаковим рівнем довіри. Переглядач PDF-файлів, текстовий редактор або фоновий демон звукового сервера мають тотожні права на читання та зміну будь-якого об'єкта в домашньому каталозі. Компрометація одного з компонентів через вразливість у сторонній бібліотеці призводить до компрометації всіх персональних даних користувача.

Мандатні механізми (MAC — Mandatory Access Control), такі як SELinux або AppArmor, дозволяють призначати профілі безпеки конкретним бінарним файлам. Вони ефективні для системних сервісів, але не вирішують проблему прикладного ПЗ з кількох причин:
1. Адміністрування політик вимагає привілеїв root та завантаження глобальних конфігурацій у систему.
2. Програми не можуть динамічно зменшувати свої привілеї залежно від контексту (наприклад, після завершення ініціалізації або перед відкриттям файлу від невідомого відправника).

Розроблений для фільтрації системних викликів механізм `seccomp-bpf` забезпечує перехоплення сисколів на основі аналізу їхніх номерів та числових аргументів у структурі `struct seccomp_data`. Проте `seccomp` не спроможний контролювати файловий доступ за шляхами. Системний виклик `openat(AT_FDCWD, "/home/alice/.ssh/id_rsa", O_RDONLY)` передає вказівник на рядок у користувацькій пам'яті. BPF-програма всередині `seccomp` не має права розіменовувати вказівники через загрозу стану гонитви типу TOCTOU (Time-of-Check to Time-of-Use): поки ядро перевіряє рядок, інший паралельний потік процесу може змінити його вміст у пам'яті. Крім того, рядкові шляхи не враховують символічні посилання, жорсткі посилання, відносні шляхи (`../`) та простори імен монтування (mount namespaces).

### 1.2. Концепція Unprivileged Self-Sandboxing

Ізоляція на основі просторів імен (User Namespaces, Mount Namespaces) та `chroot` вимагає складного конструювання віртуального файлового дерева. Для цього потрібно монтувати `/proc`, `/dev`, копіювати динамічні бібліотеки та налаштовувати UID-мапінг. Це прийнятно для контейнерів (Docker, Podman), але занадто громіздко для окремого процесу-робітника у складі браузера чи поштового клієнта.

Landlock реалізує концепцію безпривілейованого самообмеження (Unprivileged Self-Sandboxing). Замість зовнішнього опису політики адміністратором, програма самостійно конструює набір правил безпеки у своєму коді, після чого звертається до ядра з проханням застосувати ці обмеження до себе та своїх майбутніх нащадків. Оскільки ядро Linux виконує перевірку правил безпосередньо в хуках LSM на рівні структури віртуальної файлової системи (VFS), Landlock повністю усуває загрози TOCTOU та маніпуляції рядковими шляхами.

## 2. Архітектура Landlock у ядрі Linux

Внутрішня організація Landlock спирається на інфраструктуру Linux Security Modules (LSM), інтегруючись у точки перехоплення операцій з об'єктами VFS та сокетами.

### 2.1. Ієрархія доменів та шарів правил

Коли процес створює та застосовує набір правил Landlock, ядро формує внутрішній об'єкт — домен (domain), який представляється структурою `struct landlock_ruleset`. Цей домен прив'язується до структури привілеїв поточного процесу (`current->cred->security`).

Landlock підтримує пошарове накладання обмежень. Якщо процес спочатку застосовує один ruleset, а пізніше — інший, ядро не замінює старі правила, а додає новий шар (layer) до існуючого домену.

```
Шар 1 (Layer 1): Дозволено читання в /usr та /etc
Шар 2 (Layer 2): Дозволено читання та запис лише в /tmp/session_123
-------------------------------------------------------------------
Результат (Intersection): Доступ надається ЛИШЕ якщо він дозволений 
                           ОДНОЧАСНО у Шар 1 ТА у Шар 2.
```

Операція перетину (intersection) гарантує монотонність зменшення привілеїв. Жоден наступний виклик не може скасувати обмеження, накладені попередніми шарами, або додати нові дозволи поза межами вже існуючих.

### 2.2. Внутрішні структури ядра: landlock_ruleset, landlock_hierarchy та landlock_object

Усередині ядра Landlock оперує кількома ключовими структурами даних, які забезпечують високу швидкість перевірки прав:

1. `struct landlock_ruleset`: Головний контейнер політики, що містить червоно-чорне дерево (`rb_node`) для швидкого пошуку об'єктів та маску контрольованих операцій `handled_access_fs`.
2. `struct landlock_hierarchy`: Описує дерево успадкування доменів. Кожен новий шар посилається на батьківський `hierarchy`, що дозволяє відстежувати глибину стекінгу та перевіряти зв'язок між процесами.
3. `struct landlock_object`: Представляє об'єкт файлової системи (inode). Він містить слабке посилання (underlying reference) на `struct inode` та список правил, пов'язаних із цим inode у різних шарах.

![Загальна архітектура застосування Landlock LSM](img/landlock-arch.svg)
*Рис. 1. Загальна архітектура застосування Landlock LSM.*

### 2.3. Послідовність перевірки VFS-хуків у ядрі

Розглянемо виклик `openat(AT_FDCWD, "/var/log/syslog", O_RDONLY)` під контролем Landlock:
1. Процес звертається до сисколу `openat()`. Системний обробник VFS `do_filp_open()` виконує резолюцію шляху через `path_lookupat()`.
2. Після успішного знаходження елемента VFS `struct path` ядро викликає LSM-хук `security_file_open(file)`.
3. Модуль Landlock перехоплює виклик у функції `landlock_file_open()`. Вона дістає активний домен із `current_cred()->security`.
4. Якщо домен порожній (Landlock не активовано), перевірка миттєво завершується успіхом.
5. Якщо домен містить активні шари, Landlock бере `path->dentry` цільового файлу і починає ітеративний підйом вгору до кореня `/`. На кожному кроці перевіряється, чи прив'язаний `landlock_object` до даного `inode`, і чи містить шар маску дозволу `LANDLOCK_ACCESS_FS_READ_FILE`.
6. Якщо підйом досягає кореня і хоча б один шар не видав дозволу, `landlock_file_open()` повертає `-EACCES`. VFS відхиляє відкриття файлу без виконання подальших системних дій.

## 3. Системний інтерфейс API Landlock

Взаємодія з Landlock з користувацького простору здійснюється через три системні виклики: `landlock_create_ruleset()`, `landlock_add_rule()` та `landlock_restrict_self()`.

### 3.1. Створення набору правил через `landlock_create_ruleset()`

Першим кроком є визначення спектра операцій, які будуть контролюватися пісочницею. Для цього заповнюється структура `struct landlock_ruleset_attr` та викликається системний виклик створення:

```c
int landlock_create_ruleset(const struct landlock_ruleset_attr *attr,
                            size_t size, uint32_t flags);
```

Аргумент `handled_access_fs` містить бітову маску дій з файловою системою, які підпадають під облік. Усі дії, вказані в цій масці, за замовчуванням переводяться в режим заборони (deny-by-default). Дії, які не були включені до `handled_access_fs`, залишаються поза контролем Landlock (для них діють лише стандартні перевірки DAC та інших LSM).

Основними бітовими прапорцями контролю файлової системи є:
- `LANDLOCK_ACCESS_FS_EXECUTE`: Виконання бінарних файлів.
- `LANDLOCK_ACCESS_FS_WRITE_FILE`: Запис даних у файли.
- `LANDLOCK_ACCESS_FS_READ_FILE`: Читання вмісту файлів.
- `LANDLOCK_ACCESS_FS_READ_DIR`: Відкриття каталогу та перегляд його вмісту.
- `LANDLOCK_ACCESS_FS_REMOVE_DIR`: Видалення порожніх каталогів.
- `LANDLOCK_ACCESS_FS_REMOVE_FILE`: Видалення файлів.
- `LANDLOCK_ACCESS_FS_MAKE_CHAR`: Створення символьних спеціальних пристроїв.
- `LANDLOCK_ACCESS_FS_MAKE_DIR`: Створення нових каталогів.
- `LANDLOCK_ACCESS_FS_MAKE_REG`: Створення звичайних файлів.
- `LANDLOCK_ACCESS_FS_MAKE_SOCK`: Створення сокетів домену UNIX.
- `LANDLOCK_ACCESS_FS_MAKE_FIFO`: Створення іменованих каналів (FIFO).
- `LANDLOCK_ACCESS_FS_MAKE_BLOCK`: Створення блокових пристроїв.
- `LANDLOCK_ACCESS_FS_MAKE_SYM`: Створення символічних посилань.

У разі успішного виклику ядро повертає новий анонімний файловий дескриптор, який представляє створений набір правил.

### 3.2. Додавання дозволів через `landlock_add_rule()`

Формування дозволених шляхів здійснюється шляхом додавання конкретних правил до створеного `ruleset_fd`:

```c
int landlock_add_rule(int ruleset_fd, enum landlock_rule_type rule_type,
                      const void *rule_attr, uint32_t flags);
```

Для файлової системи параметр `rule_type` має значення `LANDLOCK_RULE_PATH_BENEATH`, а `rule_attr` вказує на структуру `struct landlock_path_beneath_attr`:

```c
struct landlock_path_beneath_attr {
    __u64 allowed_access;
    __s32 parent_fd;
};
```

Поле `parent_fd` є файловим дескриптором каталогу або файлу, відкритого за допомогою `open()` з прапорцем `O_PATH` або `O_RDONLY`. Прапорець `O_PATH` є оптимальним, оскільки він відкриває дескриптор без виконання фактичного читання чи запису об'єкта. Поле `allowed_access` задає підмножину дозволених дій із тих, які були раніше зареєстровані в `handled_access_fs`. Правило діє рекурсивно на сам об'єкт та всі його дочірні елементи.

### 3.3. Обов'язкова установка `PR_SET_NO_NEW_PRIVS`

Перед активацією набору правил процес зобов'язаний встановити прапорець `NO_NEW_PRIVS` через системний виклик `prctl`.

:::tabs
```c
/* Установити NO_NEW_PRIVS у C */
if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
    perror("prctl(PR_SET_NO_NEW_PRIVS)");
    return -1;
}
```
```cpp
// Установити NO_NEW_PRIVS у C++
if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
    throw std::system_error(errno, std::generic_category(), 
                           "Помилка prctl(PR_SET_NO_NEW_PRIVS)");
}
```
:::

Установлення `NO_NEW_PRIVS` — сувора вимога ядра до будь-яких безпривілейованих операцій із самообмеження прав. Без цього прапорця процес міг би створити пісочницю з модифікованим середовищем виконання або підміненими файлами, після чого виконати бінарний файл із встановленим SUID-бітом (наприклад, `/usr/bin/sudo` чи `/usr/bin/passwd`). Оскільки SUID-програма виконується з правами UID власника файлу (зазвичай root), підміна її середовища з боку обмеженого процесу дозволила б локально підвищити привілеї. 

Прапорець `NO_NEW_PRIVS` гарантує, що під час виконання `execve` біти SUID/SGID та файлові capabilities будуть ігноруватися ядром. Це унеможливлює здобуття нових привілеїв потоком чи його нащадками.

### 3.4. Активація ізоляції через `landlock_restrict_self()`

Завершальним етапом є застосування правил до поточного потоку виконання через системний виклик:

```c
int landlock_restrict_self(int ruleset_fd, uint32_t flags);
```

Після успішного повернення з цього виклику обмеження Landlock стають активними. Процес може закрити файловий дескриптор `ruleset_fd` за допомогою `close()`, оскільки ядро вже скопіювало та прив'язало структуру правил до кредитів процесу. Усі наступні системні виклики поточного потоку та всіх нащадків, створених через `fork()` або `clone()`, підлягатимуть суворому контролю. Домен прив'язується до кредитів потоку, що викликав: інші вже наявні потоки того самого процесу обмежень не дістають, тож багатопотокова програма мусить викликати `landlock_restrict_self()` у кожному потоці — або застосовувати пісочницю до створення потоків.

## 4. Еволюція ABI та версіонування можливостей

Розвиток Landlock відбувається шляхом поетапного розширення набору контрольованих операцій. Щоб зберегти зворотну сумісність між програмами та різними версіями ядра Linux, використовується версіонування ABI (Application Binary Interface).

### 4.1. Динамічне визначення версії ABI

Програма запитує у ядра максимальну версію ABI, яку воно підтримує, передавши прапорець `LANDLOCK_CREATE_RULESET_VERSION`.

:::tabs
```c
/* Отримання версії ABI Landlock у C */
int abi_version = landlock_create_ruleset(NULL, 0, LANDLOCK_CREATE_RULESET_VERSION);
if (abi_version < 0) {
    perror("Landlock не підтримується ядром");
}
```
```cpp
// Отримання версії ABI Landlock у C++
int abi_version = landlock_create_ruleset(nullptr, 0, LANDLOCK_CREATE_RULESET_VERSION);
if (abi_version < 0) {
    throw std::system_error(errno, std::generic_category(), 
                           "Landlock не підтримується ядром");
}
```
:::

Якщо повернуте значення від'ємне (наприклад, `-ENOSYS`), це свідчить про те, що поточне ядро не має підтримки Landlock або модуль не увімкнений у списку параметра завантаження `lsm=` — щоб Landlock працював, `landlock` має бути в цьому списку.

Коректна програма повинна маскувати біти `handled_access_fs`, залишаючи лише ті прапорці, які підтримуються поточним ABI ядра. Якщо передати ядру невизначений прапорець, виклик `landlock_create_ruleset()` завершиться з помилкою `EINVAL`.

### 4.2. Хронологія версій ABI Landlock

Хронологічний розвиток можливостей Landlock охоплює такі ключові етапи:

- **ABI 1 (Linux 5.13):** Початковий реліз. Включає базовий контроль доступу до файлової системи (13 прапорців дій: читання, запис, виконання, створення та видалення каталогів чи спеціальних файлів).
- **ABI 2 (Linux 5.19):** Додано прапорець `LANDLOCK_ACCESS_FS_REFER`. Він забезпечує контроль операцій `rename()` та `link()`. Переміщення файлів або створення жорстких посилань між різними каталогами тепер вимагає наявності дозволу `REFER` для обох каталогів (джерела та призначення).
- **ABI 3 (Linux 6.2):** Додано прапорець `LANDLOCK_ACCESS_FS_TRUNCATE`. Забезпечує контроль зміни розміру файлів через системні виклики `truncate()`, `ftruncate()` та `open()` із прапорцем `O_TRUNC`.
- **ABI 4 (Linux 6.7):** Початок розширення підсистеми на мережевий стек. Введено маску `handled_access_net` та прапорці `LANDLOCK_ACCESS_NET_BIND_TCP` і `LANDLOCK_ACCESS_NET_CONNECT_TCP` для обмеження зв'язування та встановлення TCP-з'єднань за номерами портів.
- **ABI 5 (Linux 6.10):** Додано прапорець `LANDLOCK_ACCESS_FS_IOCTL_DEV` для контролю доступу до керування спеціальними пристроями через виклики `ioctl()`.
- **ABI 6 (Linux 6.12):** Запроваджено поле `scoped` у `struct landlock_ruleset_attr` та прапорці `LANDLOCK_SCOPE_ABSTRACT_UNIX_SOCKET` і `LANDLOCK_SCOPE_SIGNAL`: перший забороняє з'єднуватися з абстрактними UNIX-сокетами, створеними поза доменом, другий — надсилати сигнали процесам за межами домену.

### 4.3. Мережевий контроль в ABI 4+

Починаючи з ABI 4, Landlock виходить за межі VFS і дозволяє контролювати мережеву активність процесів без прав root. Для створення мережевого набору правил заповнюється поле `handled_access_net`:

:::tabs
```c
/* Конфігурація мережевого ruleset у C */
struct landlock_ruleset_attr net_attr = {
    .handled_access_net = LANDLOCK_ACCESS_NET_BIND_TCP |
                          LANDLOCK_ACCESS_NET_CONNECT_TCP,
};
int net_ruleset = landlock_create_ruleset(&net_attr, sizeof(net_attr), 0);

struct landlock_net_port_attr port_attr = {
    .allowed_access = LANDLOCK_ACCESS_NET_CONNECT_TCP,
    .port = 443, /* Дозволити вихідні з'єднання лише на HTTPS */
};
landlock_add_rule(net_ruleset, LANDLOCK_RULE_NET_PORT, &port_attr, 0);
```
```cpp
// Конфігурація мережевого ruleset у C++
landlock_ruleset_attr net_attr{};
net_attr.handled_access_net = LANDLOCK_ACCESS_NET_BIND_TCP |
                              LANDLOCK_ACCESS_NET_CONNECT_TCP;

UniqueFd net_ruleset(landlock_create_ruleset(&net_attr, sizeof(net_attr), 0));

landlock_net_port_attr port_attr{};
port_attr.allowed_access = LANDLOCK_ACCESS_NET_CONNECT_TCP;
port_attr.port = 443; // Дозволити вихідні з'єднання лише на HTTPS

landlock_add_rule(net_ruleset.get(), LANDLOCK_RULE_NET_PORT, &port_attr, 0);
```
:::

Мережевий контроль блокує виклики `bind()` та `connect()` для сокетів сімейства `AF_INET` та `AF_INET6`, якщо відповідні порти не вказані у списках дозволів `LANDLOCK_RULE_NET_PORT`.

## 5. Практичний приклад: створення ізольованої пісочниці

Розглянемо практичну реалізацію утиліти-обгортки (sandbox runner), яка запускає довільну команду в ізольованому середовищі. Наша мета — дозволити програмі виконання файлів із каталогів `/usr`, `/bin`, `/lib`, `/lib64`, читання конфігурацій з `/etc`, але повністю заблокувати доступ до будь-яких інших частин файлової системи (включаючи `/home` та `/tmp`).

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/landlock.h>

#ifndef landlock_create_ruleset
static inline int landlock_create_ruleset(const struct landlock_ruleset_attr *attr,
                                          size_t size, uint32_t flags) {
    return syscall(SYS_landlock_create_ruleset, attr, size, flags);
}

static inline int landlock_add_rule(int ruleset_fd,
                                    enum landlock_rule_type rule_type,
                                    const void *rule_attr, uint32_t flags) {
    return syscall(SYS_landlock_add_rule, ruleset_fd, rule_type, rule_attr, flags);
}

static inline int landlock_restrict_self(int ruleset_fd, uint32_t flags) {
    return syscall(SYS_landlock_restrict_self, ruleset_fd, flags);
}
#endif

/* Допоміжна функція для додавання дозволу на шлях */
static int add_path_rule(int ruleset_fd, const char *path, __u64 access_mask) {
    int fd = open(path, O_PATH | O_CLOEXEC);
    if (fd < 0) {
        /* Якщо каталог відсутній у системі, ігноруємо його */
        return 0;
    }

    struct landlock_path_beneath_attr path_attr = {
        .allowed_access = access_mask,
        .parent_fd = fd,
    };

    int res = landlock_add_rule(ruleset_fd, LANDLOCK_RULE_PATH_BENEATH, &path_attr, 0);
    close(fd);
    return res;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <команда> [аргументи...]\n", argv[0]);
        return 1;
    }

    /* 1. Перевірка версії ABI */
    int abi = landlock_create_ruleset(NULL, 0, LANDLOCK_CREATE_RULESET_VERSION);
    if (abi < 1) {
        perror("Landlock не підтримується ядром");
        return 1;
    }

    /* Маска дій для ABI 1 */
    __u64 handled_fs = LANDLOCK_ACCESS_FS_EXECUTE |
                       LANDLOCK_ACCESS_FS_WRITE_FILE |
                       LANDLOCK_ACCESS_FS_READ_FILE |
                       LANDLOCK_ACCESS_FS_READ_DIR |
                       LANDLOCK_ACCESS_FS_REMOVE_DIR |
                       LANDLOCK_ACCESS_FS_REMOVE_FILE |
                       LANDLOCK_ACCESS_FS_MAKE_CHAR |
                       LANDLOCK_ACCESS_FS_MAKE_DIR |
                       LANDLOCK_ACCESS_FS_MAKE_REG |
                       LANDLOCK_ACCESS_FS_MAKE_SOCK |
                       LANDLOCK_ACCESS_FS_MAKE_FIFO |
                       LANDLOCK_ACCESS_FS_MAKE_BLOCK |
                       LANDLOCK_ACCESS_FS_MAKE_SYM;

    /* Враховуємо прапорці ABI 2 та 3, якщо ядро їх підтримує */
    if (abi >= 2) {
        handled_fs |= LANDLOCK_ACCESS_FS_REFER;
    }
    if (abi >= 3) {
        handled_fs |= LANDLOCK_ACCESS_FS_TRUNCATE;
    }

    struct landlock_ruleset_attr ruleset_attr = {
        .handled_access_fs = handled_fs,
    };

    /* 2. Створення набору правил */
    int ruleset_fd = landlock_create_ruleset(&ruleset_attr, sizeof(ruleset_attr), 0);
    if (ruleset_fd < 0) {
        perror("Помилка landlock_create_ruleset");
        return 1;
    }

    __u64 read_exec = LANDLOCK_ACCESS_FS_READ_FILE | 
                      LANDLOCK_ACCESS_FS_READ_DIR | 
                      LANDLOCK_ACCESS_FS_EXECUTE;

    __u64 read_only = LANDLOCK_ACCESS_FS_READ_FILE | 
                      LANDLOCK_ACCESS_FS_READ_DIR;

    /* 3. Додаємо дозволені шляхи */
    add_path_rule(ruleset_fd, "/usr", read_exec);
    add_path_rule(ruleset_fd, "/bin", read_exec);
    add_path_rule(ruleset_fd, "/lib", read_exec);
    add_path_rule(ruleset_fd, "/lib64", read_exec);
    add_path_rule(ruleset_fd, "/etc", read_only);

    /* 4. Встановлюємо PR_SET_NO_NEW_PRIVS */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)) {
        perror("Помилка prctl(PR_SET_NO_NEW_PRIVS)");
        close(ruleset_fd);
        return 1;
    }

    /* 5. Застосовуємо правила */
    if (landlock_restrict_self(ruleset_fd, 0)) {
        perror("Помилка landlock_restrict_self");
        close(ruleset_fd);
        return 1;
    }

    close(ruleset_fd);

    /* 6. Запуск цільової програми */
    execvp(argv[1], &argv[1]);
    perror("Помилка execvp");
    return 1;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <filesystem>
#include <system_error>
#include <utility>
#include <unistd.h>
#include <fcntl.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/landlock.h>

#ifndef landlock_create_ruleset
static inline int landlock_create_ruleset(const struct landlock_ruleset_attr *attr,
                                          size_t size, uint32_t flags) {
    return static_cast<int>(syscall(SYS_landlock_create_ruleset, attr, size, flags));
}

static inline int landlock_add_rule(int ruleset_fd,
                                    enum landlock_rule_type rule_type,
                                    const void *rule_attr, uint32_t flags) {
    return static_cast<int>(syscall(SYS_landlock_add_rule, ruleset_fd, rule_type, rule_attr, flags));
}

static inline int landlock_restrict_self(int ruleset_fd, uint32_t flags) {
    return static_cast<int>(syscall(SYS_landlock_restrict_self, ruleset_fd, flags));
}
#endif

/* RAII-обгортка для безпечного управління файловими дескрипторами */
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(std::exchange(other.fd_, -1)) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = std::exchange(other.fd_, -1);
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

struct PathPermission {
    std::filesystem::path path;
    uint64_t access_mask;
};

class LandlockSandbox {
    UniqueFd ruleset_fd_;
    uint32_t abi_version_{0};

public:
    LandlockSandbox() {
        int abi = landlock_create_ruleset(nullptr, 0, LANDLOCK_CREATE_RULESET_VERSION);
        if (abi < 1) {
            throw std::system_error(errno, std::generic_category(), "Landlock не підтримується ядром");
        }
        abi_version_ = static_cast<uint32_t>(abi);

        uint64_t handled_fs = LANDLOCK_ACCESS_FS_EXECUTE |
                             LANDLOCK_ACCESS_FS_WRITE_FILE |
                             LANDLOCK_ACCESS_FS_READ_FILE |
                             LANDLOCK_ACCESS_FS_READ_DIR |
                             LANDLOCK_ACCESS_FS_REMOVE_DIR |
                             LANDLOCK_ACCESS_FS_REMOVE_FILE |
                             LANDLOCK_ACCESS_FS_MAKE_CHAR |
                             LANDLOCK_ACCESS_FS_MAKE_DIR |
                             LANDLOCK_ACCESS_FS_MAKE_REG |
                             LANDLOCK_ACCESS_FS_MAKE_SOCK |
                             LANDLOCK_ACCESS_FS_MAKE_FIFO |
                             LANDLOCK_ACCESS_FS_MAKE_BLOCK |
                             LANDLOCK_ACCESS_FS_MAKE_SYM;

        if (abi_version_ >= 2) {
            handled_fs |= LANDLOCK_ACCESS_FS_REFER;
        }
        if (abi_version_ >= 3) {
            handled_fs |= LANDLOCK_ACCESS_FS_TRUNCATE;
        }

        landlock_ruleset_attr attr{};
        attr.handled_access_fs = handled_fs;

        int fd = landlock_create_ruleset(&attr, sizeof(attr), 0);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка landlock_create_ruleset");
        }
        ruleset_fd_.reset(fd);
    }

    void allow_path(const std::filesystem::path& p, uint64_t access_mask) {
        UniqueFd path_fd(::open(p.c_str(), O_PATH | O_CLOEXEC));
        if (!path_fd.valid()) {
            return; /* Пропускаємо відсутні шляхи */
        }

        landlock_path_beneath_attr path_attr{};
        path_attr.allowed_access = access_mask;
        path_attr.parent_fd = path_fd.get();

        if (landlock_add_rule(ruleset_fd_.get(), LANDLOCK_RULE_PATH_BENEATH, &path_attr, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка landlock_add_rule для " + p.string());
        }
    }

    void apply() {
        if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка prctl(PR_SET_NO_NEW_PRIVS)");
        }

        if (landlock_restrict_self(ruleset_fd_.get(), 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка landlock_restrict_self");
        }

        ruleset_fd_.reset(); /* Закриваємо дескриптор після успішного накладання */
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <команда> [аргументи...]\n";
        return 1;
    }

    try {
        LandlockSandbox sandbox;

        constexpr uint64_t read_exec = LANDLOCK_ACCESS_FS_READ_FILE | 
                                       LANDLOCK_ACCESS_FS_READ_DIR | 
                                       LANDLOCK_ACCESS_FS_EXECUTE;

        constexpr uint64_t read_only = LANDLOCK_ACCESS_FS_READ_FILE | 
                                       LANDLOCK_ACCESS_FS_READ_DIR;

        std::vector<PathPermission> permissions = {
            {"/usr", read_exec},
            {"/bin", read_exec},
            {"/lib", read_exec},
            {"/lib64", read_exec},
            {"/etc", read_only}
        };

        for (const auto& perm : permissions) {
            sandbox.allow_path(perm.path, perm.access_mask);
        }

        sandbox.apply();

        ::execvp(argv[1], &argv[1]);
        throw std::system_error(errno, std::generic_category(), "Помилка execvp");

    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка пісочниці: " << ex.what() << '\n';
        return 1;
    }
}
```
:::

Тестування скомпільованого бінарника показує ефективність ізоляції:

```bash
$ ./landlock_runner /bin/bash
bash-5.2$ ls /usr
bin  lib  lib64  local  share
bash-5.2$ cat /etc/hostname
workstation
bash-5.2$ ls /home
ls: cannot open directory '/home': Permission denied
bash-5.2$ touch /tmp/test.txt
touch: cannot touch '/tmp/test.txt': Permission denied
```

Спроба доступу до неперелічених каталогів миттєво блокується ядром, повертаючи помилку `Permission denied`.

## 6. Крайові випадки, пастки безпеки та продуктивність

Практична інтеграція Landlock вимагає врахування особливостей VFS та взаємодії з іншими системними механізмами.

### 6.1. Паттерн Open-Then-Sandbox та робота з дескрипторами

Виклик `landlock_restrict_self()` змінює перевірку привілеїв лише для **нових** операцій відкриття файлів та каталогів. Файлові дескриптори, які були відкриті до виклику `landlock_restrict_self()`, зберігають свої початкові права на читання та запис.

Це дозволяє використовувати архітектурний паттерн «open-then-sandbox»:
1. Процес відкриває лог-файли, файли конфігурації чи створює сокети під час ініціалізації.
2. Процес конструює суворий набір правил Landlock без надання прав на зміну конфігурацій чи читання системних каталогів.
3. Процес викликає `landlock_restrict_self()`.

Після цього процес продовжує використовувати вже відкриті дескриптори для запису логів чи взаємодії з мережею, але втрачає можливість відкрити будь-який інший файл у файловій системі.

### 6.2. Жорсткі посилання та операції Rename (Прапорець REFER)

В ABI v1 контролю за переміщенням файлів не було зовсім. Перенести файл до іншого батьківського каталогу означало б непомітно змінити набір прав, що на нього поширюються, — а виразити такий дозвіл правилами v1 було нічим. Тому ядро під Landlock просто відмовляло: `rename()` чи `link()`, у яких вихідний і цільовий каталоги різні, поверталися з помилкою `EXDEV`, наче йдеться про різні файлові системи. Перейменування в межах одного каталогу лишалося дозволеним.

Починаючи з ABI v2, прапорець `LANDLOCK_ACCESS_FS_REFER` дає змогу явно надати право переміщувати файли та створювати жорсткі посилання між різними каталогами. Для виконання `rename()` або `link()` процес повинен мати право `REFER` як для вихідного каталогу, так і для каталогу призначення.

### 6.3. Передача файлових дескрипторів через UNIX-сокети

Якщо процес у пісочниці отримує відкритий файловий дескриптор від іншого, неізольованого процесу через механізм IPC `SCM_RIGHTS` (UNIX domain socket), Landlock не блокує використання цього дескриптора. Перевірка Landlock відбувається під час виконання системних викликів відкриття (`openat`), а не під час використання вже отриманих дескрипторів через `read()` чи `write()`. Окремий випадок — `ioctl()` над файлами пристроїв: від ABI 5 ядро судить його за правами, записаними в момент відкриття файлу, тож дескриптор, відкритий поза пісочницею, і тут лишається повноправним.

Це дозволяє будувати мультипроцесні архітектури (на зразок Chrome або Firefox), де привілейований процес-брокер відкриває необхідні ресурси та передає їх дескриптори ізольованим процесам-рендерерам.

### 6.4. Діагностика та трасування помилок доступу

Діагностика збоїв доступу у програмах, захищених Landlock, вимагає аналізу кодів помилок системних викликів та перевірки статусів процесу. Основні інструменти відлагодження:

- **Інспекція status:** Перевірка значення `NoNewPrivs` у `/proc/<pid>/status` дозволяє переконатися, що процес знаходиться в режимі обмеження привілеїв:
  ```bash
  grep NoNewPrivs /proc/self/status
  NoNewPrivs: 1
  ```
- **Трасування через strace:** Утиліта `strace` дозволяє відстежити системні виклики Landlock та моменти відмови у доступі (`-EACCES`):
  ```bash
  strace -e trace=landlock_create_ruleset,landlock_add_rule,landlock_restrict_self ./landlock_runner /bin/ls /home
  ```

### 6.5. Продуктивність та обчислювальні накладні витрати

Оскільки перевірка правил Landlock здійснюється під час кожного виклику відкриття файлу чи каталогу, ядро мусить перевіряти відповідність масок доступу для кожного активного шару. 

Обчислювальна складність перевірки в ядрі описується співвідношенням:

```
T = O(L · D)
```

де `L` — кількість накладених шарів Landlock (кількість викликів `landlock_restrict_self()`), а `D` — глибина ієрархії каталогів від цільового файлу до кореня файлової системи.

Для типових 1–3 шарів ця робота губиться на тлі самої резолюції шляху, яку `openat()` виконує в будь-якому разі. Нескінченно нарощувати шари не вийде й технічно: кількість шарів у домені обмежена ядром (у поточній реалізації — 16), і виклик `landlock_restrict_self()` понад цю межу завершується помилкою `E2BIG`.

## 7. Порівняльний аналіз із суміжними механізмами

Для вибору оптимального інструменту ізоляції доцільно порівняти Landlock з іншими технологіями безпеки Linux:

| Характеристика | Landlock LSM | Seccomp-BPF | AppArmor / SELinux | Unprivileged User Namespaces |
|---|---|---|---|---|
| **Об'єкт контролю** | Шляхи VFS та TCP-порти | Номери системних викликів | Системні ресурси за профілем | Простори імен UID/GID та Mount |
| **Необхідні привілеї** | Безпривілейований (Unprivileged) | Безпривілейований (Unprivileged) | Користувач root (`CAP_MAC_ADMIN`) | Безпривілейований, якщо дистрибутив це дозволяє |
| **Гранулярність VFS** | Ієрархічна (Path Beneath) | Відсутня (лише числові аргументи виклику) | Повний контроль за шляхами/контекстами | На рівні змонтованих файлових систем |
| **Механізм налаштування** | Динамічний API в коді додатка | BPF-інструкції в коді додатка | Статичні текстові файли конфігурації | Системні виклики `unshare`/`clone` |
| **Успадкування** | Автоматичне монотонне звуження | Автоматичне монотонне звуження | Визначене в профілі (`change_profile`) | Наслідується в межах простору імен |
| **Захист від TOCTOU** | Повний (робота з inodes) | Відсутній для рядків у пам'яті | Повний (інтеграція з LSM) | Повний (на рівні мапінгу VFS) |

Найбільш ефективною практикою для розробки високонадійного ПЗ є комбінування Landlock та Seccomp-BPF. Seccomp відсікає невикористовувані системні виклики (наприклад, `kexec_load`, `reboot`, `ptrace`), а Landlock обмежує файлову систему та мережу для тих системних викликів, які були дозволені Seccomp.

## Висновок

Landlock LSM дає розробникам прикладного програмного забезпечення можливість реалізовувати принцип найменших привілеїв (Principle of Least Privilege) безпосередньо у коді додатків. Виключення потреби у правах суперкористувача та сумісність із прапорцем `PR_SET_NO_NEW_PRIVS` роблять Landlock доступним та безпечним інструментом для захисту користувацьких даних у сучасних дистрибутивах Linux.
