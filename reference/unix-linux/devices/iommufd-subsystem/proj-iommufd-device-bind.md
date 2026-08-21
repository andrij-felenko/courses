# ⚙️ Прив'язка PCIe-пристрою та налаштування DMA через /dev/iommufd

Пряме керування периферійним пристроєм PCIe з простору користувача (userspace driver у стилі DPDK, SPDK або гіпервізора QEMU) вимагає виконання суворої послідовності дій: відкриття файлового дескриптора підсистеми `/dev/iommufd`, прив'язки фізичного дескриптора пристрою VFIO до контексту IOMMUFD, виділення логічного адресного простору вводу-виводу (IOAS), відображення буфера пам'яті процесу в таблицю IOMMU та підключення пристрою до створеного адресного простору.

У цьому проекті наведено повну реалізацію процедури ініціалізації та мапінгу пам'яті через нативний uAPI ядра Linux `<linux/iommufd.h>`.

## Механізм ініціалізації та життєвий цикл об'єктів

У класичній моделі VFIO процес був змушений відкривати монолітний контейнер `/dev/vfio/vfio`, додавати в нього IOMMU-групи пристроїв і вручну керувати єдиним спільним доменом. Сучасна підсистема IOMMUFD повністю декомпозує цей процес на незалежні кроки, дозволяючи процесу простору користувача маніпулювати адресними просторами пам'яті та апаратними пристроями як окремими сутностями.

Послідовність системних викликів розгортається за шість послідовних кроків:

1. **Відкриття дескрипторів:** Процес відкриває символьний пристрій `/dev/iommufd`, що створює внутрішній контекст ядра `struct iommufd_ctx`. Одночасно відкривається дескриптор цільового пристрою VFIO — або через сучасний інтерфейс cdev (`/dev/vfio/devices/0000:01:00.0`), або через традиційний файл групи (`/dev/vfio/<group_id>`).
2. **Прив'язка пристрою (Device Bind):** За допомогою команди `ioctl(vfio_dev_fd, VFIO_DEVICE_BIND_IOMMUFD)` дескриптор пристрою реєструється всередині `iommufd_ctx`. Ядро виділяє об'єкт `struct iommufd_device` та повертає простору користувача унікальний числовий ідентифікатор `dev_id`.
3. **Виділення адресного простору (IOAS Allocation):** Команда `ioctl(iommufd, IOMMU_IOAS_ALLOC)` створює логічний адресний простір `struct iommufd_ioas` з власним внутрішнім деревом трансляції `IOPT`. Команді повертається числовий дескриптор `ioas_id`.
4. **Виділення пам'яті та закріплення сторінок (DMA Mapping):** Процес виділяє вирівняний по межі сторінки буфер у своїй віртуальній пам'яті (HVA). Системний виклик `ioctl(iommufd, IOMMU_IOAS_MAP)` викликає функцію ядра `pin_user_pages()`, яка жорстко фіксує сторінки в фізичній оперативній пам'яті хоста (HPA), забороняючи їх переміщення, стиснення чи вивантаження в swap. Після цього зв'язок `IOVA → HVA → HPA` заноситься в таблицю сторінок `IOPT`.
5. **Підключення пристрою (Attach to IOAS):** Команда `ioctl(vfio_dev_fd, VFIO_DEVICE_ATTACH_IOMMUFD_PT)` з'єднує фізичний пристрій із створеним `ioas_id`. Якщо для контролера IOMMU, де розміщено цей пристрій, ще не існує відповідного апаратного домену, ядро автоматично створює об'єкт `HWPT` (Hardware Page Table) і програмує фізичні регістри контролера IOMMU (Intel VT-d Root/Context Tables або ARM SMMUv3 Stream Tables).
6. **Виконання операцій вводу-виводу та штатне очищення:** Після налаштування трансляції периферійний пристрій може безпечно виконувати прямий доступ до оперативної пам'яті хоста за адресою IOVA. Після завершення роботи ресурси звільняються у зворотному порядку: від'єднання пристрою, видалення мапінгу пам'яті та закриття дескрипторів.

## Реалізація на мовах C та C++

Нижче наведено дві повнофункціональні реалізації: на мові C з використанням класичних системних викликів POSIX та на мові C++23 з використанням патерну RAII, обгортки дескрипторів `UniqueFd`, типів `std::expected`, вирівняних буферів `std::span` та форматованого виводу `std::format`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/vfio.h>
#include <linux/iommufd.h>
#include <errno.h>

#define PAGE_SIZE_4K 4096
#define BUFFER_SIZE  (2 * 1024 * 1024) // 2 MB Hugepage-сумісний буфер

int main(int argc, char *argv[]) {
    const char *dev_path = (argc > 1) ? argv[1] : "/dev/vfio/devices/0000:01:00.0";
    int iommufd = -1;
    int dev_fd = -1;
    void *dma_buffer = NULL;
    int ret = 0;

    printf("[1] Відкриття /dev/iommufd...\n");
    iommufd = open("/dev/iommufd", O_RDWR | O_CLOEXEC);
    if (iommufd < 0) {
        perror("Помилка відкриття /dev/iommufd");
        return 1;
    }

    printf("[2] Відкриття VFIO пристрою %s...\n", dev_path);
    dev_fd = open(dev_path, O_RDWR | O_CLOEXEC);
    if (dev_fd < 0) {
        perror("Помилка відкриття пристрою VFIO");
        ret = 1;
        goto cleanup;
    }

    printf("[3] Прив'язка пристрою через VFIO_DEVICE_BIND_IOMMUFD...\n");
    struct vfio_device_bind_iommufd bind_cmd = {
        .argsz = sizeof(bind_cmd),
        .flags = 0,
        .iommufd = iommufd,
        .dev_id = 0, // Заповнюється ядром
    };
    if (ioctl(dev_fd, VFIO_DEVICE_BIND_IOMMUFD, &bind_cmd) < 0) {
        perror("VFIO_DEVICE_BIND_IOMMUFD failed");
        ret = 1;
        goto cleanup;
    }
    uint32_t dev_id = bind_cmd.dev_id;
    printf("    -> Отримано dev_id: %u\n", dev_id);

    printf("[4] Виділення IOAS через IOMMU_IOAS_ALLOC...\n");
    struct iommu_ioas_alloc alloc_cmd = {
        .size = sizeof(alloc_cmd),
        .flags = 0,
        .out_ioas_id = 0,
    };
    if (ioctl(iommufd, IOMMU_IOAS_ALLOC, &alloc_cmd) < 0) {
        perror("IOMMU_IOAS_ALLOC failed");
        ret = 1;
        goto cleanup;
    }
    uint32_t ioas_id = alloc_cmd.out_ioas_id;
    printf("    -> Створено IOAS з id: %u\n", ioas_id);

    printf("[5] Виділення 2 MB буфера в пам'яті процесу (HVA)...\n");
    ret = posix_memalign(&dma_buffer, PAGE_SIZE_4K, BUFFER_SIZE);
    if (ret != 0 || !dma_buffer) {
        fprintf(stderr, "Помилка posix_memalign: %s\n", strerror(ret));
        ret = 1;
        goto cleanup;
    }
    memset(dma_buffer, 0xAA, BUFFER_SIZE);

    printf("[6] Відображення пам'яті через IOMMU_IOAS_MAP...\n");
    uint64_t target_iova = 0x10000000; // Цільова IOVA адреса для DMA
    struct iommu_ioas_map map_cmd = {
        .size = sizeof(map_cmd),
        .flags = IOMMU_IOAS_MAP_FIXED_IOVA | IOMMU_IOAS_MAP_READABLE | IOMMU_IOAS_MAP_WRITEABLE,
        .ioas_id = ioas_id,
        .__reserved = 0,
        .user_va = (uint64_t)dma_buffer,
        .length = BUFFER_SIZE,
        .iova = target_iova,
    };
    if (ioctl(iommufd, IOMMU_IOAS_MAP, &map_cmd) < 0) {
        perror("IOMMU_IOAS_MAP failed");
        ret = 1;
        goto cleanup;
    }
    printf("    -> Буфер HVA %p mapped до IOVA 0x%lx (довжина: %u байтів)\n",
           dma_buffer, (unsigned long)map_cmd.iova, BUFFER_SIZE);

    printf("[7] Підключення пристрою до IOAS через VFIO_DEVICE_ATTACH_IOMMUFD_PT...\n");
    struct vfio_device_attach_iommufd_pt attach_cmd = {
        .argsz = sizeof(attach_cmd),
        .flags = 0,
        .pt_id = ioas_id, // Передаємо ioas_id; ядро створить HWPT автоматично
    };
    if (ioctl(dev_fd, VFIO_DEVICE_ATTACH_IOMMUFD_PT, &attach_cmd) < 0) {
        perror("VFIO_DEVICE_ATTACH_IOMMUFD_PT failed");
        ret = 1;
        goto cleanup;
    }
    printf("    -> Пристрій dev_id %u успішно підключено до апаратної таблиці IOMMU!\n", dev_id);

    printf("[8] Тестовий цикл завершено. Очищення ресурсів...\n");

    // Відключення пристрою
    struct vfio_device_detach_iommufd_pt detach_cmd = {
        .argsz = sizeof(detach_cmd),
        .flags = 0,
    };
    ioctl(dev_fd, VFIO_DEVICE_DETACH_IOMMUFD_PT, &detach_cmd);

    // Розвідображення DMA пам'яті
    struct iommu_ioas_unmap unmap_cmd = {
        .size = sizeof(unmap_cmd),
        .ioas_id = ioas_id,
        .iova = target_iova,
        .length = BUFFER_SIZE,
    };
    ioctl(iommufd, IOMMU_IOAS_UNMAP, &unmap_cmd);

    ret = 0;

cleanup:
    if (dma_buffer) free(dma_buffer);
    if (dev_fd >= 0) close(dev_fd);
    if (iommufd >= 0) close(iommufd);
    return ret;
}
```
```cpp
#include <iostream>
#include <memory>
#include <span>
#include <string_view>
#include <system_error>
#include <expected>
#include <format>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/vfio.h>
#include <linux/iommufd.h>

namespace iommufd {

// RAII обгортка для безпечного володіння дескриптором Linux
class UniqueFd {
    int fd_{-1};
public:
    constexpr UniqueFd() noexcept = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    explicit operator bool() const noexcept { return valid(); }

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
};

// RAII буфер пам'яті, вирівняний по межі сторінки для прямого DMA
class AlignedDmaBuffer {
    void* data_{nullptr};
    size_t size_{0};
public:
    AlignedDmaBuffer(size_t size, size_t alignment = 4096) : size_(size) {
        void* ptr = nullptr;
        int res = ::posix_memalign(&ptr, alignment, size);
        if (res != 0 || !ptr) {
            throw std::system_error(res, std::generic_category(), "Не вдалося виділити DMA буфер");
        }
        data_ = ptr;
        std::memset(data_, 0, size_);
    }

    ~AlignedDmaBuffer() {
        if (data_) {
            ::free(data_);
        }
    }

    AlignedDmaBuffer(const AlignedDmaBuffer&) = delete;
    AlignedDmaBuffer& operator=(const AlignedDmaBuffer&) = delete;
    AlignedDmaBuffer(AlignedDmaBuffer&& other) noexcept 
        : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    [[nodiscard]] void* data() const noexcept { return data_; }
    [[nodiscard]] size_t size() const noexcept { return size_; }
    [[nodiscard]] std::span<std::byte> as_span() noexcept {
        return {static_cast<std::byte*>(data_), size_};
    }
};

// Клас контексту IOMMUFD
class IommuContext {
    UniqueFd fd_;
public:
    static std::expected<IommuContext, std::error_code> open() noexcept {
        int fd = ::open("/dev/iommufd", O_RDWR | O_CLOEXEC);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return IommuContext(UniqueFd(fd));
    }

    explicit IommuContext(UniqueFd fd) noexcept : fd_(std::move(fd)) {}

    [[nodiscard]] int native_handle() const noexcept { return fd_.get(); }

    std::expected<uint32_t, std::error_code> allocate_ioas() noexcept {
        struct iommu_ioas_alloc cmd = {
            .size = sizeof(cmd),
            .flags = 0,
            .out_ioas_id = 0,
        };
        if (::ioctl(fd_.get(), IOMMU_IOAS_ALLOC, &cmd) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return cmd.out_ioas_id;
    }

    std::expected<uint64_t, std::error_code> map_dma(
        uint32_t ioas_id, uint64_t target_iova, const AlignedDmaBuffer& buffer) noexcept {
        struct iommu_ioas_map cmd = {
            .size = sizeof(cmd),
            .flags = IOMMU_IOAS_MAP_FIXED_IOVA | IOMMU_IOAS_MAP_READABLE | IOMMU_IOAS_MAP_WRITEABLE,
            .ioas_id = ioas_id,
            .__reserved = 0,
            .user_va = reinterpret_cast<uint64_t>(buffer.data()),
            .length = buffer.size(),
            .iova = target_iova,
        };
        if (::ioctl(fd_.get(), IOMMU_IOAS_MAP, &cmd) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return cmd.iova;
    }

    std::error_code unmap_dma(uint32_t ioas_id, uint64_t iova, size_t length) noexcept {
        struct iommu_ioas_unmap cmd = {
            .size = sizeof(cmd),
            .ioas_id = ioas_id,
            .iova = iova,
            .length = length,
        };
        if (::ioctl(fd_.get(), IOMMU_IOAS_UNMAP, &cmd) < 0) {
            return std::error_code(errno, std::generic_category());
        }
        return {};
    }
};

// Клас прив'язаного пристрою VFIO
class VfioDevice {
    UniqueFd fd_;
    uint32_t dev_id_{0};
public:
    static std::expected<VfioDevice, std::error_code> open_and_bind(
        std::string_view dev_path, const IommuContext& ctx) noexcept {
        int dev_fd = ::open(dev_path.data(), O_RDWR | O_CLOEXEC);
        if (dev_fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        struct vfio_device_bind_iommufd bind_cmd = {
            .argsz = sizeof(bind_cmd),
            .flags = 0,
            .iommufd = ctx.native_handle(),
            .dev_id = 0,
        };
        if (::ioctl(dev_fd, VFIO_DEVICE_BIND_IOMMUFD, &bind_cmd) < 0) {
            ::close(dev_fd);
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return VfioDevice(UniqueFd(dev_fd), bind_cmd.dev_id);
    }

    VfioDevice(UniqueFd fd, uint32_t dev_id) noexcept 
        : fd_(std::move(fd)), dev_id_(dev_id) {}

    [[nodiscard]] uint32_t dev_id() const noexcept { return dev_id_; }

    std::error_code attach_ioas(uint32_t ioas_id) noexcept {
        struct vfio_device_attach_iommufd_pt attach_cmd = {
            .argsz = sizeof(attach_cmd),
            .flags = 0,
            .pt_id = ioas_id,
        };
        if (::ioctl(fd_.get(), VFIO_DEVICE_ATTACH_IOMMUFD_PT, &attach_cmd) < 0) {
            return std::error_code(errno, std::generic_category());
        }
        return {};
    }

    std::error_code detach_ioas() noexcept {
        struct vfio_device_detach_iommufd_pt detach_cmd = {
            .argsz = sizeof(detach_cmd),
            .flags = 0,
        };
        if (::ioctl(fd_.get(), VFIO_DEVICE_DETACH_IOMMUFD_PT, &detach_cmd) < 0) {
            return std::error_code(errno, std::generic_category());
        }
        return {};
    }
};

} // namespace iommufd

int main(int argc, char* argv[]) {
    const std::string_view dev_path = (argc > 1) ? argv[1] : "/dev/vfio/devices/0000:01:00.0";
    constexpr size_t BUFFER_SIZE = 2 * 1024 * 1024; // 2 MB
    constexpr uint64_t TARGET_IOVA = 0x10000000;

    auto ctx_res = iommufd::IommuContext::open();
    if (!ctx_res) {
        std::cerr << std::format("Помилка відкриття /dev/iommufd: {}\n", ctx_res.error().message());
        return 1;
    }
    auto& ctx = *ctx_res;

    std::cout << std::format("Відкриття та прив'язка пристрою {}...\n", dev_path);
    auto dev_res = iommufd::VfioDevice::open_and_bind(dev_path, ctx);
    if (!dev_res) {
        std::cerr << std::format("Помилка прив'язки VFIO пристрою: {}\n", dev_res.error().message());
        return 1;
    }
    auto& dev = *dev_res;
    std::cout << std::format("-> Отримано dev_id: {}\n", dev.dev_id());

    auto ioas_res = ctx.allocate_ioas();
    if (!ioas_res) {
        std::cerr << std::format("Помилка виділення IOAS: {}\n", ioas_res.error().message());
        return 1;
    }
    uint32_t ioas_id = *ioas_res;
    std::cout << std::format("-> Створено IOAS: {}\n", ioas_id);

    iommufd::AlignedDmaBuffer buffer(BUFFER_SIZE);
    auto map_res = ctx.map_dma(ioas_id, TARGET_IOVA, buffer);
    if (!map_res) {
        std::cerr << std::format("Помилка відображення пам'яті DMA: {}\n", map_res.error().message());
        return 1;
    }
    std::cout << std::format("-> Відображено IOVA 0x{:X} (розмір {} байтів)\n", *map_res, BUFFER_SIZE);

    auto attach_err = dev.attach_ioas(ioas_id);
    if (attach_err) {
        std::cerr << std::format("Помилка підключення пристрою до IOAS: {}\n", attach_err.message());
        return 1;
    }
    std::cout << "-> Пристрій успішно підключено до апаратного домену IOMMU!\n";

    // Акуратне відключення
    dev.detach_ioas();
    ctx.unmap_dma(ioas_id, TARGET_IOVA, BUFFER_SIZE);
    std::cout << "-> Очищення ресурсів виконано штатно.\n";

    return 0;
}
```
:::

## Крайові випадки, пастки продуктивності та діагностика

При практичній експлуатації та розробці користувацьких драйверів на базі IOMMUFD розробники найчастіше стикаються з трьома критичними аспектами:

### 1. Ліміти блокування пам'яті (`RLIMIT_MEMLOCK`)
Оскільки драйвер периферійного пристрою виконує прямий доступ до пам'яті без перехоплення помилок сторінок MMU, всі сторінки буфера повинні бути жорстко закріплені в оперативній пам'яті. Якщо процес намагається відобразити буфер обсягом 4 GB, а поточний ліміт `ulimit -l` встановлено, наприклад, у 64 KB (типове значення для не-root процесів), виклик `IOMMU_IOAS_MAP` миттєво поверне помилку `ENOMEM`. У виробничих середовищах DPDK та SPDK ліміт `memlock` піднімається до `unlimited` у файлі конфігурації `/etc/security/limits.conf` або через системний виклик `setrlimit()`.

### 2. Переваги використання Hugepages (2 MB / 1 GB)
Відображення пам'яті стандартними 4 KB сторінками для буфера обсягом 64 GB вимагає створення `16 777 216` записів у таблицях сторінок IOMMU. Це перевантажує внутрішні буфери асоціативної трансляції контролера (IOTLB), спричиняючи значні затримки під час читання заголовків пакетів або блоків NVMe. Використання сторінок Hugepages розміром 2 MB скорочує кількість записів до 32 768, а для сторінок 1 GB — до всього 64 записів, забезпечуючи практично 100% потрапляння в кеш IOTLB пристрою.

### 3. Підключення кількох пристроїв до єдиного IOAS
Головна перевага IOMMUFD над застарілим VFIO Type1 полягає в тому, що після виконання `IOMMU_IOAS_MAP` процес може підключити другий, третій або десятий пристрій (`dev_id_2`, `dev_id_3`) до того самого `ioas_id` за допомогою `VFIO_DEVICE_ATTACH_IOMMUFD_PT`. Ядро Linux використає вже наявне дерево `IOPT` і **не буде повторно закріплювати пам'ять**. Це усуває подвійний облік заблокованих сторінок та прискорює запуск складних багатопристроєвих віртуальних машин у кілька разів.

### 4. Трасування та перевірка трансляцій у ядрі
Для перевірки коректності роботи IOMMUFD та діагностики помилок `DMAR Fault` адміністратор може скористатися штатним інструментом трасування `trace-cmd`:

```
# trace-cmd record -e iommu -e iommufd
# trace-cmd report
```

У звіті трасування чітко видно всі операції виділення об'єктів `iommufd_map`, прив'язки пристроїв `iommufd_attach` та апаратні команди очищення кешів `iommu_iotlb_flush`.

### 5. Інтерфейси доступу: cdev проти файлів груп VFIO
У старих версіях ядра Linux для відкриття пристрою VFIO процес відкривав файл відповідної IOMMU-групи `/dev/vfio/<group_id>`, після чого отримував дескриптор пристрою через команду `VFIO_GROUP_GET_DEVICE_FD`.

Починаючи з Linux 6.4, VFIO отримав підтримку прямих символьних пристроїв (**VFIO cdev**), розташованих у каталозі `/dev/vfio/devices/0000:01:00.0`. Якщо ядро зібрано з параметром `CONFIG_VFIO_DEVICE_CDEV=y`, користувацький додаток відкриває безпосередньо файл потрібного PCI-пристрою, повністю минаючи концепцію файлів груп у просторі користувача. Перевірка приналежності до IOMMU-групи та наявності прав ізоляції тепер делегується виклику `VFIO_DEVICE_BIND_IOMMUFD`. Якщо хоча б один інший пристрій з тієї самої апаратної IOMMU-групи все ще контролюється штатним драйвером ядра хоста (наприклад, драйвером `nvme` або `ixgbe`), виклик `VFIO_DEVICE_BIND_IOMMUFD` поверне помилку `EBUSY`, захищаючи хост від порушення меж ізоляції.
