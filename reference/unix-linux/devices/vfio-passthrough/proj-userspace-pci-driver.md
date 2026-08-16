# ⚙️ Драйвер PCI-пристрою у просторі користувача через VFIO

Цей проєкт присвячено розробці автономного драйвера периферійного пристрою шини PCI Express у просторі користувача (userspace driver) мовами C та C++ з використанням низькорівневих інтерфейсів VFIO ядра Linux. Такий підхід лежить в основі таких високопродуктивних фреймворків, як DPDK (Data Plane Development Kit) для мережевих карт та SPDK (Storage Performance Development Kit) для накопичувачів NVMe.

---

## 1. Архітектурне обґрунтування користувацьких драйверів

Традиційні драйвери периферійних пристроїв функціонують у просторі ядра (Kernel Space) у формі модулів ядра Linux. Щоразу, коли застосунок простору користувача запитує передачу пакетів через системні виклики `read(2)` або `write(2)`, відбуваються наступні кроки:
1. Переключення контексту з простору користувача у простір ядра (User-to-Kernel context switch);
2. Копіювання даних із буфера користувача у системний буфер ядра (`copy_from_user`);
3. Переривання від пристрою про завершення передачі даних, яке обробляється в контексті обробника переривань (ISR та Bottom Half);
4. Зворотне копіювання даних та повернення в простір користувача.

При обробці мільйонів операцій на секунду (наприклад, у мережевих карточках 100 GbE, які передають до 148 мільйонів пакетів за секунду) таке переключення контексту й копіювання даних повністю виснажує ресурси центрального процесора.

Завдяки VFIO користувацький процес отримує змогу напряму програмувати кільця дескрипторів DMA та регістри BAR пристрою, оминаючи ядро хоста під час нормальної роботи. Замість обробки переривань через системні виклики драйвери у просторі користувача часто застосовують активне опитування (**Polling Mode Drivers — PMD**): воно знімає з шляху даних і переривання, і пробудження процесу, лишаючи затримку на рівні одиниць мікросекунд.

---

## 2. Покроковий алгоритм функціонування драйвера

Ініціалізація та робота користувацького драйвера підсистеми VFIO складається з семи послідовних етапів.

### Етап 1. Перевірка та підвищення лімітів закріплення пам'яті (`RLIMIT_MEMLOCK`)
Для здійснення прямого доступу до пам'яті (DMA) периферійний пристрій вимагає, щоб віртуальні сторінки пам'яті процесу хоста були жорстко прив'язані до конкретних хостових фізичних адрес (HPA). За замовчуванням ядро Linux обмежує обсяг пам'яті, яку процес може закріпити (щоб запобігти вичерпанням фізичної RAM). Драйвер повинен підвищити ліміт `RLIMIT_MEMLOCK` за допомогою системного виклику `setrlimit(2)` до потрібного обсягу (або значення `RLIM_INFINITY`).

### Етап 2. Ініціалізація контейнера та перевірка версії API
Драйвер відкриває символьний пристрій `/dev/vfio/vfio` за допомогою системного виклику `open(2)`. Через виклик `ioctl(VFIO_GET_API_VERSION)` драйвер перевіряє сумісність ядра, а через `ioctl(VFIO_CHECK_EXTENSION, VFIO_TYPE1_IOMMU)` переконується у наявності бекенду трансляції IOMMU Type1.

### Етап 3. Відкриття та перевірка IOMMU-групи
Драйвер відкриває файл групи `/dev/vfio/<group_id>`. За допомогою виклику `ioctl(VFIO_GROUP_GET_STATUS)` перевіряється наявність бітового прапорця `VFIO_GROUP_FLAGS_VIABLE`. Якщо принаймні один пристрій у цій IOMMU-групі залишається під контролем стандартного драйвера ядра хоста (наприклад `xhci_hcd` або `nouveau`), ядро скине прапорець `VIABLE` й заборонить подальші операції з міркувань ізоляції безпеки.

### Етап 4. Приєднання групи та активація домену IOMMU
Драйвер зв'язує відкриту групу з контейнером за допомогою виклику `ioctl(group_fd, VFIO_GROUP_SET_CONTAINER, &container_fd)`. Після цього над контейнером виконується команда `ioctl(container_fd, VFIO_SET_IOMMU, VFIO_TYPE1_IOMMU)`, що змушує ядро Linux виділити та ініціалізувати апаратний домен трансляції IOMMU.

### Етап 5. Отримання дескриптора пристрою (`device_fd`)
Здійснюється виклик `ioctl(group_fd, VFIO_GROUP_GET_DEVICE_FD, "0000:01:00.0")`. Ядро повертає анонімний дескриптор пристрою, який дозволяє запитувати геометричні параметри BAR-регістрів та виконувати їх відображення.

### Етап 6. Виділення та реєстрація DMA-буферів
Драйвер виділяє вирівняний по межі сторінки пам'яті буфер (наприклад, через `posix_memalign` або `mmap` із прапорцем `MAP_HUGETLB` для використання великих сторінок HugePages 2 МБ чи 1 ГБ). Потім заповнюється структура `vfio_iommu_type1_dma_map` із зазначенням HVA, бажаної IOVA адреси та розміру. Виклик `ioctl(container_fd, VFIO_IOMMU_MAP_DMA, &dma_map)` змушує ядро закріпити сторінки й запрограмувати таблиці сторінок IOMMU.

### Етап 7. Відображення MMIO-регістрів (BAR0)
Драйвер запитує розмір та зсув BAR0 через `ioctl(device_fd, VFIO_DEVICE_GET_REGION_INFO, &reg_info)`. Використовуючи отриманий зсув, драйвер викликає `mmap(2)` над дескриптором `device_fd`. В результаті процес отримує прямий вказівник на фізичні регістри пристрою і може виконувати читання та запис регістрів за допомогою volatile-покажчиків або атомарних операцій.

---

## 3. Практична реалізація драйвера

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/eventfd.h>
#include <linux/vfio.h>
#include <stdint.h>

#define DMA_BUFFER_SIZE (2 * 1024 * 1024) /* 2 MB DMA буфер */

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <group_id> <pci_bdf>\n", argv[0]);
        fprintf(stderr, "Приклад: %s 15 0000:01:00.0\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *group_id = argv[1];
    const char *pci_bdf = argv[2];

    /* 1. Збільшуємо ліміт закріпленої пам'яті (RLIMIT_MEMLOCK) */
    struct rlimit rlim = { RLIM_INFINITY, RLIM_INFINITY };
    if (setrlimit(RLIMIT_MEMLOCK, &rlim) < 0) {
        perror("setrlimit(RLIMIT_MEMLOCK)");
        return EXIT_FAILURE;
    }

    /* 2. Відкриваємо контейнер VFIO */
    int container_fd = open("/dev/vfio/vfio", O_RDWR);
    if (container_fd < 0) {
        perror("open /dev/vfio/vfio");
        return EXIT_FAILURE;
    }

    if (ioctl(container_fd, VFIO_GET_API_VERSION) != VFIO_API_VERSION ||
        !ioctl(container_fd, VFIO_CHECK_EXTENSION, VFIO_TYPE1_IOMMU)) {
        fprintf(stderr, "Непідтримувана версія VFIO або відсутній TYPE1 IOMMU\n");
        close(container_fd);
        return EXIT_FAILURE;
    }

    /* 3. Відкриваємо групу VFIO */
    char group_path[64];
    snprintf(group_path, sizeof(group_path), "/dev/vfio/%s", group_id);
    int group_fd = open(group_path, O_RDWR);
    if (group_fd < 0) {
        perror("open /dev/vfio/<group>");
        close(container_fd);
        return EXIT_FAILURE;
    }

    /* Перевіряємо стан групи */
    struct vfio_group_status status = { .argsz = sizeof(status) };
    if (ioctl(group_fd, VFIO_GROUP_GET_STATUS, &status) < 0 || !(status.flags & VFIO_GROUP_FLAGS_VIABLE)) {
        fprintf(stderr, "Група %s не є готова (деякі пристрої не під контролем VFIO)\n", group_id);
        close(group_fd);
        close(container_fd);
        return EXIT_FAILURE;
    }

    /* Приєднуємо групу до контейнера */
    if (ioctl(group_fd, VFIO_GROUP_SET_CONTAINER, &container_fd) < 0) {
        perror("ioctl(VFIO_GROUP_SET_CONTAINER)");
        close(group_fd);
        close(container_fd);
        return EXIT_FAILURE;
    }

    /* Встановлюємо тип IOMMU для контейнера */
    if (ioctl(container_fd, VFIO_SET_IOMMU, VFIO_TYPE1_IOMMU) < 0) {
        perror("ioctl(VFIO_SET_IOMMU)");
        close(group_fd);
        close(container_fd);
        return EXIT_FAILURE;
    }

    /* 4. Отримуємо дескриптор PCI-пристрою */
    int device_fd = ioctl(group_fd, VFIO_GROUP_GET_DEVICE_FD, pci_bdf);
    if (device_fd < 0) {
        perror("ioctl(VFIO_GROUP_GET_DEVICE_FD)");
        close(group_fd);
        close(container_fd);
        return EXIT_FAILURE;
    }

    /* 5. Виділяємо та реєструємо DMA-буфер у пам'яті */
    void *dma_buffer = NULL;
    if (posix_memalign(&dma_buffer, sysconf(_SC_PAGESIZE), DMA_BUFFER_SIZE) != 0) {
        perror("posix_memalign");
        close(device_fd);
        close(group_fd);
        close(container_fd);
        return EXIT_FAILURE;
    }
    memset(dma_buffer, 0, DMA_BUFFER_SIZE);

    struct vfio_iommu_type1_dma_map dma_map = {
        .argsz = sizeof(dma_map),
        .flags = VFIO_DMA_MAP_FLAG_READ | VFIO_DMA_MAP_FLAG_WRITE,
        .vaddr = (uint64_t)dma_buffer,
        .iova = 0x10000000, /* Призначаємо IOVA адресою 0x10000000 */
        .size = DMA_BUFFER_SIZE
    };

    if (ioctl(container_fd, VFIO_IOMMU_MAP_DMA, &dma_map) < 0) {
        perror("ioctl(VFIO_IOMMU_MAP_DMA)");
        free(dma_buffer);
        close(device_fd);
        close(group_fd);
        close(container_fd);
        return EXIT_FAILURE;
    }
    printf("DMA буфер зареєстровано: HVA=%p -> IOVA=0x%llx (розмір %d байтів)\n",
           dma_buffer, (unsigned long long)dma_map.iova, DMA_BUFFER_SIZE);

    /* 6. Отримуємо інформацію про BAR0 та робимо mmap */
    struct vfio_region_info reg_info = {
        .argsz = sizeof(reg_info),
        .index = VFIO_PCI_BAR0_REGION_INDEX
    };

    if (ioctl(device_fd, VFIO_DEVICE_GET_REGION_INFO, &reg_info) == 0 && reg_info.size > 0) {
        void *bar0_mmio = mmap(NULL, reg_info.size, PROT_READ | PROT_WRITE,
                               MAP_SHARED, device_fd, reg_info.offset);
        if (bar0_mmio != MAP_FAILED) {
            printf("BAR0 MMIO відображено за адресою %p (розмір %llu байтів)\n",
                   bar0_mmio, (unsigned long long)reg_info.size);
            
            /* Читаємо перший 32-бітний регістр MMIO */
            volatile uint32_t *reg0 = (volatile uint32_t *)bar0_mmio;
            printf("Значення регістра BAR0[0]: 0x%08x\n", *reg0);

            munmap(bar0_mmio, reg_info.size);
        }
    }

    /* 7. Налаштовуємо переривання MSI через eventfd */
    int efd = eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC);
    if (efd >= 0) {
        char irq_set_buf[sizeof(struct vfio_irq_set) + sizeof(int)];
        struct vfio_irq_set *irq_set = (struct vfio_irq_set *)irq_set_buf;
        irq_set->argsz = sizeof(irq_set_buf);
        irq_set->flags = VFIO_IRQ_SET_DATA_EVENTFD | VFIO_IRQ_SET_ACTION_TRIGGER;
        irq_set->index = VFIO_PCI_MSI_IRQ_INDEX;
        irq_set->start = 0;
        irq_set->count = 1;
        *(int *)&irq_set->data[0] = efd;

        if (ioctl(device_fd, VFIO_DEVICE_SET_IRQS, irq_set) == 0) {
            printf("Переривання MSI-0 успішно підключено до eventfd %d\n", efd);
        }
        close(efd);
    }

    /* Очищення ресурсів */
    struct vfio_iommu_type1_dma_unmap dma_unmap = {
        .argsz = sizeof(dma_unmap),
        .flags = 0,
        .iova = 0x10000000,
        .size = DMA_BUFFER_SIZE
    };
    ioctl(container_fd, VFIO_IOMMU_UNMAP_DMA, &dma_unmap);
    free(dma_buffer);
    close(device_fd);
    close(group_fd);
    close(container_fd);

    printf("Драйвер успішно завершив роботу.\n");
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <memory>
#include <cstring>
#include <cstdlib>
#include <utility>
#include <string>
#include <string_view>
#include <span>
#include <system_error>
#include <expected>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/eventfd.h>
#include <linux/vfio.h>

namespace vfio {

// RAII обгортка для файлових дескрипторів POSIX
class FileDescriptor {
    int fd_{-1};
public:
    constexpr FileDescriptor() noexcept = default;
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
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
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

// RAII обгортка для MMIO відображень через mmap
class MmioRegion {
    void* addr_{MAP_FAILED};
    size_t size_{0};
public:
    MmioRegion() noexcept = default;
    MmioRegion(void* addr, size_t size) noexcept : addr_(addr), size_(size) {}
    ~MmioRegion() {
        if (addr_ != MAP_FAILED && size_ > 0) {
            ::munmap(addr_, size_);
        }
    }

    MmioRegion(const MmioRegion&) = delete;
    MmioRegion& operator=(const MmioRegion&) = delete;

    MmioRegion(MmioRegion&& other) noexcept
        : addr_(other.addr_), size_(other.size_) {
        other.addr_ = MAP_FAILED;
        other.size_ = 0;
    }

    [[nodiscard]] bool valid() const noexcept { return addr_ != MAP_FAILED; }
    [[nodiscard]] std::span<volatile uint32_t> as_uint32_span() const noexcept {
        return { static_cast<volatile uint32_t*>(addr_), size_ / sizeof(uint32_t) };
    }
};

class VfioDevice {
    FileDescriptor container_fd_;
    FileDescriptor group_fd_;
    FileDescriptor device_fd_;
    void* dma_buffer_{nullptr};
    size_t dma_size_{0};
    uint64_t iova_base_{0};

public:
    VfioDevice() noexcept = default;
    VfioDevice(const VfioDevice&) = delete;
    VfioDevice& operator=(const VfioDevice&) = delete;
    VfioDevice(VfioDevice&& other) noexcept
        : container_fd_(std::move(other.container_fd_)),
          group_fd_(std::move(other.group_fd_)),
          device_fd_(std::move(other.device_fd_)),
          dma_buffer_(std::exchange(other.dma_buffer_, nullptr)),
          dma_size_(other.dma_size_),
          iova_base_(other.iova_base_) {}

    static std::expected<VfioDevice, std::error_code> create(
        std::string_view group_id, std::string_view pci_bdf, size_t dma_size) {
        
        // 1. Налаштовуємо ліміти MEMLOCK
        struct rlimit rlim{RLIM_INFINITY, RLIM_INFINITY};
        if (::setrlimit(RLIMIT_MEMLOCK, &rlim) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        // 2. Відкриваємо контейнер
        FileDescriptor container{::open("/dev/vfio/vfio", O_RDWR)};
        if (!container.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::ioctl(container.get(), VFIO_GET_API_VERSION) != VFIO_API_VERSION ||
            !::ioctl(container.get(), VFIO_CHECK_EXTENSION, VFIO_TYPE1_IOMMU)) {
            return std::unexpected(std::make_error_code(std::errc::invalid_argument));
        }

        // 3. Відкриваємо групу
        std::string group_path = "/dev/vfio/" + std::string(group_id);
        FileDescriptor group{::open(group_path.c_str(), O_RDWR)};
        if (!group.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        struct vfio_group_status status{.argsz = sizeof(status)};
        if (::ioctl(group.get(), VFIO_GROUP_GET_STATUS, &status) < 0 ||
            !(status.flags & VFIO_GROUP_FLAGS_VIABLE)) {
            return std::unexpected(std::make_error_code(std::errc::device_or_resource_busy));
        }

        int raw_container_fd = container.get();
        if (::ioctl(group.get(), VFIO_GROUP_SET_CONTAINER, &raw_container_fd) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::ioctl(container.get(), VFIO_SET_IOMMU, VFIO_TYPE1_IOMMU) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        // 4. Отримуємо пристрій
        FileDescriptor device{::ioctl(group.get(), VFIO_GROUP_GET_DEVICE_FD, pci_bdf.data())};
        if (!device.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        VfioDevice dev;
        dev.container_fd_ = std::move(container);
        dev.group_fd_ = std::move(group);
        dev.device_fd_ = std::move(device);
        dev.dma_size_ = dma_size;

        return dev;
    }

    ~VfioDevice() {
        if (dma_buffer_ && container_fd_.valid()) {
            struct vfio_iommu_type1_dma_unmap unmap{.argsz = sizeof(unmap), .flags = 0, .iova = iova_base_, .size = dma_size_};
            ::ioctl(container_fd_.get(), VFIO_IOMMU_UNMAP_DMA, &unmap);
            ::free(dma_buffer_);
        }
    }

    std::expected<uint64_t, std::error_code> map_dma_buffer(uint64_t iova) {
        void* buf = nullptr;
        if (::posix_memalign(&buf, ::sysconf(_SC_PAGESIZE), dma_size_) != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        std::memset(buf, 0, dma_size_);

        struct vfio_iommu_type1_dma_map dma_map{
            .argsz = sizeof(dma_map),
            .flags = VFIO_DMA_MAP_FLAG_READ | VFIO_DMA_MAP_FLAG_WRITE,
            .vaddr = reinterpret_cast<uint64_t>(buf),
            .iova = iova,
            .size = dma_size_
        };

        if (::ioctl(container_fd_.get(), VFIO_IOMMU_MAP_DMA, &dma_map) < 0) {
            ::free(buf);
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        dma_buffer_ = buf;
        iova_base_ = iova;
        return iova;
    }

    std::expected<MmioRegion, std::error_code> map_bar(uint32_t bar_index) {
        struct vfio_region_info reg_info{.argsz = sizeof(reg_info), .index = bar_index};
        if (::ioctl(device_fd_.get(), VFIO_DEVICE_GET_REGION_INFO, &reg_info) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        void* addr = ::mmap(nullptr, reg_info.size, PROT_READ | PROT_WRITE, MAP_SHARED, device_fd_.get(), reg_info.offset);
        if (addr == MAP_FAILED) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return MmioRegion{addr, reg_info.size};
    }
};

} // namespace vfio

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <group_id> <pci_bdf>\n";
        return EXIT_FAILURE;
    }

    auto dev_result = vfio::VfioDevice::create(argv[1], argv[2], 2 * 1024 * 1024);
    if (!dev_result) {
        std::cerr << "Помилка ініціалізації VFIO: " << dev_result.error().message() << "\n";
        return EXIT_FAILURE;
    }

    auto& dev = *dev_result;
    auto dma_res = dev.map_dma_buffer(0x10000000);
    if (dma_res) {
        std::cout << "DMA буфер зареєстровано за IOVA 0x" << std::hex << *dma_res << std::dec << "\n";
    }

    auto bar0_res = dev.map_bar(VFIO_PCI_BAR0_REGION_INDEX);
    if (bar0_res && bar0_res->valid()) {
        auto regs = bar0_res->as_uint32_span();
        std::cout << "BAR0 відображено. Кількість 32-бітних регістрів: " << regs.size() << "\n";
        if (!regs.empty()) {
            std::cout << "Значення BAR0[0]: 0x" << std::hex << regs[0] << std::dec << "\n";
        }
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 4. Оптимізації та підводні камені під час розробки

Під час практичної розробки користувацьких драйверів на базі VFIO інженери стикаються з трьома основними апаратними та системними обмеженнями:

### 4.1. Використання великих сторінок пам'яті (HugePages)
Звичайна сторінка пам'яті в архітектурі x86_64 має розмір 4 Кілобайти. Для реєстрації буфера пам'яті розміром 4 Гігобайти звичайними сторінками ядро змушене заповнити таблиці сторінок IOMMU з 1 048 576 записів. Це викликає постійні промахи буфера TLB IOMMU (IOTLB Misses), а кожен промах коштує зайвого проходу таблицями трансляції — на потоках у мільйони операцій за секунду просідання пропускної здатності добре помітне.

Використання сторінок HugePages (розміром 2 Мегабайти або 1 Гігабайт) зменшує кількість записів у таблицях IOMMU до 2048 або 4 відповідно. Драйвери DPDK обов'язково виділяють DMA-буфери через `mmap()` із прапорцями `MAP_HUGETLB | MAP_ANONYMOUS`. Для виділення HugePages у системі заздалегідь резервується пул сторінок:
```bash
echo 1024 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
```

### 4.2. Бар'єри пам'яті та когерентність кешу
Під час запису даних процесором у DMA-буфер і подальшої відправки команди пристрою через MMIO необхідно суворо контролювати порядок виконання інструкцій CPU. Процесор або компілятор може переупорядкувати операції запису так, що команда запуску DMA в BAR0 досягне пристрою *раніше*, ніж записи в сам DMA-буфер стануть видимими пристроєві.

Щоб запобігти порушенню цілісності даних, драйвер повинен застосовувати бар'єри пам'яті:
* У C++20: `std::atomic_thread_fence(std::memory_order_release);` перед записом у регістр MMIO;
* На архітектурі x86: інструкцію `sfence` чи `mfence` (`__builtin_ia32_sfence()`);
* На архітектурі ARM64: інструкції `dmb osh` (Data Memory Barrier Outer Shareable).

### 4.3. Гарантія коректного очищення ресурсів
Якщо користувацький драйвер аварійно завершує роботу (наприклад через `SIGSEGV` чи `SIGKILL`), ядро Linux автоматично закриває всі відкриті файлові дескриптори (`device_fd`, `group_fd`, `container_fd`). При закритті контейнерного дескриптора ядро розкріплює сторінки RAM, скасовує трансляцію IOMMU та надсилає сигнал Reset (Function Level Reset) на пристрій, повертаючи його у безпечний стан і запобігаючи неконтрольованому DMA в пам'ять хоста.
