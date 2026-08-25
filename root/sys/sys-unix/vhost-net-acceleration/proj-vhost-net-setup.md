# ⚙️ Практична реалізація налаштування vhost-net бекенду на C та C++

У цьому розділі розглядається практична реалізація програмного ініціалізації паравіртуалізованого мережевого бекенду `vhost-net` за допомогою системних викликів `ioctl`. Наведений приклад ілюструє повний цикл конфігурації: від створення мережевого інтерфейсу TAP у системі до мапування оперативної пам'яті гостя, налаштування кільцевих буферів `virtqueue` та прив'язки асинхронних каналів сповіщення `eventfd`.

Приклад розроблений у двох варіантах — низькорівневий C з прямими викликами POSIX API та ідіоматичний C++20 з використанням концепції RAII, типів безпечного управління ресурсами (`std::expected`), відсутністю сирих вказівників та автоматичним звільненням файлових дескрипторів.

## Покроковий алгоритм ініціалізації vhost-net бекенду

Для переведення мережевого трафіку віртуальної машини у внутрішньоядерний потік `vhost-net` програма виконує послідовність дій:

1. **Створення мережевого пристрою TAP:** Програми відкриває файловий пристрій `/dev/net/tun` і за допомогою системного виклику `ioctl(TUNSETIFF)` створює віртуальний мережевий інтерфейс рівня L2 (Ethernet TAP). Прапор `IFF_TAP` вказує на обробку повних кадових кадрів Ethernet, а прапор `IFF_NO_PI` вимикає додавання службових заголовків пакета (Packet Information), що необхідно для прямої сумісності з кадрами `virtio-net`.
2. **Відкриття пристрою vhost-net та реєстрація власника:** Програма відкриває символьний файл `/dev/vhost-net` у режимі читання/запису (`O_RDWR`). Одразу після відкриття виконується системний виклик `ioctl(VHOST_SET_OWNER)`. Ця операція прив'язує дескриптор vhost до таблиці сторінок оперативної пам'яті поточного процесу. Якщо процес спробує закрити дескриптор або завершить роботу, ядро Linux автоматично звільнить усі пов'язані ресурси.
3. **Формування та передача карти пам'яті (Memory Table):** Оскільки потік ядра `vhost-$PID` повинен мати доступ до пам'яті гостя, програма виділяє область пам'яті (у даному прикладі через `mmap()` з прапорами `MAP_PRIVATE | MAP_ANONYMOUS`). Після цього заповнюється структура `struct vhost_memory`, де вказується початкова фізична адреса гостя (GPA = 0x0), розмір виділеного сегмента та віртуальна адреса простору користувача (HVA). Ця структура передається ядру через `ioctl(VHOST_SET_MEM_TABLE)`.
4. **Конфігурація кільцевих буферів virtqueue:** Для кожної з двох черг мережевого пристрою (індекс 0 відповідає черзі прийому RX, індекс 1 — черзі передачі TX) встановлюється розмір кільця за допомогою `ioctl(VHOST_SET_VRING_NUM)`. Потім за допомогою `ioctl(VHOST_SET_VRING_ADDR)` ядрю передаються віртуальні адреси трикутника буферів (`desc_user_addr`, `avail_user_addr`, `used_user_addr`). У реальній віртуальній машині ці адреси виділяє ядро гостьової операційної системи, а у даному тесті вони розраховуються як зсуви у мапованій пам'яті.
5. **Створення каналів сигналізації eventfd:** Для кожної черги створюються два дескриптори `eventfd` за допомогою виклику `eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC)`. Перший дескриптор (`kick_fd`) реєструється у ядрі через `VHOST_SET_VRING_KICK` і слугує для сповіщення потоку `vhost` про появу нових буферів від гостя. Другий дескриптор (`call_fd`) реєструється через `VHOST_SET_VRING_CALL` і слугує для виклику MSI-X переривань у гості після обробки пакетів.
6. **Прив'язка мережевого бекенду TAP:** Завершальним кроком є виконання виклику `ioctl(VHOST_NET_SET_BACKEND)` для кожної черги. Після передачі файлового дескриптора TAP-пристрою ядро Linux запускає виділений потік ядра `vhost-$PID` та починає автоматичну обробку кадрів.

## Код реалізації: C та C++20

Нижче наведено повний вихідний код реалізації обома мовами.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/eventfd.h>
#include <net/if.h>
#include <linux/if_tun.h>
#include <linux/vhost.h>

#define GUEST_MEM_SIZE (1024 * 1024 * 64) // 64 MB віртуальної пам'яті гостя
#define VRING_SIZE 256                     // Кількість дескрипторів у черзі

int open_tap_device(const char *dev_name) {
    int tap_fd = open("/dev/net/tun", O_RDWR);
    if (tap_fd < 0) {
        perror("Помилка відкриття /dev/net/tun");
        return -1;
    }

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    ifr.ifr_flags = IFF_TAP | IFF_NO_PI;
    snprintf(ifr.ifr_name, IFNAMSIZ, "%s", dev_name);

    if (ioctl(tap_fd, TUNSETIFF, (void *)&ifr) < 0) {
        perror("Помилка налаштування TUNSETIFF");
        close(tap_fd);
        return -1;
    }

    return tap_fd;
}

int setup_vhost_net(int tap_fd, void *guest_mem, size_t mem_size) {
    int vhost_fd = open("/dev/vhost-net", O_RDWR);
    if (vhost_fd < 0) {
        perror("Помилка відкриття /dev/vhost-net");
        return -1;
    }

    // 1. Прив'язка власника
    if (ioctl(vhost_fd, VHOST_SET_OWNER, NULL) < 0) {
        perror("VHOST_SET_OWNER failed");
        close(vhost_fd);
        return -1;
    }

    // 2. Налаштування карти пам'яті
    size_t mem_table_size = sizeof(struct vhost_memory) + sizeof(struct vhost_memory_region);
    struct vhost_memory *mem = (struct vhost_memory *)calloc(1, mem_table_size);
    if (!mem) {
        perror("Помилка виділення пам'яті під vhost_memory");
        close(vhost_fd);
        return -1;
    }

    mem->nregions = 1;
    mem->regions[0].guest_phys_addr = 0x0;
    mem->regions[0].memory_size = mem_size;
    mem->regions[0].userspace_addr = (uint64_t)guest_mem;

    if (ioctl(vhost_fd, VHOST_SET_MEM_TABLE, mem) < 0) {
        perror("VHOST_SET_MEM_TABLE failed");
        free(mem);
        close(vhost_fd);
        return -1;
    }
    free(mem);

    // 3. Створення dummy-структур vring у мапованій пам'яті
    // У реальній ВМ ці структури виділяє гостьове ядро або гіпервізор
    uint8_t *vring_buf = (uint8_t *)guest_mem + 0x10000;
    
    // 4. Конфігурація черг (0 = RX, 1 = TX)
    for (int q = 0; q < 2; q++) {
        struct vhost_vring_state state = { .index = q, .num = VRING_SIZE };
        if (ioctl(vhost_fd, VHOST_SET_VRING_NUM, &state) < 0) {
            perror("VHOST_SET_VRING_NUM failed");
            close(vhost_fd);
            return -1;
        }

        // Задаємо адреси vring у HVA
        struct vhost_vring_addr addr = {
            .index = q,
            .flags = 0,
            .desc_user_addr = (uint64_t)(vring_buf + q * 0x4000),
            .avail_user_addr = (uint64_t)(vring_buf + q * 0x4000 + 0x1000),
            .used_user_addr = (uint64_t)(vring_buf + q * 0x4000 + 0x2000),
            .log_guest_addr = 0
        };

        if (ioctl(vhost_fd, VHOST_SET_VRING_ADDR, &addr) < 0) {
            perror("VHOST_SET_VRING_ADDR failed");
            close(vhost_fd);
            return -1;
        }

        // Створення та прив'язка eventfd для KICK та CALL
        int kick_fd = eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC);
        int call_fd = eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC);

        struct vhost_vring_file kick_file = { .index = q, .fd = kick_fd };
        struct vhost_vring_file call_file = { .index = q, .fd = call_fd };

        if (ioctl(vhost_fd, VHOST_SET_VRING_KICK, &kick_file) < 0 ||
            ioctl(vhost_fd, VHOST_SET_VRING_CALL, &call_file) < 0) {
            perror("VHOST_SET_VRING_KICK/CALL failed");
            close(kick_fd); close(call_fd); close(vhost_fd);
            return -1;
        }

        // 5. Прив'язка TAP-дескриптора як бекенду черги
        struct vhost_vring_file backend = { .index = q, .fd = tap_fd };
        if (ioctl(vhost_fd, VHOST_NET_SET_BACKEND, &backend) < 0) {
            perror("VHOST_NET_SET_BACKEND failed");
            close(vhost_fd);
            return -1;
        }
    }

    printf("vhost-net успішно ініціалізований та прив'язаний до TAP!\n");
    return vhost_fd;
}

int main(void) {
    void *guest_memory = mmap(NULL, GUEST_MEM_SIZE, PROT_READ | PROT_WRITE,
                              MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (guest_memory == MAP_FAILED) {
        perror("mmap failed");
        return 1;
    }

    int tap_fd = open_tap_device("vhost-tap0");
    if (tap_fd < 0) {
        munmap(guest_memory, GUEST_MEM_SIZE);
        return 1;
    }

    int vhost_fd = setup_vhost_net(tap_fd, guest_memory, GUEST_MEM_SIZE);
    if (vhost_fd >= 0) {
        printf("Натисніть Enter для завершення роботи...\n");
        getchar();
        close(vhost_fd);
    }

    close(tap_fd);
    munmap(guest_memory, GUEST_MEM_SIZE);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <system_error>
#include <span>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/eventfd.h>
#include <net/if.h>
#include <linux/if_tun.h>
#include <linux/vhost.h>

namespace vhost {

class FileDescriptor {
public:
    explicit FileDescriptor(int fd = -1) noexcept : fd_(fd) {}
    ~FileDescriptor() { reset(); }

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
        int old_fd = fd_;
        fd_ = -1;
        return old_fd;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

class GuestMemory {
public:
    static std::expected<GuestMemory, std::error_code> allocate(size_t size) {
        void* addr = ::mmap(nullptr, size, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (addr == MAP_FAILED) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return GuestMemory(addr, size);
    }

    ~GuestMemory() {
        if (addr_ && size_ > 0) {
            ::munmap(addr_, size_);
        }
    }

    GuestMemory(const GuestMemory&) = delete;
    GuestMemory& operator=(const GuestMemory&) = delete;

    GuestMemory(GuestMemory&& other) noexcept : addr_(other.addr_), size_(other.size_) {
        other.addr_ = nullptr;
        other.size_ = 0;
    }

    GuestMemory& operator=(GuestMemory&& other) noexcept {
        if (this != &other) {
            if (addr_ && size_ > 0) ::munmap(addr_, size_);
            addr_ = other.addr_;
            size_ = other.size_;
            other.addr_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] void* data() const noexcept { return addr_; }
    [[nodiscard]] size_t size() const noexcept { return size_; }

private:
    GuestMemory(void* addr, size_t size) : addr_(addr), size_(size) {}
    void* addr_{nullptr};
    size_t size_{0};
};

class VhostNetBackend {
public:
    static std::expected<VhostNetBackend, std::error_code> create(std::string_view tap_name, const GuestMemory& memory) {
        FileDescriptor tap_fd(::open("/dev/net/tun", O_RDWR));
        if (!tap_fd.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        struct ifreq ifr{};
        ifr.ifr_flags = IFF_TAP | IFF_NO_PI;
        std::strncpy(ifr.ifr_name, tap_name.data(), std::min(tap_name.size(), sizeof(ifr.ifr_name) - 1));

        if (::ioctl(tap_fd.get(), TUNSETIFF, &ifr) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        FileDescriptor vhost_fd(::open("/dev/vhost-net", O_RDWR));
        if (!vhost_fd.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::ioctl(vhost_fd.get(), VHOST_SET_OWNER, nullptr) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        // Передача карти пам'яті
        std::vector<uint8_t> mem_buf(sizeof(vhost_memory) + sizeof(vhost_memory_region));
        auto* mem = reinterpret_cast<vhost_memory*>(mem_buf.data());
        mem->nregions = 1;
        mem->regions[0].guest_phys_addr = 0x0;
        mem->regions[0].memory_size = memory.size();
        mem->regions[0].userspace_addr = reinterpret_cast<uint64_t>(memory.data());

        if (::ioctl(vhost_fd.get(), VHOST_SET_MEM_TABLE, mem) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        VhostNetBackend backend(std::move(tap_fd), std::move(vhost_fd));
        if (auto res = backend.configure_queues(memory); !res) {
            return std::unexpected(res.error());
        }

        return backend;
    }

private:
    VhostNetBackend(FileDescriptor tap_fd, FileDescriptor vhost_fd)
        : tap_fd_(std::move(tap_fd)), vhost_fd_(std::move(vhost_fd)) {}

    std::expected<void, std::error_code> configure_queues(const GuestMemory& memory) {
        auto* base_vring = reinterpret_cast<uint8_t*>(memory.data()) + 0x10000;

        for (uint32_t q = 0; q < 2; ++q) {
            vhost_vring_state state{.index = q, .num = 256};
            if (::ioctl(vhost_fd_.get(), VHOST_SET_VRING_NUM, &state) < 0) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }

            vhost_vring_addr addr{
                .index = q,
                .flags = 0,
                .desc_user_addr = reinterpret_cast<uint64_t>(base_vring + q * 0x4000),
                .used_user_addr = reinterpret_cast<uint64_t>(base_vring + q * 0x4000 + 0x2000),
                .avail_user_addr = reinterpret_cast<uint64_t>(base_vring + q * 0x4000 + 0x1000),
                .log_guest_addr = 0
            };

            if (::ioctl(vhost_fd_.get(), VHOST_SET_VRING_ADDR, &addr) < 0) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }

            FileDescriptor kick_fd(::eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC));
            FileDescriptor call_fd(::eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC));

            vhost_vring_file kick_file{.index = q, .fd = kick_fd.get()};
            vhost_vring_file call_file{.index = q, .fd = call_fd.get()};

            if (::ioctl(vhost_fd_.get(), VHOST_SET_VRING_KICK, &kick_file) < 0 ||
                ::ioctl(vhost_fd_.get(), VHOST_SET_VRING_CALL, &call_file) < 0) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }

            vhost_vring_file backend{.index = q, .fd = tap_fd_.get()};
            if (::ioctl(vhost_fd_.get(), VHOST_NET_SET_BACKEND, &backend) < 0) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }

            kick_fds_.push_back(std::move(kick_fd));
            call_fds_.push_back(std::move(call_fd));
        }
        return {};
    }

    FileDescriptor tap_fd_;
    FileDescriptor vhost_fd_;
    std::vector<FileDescriptor> kick_fds_;
    std::vector<FileDescriptor> call_fds_;
};

} // namespace vhost

int main() {
    auto guest_mem = vhost::GuestMemory::allocate(64 * 1024 * 1024);
    if (!guest_mem) {
        std::cerr << "Помилка виділення пам'яті: " << guest_mem.error().message() << '\n';
        return 1;
    }

    auto backend = vhost::VhostNetBackend::create("vhost-tap0", *guest_mem);
    if (!backend) {
        std::cerr << "Помилка налаштування vhost-net: " << backend.error().message() << '\n';
        return 1;
    }

    std::cout << "vhost-net успішно ініціалізовано на C++20 (RAII, std::expected)!\n";
    std::cout << "Натисніть Enter для виходу...\n";
    std::cin.get();

    return 0;
}
```
:::

## Зіставлення архітектури реалізацій мовами C та C++

Наведений код демонструє глибоку різницю між підходами до системного програмування у мовах C та C++:

1. **Управління ресурсами та файловими дескрипторами:**
   - У варіанті мовою C системні файлові дескриптори (`tap_fd`, `vhost_fd`, `kick_fd`, `call_fd`) контролюються вручну. У разі виникнення помилки на будь-якому кроці програміст змушений явно викликати `close()` для кожного відкритого файла перед виходом з функції.
   - У варіанті мовою C++20 створено клас-обгортку `vhost::FileDescriptor`, який реалізує семантику переміщення (Move-Only semantics) та автоматично викликає `close()` у деструкторі. Це унеможливлює витік файлових дескрипторів при передчасному виході з функції або при виникненні помилок.

2. **Виділення пам'яті під гостьовий простір:**
   - Мова C спирається на виклики `mmap()` та `free()`, вимагаючи контролю за розміром регіонів та перевірки вказівників на `MAP_FAILED` та `NULL`.
   - Мова C++20 інкапсулює відображення оперативної пам'яті у класі `vhost::GuestMemory`. Деструктор об'єкта самостійно виконує `munmap()`, а статичний метод `allocate()` повертає моніадичний тип `std::expected`, що виключає необхідність використання сирих вказівників.

3. **Обробка системних помилок:**
   - У коді C перевірка викликів здійснюється через аналіз від'ємного значення повернення та виклик `perror()`.
   - У коді C++20 використовується стандартний об'єкт помилки `std::error_code`, поєднаний із монадою `std::expected`. Це дозволяє передавати системний код помилки `errno` вище за стеком викликів у вигляді прозорого типу без використання винятків (Exceptions), що зазвичай критично для системного та embedded-програмування.

## Технічні нюанси та поширені пастки при розробці

Під час практичного програмування бекенду `vhost-net` розробники часто стикаються з непочесними помилками ядра Linux:

1. **Вимоги до вирівнювання адрес кільця virtqueue:** Адреси, які передаються у структурі `vhost_vring_addr`, повинні мати суворе вирівнювання у пам'яті. Таблиця `vring_desc` вимагає вирівнювання на 16 байтів, `vring_avail` — на 2 байти, а `vring_used` — на 4 байти. Передача недозволених адрес призводить до миттєвого повернення помилки `-EFAULT` при спробі запуску потоку ядра.
2. **Права доступу та системні привілеї:** Створення TAP-пристроїв та взаємодія з символьним файлом `/dev/vhost-net` вимагають системних привілеїв суперкористувача (`root`) або наявності правової категорії `CAP_NET_ADMIN` у cgroup процесу. У разі відсутності привілеїв виклики `TUNSETIFF` або `VHOST_SET_OWNER` повертають помилку `EPERM`.
3. **Життєвий цикл файлових дескрипторів eventfd:** Файлові дескриптори `kick_fd` та `call_fd` повинні залишатися відкритими протягом усього часу роботи бекенду. Якщо процес гіпервізора випадково закриє `kick_fd`, ядро Linux відключить обробник сповіщень `ioeventfd`, і потік `vhost-net` перестане отримувати кадри від гостя.
