# 📋 Специфікація системних викликів перенаправлення та маніпулювання дескрипторами

Ця довідкова специфікація надає повний контракт системних викликів ядра Linux (`dup`, `dup2`, `dup3`, `pipe`, `pipe2`, `fcntl`) та детальний опис відповідних ядерних структур даних, які реалізують низькорівневе маніпулювання файловими дескрипторами та перенаправлення потоків введення-виведення.

---

## 1. Системні виклики маніпуляції дескрипторами

### 1.1 `dup`

Системний виклик `dup` створює новий файловий дескриптор, який посилається на той самий відкритий об'єкт файлу у ядрі (`struct file`), що й заданий дескриптор `oldfd`.

:::tabs
```c
#include <unistd.h>

int dup(int oldfd);
```
```cpp
#include <unistd.h>
#include <system_error>

int newfd = ::dup(oldfd);
```
:::

*   **`oldfd`**: Існуючий відкритий файловий дескриптор процесу.
*   **Повертає значення**: У разі успішного виконання повертається найменший вільний номер дескриптора в таблиці даного процесу. У разі виникнення помилки повертається значення `-1`, а системна змінна `errno` встановлюється у відповідний код помилки.
*   **Властивості та семантика**: Новостворений дескриптор повністю ділить з дескриптором `oldfd` поточну позицію читання або запису у файлі (`f_pos`), прапорці статусу відкритого файлу (`f_flags`), прапорці доступу та вказівник на іноду VFS. Однак новий дескриптор володіє власним незалежним набором прапорців дескриптора (file descriptor flags). Прапорець close-on-exec (`FD_CLOEXEC`) у новоствореного дескриптора завжди скинутий у значення `0`.

---

### 1.2 `dup2`

Системний виклик `dup2` атомарно копіює вказівник дескриптора `oldfd` у цільовий дескриптор з номером `newfd`.

:::tabs
```c
#include <unistd.h>

int dup2(int oldfd, int newfd);
```
```cpp
#include <unistd.h>
#include <system_error>

int res = ::dup2(oldfd, newfd);
```
:::

*   **`oldfd`**: Вхідний існуючий файловий дескриптор.
*   **`newfd`**: Цільовий номер дескриптора, який перевизначається викликом.
*   **Повертає значення**: У разі успіху повертає цільовий дескриптор `newfd`. У разі помилки повертається `-1` з відповідним кодом у `errno`.
*   **Детальні правила поведінки**:
    1. Якщо дескриптор `newfd` був раніше відкритий у процесі, ядро атомарно закриває його перед виконанням дублювання. Помилки закриття при цьому мовчки ігноруються.
    2. Якщо `oldfd == newfd` і `oldfd` є дійсним відкритим дескриптором, виклик `dup2` негайно повертає `newfd` без жодних змін і без повторного закриття.
    3. Якщо `oldfd` є недійсним дескриптором, виклик завершується помилкою `EBADF`, а цільовий дескриптор `newfd` залишається нечіпаним і **не закривається**.

---

### 1.3 `dup3`

Розширений системний виклик (доступний у Linux починаючи з версії ядра 2.6.27), що дозволяє атомарно встановлювати додаткові прапорці для новостворюваного дескриптора.

:::tabs
```c
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>

int dup3(int oldfd, int newfd, int flags);
```
```cpp
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <system_error>

int res = ::dup3(oldfd, newfd, O_CLOEXEC);
```
:::

*   **`flags`**: Битова маска прапорців створення дескриптора. Наразі підтримується наступний прапорець:
    *   `O_CLOEXEC`: Атомарно встановлює прапорець `FD_CLOEXEC` на новоствореному дескрипторі `newfd`.
*   **Ключові відмінності від `dup2`**:
    1. Якщо `oldfd == newfd`, виклик `dup3()` **завжди** повертає помилку `EINVAL`. Це зроблено для запобігання непомітним логічним помилкам у програмах.
    2. Усуває стан гонки (race condition) у багатопотокових програмах між викликом дублювання дескриптора та наступним явним встановленням прапорця `fcntl(newfd, F_SETFD, FD_CLOEXEC)`.

---

### 1.4 `pipe` та `pipe2`

Створюють однонаправлений анонімний канал даних (pipe) у пам'яті ядра з двома пов'язаними дескрипторами.

:::tabs
```c
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>

int pipe(int pipefd[2]);
int pipe2(int pipefd[2], int flags);
```
```cpp
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <array>
#include <system_error>

std::array<int, 2> fds{};
int res1 = ::pipe(fds.data());
int res2 = ::pipe2(fds.data(), O_CLOEXEC);
```
:::

*   **`pipefd[0]`**: Дескриптор для читання даних з каналу (read end).
*   **`pipefd[1]`**: Дескриптор для запису даних у канал (write end).
*   **`flags` (для `pipe2`)**:
    *   `O_CLOEXEC`: Встановлює прапорець close-on-exec для обох створених дескрипторів.
    *   `O_NONBLOCK`: Встановлює неблокуючий режим введення-виведення для обох кінців каналу.
    *   `O_DIRECT`: Створює канал у режимі пакетизації даних (packet mode, доступно в Linux 4.5+).

---

### 1.5 `fcntl` (Операції `F_DUPFD` та `F_DUPFD_CLOEXEC`)

Дозволяє дублювати файловий дескриптор із можливістю вказати нижню межу номера нового дескриптора.

:::tabs
```c
#include <fcntl.h>

int fcntl(int fd, int cmd, ... /* int arg */ );
```
```cpp
#include <fcntl.h>
#include <system_error>

int newfd = ::fcntl(fd, F_DUPFD_CLOEXEC, 10);
```
:::

*   **`cmd = F_DUPFD`**: Дублює дескриптор `fd`, використовуючи найменший вільний номер дескриптора, який є **більшим або дорівнює** третьому аргументу `arg`.
*   **`cmd = F_DUPFD_CLOEXEC`**: Виконує аналогічне дублювання, як і `F_DUPFD`, але додатково атомарно встановлює прапорець `FD_CLOEXEC` на новому дескрипторі.

---

## 2. Прапорці відкриття файлів та прапорці дескрипторів

У системних викликах маніпулювання дескрипторами важливо розрізняти дві принципово різні категорії прапорців:

### 2.1 Прапорці дескриптора (File Descriptor Flags)

Ці прапорці прив'язані до конкретного осередку у таблиці дескрипторів процесу (`struct fdtable`). Наразі існує єдиний прапорець дескриптора:

*   **`FD_CLOEXEC` (Close-on-exec)**: Якщо цей біт встановлено у `1`, ядро автоматично закриє даний файловий дескриптор під час виконання будь-якого успішного системного виклику `execve()`. Якщо біт скинуто у `0`, дескриптор залишається відкритим і успадковується новою програмою.
*   **Отримання та зміна**: Виконується викликами `fcntl(fd, F_GETFD)` та `fcntl(fd, F_SETFD, flags)`.

### 2.2 Прапорці статусу відкритого файлу (File Status Flags)

Ці прапорці зберігаються в системному об'єкті `struct file` і є спільними для всіх дескрипторів, що вказують на цей об'єкт:

*   **`O_RDONLY`, `O_WRONLY`, `O_RDWR`**: Режим доступу при відкритті (читання, запис, читання-запис).
*   **`O_APPEND`**: Режим примусового дописування в кінець файлу перед кожною операцією `write()`.
*   **`O_NONBLOCK` / `O_NDELAY`**: Неблокуючий режим I/O (повертає `EAGAIN` / `EWOULDBLOCK`, якщо дані відсутні).
*   **`O_TRUNC`**: Автоматичне обрізання файлу до нульової довжини при відкритті.
*   **`O_CREAT`**: Автоматичне створення файлу при його відсутності.
*   **`O_EXCL`**: Гарантує, що файл буде створено атомарно; якщо файл вже існує, `open()` повертає помилку `EEXIST`.
*   **`O_DIRECT`**: Пряме введення-виведення без використання дискового кешу сторінок ядра (Page Cache).
*   **Отримання та зміна**: Виконується викликами `fcntl(fd, F_GETFL)` та `fcntl(fd, F_SETFL, flags)`.

---

## 3. Коди помилок системних викликів

У разі невдалого виконання системних викликів змінна `errno` містить один із наступних кодів помилок:

| Код помилки | Константа | Причина виклику |
| :--- | :--- | :--- |
| `9` | `EBADF` | Аргумент `oldfd` не є дійсним відкритим дескриптором, або `newfd` знаходиться поза допустимим діапазоном. |
| `24` | `EMFILE` | Процес вичерпав ліміт відкритих файлових дескрипторів (`RLIMIT_NOFILE`). |
| `23` | `ENFILE` | Досягнуто загальносистемного ліміту відкритих файлів у ядрі Linux (`/proc/sys/fs/file-max`). |
| `22` | `EINVAL` | Системний виклик `dup3()` викликано з умовами `oldfd == newfd`, або передано непідтримувані прапорці. |
| `14` | `EFAULT` | Вказівник масиву `pipefd` посилається на недоступну або незахищену область пам'яті процесу. |
| `32` | `EPIPE` | Спроба запису в канал pipe, читальний кінець якого закрито у всіх процесах. |
| `4` | `EINTR` | Системний виклик було перервано доставкою сигналу процесу до того, як операція завершилася. |

---

## 4. Таблиця ядерних структур даних

Маніпулювання дескрипторами в Linux спирається на чітку трирівневу ієрархію C-структур у просторі ядра:

```
[task_struct] ──> [files_struct] ──> [fdtable] ──> [struct file] ──> [struct inode]
```

### 4.1 Ключові поля ядерних структур (Linux Kernel Source)

Цитата вихідного коду структур даних ядра Linux:

```c
/* kernel/include/linux/fdtable.h */
struct fdtable {
    unsigned int max_fds;
    struct file **fd;      /* Масив вказівників на відкриті файли ядра */
    unsigned long *close_on_exec;
    unsigned long *open_fds;
    struct rcu_head rcu;
};

struct files_struct {
    atomic_t count;
    bool resize_in_progress;
    wait_queue_head_t resize_wait;
    struct fdtable __rcu *fdt;
    struct fdtable fdtab;
    /* Початковий статичний масив для швидкого доступу без динамічної пам'яті */
    struct file * fd_array[NR_OPEN_DEFAULT];
};

/* kernel/include/linux/fs.h */
struct file {
    union {
        struct llist_node   fu_llist;
        struct rcu_head     fu_rcuhead;
    } f_u;
    struct path             f_path;
    struct inode           *f_inode;     /* Вказівник на іноду VFS */
    const struct file_operations *f_op;  /* Таблиця системних операцій файлу */
    spinlock_t              f_lock;
    atomic_long_t           f_count;     /* Лічильник посилань на відкритий файл */
    unsigned int            f_flags;     /* Прапорці відкриття (O_RDWR, O_APPEND...) */
    fmode_t                 f_mode;
    loff_t                  f_pos;       /* Поточна позиція зміщення у файлі */
    struct fown_struct      f_owner;
};

struct file_operations {
    struct module *owner;
    loff_t (*llseek) (struct file *, loff_t, int);
    ssize_t (*read) (struct file *, char __user *, size_t, loff_t *);
    ssize_t (*write) (struct file *, const char __user *, size_t, loff_t *);
    __poll_t (*poll) (struct file *, struct poll_table_struct *);
    long (*unlocked_ioctl) (struct file *, unsigned int, unsigned long);
    int (*mmap) (struct file *, struct vm_area_struct *);
    int (*open) (struct inode *, struct file *);
    int (*flush) (struct file *, fl_owner_t id);
    int (*release) (struct inode *, struct file *);
    int (*fsync) (struct file *, loff_t, loff_t, int datasync);
};
```

### 4.2 Пояснення внутрішніх механізмів ядра

*   **RCU (Read-Copy Update) для `fdtable`**: Пошук дескриптора в масиві `fd` виконується без використання важких блокувань завдяки механізму RCU. Це гарантує надзвичайно високу швидкість виконання системних викликів `read()` та `write()` у багатопотокових системах.
*   **Динамічне розширення `fdtable`**: Початково структура `files_struct` містить статичний масив `fd_array` на 64 дескриптори (`NR_OPEN_DEFAULT`). Якщо процес відкриває більше 64 файлів, ядро динамічно виділяє новий більший масив `fdtable`, копіює туди вказівники та оновлює посилання через RCU.
*   **Атомарні лічильники `f_count`**: Збільшення та зменшення кількості посилань на об'єкт `struct file` виконується атомарними інструкціями процесора (`atomic_long_inc` / `atomic_long_dec`). Об'єкт знищується та звільняється з пам'яті лише тоді, коли `f_count` досягає нульового значення.

---

## 5. Порівняльна характеристика методів дублювання FD

Нижче наведено порівняння параметрів різних методів дублювання дескрипторів:

| Характеристика | `dup()` | `dup2()` | `dup3()` | `fcntl(F_DUPFD)` |
| :--- | :--- | :--- | :--- | :--- |
| **Вибір номера FD** | Автоматичний (найменший) | Явно заданий (`newfd`) | Явно заданий (`newfd`) | Найменший `>= arg` |
| **Атомарне закриття `newfd`** | Ні | Так | Так | Ні |
| **Підтримка `O_CLOEXEC`** | Ні | Ні | Так (через `flags`) | Ні (потрібен `F_DUPFD_CLOEXEC`) |
| **Поведінка при `oldfd == newfd`** | N/A | Повертає `newfd` | Помилка `EINVAL` | N/A |
| **Стандарт / Версія** | POSIX.1-2001 | POSIX.1-2001 | Linux 2.6.27+ | POSIX.1-2001 |

---

## 6. Приклади використання в C та C++

### 6.1 Атомарне перенаправлення з використанням `dup3`

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

int redirect_stdout_safe(const char *filename) {
    int fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
    if (fd < 0) {
        perror("open failed");
        return -1;
    }

    /* Атомарно замінюємо STDOUT_FILENO (FD 1) і ставимо O_CLOEXEC на випадок exec */
    if (dup3(fd, STDOUT_FILENO, O_CLOEXEC) < 0) {
        perror("dup3 failed");
        close(fd);
        return -1;
    }

    /* Закриваємо тимчасовий дескриптор, бо FD 1 вже вказує на файл */
    close(fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>

class SafeRedirector {
public:
    static std::error_code redirect_stdout(std::string_view filename) {
        int fd = ::open(filename.data(), O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
        if (fd < 0) {
            return std::error_code(errno, std::generic_category());
        }

        if (::dup3(fd, STDOUT_FILENO, O_CLOEXEC) < 0) {
            int err = errno;
            ::close(fd);
            return std::error_code(err, std::generic_category());
        }

        ::close(fd);
        return {};
    }
};
```
:::

### 6.2 Створення та зв'язування анонімного каналу `pipe2`

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int create_bound_pipe(int *read_fd, int *write_fd) {
    int pipefds[2];
    if (pipe2(pipefds, O_CLOEXEC) < 0) {
        perror("pipe2 failed");
        return -1;
    }

    *read_fd = pipefds[0];
    *write_fd = pipefds[1];
    return 0;
}
```
```cpp
#include <iostream>
#include <utility>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>

struct PipePair {
    int read_fd{-1};
    int write_fd{-1};

    ~PipePair() {
        if (read_fd >= 0) ::close(read_fd);
        if (write_fd >= 0) ::close(write_fd);
    }
};

std::pair<PipePair, std::error_code> create_safe_pipe() {
    int fds[2];
    if (::pipe2(fds, O_CLOEXEC) < 0) {
        return {{}, std::error_code(errno, std::generic_category())};
    }
    return {PipePair{fds[0], fds[1]}, {}};
}
```
:::
