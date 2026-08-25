# ⚙️ Реалізація сервера vhost-user на сокетах Unix з передачею дескрипторів

Сервер vhost-user приймає керуючі команди від процесу гіпервізора QEMU через потоковий сокет домену Unix (`AF_UNIX`). Головна інженерна складність реалізації полягає в коректній обробці допоміжних керуючих даних (`ancillary data`), якими ядро Linux дублює та передає відкриті файлові дескриптори оперативної пам'яті гостя (`memfd`/`hugetlbfs`) та дескриптори сповіщень `eventfd`.

## Механізм передачі файлових дескрипторів через SCM_RIGHTS

Звичайні системні виклики `read()` та `write()` передають через сокет лише послідовність байтів корисного навантаження. Проте файловий дескриптор у Linux — це лише числовий індекс у таблиці дескрипторів конкретного процесу. Якщо процес QEMU просто передасть число `4` іншому процесу, це число не матиме жодного сенсу в адресному просторі отримувача, оскільки вказуватиме на випадковий локальний файл або взагалі буде закритим.

Для реалізації міжпроцесного розділення ресурсів протокол використовує системний виклик `recvmsg()` та службові керуючі повідомлення типу `SCM_RIGHTS`. Коли відправник запаковує дескриптор у структуру `struct cmsghdr`, ядро Linux перехоплює повідомлення, знаходить відповідну структуру ядра `struct file`, створює новий вільний дескриптор у таблиці цільового процесу й інжектує його числове значення в масив керуючих даних, що надходить отримувачу.

Отримувач зобов'язаний виділити спеціальний буфер за допомогою макросів `CMSG_SPACE()` та `CMSG_LEN()`, які гарантують правильне вирівнювання структур заголовків у пам'яті відповідно до вимог архітектури процесора.

## Реалізація обробника повідомлень

Нижче наведено повністю працездатну реалізацію мінімального бекенд-сервера двома мовами (чистий C та ідіоматичний сучасний C++23). Програма демонструє повний цикл ініціалізації: встановлення з'єднання, отримання заголовка повідомлення разом із дескрипторами `SCM_RIGHTS`, відображення регіонів пам'яті через `mmap()` та алгоритм трансляції фізичних адрес гостя (GPA) у прямі покажчики простору сервера (Backend HVA).

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/mman.h>

#define VHOST_USER_SET_MEM_TABLE 5
#define VHOST_MEMORY_MAX_NREGIONS 8
#define VHOST_USER_VERSION 0x1

struct vhost_user_memory_region {
    uint64_t guest_phys_addr;
    uint64_t memory_size;
    uint64_t userspace_addr;
    uint64_t mmap_offset;
};

struct vhost_user_memory {
    uint32_t nregions;
    uint32_t padding;
    struct vhost_user_memory_region regions[VHOST_MEMORY_MAX_NREGIONS];
};

struct vhost_user_msg {
    uint32_t request;
    uint32_t flags;
    uint32_t size;
    union {
        uint64_t u64;
        struct vhost_user_memory memory;
        uint8_t raw[1024];
    } payload;
} __attribute__((packed));

struct mapped_region {
    uint64_t gpa;
    uint64_t size;
    uint64_t qemu_va;
    uint64_t mmap_offset;
    void *mmap_addr;
};

struct backend_state {
    struct mapped_region regions[VHOST_MEMORY_MAX_NREGIONS];
    uint32_t nregions;
};

/* Зчитування повідомлення з сокета разом із файловими дескрипторами SCM_RIGHTS */
static ssize_t recv_vhost_msg(int sock_fd, struct vhost_user_msg *msg,
                              int *fds, size_t *num_fds) {
    struct msghdr msgh;
    struct iovec iov[1];
    /* Виділяємо буфер під масив файлових дескрипторів із правильним вирівнюванням */
    char cmsg_buf[CMSG_SPACE(sizeof(int) * VHOST_MEMORY_MAX_NREGIONS)];
    
    memset(&msgh, 0, sizeof(msgh));
    memset(cmsg_buf, 0, sizeof(cmsg_buf));
    *num_fds = 0;

    /* Читаємо спочатку 12 байтів фіксованого заголовка */
    iov[0].iov_base = msg;
    iov[0].iov_len = 12;

    msgh.msg_iov = iov;
    msgh.msg_iovlen = 1;
    msgh.msg_control = cmsg_buf;
    msgh.msg_controllen = sizeof(cmsg_buf);

    ssize_t ret = recvmsg(sock_fd, &msgh, 0);
    if (ret <= 0) return ret;

    /* Витягуємо передані дескриптори з керуючого повідомлення ядра */
    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msgh);
    if (cmsg && cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_RIGHTS) {
        size_t fd_bytes = cmsg->cmsg_len - CMSG_LEN(0);
        *num_fds = fd_bytes / sizeof(int);
        memcpy(fds, CMSG_DATA(cmsg), fd_bytes);
    }

    /* Якщо повідомлення містить корисне навантаження — дочитуємо тіло з потоку */
    if (msg->size > 0) {
        if (msg->size > sizeof(msg->payload)) {
            errno = EINVAL;
            return -1;
        }
        size_t received = 0;
        while (received < msg->size) {
            ssize_t n = read(sock_fd, (char *)&msg->payload + received, msg->size - received);
            if (n <= 0) return -1;
            received += (size_t)n;
        }
    }

    return ret + (ssize_t)msg->size;
}

/* Відображення отриманих регіонів у пам'ять сервера через mmap() */
static int handle_set_mem_table(struct backend_state *state,
                                const struct vhost_user_memory *mem,
                                const int *fds, size_t num_fds) {
    if (mem->nregions != num_fds || mem->nregions > VHOST_MEMORY_MAX_NREGIONS) {
        fprintf(stderr, "Помилка: кількість регіонів (%u) != кількості fd (%zu)\n",
                mem->nregions, num_fds);
        return -1;
    }

    /* Звільняємо попередні відображення, якщо вони були активні */
    for (uint32_t i = 0; i < state->nregions; ++i) {
        if (state->regions[i].mmap_addr) {
            munmap(state->regions[i].mmap_addr, state->regions[i].size + state->regions[i].mmap_offset);
        }
    }

    state->nregions = mem->nregions;
    for (uint32_t i = 0; i < mem->nregions; ++i) {
        const struct vhost_user_memory_region *r = &mem->regions[i];
        size_t total_size = r->memory_size + r->mmap_offset;
        
        void *addr = mmap(NULL, total_size, PROT_READ | PROT_WRITE,
                          MAP_SHARED, fds[i], 0);
        if (addr == MAP_FAILED) {
            perror("mmap failed");
            return -1;
        }

        state->regions[i].gpa = r->guest_phys_addr;
        state->regions[i].size = r->memory_size;
        state->regions[i].qemu_va = r->userspace_addr;
        state->regions[i].mmap_offset = r->mmap_offset;
        state->regions[i].mmap_addr = addr;

        printf("Регіон [%u]: GPA=0x%lx..0x%lx -> HVA=%p (fd=%d)\n",
               i, r->guest_phys_addr, r->guest_phys_addr + r->memory_size,
               (void *)((char *)addr + r->mmap_offset), fds[i]);
        
        /* Закриваємо дескриптор: mmap утримує внутрішнє посилання ядра на файл */
        close(fds[i]);
    }
    return 0;
}

/* Трансляція фізичної адреси гостя (GPA) у покажчик у просторі сервера (HVA) */
static void *gpa_to_hva(const struct backend_state *state, uint64_t gpa) {
    for (uint32_t i = 0; i < state->nregions; ++i) {
        const struct mapped_region *r = &state->regions[i];
        if (gpa >= r->gpa && gpa < (r->gpa + r->size)) {
            uint64_t offset = gpa - r->gpa;
            return (char *)r->mmap_addr + r->mmap_offset + offset;
        }
    }
    return NULL;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <array>
#include <cstring>
#include <cstdint>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/mman.h>

constexpr uint32_t VHOST_USER_SET_MEM_TABLE = 5;
constexpr size_t VHOST_MEMORY_MAX_NREGIONS = 8;
constexpr uint32_t VHOST_USER_VERSION = 0x1;

struct VhostUserMemoryRegion {
    uint64_t guest_phys_addr{0};
    uint64_t memory_size{0};
    uint64_t userspace_addr{0};
    uint64_t mmap_offset{0};
};

struct VhostUserMemory {
    uint32_t nregions{0};
    uint32_t padding{0};
    VhostUserMemoryRegion regions[VHOST_MEMORY_MAX_NREGIONS];
};

struct VhostUserMsg {
    uint32_t request{0};
    uint32_t flags{0};
    uint32_t size{0};
    union {
        uint64_t u64;
        VhostUserMemory memory;
        uint8_t raw[1024];
    } payload;
} __attribute__((packed));

/* RAII обгортка для автоматичного закриття дескриптора */
class ScopedFd {
    int fd_{-1};
public:
    explicit ScopedFd(int fd = -1) noexcept : fd_(fd) {}
    ~ScopedFd() { reset(); }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& other) noexcept : fd_(other.release()) {}
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) reset(other.release());
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }
    void reset(int fd = -1) noexcept {
        if (fd_ >= 0) ::close(fd_);
        fd_ = fd;
    }
};

/* Інкапсуляція відображеної області пам'яті через RAII */
class MappedRegion {
    uint64_t gpa_{0};
    uint64_t size_{0};
    uint64_t qemu_va_{0};
    uint64_t mmap_offset_{0};
    void* mmap_addr_{MAP_FAILED};
    size_t total_mapped_size_{0};

public:
    MappedRegion(uint64_t gpa, uint64_t size, uint64_t qemu_va,
                 uint64_t mmap_offset, int fd)
        : gpa_(gpa), size_(size), qemu_va_(qemu_va), mmap_offset_(mmap_offset) {
        total_mapped_size_ = size + mmap_offset;
        mmap_addr_ = ::mmap(nullptr, total_mapped_size_, PROT_READ | PROT_WRITE,
                            MAP_SHARED, fd, 0);
        if (mmap_addr_ == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "mmap region failed");
        }
    }

    ~MappedRegion() {
        if (mmap_addr_ != MAP_FAILED) {
            ::munmap(mmap_addr_, total_mapped_size_);
        }
    }

    MappedRegion(MappedRegion&& other) noexcept
        : gpa_(other.gpa_), size_(other.size_), qemu_va_(other.qemu_va_),
          mmap_offset_(other.mmap_offset_), mmap_addr_(other.mmap_addr_),
          total_mapped_size_(other.total_mapped_size_) {
        other.mmap_addr_ = MAP_FAILED;
    }

    MappedRegion& operator=(MappedRegion&& other) noexcept {
        if (this != &other) {
            if (mmap_addr_ != MAP_FAILED) ::munmap(mmap_addr_, total_mapped_size_);
            gpa_ = other.gpa_;
            size_ = other.size_;
            qemu_va_ = other.qemu_va_;
            mmap_offset_ = other.mmap_offset_;
            mmap_addr_ = other.mmap_addr_;
            total_mapped_size_ = other.total_mapped_size_;
            other.mmap_addr_ = MAP_FAILED;
        }
        return *this;
    }

    [[nodiscard]] bool contains(uint64_t gpa) const noexcept {
        return gpa >= gpa_ && gpa < (gpa_ + size_);
    }

    [[nodiscard]] std::byte* translate(uint64_t gpa) const noexcept {
        if (!contains(gpa)) return nullptr;
        auto* base = static_cast<std::byte*>(mmap_addr_);
        return base + mmap_offset_ + (gpa - gpa_);
    }

    [[nodiscard]] uint64_t gpa() const noexcept { return gpa_; }
    [[nodiscard]] uint64_t size() const noexcept { return size_; }
};

class VhostUserBackend {
    std::vector<MappedRegion> regions_;

public:
    std::expected<void, std::string> process_mem_table(
        const VhostUserMemory& mem, std::span<const int> fds) {
        if (mem.nregions != fds.size()) {
            return std::unexpected("Кількість регіонів не збігається з кількістю дескрипторів");
        }

        std::vector<MappedRegion> new_regions;
        new_regions.reserve(mem.nregions);

        for (uint32_t i = 0; i < mem.nregions; ++i) {
            const auto& r = mem.regions[i];
            try {
                new_regions.emplace_back(r.guest_phys_addr, r.memory_size,
                                         r.userspace_addr, r.mmap_offset, fds[i]);
            } catch (const std::exception& e) {
                return std::unexpected(std::string("Не вдалося відобразити пам'ять: ") + e.what());
            }
        }

        regions_ = std::move(new_regions);
        return {};
    }

    [[nodiscard]] void* gpa_to_hva(uint64_t gpa) const noexcept {
        for (const auto& r : regions_) {
            if (auto* ptr = r.translate(gpa)) {
                return ptr;
            }
        }
        return nullptr;
    }
};
```
:::

## Покроковий розбір функціонування коду

Процес обробки вхідних повідомлень побудований на суворій послідовності дій:

1. **Двоетапне зчитування повідомлення**: Потоковий сокет `SOCK_STREAM` не гарантує збереження меж повідомлень. Якщо повідомлення велике, виклик `recvmsg()` може повернути лише перші байти. Тому код спочатку читає рівно 12 байтів заголовка разом із допоміжними даними `SCM_RIGHTS`, з'ясовує очікуваний розмір корисного навантаження (`msg->size`), і за необхідності запускає цикл дочитування залишку тіла повідомлення.
2. **Парсинг блоку допоміжних даних**: Макрос `CMSG_FIRSTHDR(&msgh)` повертає вказівник на перший заголовок керуючого повідомлення. Сервер перевіряє, що рівень повідомлення дорівнює `SOL_SOCKET`, а тип — `SCM_RIGHTS`. Довжина масиву дескрипторів обчислюється як `cmsg->cmsg_len - CMSG_LEN(0)`.
3. **Відображення пам'яті через `mmap()`**: Для кожного отриманого дескриптора сервер викликає `mmap()` із прапорцями `MAP_SHARED` та `PROT_READ | PROT_WRITE`. Розмір відображення має обов'язково враховувати зміщення `mmap_offset`, оскільки кілька регіонів фізичної пам'яті гостя можуть знаходитися всередині одного великого файлу (наприклад, єдиного бекенда HugePages).
4. **Утилізація дескрипторів**: Одразу після успішного виконання `mmap()` сервер закриває файловий дескриптор викликом `close()`. Це запобігає вичерпанню ліміту відкритих файлів процесу (`RLIMIT_NOFILE`), оскільки ядро Linux утримує власне посилання на структуру відкритого файлу, доки існує хоча б одне активне відображення віртуальної пам'яті.

## Валідація буферів та бар'єри пам'яті

Під час вичитування дескрипторів із кілець virtqueue сервер обов'язково має дотримуватися правил безпеки доступу до неперевіреної пам'яті:

1. **Перевірка меж ланцюжка дескрипторів**: Гостьовий драйвер може передати ланцюжок дескрипторів із прапорцем `VRING_DESC_F_NEXT`. Сервер зобов'язаний обмежувати максимальну довжину ланцюжка (зазвичай не більше розміру самої черги, наприклад 256 елементів), щоб уникнути зациклення при пошкодженні кільця.
2. **Перевірка перетину регіонів**: Якщо буфер пакета починається в одному регіоні пам'яті, а закінчується в іншому (наприклад, на межі PCI Hole), пряме читання `memcpy` призведе до помилки сегментації (`SIGSEGV`). Сервер зобов'язаний розбивати читання таких буферів на частини.
3. **Синхронізація через бар'єри пам'яті**: Перед читанням змісту буфера за адресою `addr` сервер зобов'язаний виконати бар'єр читання пам'яті (`smp_rmb()` у ядрі або `std::atomic_thread_fence(std::memory_order_acquire)` у C++), щоб переконатися, що дані пакета були повністю скинуті процесором гостя до оновлення індексу в Avail Ring.

## Діагностика та налагодження

Для діагностики передачі повідомлень та файлових дескрипторів використовуються стандартні інструменти трасування Linux:

```bash
# Трасування передачі SCM_RIGHTS повідомлень через сокет
strace -e recvmsg,sendmsg,mmap,munmap -p <PID_СЕРВЕРА>

# Перевірка відкритих сокетів та стану черг утилітою ss
ss -x -a -p | grep vhost
```

При використанні `strace` у виводі `recvmsg()` чітко видно передані дескриптори:
`recvmsg(3, {msg_name=NULL, msg_iov=[{iov_base="\x05\x00\x00\x00...", iov_len=12}], msg_control=[{cmsg_len=20, cmsg_level=SOL_SOCKET, cmsg_type=SCM_RIGHTS, cmsg_data=[4, 5]}], msg_flags=0}, 0) = 12`.

## Типові підводні камені реалізації

1. **Втрата дескрипторів при недостатньому буфері**: Якщо контрольний буфер `cmsg_buf` буде виділено за розміром сирого масиву `sizeof(int) * N` без обгортки макросом `CMSG_SPACE()`, структури `cmsghdr` не помістяться в пам'яті. Ядро виставить прапорець `MSG_CTRUNC` і скине дескриптори, що призведе до неможливості змонтувати пам'ять гостя.
2. **Повторне надсилання `VHOST_USER_SET_MEM_TABLE`**: Гіпервізор може надіслати оновлену таблицю пам'яті в процесі роботи гостьової системи (наприклад, при динамічному додаванні пам'яті virtio-mem або під час міграції). Сервер зобов'язаний коректно демонтувати старі регіони через `munmap()`, інакше виникне стрімкий витік віртуального адресного простору хоста.
3. **Безпека перевірки меж GPA**: Перед доступом до пам'яті гостя за адресою з дескриптора virtio сервер завжди повинен перевіряти потрапляння адреси в зареєстровані межі регіонів (`gpa >= region->gpa && gpa + len <= region->gpa + region->size`), щоб шкідливий або зламаний гостьовий драйвер не міг прочитати приватну пам'ять самого сервера.
