# ⚙️ Практичне виділення, відображення та експорт GEM dumb-буфера через PRIME

Пряма робота з графічним процесором та апаратним скануванням дисплея в Linux вимагає виділення відеопам'яті через підсистему Graphics Execution Manager (GEM), отримання доступу до пікселів процесором через системний виклик `mmap` та експорту буферів іншим процесам через механізм PRIME. Нижче реалізовано повний приклад програми, яка створює лінійний буфер кадру (dumb buffer), заповнює його графічним візерунком і передає дескриптор `dma-buf` для спільного використання між процесами.

## Задача та архітектура рішення

Програма демонструє повний життєвий цикл взаємодії прикладного коду з ядром DRM:
1. **Відкриття вузла DRM**: підключення до контролера дисплея `/dev/dri/card0` або рендерера `/dev/dri/renderD128`.
2. **Виділення GEM-буфера**: виклик `DRM_IOCTL_MODE_CREATE_DUMB` для створення лінійного буфера роздільністю 640×480 пікселів у форматі 32-біт ARGB.
3. **Отримання фальшивого зміщення**: виклик `DRM_IOCTL_MODE_MAP_DUMB` для реєстрації діапазону в менеджері VMA ядра.
4. **Відображення в адресний простір**: виклик `mmap()` за отриманим зміщенням і заповнення буфера градієнтом.
5. **Експорт у PRIME fd**: конвертація локального числового хендла GEM у файловий дескриптор `dma-buf` через `DRM_IOCTL_PRIME_HANDLE_TO_FD`.
6. **Імпорт у вторинному контексті**: перевірка імпорту дескриптора через `DRM_IOCTL_PRIME_FD_TO_HANDLE` для емуляції міжпроцесного передавання кадру.
7. **Коректне очищення**: звільнення віртуальної пам'яті та деструкція буфера.

## Детальний розбір етапів взаємодії з ядром

Перед виконанням коду важливо розуміти, які трансформації відбуваються всередині ядра на кожному кроці:

* **Виділення пам'яті (`DRM_IOCTL_MODE_CREATE_DUMB`)**: драйвер обчислює мінімальний крок рядка (`pitch`), необхідний для апаратного блоку сканування дисплея (CRTC) або DMA-контролера. Наприклад, для 640 пікселів за глибини 32 біти мінімальна ширина рядка становить 2560 байтів. Якщо апаратний блок вимагає вирівнювання за межею 256 байтів, ядро залишає `pitch = 2560` (бо 2560 ділиться на 256 без залишку). Потім розмір множиться на висоту й округлюється вгору до розміру сторінки ядра (`PAGE_SIZE`, зазвичай 4096 байтів). Успішне виділення повертає локальний ідентифікатор `handle`.
* **Отримання зміщення (`DRM_IOCTL_MODE_MAP_DUMB`)**: оскільки системний виклик `mmap()` вимагає числового зміщення `offset`, ядро виділяє для цього буфера унікальний діапазон у внутрішньому адресному просторі менеджера `drm_vma_offset_manager`. Це число не є фізичною адресою в оперативній пам'яті чи на шині PCI, а слугує унікальним ключем пошуку в червоно-чорному дереві ядра.
* **Відображення сторінок (`mmap`)**: при виклику `mmap()` ядро створює структуру `vm_area_struct` у віртуальному адресному просторі процесу, прив'язуючи її до таблиці операцій `drm_gem_vm_ops`. Фізичні сторінки виділяються та мапуються в таблицю сторінок процесу лише тоді, коли процесор уперше звертається за адресою, викликаючи обробник сторінкового збою `fault()`.
* **Експорт дескриптора PRIME**: виклик `DRM_IOCTL_PRIME_HANDLE_TO_FD` створює в анонімній файловій системі `anon_inodefs` новий об'єкт `struct dma_buf`. Цей об'єкт отримує власне системне посилання на початковий GEM-буфер, що гарантує збереження пам'яті навіть у тому разі, якщо процес-творець передчасно закриє свій локальний числовий хендл.

## Реалізація на мовах C та C++

У реалізації на C керування пам'яттю та дескрипторами виконується вручну з перевіркою кожного коду помилки. У версії на C++ застосовано ідіому RAII (англ. *Resource Acquisition Is Initialization*), розумні обгортки над файловими дескрипторами та безпечний тип `std::span` для доступу до піксельних даних.

:::tabs
```c
/* gem_dumb_prime.c - Виділення та експорт GEM буфера мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

#define WIDTH  640
#define HEIGHT 480
#define BPP    32

int main(void)
{
    int drm_fd = -1;
    int prime_fd = -1;
    int client_fd = -1;
    uint8_t *map_ptr = MAP_FAILED;
    struct drm_mode_create_dumb create_req;
    struct drm_mode_map_dumb map_req;
    struct drm_mode_destroy_dumb destroy_req;
    struct drm_prime_handle prime_req;
    int ret = 0;

    /* 1. Відкриваємо основний пристрій DRM */
    drm_fd = open("/dev/dri/card0", O_RDWR | O_CLOEXEC);
    if (drm_fd < 0) {
        perror("Помилка відкриття /dev/dri/card0");
        return EXIT_FAILURE;
    }

    /* 2. Запитуємо створення лінійного dumb-буфера */
    memset(&create_req, 0, sizeof(create_req));
    create_req.width = WIDTH;
    create_req.height = HEIGHT;
    create_req.bpp = BPP;

    if (ioctl(drm_fd, DRM_IOCTL_MODE_CREATE_DUMB, &create_req) < 0) {
        perror("DRM_IOCTL_MODE_CREATE_DUMB завершився помилкою");
        ret = EXIT_FAILURE;
        goto cleanup_fd;
    }

    printf("[DRM] Створено GEM буфер: хендл=%u, розмір=%llu байтів, pitch=%u байтів\n",
           create_req.handle, (unsigned long long)create_req.size, create_req.pitch);

    /* 3. Отримуємо фальшиве зміщення (fake offset) для виклику mmap */
    memset(&map_req, 0, sizeof(map_req));
    map_req.handle = create_req.handle;

    if (ioctl(drm_fd, DRM_IOCTL_MODE_MAP_DUMB, &map_req) < 0) {
        perror("DRM_IOCTL_MODE_MAP_DUMB завершився помилкою");
        ret = EXIT_FAILURE;
        goto cleanup_buffer;
    }

    printf("[DRM] Отримано фальшиве зміщення ядра: 0x%llx\n",
           (unsigned long long)map_req.offset);

    /* 4. Відображаємо сторінки буфера в адресний простір процесу */
    map_ptr = (uint8_t *)mmap(NULL, create_req.size, PROT_READ | PROT_WRITE,
                              MAP_SHARED, drm_fd, (off_t)map_req.offset);
    if (map_ptr == MAP_FAILED) {
        perror("mmap завершився помилкою");
        ret = EXIT_FAILURE;
        goto cleanup_buffer;
    }

    /* 5. Заповнюємо буфер градієнтом (формат XRGB8888) */
    for (uint32_t y = 0; y < HEIGHT; ++y) {
        uint32_t *row = (uint32_t *)(map_ptr + y * create_req.pitch);
        for (uint32_t x = 0; x < WIDTH; ++x) {
            uint8_t r = (uint8_t)((x * 255) / WIDTH);
            uint8_t g = (uint8_t)((y * 255) / HEIGHT);
            uint8_t b = 128;
            row[x] = (0xFF << 24) | (r << 16) | (g << 8) | b;
        }
    }
    printf("[CPU] Буфер успішно заповнено графічним градієнтом.\n");

    /* 6. Експортуємо GEM-хендл у файловий дескриптор dma-buf (PRIME) */
    memset(&prime_req, 0, sizeof(prime_req));
    prime_req.handle = create_req.handle;
    prime_req.flags = DRM_CLOEXEC | DRM_RDWR;

    if (ioctl(drm_fd, DRM_IOCTL_PRIME_HANDLE_TO_FD, &prime_req) < 0) {
        perror("DRM_IOCTL_PRIME_HANDLE_TO_FD завершився помилкою");
        ret = EXIT_FAILURE;
        goto cleanup_mmap;
    }
    prime_fd = prime_req.fd;
    printf("[PRIME] Буфер експортовано в dma-buf fd=%d\n", prime_fd);

    /* 7. Емулюємо імпорт дескриптора у вторинному клієнтському контексті */
    client_fd = open("/dev/dri/card0", O_RDWR | O_CLOEXEC);
    if (client_fd >= 0) {
        struct drm_prime_handle import_req;
        memset(&import_req, 0, sizeof(import_req));
        import_req.fd = prime_fd;

        if (ioctl(client_fd, DRM_IOCTL_PRIME_FD_TO_HANDLE, &import_req) == 0) {
            printf("[Клієнт] Успішно імпортовано dma-buf: локальний хендл=%u\n",
                   import_req.handle);

            /* Закриваємо імпортований локальний хендл */
            struct drm_gem_close close_req = { .handle = import_req.handle, .pad = 0 };
            ioctl(client_fd, DRM_IOCTL_GEM_CLOSE, &close_req);
        }
        close(client_fd);
    }

cleanup_mmap:
    if (map_ptr != MAP_FAILED) {
        munmap(map_ptr, create_req.size);
    }
    if (prime_fd >= 0) {
        close(prime_fd);
    }

cleanup_buffer:
    memset(&destroy_req, 0, sizeof(destroy_req));
    destroy_req.handle = create_req.handle;
    if (ioctl(drm_fd, DRM_IOCTL_MODE_DESTROY_DUMB, &destroy_req) < 0) {
        perror("DRM_IOCTL_MODE_DESTROY_DUMB помилка");
    } else {
        printf("[DRM] Dumb-буфер успішно звільнено в ядрі.\n");
    }

cleanup_fd:
    close(drm_fd);
    return ret;
}
```
```cpp
// gem_dumb_prime.cpp - Виділення та експорт GEM буфера мовою C++
#include <iostream>
#include <memory>
#include <span>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

namespace drm {

// RAII обгортка для володіння файловим дескриптором
class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

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
    int fd_;
};

// RAII обгортка для GEM dumb-буфера
class DumbBuffer {
public:
    DumbBuffer(int drm_fd, uint32_t width, uint32_t height, uint32_t bpp)
        : drm_fd_(drm_fd), width_(width), height_(height)
    {
        struct drm_mode_create_dumb create_req{};
        create_req.width = width;
        create_req.height = height;
        create_req.bpp = bpp;

        if (::ioctl(drm_fd_, DRM_IOCTL_MODE_CREATE_DUMB, &create_req) < 0) {
            throw std::system_error(errno, std::generic_category(),
                                    "Не вдалося створити dumb буфер");
        }

        handle_ = create_req.handle;
        pitch_ = create_req.pitch;
        size_ = create_req.size;

        // Отримуємо фальшиве зміщення для mmap
        struct drm_mode_map_dumb map_req{};
        map_req.handle = handle_;
        if (::ioctl(drm_fd_, DRM_IOCTL_MODE_MAP_DUMB, &map_req) < 0) {
            cleanup();
            throw std::system_error(errno, std::generic_category(),
                                    "Не вдалося отримати fake offset");
        }

        void* ptr = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE,
                           MAP_SHARED, drm_fd_, static_cast<off_t>(map_req.offset));
        if (ptr == MAP_FAILED) {
            cleanup();
            throw std::system_error(errno, std::generic_category(),
                                    "Помилка mmap буфера");
        }
        data_ = static_cast<uint8_t*>(ptr);
    }

    ~DumbBuffer() noexcept {
        cleanup();
    }

    DumbBuffer(const DumbBuffer&) = delete;
    DumbBuffer& operator=(const DumbBuffer&) = delete;

    DumbBuffer(DumbBuffer&& other) noexcept
        : drm_fd_(other.drm_fd_), handle_(other.handle_),
          pitch_(other.pitch_), size_(other.size_),
          width_(other.width_), height_(other.height_),
          data_(other.data_)
    {
        other.handle_ = 0;
        other.data_ = nullptr;
    }

    [[nodiscard]] uint32_t handle() const noexcept { return handle_; }
    [[nodiscard]] uint32_t pitch() const noexcept { return pitch_; }
    [[nodiscard]] uint64_t size() const noexcept { return size_; }
    [[nodiscard]] uint32_t width() const noexcept { return width_; }
    [[nodiscard]] uint32_t height() const noexcept { return height_; }

    [[nodiscard]] std::span<uint8_t> bytes() noexcept {
        return {data_, static_cast<std::size_t>(size_)};
    }

    [[nodiscard]] UniqueFd export_prime_fd() const {
        struct drm_prime_handle prime_req{};
        prime_req.handle = handle_;
        prime_req.flags = DRM_CLOEXEC | DRM_RDWR;

        if (::ioctl(drm_fd_, DRM_IOCTL_PRIME_HANDLE_TO_FD, &prime_req) < 0) {
            throw std::system_error(errno, std::generic_category(),
                                    "Помилка експорту в PRIME dma-buf");
        }
        return UniqueFd(prime_req.fd);
    }

    void render_gradient() {
        for (uint32_t y = 0; y < height_; ++y) {
            auto* row = reinterpret_cast<uint32_t*>(data_ + y * pitch_);
            for (uint32_t x = 0; x < width_; ++x) {
                uint8_t r = static_cast<uint8_t>((x * 255) / width_);
                uint8_t g = static_cast<uint8_t>((y * 255) / height_);
                uint8_t b = 128;
                row[x] = (0xFF << 24) | (r << 16) | (g << 8) | b;
            }
        }
    }

private:
    void cleanup() noexcept {
        if (data_ && data_ != MAP_FAILED) {
            ::munmap(data_, size_);
            data_ = nullptr;
        }
        if (handle_ != 0) {
            struct drm_mode_destroy_dumb destroy_req{};
            destroy_req.handle = handle_;
            ::ioctl(drm_fd_, DRM_IOCTL_MODE_DESTROY_DUMB, &destroy_req);
            handle_ = 0;
        }
    }

    int drm_fd_{-1};
    uint32_t handle_{0};
    uint32_t pitch_{0};
    uint64_t size_{0};
    uint32_t width_{0};
    uint32_t height_{0};
    uint8_t* data_{nullptr};
};

} // namespace drm

int main() {
    try {
        drm::UniqueFd drm_device(::open("/dev/dri/card0", O_RDWR | O_CLOEXEC));
        if (!drm_device.valid()) {
            throw std::system_error(errno, std::generic_category(),
                                    "Не вдалося відкрити /dev/dri/card0");
        }

        std::cout << "[DRM] Відкрито графічний пристрій\n";

        // Створюємо та відображаємо буфер 640x480
        drm::DumbBuffer buffer(drm_device.get(), 640, 480, 32);
        std::cout << "[DRM] Створено буфер: хендл=" << buffer.handle()
                  << ", pitch=" << buffer.pitch()
                  << ", розмір=" << buffer.size() << " байтів\n";

        // Малюємо тестовий візерунок
        buffer.render_gradient();
        std::cout << "[CPU] Візерунок згенеровано через std::span\n";

        // Експортуємо дескриптор dma-buf для передавання через IPC
        drm::UniqueFd prime_fd = buffer.export_prime_fd();
        std::cout << "[PRIME] dma-buf експортовано успішно, fd=" << prime_fd.get() << "\n";

        // Тестуємо імпорт у новому дескрипторі
        drm::UniqueFd client_device(::open("/dev/dri/card0", O_RDWR | O_CLOEXEC));
        if (client_device.valid()) {
            struct drm_prime_handle import_req{};
            import_req.fd = prime_fd.get();

            if (::ioctl(client_device.get(), DRM_IOCTL_PRIME_FD_TO_HANDLE, &import_req) == 0) {
                std::cout << "[Клієнт] Імпортовано буфер: новий локальний хендл="
                          << import_req.handle << "\n";

                struct drm_gem_close close_req{.handle = import_req.handle, .pad = 0};
                ::ioctl(client_device.get(), DRM_IOCTL_GEM_CLOSE, &close_req);
            }
        }

        std::cout << "[Завершення] Усі ресурси автоматично звільняються RAII деструкторами.\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## Ключові підводні камені та особливості архітектури

При практичній роботі з відображеними GEM-буферами слід враховувати такі апаратні та системні фактори:

1. **Вирівнювання довжини рядка (stride/pitch)**: розмір рядка пікселів у байтах майже ніколи не дорівнює `width * (bpp / 8)`. Апаратні контролери вимагають вирівнювання за межами 64, 128 або 256 байтів для ефективної роботи каналів DMA. Прямий розрахунок індексу `ptr[y * width + x]` призведе до спотворення зображення (зсуву та нахилу рядків). Необхідно завжди використовувати значення `pitch`, повернене ядром.
2. **Тип кешування пам'яті (Write-Combining)**: пам'ять dumb-буферів відображається ядром з атрибутами Write-Combining (WC, прапорець `pgprot_writecombine`). Запис даних процесором у таку пам'ять буферизується у внутрішніх буферах скидання (англ. *write-combining fill buffers*) і скидається широкими пачками по 64 байти, що забезпечує максимальну пропускну здатність шини. Проте читання здійснюється в обхід L1/L2 кешів процесора — кожне звернення до пікселя вимагає окремої транзакції на системній шині та може бути у 50–100 разів повільнішим за звичайну системну пам'ять. Програмні операції альфа-змішування (alpha-blending) або фільтрації безпосередньо в dumb-буфері створюють критичне падіння швидкодії. Якщо читання необхідне, операції слід виконувати в окремому проміжному буфері системного ОЗП, а фінальний результат копіювати в GEM-буфер суто лінійним записом.
3. **Обмеження dumb-буферів**: механізм призначений виключно для невимогливих лінійних буферів сканування екрана (курсори миші, тестові фреймбуфери, сплеш-скріни завантаження). Він не підтримує апаратний тайлінг (tiled layout), стиснення пам'яті без втрат (наприклад, Intel DCC або AMD DCC) та виділення виділеної відеопам'яті GDDR6. Для високопродуктивного 3D-рендерингу слід використовувати драйверо-специфічні виклики виділення пам'яті через Vulkan або Generic Buffer Management (GBM).
4. **Передавання через IPC**: у реальних графічних системах (наприклад, Wayland) отриманий дескриптор `prime_fd` передається композитору через локальний доменний UNIX-сокет за допомогою допоміжного повідомлення керування `sendmsg()` з атрибутом `SCM_RIGHTS`. Це дозволяє композитору викликати `DRM_IOCTL_PRIME_FD_TO_HANDLE`, зв'язати отриманий GEM-хендл із площиною відображення через виклик `drmModeAddFB2()` та передати буфер на пряме апаратне сканування контролером екрана без жодного копіювання байтів пам'яті.
