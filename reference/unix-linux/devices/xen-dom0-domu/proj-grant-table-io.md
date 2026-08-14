# ⚙️ Практичний обмін даними між DomU та Dom0 через Grant Tables та Event Channels

Ця вставка демонструє практичну реалізацію безкопіювального (zero-copy) обміну даними між гостьовим доменом (DomU) та доменом управління (Dom0) у просторі користувача Linux. У тексті розглянуто повний цикл передачі даних: від виділення грант-посилання (grant reference) у гості до його відображення (mapping) та обробки подій у Dom0 за допомогою системних символьних пристроїв `/dev/xen/gntdev` та `/dev/xen/evtchn`.

## Архітектурний контекст та задача

У розробці системних сервісів та бекендів віртуальних пристроїв виникає задача передачі великих масивів даних (наприклад, блоків файлової системи або мережевих пакетів) між двома ізольованими віртуальними машинами. Традиційний підхід із копіюванням даних через сокети або пайпи спричиняє копіювання байтів із простору користувача в ядро DomU, потім у гіпервізор, звідти в ядро Dom0 і нарешті у бекенд-процес. Це вимагає чотирьох копіювань та множинних перемикань контексту ЦП.

Механізм Grant Tables дозволяє реалізувати повністю безкопіювальний обмін (Zero-Copy):
1. **DomU (Grantor)**: Виділяє фізичну сторінку ОЗП, заповнює її корисним навантаженням та реєструє у власній Grant Table, отримуючи числовий ідентифікатор `gref` (наприклад, 42). Також створює незв'язаний порт Event Channel.
2. **Передача метаданих**: DomU надсилає пару `(gref, port)` до Dom0 через Xenstore або спільне кільце управління.
3. **Dom0 (Mapper)**: Викликає `ioctl(IOCTL_GNTDEV_MAP_GRANT_REF)` над пристроєм `/dev/xen/gntdev`, отримуючи віртуальне зміщення, та мапить фізичну сторінку DomU у свій адресний простір за допомогою системного виклику `mmap()`.
4. **Сповіщення та очищення**: Dom0 обробляє дані безпосередньо у фізичній сторінці DomU, надсилає віртуальне переривання через `/dev/xen/evtchn` та розмаплює сторінку (`unmap`), після чого DomU звільняє запис у своїй таблиці грантів.

## Детальний розбір реалізації мапування та обробки в Dom0

Програма бекенда для Dom0 отримує аргументами командного рядка ідентифікатор домену-власника `domid`, індекс гранту `gref` та номер порту каналу подій `evtchn_port`. 

Послідовність дій у коді:
1. **Відкриття драйвера грантів**: Програма відкриває пристрій `/dev/xen/gntdev` у режимі читання/запису.
2. **Формування структури мапування**: Створюється запит `struct ioctl_gntdev_map_grant_ref`, у якому вказується кількість грантів (`count = 1`), ідентифікатор гостя `domid` та індекс `gref`.
3. **Виконання ioctl**: Ядро Linux звертається до гіпервізора Xen за допомогою гіпервиклику `HYPERVISOR_grant_table_op`. Гіпервізор перевіряє права в таблиці грантів DomU і, якщо доступ дозволено, повертає 64-бітне псевдо-зміщення `index`.
4. **Викликання mmap()**: Передача отриманого `index` у виклик `mmap()` з прапорцями `MAP_SHARED` та `PROT_READ | PROT_WRITE` створює відображення кадру пам'яті DomU в адресний простір процесу Dom0.
5. **Генерація Upcall**: Після обробки вмісту програма відкриває `/dev/xen/evtchn` і виконує `IOCTL_EVTCHN_NOTIFY`, змушуючи гіпервізор інжектувати віртуальне переривання в ядро DomU.
6. **Очищення ресурсів**: Розмапування виконується у зворотному порядку: спочатку `munmap()`, а потім `IOCTL_GNTDEV_UNMAP_GRANT_REF` для інвалідації запису в гіпервізорі.

Нижче наведено робочі приклади програми у двох варіантах: процедурний C та об'єктно-орієнтований C++20 з використанням концепції RAII.

:::tabs
```c
/* Dom0 Backend Mapper у стилі C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <errno.h>

#include <xen/gntdev.h>
#include <xen/evtchn.h>

#define PAGE_SIZE 4096

int process_remote_grant(uint32_t remote_domid, uint32_t gref, uint32_t remote_port) {
    int gntdev_fd = -1;
    int evtchn_fd = -1;
    void *mapped_page = MAP_FAILED;
    int ret = 0;

    /* 1. Відкриття пристрою gntdev */
    gntdev_fd = open("/dev/xen/gntdev", O_RDWR);
    if (gntdev_fd < 0) {
        perror("Не вдалося відкрити /dev/xen/gntdev");
        return -1;
    }

    /* 2. Підготовка структури для відображення grant reference */
    struct ioctl_gntdev_map_grant_ref map_req;
    memset(&map_req, 0, sizeof(map_req));
    map_req.count = 1;
    map_req.refs[0].domid = remote_domid;
    map_req.refs[0].ref = gref;

    if (ioctl(gntdev_fd, IOCTL_GNTDEV_MAP_GRANT_REF, &map_req) < 0) {
        perror("Помилка ioctl IOCTL_GNTDEV_MAP_GRANT_REF");
        close(gntdev_fd);
        return -1;
    }

    /* 3. Отримання вказівника на пам'ять через mmap() за отриманим зміщенням */
    mapped_page = mmap(NULL, PAGE_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED,
                       gntdev_fd, map_req.index);
    if (mapped_page == MAP_FAILED) {
        perror("Помилка mmap для сторінки гранту");
        ret = -1;
        goto out_unmap_ioctl;
    }

    printf("[Dom0] Успішно замаплено сторінку DomU (MFN через gref %u): \"%s\"\n",
           gref, (char *)mapped_page);

    /* 4. Відкриття пристрою event channel та надсилання сповіщення */
    evtchn_fd = open("/dev/xen/evtchn", O_RDWR);
    if (evtchn_fd >= 0) {
        struct ioctl_evtchn_notify notify;
        notify.port = remote_port;
        if (ioctl(evtchn_fd, IOCTL_EVTCHN_NOTIFY, &notify) < 0) {
            perror("Помилка надсилання сповіщення Event Channel");
        } else {
            printf("[Dom0] Надіслано upcall у порт Event Channel %u\n", remote_port);
        }
        close(evtchn_fd);
    }

out_unmap_ioctl:
    /* 5. Звільнення mmap та розмапування через ioctl */
    if (mapped_page != MAP_FAILED) {
        munmap(mapped_page, PAGE_SIZE);
    }

    struct ioctl_gntdev_unmap_grant_ref unmap_req;
    unmap_req.index = map_req.index;
    unmap_req.count = 1;
    ioctl(gntdev_fd, IOCTL_GNTDEV_UNMAP_GRANT_REF, &unmap_req);

    close(gntdev_fd);
    return ret;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Використання: %s <domid> <gref> <evtchn_port>\n", argv[0]);
        return 1;
    }

    uint32_t domid = (uint32_t)atoi(argv[1]);
    uint32_t gref = (uint32_t)atoi(argv[2]);
    uint32_t port = (uint32_t)atoi(argv[3]);

    return process_remote_grant(domid, gref, port) == 0 ? 0 : 1;
}
```
```cpp
// Dom0 Backend Mapper у стилі ідіоматичного C++20 (RAII, std::span, std::expected)
#include <iostream>
#include <string_view>
#include <span>
#include <memory>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>

#include <xen/gntdev.h>
#include <xen/evtchn.h>

namespace xen {

constexpr std::size_t PageSize = 4096;

// RAII обгортка для файлового дескриптора
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

// RAII обгортка для відображеної сторінки гранту
class MappedGrant {
    UniqueFd& gntdev_fd_;
    std::uint64_t map_index_{0};
    void* addr_{MAP_FAILED};

public:
    MappedGrant(UniqueFd& gntdev_fd, std::uint32_t domid, std::uint32_t gref)
        : gntdev_fd_(gntdev_fd) {

        ioctl_gntdev_map_grant_ref map_req{};
        map_req.count = 1;
        map_req.refs[0].domid = domid;
        map_req.refs[0].ref = gref;

        if (::ioctl(gntdev_fd_.get(), IOCTL_GNTDEV_MAP_GRANT_REF, &map_req) < 0) {
            throw std::system_error(errno, std::generic_category(), "IOCTL_GNTDEV_MAP_GRANT_REF failed");
        }

        map_index_ = map_req.index;
        addr_ = ::mmap(nullptr, PageSize, PROT_READ | PROT_WRITE, MAP_SHARED,
                       gntdev_fd_.get(), map_index_);

        if (addr_ == MAP_FAILED) {
            // Очищення через ioctl у разі збою mmap
            ioctl_gntdev_unmap_grant_ref unmap_req{map_index_, 1};
            ::ioctl(gntdev_fd_.get(), IOCTL_GNTDEV_UNMAP_GRANT_REF, &unmap_req);
            throw std::system_error(errno, std::generic_category(), "mmap failed for grant page");
        }
    }

    ~MappedGrant() {
        if (addr_ != MAP_FAILED) {
            ::munmap(addr_, PageSize);
            ioctl_gntdev_unmap_grant_ref unmap_req{map_index_, 1};
            ::ioctl(gntdev_fd_.get(), IOCTL_GNTDEV_UNMAP_GRANT_REF, &unmap_req);
        }
    }

    MappedGrant(const MappedGrant&) = delete;
    MappedGrant& operator=(const MappedGrant&) = delete;

    [[nodiscard]] std::span<std::byte> buffer() noexcept {
        return {static_cast<std::byte*>(addr_), PageSize};
    }

    [[nodiscard]] std::span<const std::byte> buffer() const noexcept {
        return {static_cast<const std::byte*>(addr_), PageSize};
    }
};

// Функція обробки гранту з поверненням std::expected
std::expected<void, std::string> process_grant(std::uint32_t domid, std::uint32_t gref, std::uint32_t port) {
    UniqueFd gntdev{::open("/dev/xen/gntdev", O_RDWR)};
    if (!gntdev.valid()) {
        return std::unexpected("Cannot open /dev/xen/gntdev");
    }

    try {
        MappedGrant grant{gntdev, domid, gref};
        auto buf = grant.buffer();
        
        std::string_view message{reinterpret_cast<const char*>(buf.data())};
        std::cout << "[Dom0 C++] Data from DomU: " << message << std::endl;

        // Сповіщення через Event Channel
        UniqueFd evtchn{::open("/dev/xen/evtchn", O_RDWR)};
        if (evtchn.valid()) {
            ioctl_evtchn_notify notify{port};
            if (::ioctl(evtchn.get(), IOCTL_EVTCHN_NOTIFY, &notify) == 0) {
                std::cout << "[Dom0 C++] Sent notify to port " << port << std::endl;
            }
        }
        return {};
    } catch (const std::exception& ex) {
        return std::unexpected(ex.what());
    }
}

} // namespace xen

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Usage: " << argv[0] << " <domid> <gref> <evtchn_port>\n";
        return 1;
    }

    auto domid = static_cast<std::uint32_t>(std::stoul(argv[1]));
    auto gref  = static_cast<std::uint32_t>(std::stoul(argv[2]));
    auto port  = static_cast<std::uint32_t>(std::stoul(argv[3]));

    auto result = xen::process_grant(domid, gref, port);
    if (!result) {
        std::cerr << "[Error] " << result.error() << std::endl;
        return 1;
    }

    return 0;
}
```
:::

## Опис переваг C++20 підходу та безпека ресурсів

У реальних бекенд-сервісах (наприклад, драйверах блокових дисків QCOW2 чи мережевих маршрутизаторах) витік ресурсів або некоректний порядок їх очищення призводить до паніки ядра гіпервізора чи виснаження таблиці грантів.

Приклад на C++20 демонструє захищені інженерні практики:
- **RAII-класи `UniqueFd` та `MappedGrant`**: гарантують автоматичне закриття файлових дескрипторів та розмапування сторінок пам'яті при виході з області видимості, навіть якщо під час обробки виник виняток (`std::exception`).
- **Використання `std::span`**: створює безпечний огляд буфера пам'яті без копіювання даних та без ризику виходу за межі виділеної 4096-байтної сторінки.
- **Тип `std::expected`**: дозволяє явно обробляти помилки без прихованого переходу через винятки або небезпечні коди повернення в стилі C.

## Часті підводні камені та крайні випадки

1. **Вирівнювання пам'яті за межею сторінки (Page Alignment)**:
   Гіпервізор Xen працює виключно зі сторінками пам'яті розміром 4096 байтів (на x86/ARM). Спроба надати грант на буфер, розміщений у середині сторінки без вирівнювання (`posix_memalign` або `alloc_page`), призведе до витоку сусідніх даних із тієї ж фізичної сторінки.

2. **Невиконане розмапування (`unmap`) та виснаження Grant References**:
   Якщо Dom0 закриє дескриптор `/dev/xen/gntdev` без явно викликаного `IOCTL_GNTDEV_UNMAP_GRANT_REF`, ядро Linux виконає очищення при закритті файл-дескриптора. Однак при високій частоті I/O затримка між викликами створює ризик виснаження таблиці грантів в гості (за замовчуванням у DomU доступно 32–512 записів gref).

3. **Перегони при Live Migration (Живій міграції)**:
   Під час живий міграції DomU на інший фізичний хост усі активні гранти мають бути тимчасово призупинені (`freeze`) або розмаплені. Якщо Dom0 утримує мапування під час міграції, гіпервізор відхилить занулення сторінки, що спричинить паніку ядра гостя.

4. **Інвалідація TLB та накладні витрати на unmap**:
   Кожен виклик `unmap` у Dom0 вимагає видалення запису з таблиць сторінок ядра та виклику снайперської інвалідації TLB (*TLB shootdown*) на всіх фізичних ядрах CPU хоста. Для оптимізації високонавантажених драйверів використовують повторне використання мапувань (Grant Ring Pooling) замість мапування на кожну окрему операцію.
