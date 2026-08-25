# 📋 Системний інтерфейс каналів та маніпуляції файловими дескрипторами

Цей довідник описує системні виклики ядра Linux для створення безназваних каналів, дублювання файлових дескрипторів, керування буферами каналів через системний інтерфейс `fcntl()`, інспектування дескрипторів через `procfs`, а також розширені системні виклики для передачі даних без копіювання (`splice`, `vmsplice`, `tee`).

## 1. Створення каналів: `pipe()` та `pipe2()`

Системний виклик `pipe()` створює односпрямований безназваний канал міжпроцесної взаємодії та повертає два файлові дескриптори.

### Сигнатури та розширений виклик Linux

:::tabs
```c
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>

// Базовий виклик POSIX
int pipe(int pipefd[2]);

// Розширений системний виклик Linux з прапорцями атомарного налаштування
int pipe2(int pipefd[2], int flags);
```
```cpp
#include <array>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>

// Ідіоматична C++ обгортка над системними викликами pipe/pipe2
std::array<int, 2> create_pipe_pair(int flags = O_CLOEXEC) {
    std::array<int, 2> pipefd{-1, -1};
    if (::pipe2(pipefd.data(), flags) == -1) {
        throw std::system_error(errno, std::generic_category(), "pipe2 failed");
    }
    return pipefd;
}
```
:::

Виклики заповнюють масив `pipefd` двома новими файловими дескрипторами:
- **`pipefd[0]`** — дескриптор, відкритий виключно для **зчитування** (read end).
- **`pipefd[1]`** — дескриптор, відкритий виключно для **запису** (write end).

### Допустимі значення `flags` у системному виклику `pipe2()`

| Прапорець | Опис та системна поведінка |
| :--- | :--- |
| **`O_CLOEXEC`** | Встановлює прапор `FD_CLOEXEC` (Close-on-Exec) для обох нових файлових дескрипторів. Це гарантує, що дескриптори автоматично закриються під час успішного системного виклику `execve()`. Використання `O_CLOEXEC` у `pipe2()` усуває гонитву дескрипторів (file descriptor leak race condition) у багатопотокових програмах, де один потік викликає `fork()`, а інший створює новий файл. |
| **`O_NONBLOCK`** | Встановлює неблокуючий режим читання та запису для обох дескрипторів. Якщо буфер порожній, `read()` повертає -1 та встановлює `errno = EAGAIN` або `EWOULDBLOCK`. Якщо буфер повний, `write()` повертає -1 та встановлює `errno = EAGAIN`. |
| **`O_DIRECT`** | (Починаючи з ядра Linux 4.5) Задає режим каналу "packet mode". Записи у канал сприймаються як окремі пакети. Наступний виклик `read()` зчитуватиме по одному пакету за раз, навіть якщо розмір прочитаного буфера більший за розмір пакета. |

### Детальні коди помилок системних викликів `pipe()` / `pipe2()`

У разі успіху виклики повертають 0. У разі помилки повертається -1, а змінна `errno` встановлюється в одне з наступних значень:

- **`EFAULT`:** Вказівник `pipefd` посилається на недопустимий або незахищений адресний простір процесу.
- **`EMFILE`:** Процес досяг системного ліміту на кількість відкритих файлових дескрипторів (`RLIMIT_NOFILE`).
- **`ENFILE`:** Операційна система досягла глобального ліміту на загальну кількість відкритих файлів у системі (контролюється файлом `/proc/sys/fs/file-max`).
- **`EINVAL`:** (тільки для `pipe2()`) Передано недопустиме поєднання прапорців у параметрі `flags`.

---

## 2. Дублювання файлових дескрипторів: `dup()`, `dup2()`, `dup3()`

Функції сімейства `dup` створюють копію відкритого файлового дескриптора. Новий дескриптор посилається на той самий запис у системній таблиці відкритих файлів ядра (`struct file`), що й оригінал.

### Сигнатури та C/C++ обгортки

:::tabs
```c
#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>

// Дублювання в найменший вільний дескриптор
int dup(int oldfd);

// Атомарне дублювання newfd = oldfd з безпечним закриттям старого newfd
int dup2(int oldfd, int newfd);

// Розширене дублювання з атомарним прапорцем O_CLOEXEC
int dup3(int oldfd, int newfd, int flags);
```
```cpp
#include <system_error>
#include <unistd.h>
#include <fcntl.h>

void safe_dup2(int oldfd, int newfd) {
    if (::dup2(oldfd, newfd) == -1) {
        throw std::system_error(errno, std::generic_category(), "dup2 failed");
    }
}

void safe_dup3(int oldfd, int newfd, int flags = O_CLOEXEC) {
    if (::dup3(oldfd, newfd, flags) == -1) {
        throw std::system_error(errno, std::generic_category(), "dup3 failed");
    }
}
```
:::

### Порівняльний аналіз поведінки функцій дублювання

1. **`dup(oldfd)`:**
   Шукає найменший невідкритий номер файлового дескриптора в таблиці поточного процесу (наприклад, дескриптор 3) і дублює в нього `oldfd`.
2. **`dup2(oldfd, newfd)`:**
   Атомарно робить `newfd` копією `oldfd`.
   - Якщо `newfd` вже відкритий, `dup2()` спочатку безпечно закриває його, не генеруючи помилок `EBADF`.
   - Якщо `oldfd == newfd` і `oldfd` є дійсним дескриптором, функція просто повертає `newfd`, нічого не роблячи.
   - Прапор `FD_CLOEXEC` у нового дескриптора `newfd` **завжди скидається** (дублікат залишається відкритим після `exec`).
3. **`dup3(oldfd, newfd, flags)`:**
   Аналог `dup2()`, але дозволяє атомарно встановити прапорець `O_CLOEXEC` для дубліката.
   - Відмінність від `dup2()`: якщо `oldfd == newfd`, виклик `dup3()` завершується з помилкою `EINVAL`.

---

## 3. Керування буфером та конфігурація через `fcntl()`

Ядро Linux дозволяє читати та змінювати розмір кільцевого буфера каналу під час виконання програми без її перезапуску.

### Команди `fcntl` для каналів

:::tabs
```c
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

long get_pipe_capacity(int fd) {
    // Повертає поточний розмір буфера каналу в байтах
    return fcntl(fd, F_GETPIPE_SZ);
}

long set_pipe_capacity(int fd, long new_size) {
    // Встановлює новий розмір буфера каналу (буде округлено до PAGE_SIZE)
    return fcntl(fd, F_SETPIPE_SZ, new_size);
}
```
```cpp
#include <system_error>
#include <fcntl.h>
#include <unistd.h>

std::size_t get_cpp_pipe_capacity(int fd) {
    long sz = ::fcntl(fd, F_GETPIPE_SZ);
    if (sz == -1) {
        throw std::system_error(errno, std::generic_category(), "F_GETPIPE_SZ failed");
    }
    return static_cast<std::size_t>(sz);
}

std::size_t set_cpp_pipe_capacity(int fd, std::size_t new_size) {
    long sz = ::fcntl(fd, F_SETPIPE_SZ, static_cast<long>(new_size));
    if (sz == -1) {
        throw std::system_error(errno, std::generic_category(), "F_SETPIPE_SZ failed");
    }
    return static_cast<std::size_t>(sz);
}
```
:::

### Системні параметри та обмеження буферів у `/proc/sys/fs/`

Налаштування буферів каналів обмежуються системними файлами Linux у псевдофайловій системі `sysctl`:

1. **`/proc/sys/fs/pipe-max-size`:**
   Визначає максимальний розмір буфера каналу, який звичайний (непривілейований) процес може встановити через `fcntl(F_SETPIPE_SZ)`. За замовчуванням це значення становить 1048576 байт (1 MB). Процес із привілеєм `CAP_SYS_RESOURCE` може перевищувати цей ліміт.
2. **`/proc/sys/fs/pipe-user-pages-hard`:**
   Максимальна загальна кількість сторінок оперативної пам'яті, які непривілейований користувач може виділити під усі свої канали. При досягненні цього ліміту створення нових каналів або розширення існуючих повертає помилку `NOSPACE` або `EPERM`.
3. **`/proc/sys/fs/pipe-user-pages-soft`:**
   М'який ліміт сторінок на користувача. Якщо ліміт перевищено, розмір нових каналів автоматично обмежується розміром однієї сторінки (4 KB) замість стандартних 16 сторінок (64 KB).

---

## 4. Передача даних без копіювання: `splice()`, `tee()`, `vmsplice()`

Для забезпечення максимально високої пропускної здатності при передачі великих обсягів даних ядро Linux надає спеціалізоване сімейство системних викликів "zero-copy". Вони дозволяють переміщати сторінки пам'яті між каналами, файлами та мережевими сокетами без копіювання даних у простір користувача.

### Сигнатури викликів zero-copy

:::tabs
```c
#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>

// Переміщує байти між файловим дескриптором та каналом без копіювання
ssize_t splice(int fd_in, loff_t *off_in, int fd_out, loff_t *off_out, size_t len, unsigned int flags);

// Дублює байти з одного каналу у інший без їхнього видалення з першого
ssize_t tee(int fd_in, int fd_out, size_t len, unsigned int flags);

// Мапить сторінки пам'яті користувача безпосередньо у буфер каналу
ssize_t vmsplice(int fd, const struct iovec *iov, unsigned long nr_segs, unsigned int flags);
```
```cpp
#include <system_error>
#include <fcntl.h>
#include <unistd.h>

std::size_t splice_data(int fd_in, int fd_out, std::size_t len) {
    ssize_t bytes = ::splice(fd_in, nullptr, fd_out, nullptr, len, SPLICE_F_MOVE | SPLICE_F_MORE);
    if (bytes == -1) {
        throw std::system_error(errno, std::generic_category(), "splice failed");
    }
    return static_cast<std::size_t>(bytes);
}
```
:::

### Прапорці керування zero-copy операціями

- **`SPLICE_F_MOVE`:** Підказує ядру спробувати перемістити сторінки пам'яті замість їхнього копіювання (актуально для сумісних файлових систем).
- **`SPLICE_F_NONBLOCK`:** Робить операцію `splice()` неблокуючою.
- **`SPLICE_F_MORE`:** Підказує ядру, що після цього виклику надійде більше даних (оптимізація для мережевих сокетів TCP).

---

## 5. Інспектування каналів через `procfs` та системні утиліти

Під час діагностики системних проблем або зависань утиліт виникає потреба перевірити стан відкритих каналів у працюючому процесі.

### Аналіз файлів у `/proc/[pid]/fd/` та `/proc/[pid]/fdinfo/`

Для кожного відкритого каналу в каталозі `/proc/[pid]/fd/` створюється символічне посилання вигляду:

```text
lr-x------ 1 user group 64 Aug 14 10:00 3 -> pipe:[456789]
l-wx------ 1 user group 64 Aug 14 10:00 4 -> pipe:[456789]
```

Число у квадратних дужках `456789` позначає унікальний номер індексного вузла (inode number) даного каналу у VFS. Якщо два процеси мають дескриптори, що вказують на однакове число `pipe:[456789]`, це означає, що вони з'єднані через один і той самий канал.

Файл `/proc/[pid]/fdinfo/[fd]` містить додаткову системну інформацію про стан каналу, позицію прочитаних даних та внутрішні прапорці доступу:

```text
pos:    0
flags:  02000000
mnt_id: 15
ino:    456789
```

Завдяки цьому файлу системний адміністратор або розробник може дізнатися точний номери індексного вузла та прапорці доступу каналу без зупинки роботи процесу.

### Моніторинг за допомогою утиліт `lsof` та `strace`

Для пошуку всіх процесів, об'єднаних спільним каналом у працюючій системі, використовується утиліта `lsof`:

```bash
lsof -g | grep 456789
```

Для детального відстеження створення та підключення каналів у реальному часі використовується `strace`:

```bash
strace -f -e trace=pipe,pipe2,dup2,close,execve ./my_pipeline
```

Опція `-f` є обов'язковою, оскільки вона наказує `strace` стежити за всіма дочірніми процесами, які створюються за допомогою виклику `fork()`.

---

## 6. Передача дескрипторів через UNIX Domain Sockets (`SCM_RIGHTS`)

Хоча класичний канал є безназваним і здебільшого успадковується дочірніми процесами після виклику `fork()`, ядро Linux дозволяє передавати вже існуючий дескриптор каналу між двома абсолютно чужими процесами.

Для цього використовується сокет локального домену (UNIX Domain Socket) та допоміжний механізм контрольних повідомлень `sendmsg()` / `recvmsg()` з параметром **`SCM_RIGHTS`**.

При передачі дескриптора через `SCM_RIGHTS` ядро копіює запис із таблиці файлових дескрипторів першого процесу і виділяє новий номер дескриптора у таблиці другого процесу. Обидва дескриптори у різних процесах вказують на той самий запис `struct file` та той самий кільцевий буфер каналу у ядрі.

---

## 7. Повний приклад налаштування неблокуючого каналу з розширеним буфером

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

int create_nonblocking_custom_pipe(int fds[2], long target_size) {
    // 1. Атомарно створюємо неблокуючий канал із прапором close-on-exec
    if (pipe2(fds, O_CLOEXEC | O_NONBLOCK) == -1) {
        perror("pipe2 failed");
        return -1;
    }

    // 2. Спробуємо збільшити розмір буфера
    long actual_size = fcntl(fds[1], F_SETPIPE_SZ, target_size);
    if (actual_size == -1) {
        perror("F_SETPIPE_SZ failed (continuing with default size)");
    } else {
        printf("Pipe capacity successfully changed to %ld bytes\n", actual_size);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <array>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>

class CustomPipe {
public:
    explicit CustomPipe(std::size_t initial_buffer_size = 131072) {
        if (::pipe2(fds_.data(), O_CLOEXEC | O_NONBLOCK) == -1) {
            throw std::system_error(errno, std::generic_category(), "pipe2 failed");
        }

        long res = ::fcntl(fds_[1], F_SETPIPE_SZ, static_cast<long>(initial_buffer_size));
        if (res != -1) {
            capacity_ = static_cast<std::size_t>(res);
        } else {
            capacity_ = 65536; // За замовчуванням 64KB
        }
    }

    ~CustomPipe() {
        if (fds_[0] != -1) ::close(fds_[0]);
        if (fds_[1] != -1) ::close(fds_[1]);
    }

    CustomPipe(const CustomPipe&) = delete;
    CustomPipe& operator=(const CustomPipe&) = delete;

    CustomPipe(CustomPipe&& other) noexcept : fds_(other.fds_), capacity_(other.capacity_) {
        other.fds_ = {-1, -1};
    }

    int read_fd() const noexcept { return fds_[0]; }
    int write_fd() const noexcept { return fds_[1]; }
    std::size_t capacity() const noexcept { return capacity_; }

private:
    std::array<int, 2> fds_{-1, -1};
    std::size_t capacity_{0};
};
```
:::
