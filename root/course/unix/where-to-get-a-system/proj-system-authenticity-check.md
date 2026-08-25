# ⚙️ Розробка системного зонда автентичності ядра

Щоб перевірити, в якому саме середовищі виконується програма — на фізичному залізі, у віртуальній машині KVM/QEMU, всередині мікро-ВМ WSL2, у контейнері Docker чи під шаром емуляції, — недостатньо просто викликати утиліту `uname`.

Справжній системний зонд виконує комплексне, багаторівневе дослідження апаратних та програмних інваріантів ядра:
1. Виконує процесорну інструкцію `CPUID` для виявлення біта гіпервізора та вичитування фірмового 12-байтового підпису віртуалізації;
2. Сканує віртуальні структури псевдофайлових систем `/proc` та `/sys` на наявність характерних вузлів ядра та таблиць SMBIOS/DMI;
3. Перевіряє маркери ізоляції просторів імен контейнерів (`/.dockerenv`, `/run/.containerenv`, змінна `container=` у `/proc/1/environ`);
4. Здійснює практичний тест на [POSIX-семантику відкладеного видалення відкритого файлу](root:unix/where-to-get-a-system) через системний виклик `unlink()`;
5. Перевіряє працездатність сокетів `AF_UNIX` та передачу файлових дескрипторів між процесами через керуючі повідомлення `SCM_RIGHTS`.

Нижче наведено повну реалізацію системного діагностичного зонда мовами C та C++.

:::tabs
@tab C
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <sys/un.h>

#if defined(__x86_64__) || defined(__i386__)
#include <cpuid.h>

static void probe_cpuid_hypervisor(void) {
    unsigned int eax = 0, ebx = 0, ecx = 0, edx = 0;
    
    /* Листок 1: ECX біт 31 позначає наявність гіпервізора */
    if (__get_cpuid(1, &eax, &ebx, &ecx, &edx)) {
        bool is_hypervisor = (ecx & (1U << 31)) != 0;
        printf("[CPUID] Біт гіпервізора (Leaf 1, ECX.31): %s\n",
               is_hypervisor ? "1 (Виявлено віртуалізацію)" : "0 (Пряме залізо / Bare Metal)");
        
        if (is_hypervisor) {
            /* Листок 0x40000000: Підпис виробника гіпервізора */
            if (__get_cpuid(0x40000000, &eax, &ebx, &ecx, &edx)) {
                char sig[13] = {0};
                memcpy(sig + 0, &ebx, 4);
                memcpy(sig + 4, &ecx, 4);
                memcpy(sig + 8, &edx, 4);
                printf("[CPUID] Сигнатура гіпервізора: \"%s\"\n", sig);
            }
        }
    }
}
#else
static void probe_cpuid_hypervisor(void) {
    printf("[CPUID] Архітектура не x86_64 (зондування CPUID пропущено)\n");
}
#endif

static void probe_proc_kernel_version(void) {
    int fd = open("/proc/version", O_RDONLY);
    if (fd < 0) {
        printf("[PROC] /proc/version: НЕ ЗНАЙДЕНО (можлива емуляція Windows / Cygwin)\n");
        return;
    }
    
    char buf[512];
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    
    if (n > 0) {
        buf[n] = '\0';
        printf("[PROC] /proc/version знайдено:\n       %.120s...\n", buf);
        
        if (strstr(buf, "microsoft-standard-WSL2")) {
            printf("[ІДЕНТИФІКАЦІЯ] Виявлено середовище: WSL2 (Windows Hyper-V Micro-VM)\n");
        } else if (strstr(buf, "Microsoft")) {
            printf("[ІДЕНТИФІКАЦІЯ] Виявлено середовище: WSL1 (Емуляція ядра NT lxcore.sys)\n");
        }
    }
}

static void probe_dmi_product(void) {
    int fd = open("/sys/class/dmi/id/product_name", O_RDONLY);
    if (fd >= 0) {
        char buf[128];
        ssize_t n = read(fd, buf, sizeof(buf) - 1);
        close(fd);
        if (n > 0) {
            buf[n] = '\0';
            /* Прибираємо символ нового рядка */
            char *nl = strchr(buf, '\n');
            if (nl) *nl = '\0';
            printf("[SYSFS] DMI product_name: \"%s\"\n", buf);
        }
    } else {
        printf("[SYSFS] DMI таблиці недоступні у /sys/class/dmi/id/\n");
    }
}

static void probe_container_markers(void) {
    bool is_docker = (access("/.dockerenv", F_OK) == 0);
    bool is_containerenv = (access("/run/.containerenv", F_OK) == 0);
    
    printf("[CONTAINER] Маркери контейнеризації:\n");
    printf("            /.dockerenv: %s\n", is_docker ? "ТАК (Docker)" : "НІ");
    printf("            /run/.containerenv: %s\n", is_containerenv ? "ТАК (Podman)" : "НІ");
    
    int fd = open("/proc/1/environ", O_RDONLY);
    if (fd >= 0) {
        char buf[1024];
        ssize_t n = read(fd, buf, sizeof(buf) - 1);
        close(fd);
        if (n > 0) {
            buf[n] = '\0';
            /* Змінні середовища розділені нульовими байтами */
            for (ssize_t i = 0; i < n; i += strlen(buf + i) + 1) {
                if (strncmp(buf + i, "container=", 10) == 0) {
                    printf("            /proc/1/environ: %s\n", buf + i);
                    break;
                }
            }
        }
    }
}

static void probe_posix_unlink_semantics(void) {
    char tmppath[] = "/tmp/probe_unlink_XXXXXX";
    int fd = mkstemp(tmppath);
    if (fd < 0) {
        printf("[POSIX-ТЕСТ] Не вдалося створити тимчасовий файл: %s\n", strerror(errno));
        return;
    }
    
    const char *payload = "Справжнє ядро зберігає inode відкритого файлу!";
    write(fd, payload, strlen(payload));
    
    /* Видаляємо запис з каталогу, поки дескриптор відкритий */
    if (unlink(tmppath) != 0) {
        printf("[POSIX-ТЕСТ] unlink() відкритого файлу ПРОВАЛЕНО: %s\n", strerror(errno));
        close(fd);
        return;
    }
    
    /* Перевіряємо, чи файл зник із файлової системи */
    if (access(tmppath, F_OK) == 0) {
        printf("[POSIX-ТЕСТ] Файл лишився видимим після unlink (порушення семантики POSIX)\n");
    } else {
        /* Зчитуємо дані з відкритого дескриптора безіменного файлу */
        lseek(fd, 0, SEEK_SET);
        char readbuf[128] = {0};
        ssize_t rb = read(fd, readbuf, sizeof(readbuf) - 1);
        if (rb > 0 && strcmp(readbuf, payload) == 0) {
            printf("[POSIX-ТЕСТ] unlink() семантика: ВІДПОВІДАЄ POSIX (inode активний до close)\n");
        } else {
            printf("[POSIX-ТЕСТ] Не вдалося прочитати з безіменного дескриптора\n");
        }
    }
    
    close(fd);
}

static void probe_af_unix_fd_passing(void) {
    int sv[2];
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, sv) < 0) {
        printf("[AF_UNIX] socketpair() провалено: %s\n", strerror(errno));
        return;
    }
    
    /* Створюємо тестовий файл для передачі його дескриптора */
    int test_fd = open("/dev/null", O_RDONLY);
    if (test_fd < 0) {
        close(sv[0]);
        close(sv[1]);
        return;
    }
    
    /* Формуємо повідомлення з SCM_RIGHTS */
    struct msghdr msg = {0};
    char iov_buf[1] = {'X'};
    struct iovec io = {.iov_base = iov_buf, .iov_len = sizeof(iov_buf)};
    msg.msg_iov = &io;
    msg.msg_iovlen = 1;
    
    char cmsg_buf[CMSG_SPACE(sizeof(int))];
    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);
    
    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));
    memcpy(CMSG_DATA(cmsg), &test_fd, sizeof(int));
    
    if (sendmsg(sv[0], &msg, 0) < 0) {
        printf("[AF_UNIX] sendmsg(SCM_RIGHTS) провалено: %s (емуляція сокетів)\n", strerror(errno));
    } else {
        printf("[AF_UNIX] SCM_RIGHTS передача дескриптора: УСПІШНО (справжнє ядро IPC)\n");
    }
    
    close(test_fd);
    close(sv[0]);
    close(sv[1]);
}

int main(void) {
    printf("=== ДІАГНОСТИЧНИЙ ЗОНД АВТЕНТИЧНОСТІ ЯДРА ===\n\n");
    probe_cpuid_hypervisor();
    printf("\n");
    probe_proc_kernel_version();
    printf("\n");
    probe_dmi_product();
    printf("\n");
    probe_container_markers();
    printf("\n");
    probe_posix_unlink_semantics();
    printf("\n");
    probe_af_unix_fd_passing();
    printf("\n============================================\n");
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <array>
#include <vector>
#include <expected>
#include <system_error>
#include <span>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <sys/un.h>

#if defined(__x86_64__) || defined(__i386__)
#include <cpuid.h>
#endif

// RAII-обгортка для файлових дескрипторів
class FileDescriptor {
public:
    explicit FileDescriptor(int fd = -1) noexcept : fd_(fd) {}
    ~FileDescriptor() noexcept { reset(); }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.release()) {}
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

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

private:
    int fd_{-1};
};

void probe_cpuid_hypervisor() noexcept {
#if defined(__x86_64__) || defined(__i386__)
    unsigned int eax = 0, ebx = 0, ecx = 0, edx = 0;
    
    if (__get_cpuid(1, &eax, &ebx, &ecx, &edx)) {
        bool is_hypervisor = (ecx & (1U << 31)) != 0;
        std::cout << "[CPUID] Біт гіпервізора (Leaf 1, ECX.31): "
                  << (is_hypervisor ? "1 (Виявлено віртуалізацію)" : "0 (Пряме залізо / Bare Metal)")
                  << '\n';
        
        if (is_hypervisor && __get_cpuid(0x40000000, &eax, &ebx, &ecx, &edx)) {
            std::array<char, 13> sig{};
            std::memcpy(sig.data() + 0, &ebx, 4);
            std::memcpy(sig.data() + 4, &ecx, 4);
            std::memcpy(sig.data() + 8, &edx, 4);
            std::cout << "[CPUID] Сигнатура гіпервізора: \"" << sig.data() << "\"\n";
        }
    }
#else
    std::cout << "[CPUID] Архітектура не x86_64 (зондування CPUID пропущено)\n";
#endif
}

void probe_proc_kernel_version() {
    FileDescriptor fd(::open("/proc/version", O_RDONLY));
    if (!fd.valid()) {
        std::cout << "[PROC] /proc/version: НЕ ЗНАЙДЕНО (можлива емуляція Windows / Cygwin)\n";
        return;
    }

    std::array<char, 512> buf{};
    ssize_t n = ::read(fd.get(), buf.data(), buf.size() - 1);
    if (n > 0) {
        std::string_view content(buf.data(), static_cast<size_t>(n));
        std::cout << "[PROC] /proc/version знайдено:\n       "
                  << content.substr(0, 120) << "...\n";

        if (content.find("microsoft-standard-WSL2") != std::string_view::npos) {
            std::cout << "[ІДЕНТИФІКАЦІЯ] Виявлено середовище: WSL2 (Windows Hyper-V Micro-VM)\n";
        } else if (content.find("Microsoft") != std::string_view::npos) {
            std::cout << "[ІДЕНТИФІКАЦІЯ] Виявлено середовище: WSL1 (Емуляція ядра NT lxcore.sys)\n";
        }
    }
}

void probe_dmi_product() {
    FileDescriptor fd(::open("/sys/class/dmi/id/product_name", O_RDONLY));
    if (fd.valid()) {
        std::array<char, 128> buf{};
        ssize_t n = ::read(fd.get(), buf.data(), buf.size() - 1);
        if (n > 0) {
            std::string_view name(buf.data(), static_cast<size_t>(n));
            if (!name.empty() && name.back() == '\n') {
                name.remove_suffix(1);
            }
            std::cout << "[SYSFS] DMI product_name: \"" << name << "\"\n";
        }
    } else {
        std::cout << "[SYSFS] DMI таблиці недоступні у /sys/class/dmi/id/\n";
    }
}

void probe_container_markers() {
    bool is_docker = (::access("/.dockerenv", F_OK) == 0);
    bool is_containerenv = (::access("/run/.containerenv", F_OK) == 0);

    std::cout << "[CONTAINER] Маркери контейнеризації:\n"
              << "            /.dockerenv: " << (is_docker ? "ТАК (Docker)" : "НІ") << '\n'
              << "            /run/.containerenv: " << (is_containerenv ? "ТАК (Podman)" : "НІ") << '\n';

    FileDescriptor fd(::open("/proc/1/environ", O_RDONLY));
    if (fd.valid()) {
        std::array<char, 1024> buf{};
        ssize_t n = ::read(fd.get(), buf.data(), buf.size() - 1);
        if (n > 0) {
            std::span<const char> bytes(buf.data(), static_cast<size_t>(n));
            size_t offset = 0;
            while (offset < bytes.size()) {
                std::string_view var(bytes.data() + offset);
                if (var.starts_with("container=")) {
                    std::cout << "            /proc/1/environ: " << var << '\n';
                    break;
                }
                offset += var.size() + 1;
            }
        }
    }
}

void probe_posix_unlink_semantics() {
    char tmppath[] = "/tmp/probe_unlink_XXXXXX";
    FileDescriptor fd(::mkstemp(tmppath));
    if (!fd.valid()) {
        std::cout << "[POSIX-ТЕСТ] Не вдалося створити тимчасовий файл\n";
        return;
    }

    constexpr std::string_view payload = "Справжнє ядро зберігає inode відкритого файлу!";
    ::write(fd.get(), payload.data(), payload.size());

    if (::unlink(tmppath) != 0) {
        std::cout << "[POSIX-ТЕСТ] unlink() відкритого файлу ПРОВАЛЕНО (семантика блокування)\n";
        return;
    }

    if (::access(tmppath, F_OK) == 0) {
        std::cout << "[POSIX-ТЕСТ] Файл лишився видимим після unlink (порушення POSIX)\n";
    } else {
        ::lseek(fd.get(), 0, SEEK_SET);
        std::array<char, 128> readbuf{};
        ssize_t rb = ::read(fd.get(), readbuf.data(), readbuf.size() - 1);
        if (rb > 0 && std::string_view(readbuf.data(), static_cast<size_t>(rb)) == payload) {
            std::cout << "[POSIX-ТЕСТ] unlink() семантика: ВІДПОВІДАЄ POSIX (inode активний до close)\n";
        } else {
            std::cout << "[POSIX-ТЕСТ] Не вдалося прочитати з безіменного дескриптора\n";
        }
    }
}

void probe_af_unix_fd_passing() {
    std::array<int, 2> sv{-1, -1};
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, sv.data()) < 0) {
        std::cout << "[AF_UNIX] socketpair() провалено: емуляція сокетів\n";
        return;
    }

    FileDescriptor sock0(sv[0]);
    FileDescriptor sock1(sv[1]);
    FileDescriptor test_fd(::open("/dev/null", O_RDONLY));

    if (!test_fd.valid()) {
        return;
    }

    struct msghdr msg{};
    char iov_buf[1] = {'X'};
    struct iovec io{.iov_base = iov_buf, .iov_len = sizeof(iov_buf)};
    msg.msg_iov = &io;
    msg.msg_iovlen = 1;

    alignas(struct cmsghdr) char cmsg_buf[CMSG_SPACE(sizeof(int))]{};
    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);

    struct cmsghdr* cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));
    int raw_test_fd = test_fd.get();
    std::memcpy(CMSG_DATA(cmsg), &raw_test_fd, sizeof(int));

    if (::sendmsg(sock0.get(), &msg, 0) < 0) {
        std::cout << "[AF_UNIX] sendmsg(SCM_RIGHTS) провалено: емуляція без підтримки передачі дескрипторів\n";
    } else {
        std::cout << "[AF_UNIX] SCM_RIGHTS передача дескриптора: УСПІШНО (справжнє ядро IPC)\n";
    }
}

int main() {
    std::cout << "=== ДІАГНОСТИЧНИЙ ЗОНД АВТЕНТИЧНОСТІ ЯДРА ===\n\n";
    probe_cpuid_hypervisor();
    std::cout << '\n';
    probe_proc_kernel_version();
    std::cout << '\n';
    probe_dmi_product();
    std::cout << '\n';
    probe_container_markers();
    std::cout << '\n';
    probe_posix_unlink_semantics();
    std::cout << '\n';
    probe_af_unix_fd_passing();
    std::cout << "\n============================================\n";
    return 0;
}
```
:::

## Поетапний аналіз діагностичних фаз

Кожна функція системного зонда спрямована на перевірку конкретного інваріанта операційної системи та структур ядра:

### Фаза 1: Апаратне зондування CPUID

Інструкція `CPUID` на архітектурі x86_64 є непривілейованою і може вільно виконуватися з простору користувача у Ring 3. Проте всередині віртуальної машини будь-яке виконання цієї інструкції безумовно спричиняє апаратний вихід у гіпервізор (VM-Exit).

Гіпервізор перехоплює виконання, формує значення регістрів та повертає їх гостьовій програмі. Специфікація віртуалізації резервує 31-й біт регістру `ECX` при запиті листка `EAX=1`: якщо він встановлений у `1`, гіпервізор зобов'язаний відкрити діапазон спеціальних листків `0x40000000–0x400000FF`. Запитуючи листок `0x40000000`, зонд отримує 12 байтів ASCII-тексту безпосередньо з регістрів `EBX`, `ECX`, `EDX`.

### Фаза 2: Інспекція /proc/version

Ядро Linux експортує повний рядок ідентифікації збірки через віртуальний вузол `procfs`. У WSL2 цей рядок завжди містить специфічний маркер `microsoft-standard-WSL2`, що свідчить про використання власного ядра Microsoft, зібраного для мікро-ВМ Hyper-V.

У старому WSL1 замість повноцінного номера ядра Linux повертався штучний рядок версії `4.4.0-...-Microsoft`, який генерувався драйвером трансляції системних викликів `lxcore.sys`.

### Фаза 3: Зчитування DMI-таблиць через sysfs

Підсистема ядра Linux `dmi_scan` під час ініціалізації зчитує структури SMBIOS з фізичної пам'яті комп'ютера (діапазон `0xF0000–0xFFFFF`) або з таблиць UEFI. Отримані текстові поля експортуються як псевдофайли у каталозі `/sys/class/dmi/id/`.

У віртуальних машинах гіпервізори KVM та QEMU за замовчуванням заповнюють поле `product_name` значеннями `KVM` або `Standard PC (Q35 + ICH9, 2009)`, тоді як VirtualBox записує `VirtualBox`. На фізичному комп'ютері цей вузол повертає точну назву материнської плати або ноутбука.

### Фаза 4: Детекція просторів імен контейнерів

Контейнерні рушії залишають характерні сліди у файловій системі. Docker створює маркерний порожній файл `/.dockerenv`, а Podman використовує файл `/run/.containerenv`.

Крім того, оскільки процес ініціалізації контейнера запускається через спеціальну службу запуску, у файлі `/proc/1/environ` завжди зберігається змінна `container=docker` або `container=podman`, доступна для читання процесам усередині простору імен PID. Програма-зонд обходить нульові байти розділювачів змінних оточення і знаходить точний префікс.

### Фаза 5: Семантичний тест unlink() для відкритих дескрипторів

Це ключовий тест автентичності VFS. Програма створює тимчасовий файл за допомогою функції `mkstemp()`, записує туди дані, а потім викликає системний виклик `unlink()`.

У справжній системі POSIX запис імені файлу негайно зникає з каталогу (`access()` повертає помилку `ENOENT`), проте лічильник посилань `i_nlink` структур `struct inode` ядра падає до нуля, тоді як лічильник відкритих дескрипторів `i_count` залишається рівним `1`. Програма продовжує читати дані через виклик `lseek()` та `read()`. В емуляторах Windows NT цей виклик завершується помилкою через блокування зайнятого файлу.

### Фаза 6: Передача дескрипторів крізь сокети AF_UNIX

Зонд створює пару зв'язаних сокетів `socketpair(AF_UNIX, SOCK_STREAM)` і пакує відкритий файловий дескриптор у допоміжний блок керування повідомлення `struct cmsghdr` з типом `SCM_RIGHTS`.

У нативному ядрі Linux системний виклик `sendmsg()` передає посилання на внутрішній об'єкт `struct file` ядра до буфера сокета приймача. Коли приймач робить `recvmsg()`, ядро виділяє новий вільний номер дескриптора в таблиці `files_struct` процесу-отримувача та збільшує лічильник посилань на файл. В емуляторах ця операція завершується помилкою `EOPNOTSUPP`.

## Архітектурні деталі C++ реалізації

Версія мовою C++ демонструє ідіоматичний підхід до системного програмування:
1. **RAII-клас `FileDescriptor`**: гарантує закриття файлових дескрипторів через `::close()` при виході зі скоупу (зокрема при генерації винятків), запобігаючи витоку ресурсів дескрипторної таблиці процесу.
2. **Семантика переміщення (Move Semantics)**: конструктор та оператор переміщення дозволяють безпечно передавати володіння дескриптором без небезпеки подвійного закриття (*double close*).
3. **Безпечні перегляди пам'яті (`std::string_view` та `std::span`)**: усувають зайве динамічне виділення пам'яті в купі (`heap allocations`) при розборі рядків `/proc/version` та масивів змінних `/proc/1/environ`.
4. **Суворе вирівнювання пам'яті (`alignas(struct cmsghdr)`)**: гарантує, що буфер допоміжних даних керуючого повідомлення сокета розташовується за адресою, кратною машинному слову, що вимагається макросом `CMSG_FIRSTHDR`.

## Інструкція зі збірки та запуску

Для компіляції та запуску зонда скористайтеся стандартними компіляторами GCC або Clang. Прапорець `-D_GNU_SOURCE` необхідний у версії C для відкриття сигнатур `socketpair`, `struct msghdr` та макросів `CMSG_*`:

```sh
# Збірка C-версії (вимагає стандарту C11 або вище)
gcc -O2 -Wall -Wextra -std=c11 probe.c -o probe_c
./probe_c

# Збірка C++ версії (вимагає стандарту C++20 або вище)
g++ -O2 -Wall -Wextra -std=c++20 probe.cpp -o probe_cpp
./probe_cpp
```

При запуску всередині віртуальної машини KVM або QEMU вивід інструкції CPUID миттєво поверне сигнатуру `"KVMKVMKVM"`, тоді як на чистому залізі зонд покаже нульовий біт гіпервізора та прочитає назву реальної материнської плати. Зонд не потребує прав суперкористувача `root`, оскільки всі використані інтерфейси VFS та процесорні інструкції доступні звичайному непривілейованому процесу.
