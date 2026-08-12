# ⚙️ Практика розділюваної пам'яті: POSIX shm_open та memfd_create з опечатуванням

Цей проєкт показує розробку програмного інтерфейсу для безпечного обміну даними між процесами (IPC) за допомогою механізмів розділюваної пам'яті Linux: класичного POSIX `shm_open` та сучасного анонімного файлового дескриптора `memfd_create` із застосуванням опечатування (File Sealing).

## Концепція безпечного IPC без файлової системи

У традиційній POSIX-моделі обмін розділюваною пам'яттю між процесами реалізується через системний виклик `shm_open()`, який створює об'єкт у псевдофайловій системі `tmpfs`, змонтованій у шлях `/dev/shm`. Процеси відкривають один і той самий файл за відомим іменем (наприклад, `/my_shared_memory`), розширюють його розмір викликом `ftruncate()` і відображають у свій віртуальний адресний простір за допомогою `mmap(..., MAP_SHARED, fd, 0)`.

Незважаючи на високу швидкість передачі даних (яка дорівнює швидкості прямого доступу до RAM без копіювання буферів у ядро), ця класична схема має дві суттєві проблеми безпеки:

1. **Глобальна видимість у файловому дереві:**
   Ім'я файла у `/dev/shm` є видимим усьому середовищу користувача. Будь-який сторонній процес, що заповнений у тому самому UID або має права читання/запису, може відкрити файл розділюваної пам'яті, прочитати чутливі дані або записати туди випадкове сміття.

2. **Вразливість до аварійного обриву розміру (SIGBUS):**
   Якщо один із процесів-учасників обміну (або недобросовісний клієнт) виконає системний виклик `ftruncate(fd, 0)` або уріже файл розділюваної пам'яті, то для всіх інших процесів, які в цей момент зчитують байти з відображеної області `mmap`, процесор згенерує апаратне переривання помилки шини `SIGBUS` (англ. *bus error*). Якщо процес не має спеціального обробника `SIGBUS`, операційна система негайно завершить його аварійно.

### Механізм анонімних дескрипторів memfd_create та опечатування

Для усунення цих вразливостей у ядрі Linux (починаючи з версії 3.17) розроблено системний виклик `memfd_create()`. Він створює анонімну файлову структуру `struct file` у внутрішньому прихованому монтуванні `shmem_mnt` ядра без будь-якого запису в файловому дереві `/dev/shm` чи `/tmp`.

Отриманий файловий дескриптор передається іншому процесу через UNIX-сокет за допомогою допоміжних даних `SCM_RIGHTS`. Сторонні процеси в системі взагалі не мають способу знайти або відкрити цей дескриптор, оскільки він не має шляху в файловій системі.

Для захисту від обриву розміру файла та несанкціонованого запису підсистема `shmem` реалізує механізм опечатування (англ. *file sealing*). Після виділення пам'яті та заповнення буфера початковими даними процес-власник застосовує прапорці `F_ADD_SEALS` через системний виклик `fcntl()`:

* `F_SEAL_SHRINK` — забороняє зменшувати розмір файла (викликами `ftruncate()` або `fallocate()`). Спроба урізати файл повертає помилку `-EPERM`.
* `F_SEAL_GROW` — забороняє збільшувати розмір файла через `ftruncate()` або `write()`.
* `F_SEAL_WRITE` — забороняє будь-які подальші операції запису у буфер через системні виклики або нові відображення `mmap` із прапором `PROT_WRITE`.
* `F_SEAL_SEAL` — забороняє змінювати самий набір печаток на файлі (унеможливлює зняття або додавання нових печаток надалі).

Завдяки опечатуванню графічні сервери (Wayland), аудіодемони (PipeWire) та контейнерні середовища отримали можливість безпечно ділитися буферами пам'яті з ізольованими застосунками без ризику падіння від `SIGBUS`.

## Передача файлових дескрипторів через SCM_RIGHTS

Оскільки анонімний дескриптор `memfd` не має імені в каталогах ФС, процес-творець повинен передати його дескриптор процесу-отримачу. В операційній системі Linux це робиться через локальний доменний сокет Unix (Unix Domain Socket, `AF_UNIX`).

Передача файлового дескриптора виконується за допомогою системних викликів `sendmsg()` та `recvmsg()` із використанням керувального повідомлення `struct cmsghdr` з типом `SCM_RIGHTS`:

:::tabs
```c
/* Передача дескриптора через UNIX-сокет у C */
struct msghdr msg = {0};
struct cmsghdr *cmsg;
char buf[CMSG_SPACE(sizeof(int))];

msg.msg_control = buf;
msg.msg_controllen = sizeof(buf);

cmsg = CMSG_FIRSTHDR(&msg);
cmsg->cmsg_level = SOL_SOCKET;
cmsg->cmsg_type = SCM_RIGHTS;
cmsg->cmsg_len = CMSG_LEN(sizeof(int));

*((int *) CMSG_DATA(cmsg)) = memfd;
sendmsg(socket_fd, &msg, 0);
```
```cpp
// Ідіоматична передача дескриптора у C++
struct msghdr msg{};
alignas(struct cmsghdr) std::array<std::byte, CMSG_SPACE(sizeof(int))> buf{};

msg.msg_control = buf.data();
msg.msg_controllen = buf.size();

auto* cmsg = CMSG_FIRSTHDR(&msg);
cmsg->cmsg_level = SOL_SOCKET;
cmsg->cmsg_type = SCM_RIGHTS;
cmsg->cmsg_len = CMSG_LEN(sizeof(int));

std::memcpy(CMSG_DATA(cmsg), &memfd, sizeof(int));
if (::sendmsg(socket_fd, &msg, 0) < 0) {
    throw std::system_error(errno, std::generic_category());
}
```
:::

Ядро Linux під час виконання `sendmsg()` створює дублікат файлової структури у таблиці дескрипторів процесу-отримувача, гарантуючи атомарну передачу прав доступу до сторінок `shmem`.

## Двомовна реалізація створити та опечатати анонімну пам'ять

Нижче наведено робочі реалізації створення анонімного об'єкта `memfd`, встановлення його розміру, заповнення даними та накладання опечатування. Для C показано низькорівневі системні виклики POSIX/Linux, а для C++ — ідіоматичний обгортковий клас RAII із керуванням життєвим циклом, `std::span` та `std::expected` для обробки помилок.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <errno.h>

/* Створення опечатаного memfd буфера у C */
int create_sealed_buffer(const char *name, size_t size, const char *initial_data) {
    int fd = memfd_create(name, MFD_ALLOW_SEALING | MFD_CLOEXEC);
    if (fd < 0) {
        perror("memfd_create failed");
        return -1;
    }

    if (ftruncate(fd, (off_t)size) < 0) {
        perror("ftruncate failed");
        close(fd);
        return -1;
    }

    void *ptr = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (ptr == MAP_FAILED) {
        perror("mmap failed");
        close(fd);
        return -1;
    }

    if (initial_data) {
        size_t len = strlen(initial_data);
        if (len > size) len = size;
        memcpy(ptr, initial_data, len);
    }

    /* Завершення запису: відмонтовуємо покажчик перед опечатуванням запису */
    munmap(ptr, size);

    /* Застосування печаток: заборона зміни розміру та подальшого запису */
    if (fcntl(fd, F_ADD_SEALS, F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_WRITE | F_SEAL_SEAL) < 0) {
        perror("fcntl F_ADD_SEALS failed");
        close(fd);
        return -1;
    }

    return fd;
}

int main(void) {
    const char *payload = "Приклад даних у розділюваній пам'яті shmem/tmpfs";
    size_t buf_size = 4096;

    int memfd = create_sealed_buffer("ipc_shared_buffer", buf_size, payload);
    if (memfd < 0) {
        return EXIT_FAILURE;
    }

    printf("Успішно створено опечатаний memfd дескриптор: %d\n", memfd);

    /* Спроба змінити розмір опечатаного файла поверне помилку EPERM */
    if (ftruncate(memfd, 8192) < 0) {
        printf("Перевірка печатки успішна: ftruncate повернув помилку (errno=%d: %s)\n",
               errno, strerror(errno));
    }

    close(memfd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <span>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>

// Ідіоматична обгортка RAII для анонімної пам'яті memfd у C++
class SealedMemFd {
public:
    SealedMemFd(int fd, std::size_t size) noexcept : fd_{fd}, size_{size} {}
    
    ~SealedMemFd() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SealedMemFd(const SealedMemFd&) = delete;
    SealedMemFd& operator=(const SealedMemFd&) = delete;

    SealedMemFd(SealedMemFd&& other) noexcept : fd_{other.fd_}, size_{other.size_} {
        other.fd_ = -1;
        other.size_ = 0;
    }

    SealedMemFd& operator=(SealedMemFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            size_ = other.size_;
            other.fd_ = -1;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }

    static std::expected<SealedMemFd, std::error_code> create(
        std::string_view name,
        std::size_t size,
        std::span<const std::uint8_t> initial_data = {}
    ) {
        int fd = ::memfd_create(name.data(), MFD_ALLOW_SEALING | MFD_CLOEXEC);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::ftruncate(fd, static_cast<off_t>(size)) < 0) {
            int err = errno;
            ::close(fd);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        if (!initial_data.empty()) {
            void* ptr = ::mmap(nullptr, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
            if (ptr == MAP_FAILED) {
                int err = errno;
                ::close(fd);
                return std::unexpected(std::error_code(err, std::generic_category()));
            }

            std::size_t copy_bytes = std::min(size, initial_data.size());
            std::memcpy(ptr, initial_data.data(), copy_bytes);
            ::munmap(ptr, size);
        }

        // Застосовуємо печатки безпеки
        int seal_flags = F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_WRITE | F_SEAL_SEAL;
        if (::fcntl(fd, F_ADD_SEALS, seal_flags) < 0) {
            int err = errno;
            ::close(fd);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        return SealedMemFd(fd, size);
    }

private:
    int fd_{-1};
    std::size_t size_{0};
};

int main() {
    std::string_view payload = "Ідіоматична розділювана пам'ять C++ у shmem";
    auto data_span = std::span<const std::uint8_t>(
        reinterpret_cast<const std::uint8_t*>(payload.data()), payload.size()
    );

    auto result = SealedMemFd::create("cpp_sealed_shm", 4096, data_span);
    if (!result) {
        std::cerr << "Помилка створення memfd: " << result.error().message() << '\n';
        return 1;
    }

    const auto& memfd = *result;
    std::cout << "Успішно створено C++ RAII SealedMemFd дескриптор: " 
              << memfd.native_handle() << " розміром " << memfd.size() << " байтів\n";

    // Спроба змінити розмір опечатаного файла поверне EPERM
    if (::ftruncate(memfd.native_handle(), 8192) < 0) {
        std::cout << "Перевірка печатки C++ успішна: ftruncate заблоковано ядром ("
                  << std::strerror(errno) << ")\n";
    }

    return 0;
}
```
:::

## Крайові випадки та обробка помилок у високоризикованому IPC

Під час розробки систем міжпроцесного обміну на основі `memfd` та `tmpfs` слід враховувати такі крайові випадки:

1. **Неповнота заповнення буфера до опечатування:**
   Якщо процес застосує `F_SEAL_WRITE` до того, як відмонтує відображення `mmap` (`munmap`), ядро дозволить завершити запис через уже існуюче відображення, але заблокує будь-які нові виклики `mmap` із прапором `PROT_WRITE`. Правильний порядок дій вимагає явного виклику `munmap()` до виклику `fcntl(fd, F_ADD_SEALS, ...)`.

2. **Вплив прапорця MFD_HUGETLB:**
   Системний виклик `memfd_create()` дозволяє передавати прапорець `MFD_HUGETLB`, що примусово виділяє анонімний буфер із підсистеми HugeTLB (наприклад, сторінками по 2 МБ або 1 ГБ). Однак для таких буферів опечатування `F_SEAL_WRITE` має обмеження на деяких версіях ядер.

3. **Синхронізація кешу процесора при міжпроцесному доступі:**
   У багатопроцесорних системах обмін даними через `mmap` у `shmem` потребує бар'єрів пам'яті (англ. *memory barriers*) або атомарних операцій (`std::atomic_thread_fence`), щоб зміни, внесені одним процесором, сталі видимими іншому без затримок у L1/L2 кшині CPU.
