# ⚙️ Створення тайлованого буфера GBM, експорт dma-buf та імпорт у KMS FB2

У сучасному графічному стеку Linux створення кадрового буфера з апаратним тайлінгом та передавання його дисплейному контролеру вимагає узгодженої взаємодії трьох ключових рівнів архітектури:

1. **Generic Buffer Management (GBM / Mesa):** простір користувача запитує виділення відеопам'яті у графічного процесора, передаючи список бажаних 64-бітних модифікаторів DRM (наприклад, Intel Tile4, Y-Tile або резервний `DRM_FORMAT_MOD_LINEAR`). Драйвер GPU обирає найбільш енергоефективний та швидкісний варіант серед тих, які підтримуються апаратно.
2. **Експорт дескрипторів dma-buf:** для кожної логічної площини (пікселі основного кольору, допоміжні метадані стиснення CCS/DCC, теги швидкого очищення) драйвер повертає файловий дескриптор [dma-buf](root:sys-unix/dma-buf), крок рядка (stride / pitch) та зміщення в байтах від початку буфера.
3. **Імпорт у конвеєр відображення DRM KMS:** композитор викликає системний виклик `DRM_IOCTL_MODE_ADDFB2` із прапорцем `DRM_MODE_FB_MODIFIERS`, реєструючи єдиний об'єкт `drmModeFB` для безпосереднього апаратного сканування дисплейною площиною.

## Повний алгоритм роботи конвеєра

Перед тим як виділяти пам'ять, композитор або програма перегляду має з'ясувати, які саме розкладки пам'яті здатен прочитати апаратний дисплейний контролер. Для цього зчитується властивість `IN_FORMATS` відповідної площини KMS. Отриманий масив 64-бітних модифікаторів передається у функцію виділення пам'яті `gbm_bo_create_with_modifiers2()`.

Графічний процесор резервує область у відеопам'яті (VRAM або системному ОЗП через IOMMU), розбиває її на тайли згідно з обраним модифікатором і за потреби ініціалізує службову область метаданих стиснення. Наступним кроком простір користувача отримує опис кожної площини через API бібліотеки GBM та конвертує дескриптори `dma-buf` у локальні числові хендли GEM ядра.

Нижче наведено робочий приклад повного циклу: від виділення тайлованого буфера в GPU до його реєстрації у підсистемі KMS.

:::tabs
```c
/* gbm-kms-pipeline.c — виділення буфера з модифікаторами та імпорт у KMS */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <gbm.h>
#include <drm_fourcc.h>

/* Структура для зберігання зареєстрованого кадрового буфера KMS */
struct kms_framebuffer {
    uint32_t fb_id;
    uint32_t width;
    uint32_t height;
    uint32_t format;
    uint64_t modifier;
    int plane_fds[4];
    uint32_t plane_count;
};

/* Створення буфера через GBM та імпорт у KMS */
int create_tiled_kms_fb(int drm_fd, struct gbm_device *gbm,
                        uint32_t width, uint32_t height,
                        uint32_t format, const uint64_t *modifiers,
                        uint32_t mod_count, struct kms_framebuffer *out_fb)
{
    if (!gbm || !modifiers || mod_count == 0 || !out_fb) {
        return -EINVAL;
    }

    memset(out_fb, 0, sizeof(*out_fb));
    for (int i = 0; i < 4; i++) {
        out_fb->plane_fds[i] = -1;
    }

    /* 1. Виділення буфера в GPU з переліком дозволених модифікаторів */
    struct gbm_bo *bo = gbm_bo_create_with_modifiers2(
        gbm, width, height, format, modifiers, mod_count,
        GBM_BO_USE_RENDERING | GBM_BO_USE_SCANOUT
    );

    if (!bo) {
        fprintf(stderr, "Помилка gbm_bo_create_with_modifiers2: %s\n", strerror(errno));
        return -errno;
    }

    uint64_t chosen_mod = gbm_bo_get_modifier(bo);
    int plane_count = gbm_bo_get_plane_count(bo);
    if (plane_count <= 0 || plane_count > 4) {
        fprintf(stderr, "Некоректна кількість площин буфера: %d\n", plane_count);
        gbm_bo_destroy(bo);
        return -EINVAL;
    }

    uint32_t handles[4] = {0};
    uint32_t strides[4] = {0};
    uint32_t offsets[4] = {0};
    uint64_t mods[4] = {0};

    /* 2. Отримання дескрипторів dma-buf та геометрії для кожної площини */
    for (int p = 0; p < plane_count; p++) {
        int fd = gbm_bo_get_fd_for_plane(bo, p);
        if (fd < 0) {
            fprintf(stderr, "Помилка експорту dma-buf для площини %d: %s\n", p, strerror(errno));
            for (int i = 0; i < p; i++) {
                if (out_fb->plane_fds[i] >= 0) close(out_fb->plane_fds[i]);
            }
            gbm_bo_destroy(bo);
            return -errno;
        }

        out_fb->plane_fds[p] = fd;
        strides[p] = gbm_bo_get_stride_for_plane(bo, p);
        offsets[p] = gbm_bo_get_offset(bo, p);
        mods[p] = chosen_mod;

        /* Імпорт dma-buf FD як GEM-хендлу для цього пристрою DRM */
        int ret = drmPrimeFDToHandle(drm_fd, fd, &handles[p]);
        if (ret < 0) {
            fprintf(stderr, "Помилка drmPrimeFDToHandle для площини %d: %s\n", p, strerror(errno));
            for (int i = 0; i <= p; i++) {
                if (out_fb->plane_fds[i] >= 0) close(out_fb->plane_fds[i]);
            }
            gbm_bo_destroy(bo);
            return ret;
        }
    }

    /* 3. Реєстрація кадрового буфера у KMS з явними модифікаторами */
    uint32_t fb_id = 0;
    int ret = drmModeAddFB2WithModifiers(
        drm_fd, width, height, format,
        handles, strides, offsets, mods,
        &fb_id, DRM_MODE_FB_MODIFIERS
    );

    /* Закриваємо локальні GEM-хендли (KMS FB утримує власні посилання ядра) */
    for (int p = 0; p < plane_count; p++) {
        struct drm_gem_close req = { .handle = handles[p] };
        drmIoctl(drm_fd, DRM_IOCTL_GEM_CLOSE, &req);
    }

    if (ret < 0) {
        fprintf(stderr, "Помилка drmModeAddFB2WithModifiers: %s (код %d)\n", strerror(errno), ret);
        for (int p = 0; p < plane_count; p++) {
            if (out_fb->plane_fds[p] >= 0) close(out_fb->plane_fds[p]);
        }
        gbm_bo_destroy(bo);
        return ret;
    }

    /* Зберігаємо результати у вихідну структуру */
    out_fb->fb_id = fb_id;
    out_fb->width = width;
    out_fb->height = height;
    out_fb->format = format;
    out_fb->modifier = chosen_mod;
    out_fb->plane_count = plane_count;

    printf("Створено KMS FB #%u: %ux%u, format=0x%08x, mod=0x%016" PRIx64 ", площин=%u\n",
           fb_id, width, height, format, chosen_mod, plane_count);

    /* Звільняємо тимчасовий об'єкт GBM (буфер утримується через dma-buf та KMS FB) */
    gbm_bo_destroy(bo);
    return 0;
}

/* Звільнення кадрового буфера */
void free_kms_fb(int drm_fd, struct kms_framebuffer *fb)
{
    if (!fb || fb->fb_id == 0) return;

    drmModeRmFB(drm_fd, fb->fb_id);
    for (uint32_t i = 0; i < fb->plane_count; i++) {
        if (fb->plane_fds[i] >= 0) {
            close(fb->plane_fds[i]);
            fb->plane_fds[i] = -1;
        }
    }
    fb->fb_id = 0;
}
```
```cpp
// gbm-kms-pipeline.cpp — ідіоматичний конвеєр виділення з RAII та std::span
#include <cerrno>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <inttypes.h>
#include <iostream>
#include <memory>
#include <span>
#include <string>
#include <system_error>
#include <vector>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <gbm.h>
#include <drm_fourcc.h>

namespace drm {

// RAII обгортка для файлового дескриптора
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

// RAII обгортка для буферного об'єкта GBM
struct GbmBoDeleter {
    void operator()(gbm_bo* bo) const noexcept {
        if (bo) gbm_bo_destroy(bo);
    }
};
using UniqueGbmBo = std::unique_ptr<gbm_bo, GbmBoDeleter>;

// Клас кадрового буфера KMS з автоматичним видаленням
class KmsFramebuffer {
public:
    KmsFramebuffer(int drm_fd, uint32_t fb_id, uint32_t width, uint32_t height,
                   uint32_t format, uint64_t modifier, std::vector<UniqueFd> plane_fds)
        : drm_fd_(drm_fd), fb_id_(fb_id), width_(width), height_(height),
          format_(format), modifier_(modifier), plane_fds_(std::move(plane_fds)) {}

    ~KmsFramebuffer() noexcept {
        if (fb_id_ != 0 && drm_fd_ >= 0) {
            drmModeRmFB(drm_fd_, fb_id_);
        }
    }

    KmsFramebuffer(const KmsFramebuffer&) = delete;
    KmsFramebuffer& operator=(const KmsFramebuffer&) = delete;
    KmsFramebuffer(KmsFramebuffer&&) noexcept = default;
    KmsFramebuffer& operator=(KmsFramebuffer&&) noexcept = default;

    [[nodiscard]] uint32_t id() const noexcept { return fb_id_; }
    [[nodiscard]] uint32_t width() const noexcept { return width_; }
    [[nodiscard]] uint32_t height() const noexcept { return height_; }
    [[nodiscard]] uint32_t format() const noexcept { return format_; }
    [[nodiscard]] uint64_t modifier() const noexcept { return modifier_; }

    // Фабричний метод виділення буфера
    static std::unique_ptr<KmsFramebuffer> create(
        int drm_fd, gbm_device* gbm, uint32_t width, uint32_t height,
        uint32_t format, std::span<const uint64_t> modifiers)
    {
        if (!gbm || modifiers.empty()) {
            throw std::invalid_argument("Некоректні параметри GBM або порожній список модифікаторів");
        }

        // 1. Створення буфера з модифікаторами через GBM
        UniqueGbmBo bo(gbm_bo_create_with_modifiers2(
            gbm, width, height, format, modifiers.data(),
            static_cast<uint32_t>(modifiers.size()),
            GBM_BO_USE_RENDERING | GBM_BO_USE_SCANOUT
        ));

        if (!bo) {
            throw std::system_error(errno, std::generic_category(), "gbm_bo_create_with_modifiers2 не вдався");
        }

        const uint64_t chosen_mod = gbm_bo_get_modifier(bo.get());
        const int plane_count = gbm_bo_get_plane_count(bo.get());
        if (plane_count <= 0 || plane_count > 4) {
            throw std::runtime_error("Некоректна кількість площин: " + std::to_string(plane_count));
        }

        uint32_t handles[4] = {0};
        uint32_t strides[4] = {0};
        uint32_t offsets[4] = {0};
        uint64_t mods[4] = {0};
        std::vector<UniqueFd> plane_fds;
        plane_fds.reserve(plane_count);

        // 2. Експорт кожної площини
        for (int p = 0; p < plane_count; ++p) {
            int fd = gbm_bo_get_fd_for_plane(bo.get(), p);
            if (fd < 0) {
                throw std::system_error(errno, std::generic_category(), "gbm_bo_get_fd_for_plane помилка");
            }
            plane_fds.emplace_back(fd);

            strides[p] = gbm_bo_get_stride_for_plane(bo.get(), p);
            offsets[p] = gbm_bo_get_offset(bo.get(), p);
            mods[p] = chosen_mod;

            int ret = drmPrimeFDToHandle(drm_fd, fd, &handles[p]);
            if (ret < 0) {
                throw std::system_error(-ret, std::generic_category(), "drmPrimeFDToHandle помилка");
            }
        }

        // 3. Реєстрація у KMS
        uint32_t fb_id = 0;
        int ret = drmModeAddFB2WithModifiers(
            drm_fd, width, height, format,
            handles, strides, offsets, mods,
            &fb_id, DRM_MODE_FB_MODIFIERS
        );

        // Закриття локальних хендлів GEM
        for (int p = 0; p < plane_count; ++p) {
            drm_gem_close req{ .handle = handles[p] };
            drmIoctl(drm_fd, DRM_IOCTL_GEM_CLOSE, &req);
        }

        if (ret < 0) {
            throw std::system_error(-ret, std::generic_category(), "drmModeAddFB2WithModifiers помилка");
        }

        std::cout << "KMS Framebuffer створено успішно: ID=" << fb_id
                  << ", Mod=0x" << std::hex << chosen_mod << std::dec
                  << ", Planes=" << plane_count << "\n";

        return std::make_unique<KmsFramebuffer>(
            drm_fd, fb_id, width, height, format, chosen_mod, std::move(plane_fds)
        );
    }

private:
    int drm_fd_{-1};
    uint32_t fb_id_{0};
    uint32_t width_{0};
    uint32_t height_{0};
    uint32_t format_{0};
    uint64_t modifier_{DRM_FORMAT_MOD_INVALID};
    std::vector<UniqueFd> plane_fds_;
};

} // namespace drm
```
:::

## Що відбувається всередині ядра при виклику AddFB2

Коли простір користувача передає структуру `drm_mode_fb_cmd2` у системний виклик `DRM_IOCTL_MODE_ADDFB2`, підсистема ядра DRM KMS виконує сувору багатоступеневу верифікацію:

1. **Перевірка формату та прапорців:** ядро переконується, що переданий FourCC зареєстровано у глобальній таблиці форматів ядра (`drm_fourcc.c`). Якщо встановлено прапорець `DRM_MODE_FB_MODIFIERS`, ядро вимагає, щоб усі задіяні площини мали валідні значення модифікаторів (значення `DRM_FORMAT_MOD_INVALID` у цьому виклику заборонене).
2. **Пошук GEM-об'єктів за хендлами:** ядро перетворює числові значення `handles[p]` у покажчики на внутрішні структури `struct drm_gem_object`. Для кожної площини перевіряється, чи належить GEM-об'єкт поточному файловому дескриптору процесу та чи достатній його фізичний розмір для розміщення площини із заданим кроком `pitches[p]` та зміщенням `offsets[p]`.
3. **Виклик драйверо-специфічного конструктора:** ядро передає команду у зворотний виклик драйвера відеокарти (наприклад, `intel_user_framebuffer_create` у драйвері i915/Xe або `amdgpu_display_user_framebuffer_create` у amdgpu). Драйвер виконує апаратну перевірку:
   * Чи підтримує графічний чип саме цей модифікатор (наприклад, чи не намагається користувач виділити Intel Tile4 на старій архітектурі Skylake, де підтримується максимум Y-Tile).
   * Чи відповідає вирівнювання зміщень та кроку вимогам апаратного блоку сканування (наприклад, крок тайла Tile4 має бути строго кратним 512 байтам, а зміщення площини метаданих CCS — кратним 4096 байтам).
4. **Створення екземпляра `struct drm_framebuffer`:** ядро створює довгоживучий об'єкт кадрового буфера, інкрементує лічильники посилань на відповідні GEM-об'єкти та повертає простору користувача унікальний числовий ідентифікатор `fb_id`.

## Підводні камені та практичні пастки

1. **Час життя файлових дескрипторів та GEM-хендлів:**
   * Виклик `drmPrimeFDToHandle()` створює локальний GEM-хендл у файловому описі DRM. Після того, як `drmModeAddFB2WithModifiers()` успішно повертає `fb_id`, сам об'єкт кадрового буфера ядра збільшує лічильник посилань на відповідні об'єкти пам'яті.
   * Простір користувача **зобов'язаний** закрити тимчасові хендли викликом `DRM_IOCTL_GEM_CLOSE`, інакше у системі виникне витік хендлів ядра (handle leak). Таблиця хендлів процесу в ядрі обмежена, і її переповнення призведе до помилок `-ENOSPC` у наступних графічних викликах.
   * Водночас файлові дескриптори `plane_fds` можна або закрити одразу, або зберегти (наприклад, якщо композитор планує передати їх іншому процесу через сокет домену Unix за протоколом Wayland).

2. **Один спільний dma-buf проти кількох фізичних файлів:**
   * Для буферів із допоміжними площинами стиснення (як-от Intel CCS чи AMD DCC) функція `gbm_bo_get_fd_for_plane(bo, 0)` та `gbm_bo_get_fd_for_plane(bo, 1)` найчастіше повертають два **незалежні файлові дескриптори**, які насправді посилаються на один і той самий анонімний об'єкт `struct dma_buf` у ядрі, але мають різні зміщення `offsets[p]`.
   * Кожен із цих числових дескрипторів є окремим записом у таблиці дескрипторів процесу, тому закривати їх потрібно окремо. Некоректне закриття лише нульового дескриптора залишає відкритими дескриптори допоміжних площин.

3. **Попередня перевірка через атомарний тестовий комміт:**
   * Навіть якщо ядро успішно виконало `drmModeAddFB2WithModifiers`, це не гарантує, що конкретна апаратна площина CRTC здатна показати цей буфер за поточної тактової частоти піксельного генератора (dotclock), поточної глибини кольору чи активного апаратного масштабування.
   * Перед виведенням на екран надійний композитор виконує тестовий виклик `drmModeAtomicCommit()` із прапорцем `DRM_MODE_ATOMIC_TEST_ONLY`. Якщо повертається `-EINVAL` або `-ERANGE`, композитор миттєво перемикається на програмне або GPU-компонування кадру без візуального мерехтіння дисплея.

4. **Прямий доступ центрального процесора (CPU mmap):**
   * Якщо програма спробує відобразити виділений буфер у свій адресний простір через `mmap()` на дескриптор `dma-buf`, процесор отримає прямий доступ до фізичних сторінок пам'яті.
   * Для лінійного модифікатора `DRM_FORMAT_MOD_LINEAR` процесор може читати й записувати пікселі як стандартний двовимірний масив.
   * Проте для будь-якого тайлованого чи стисненого модифікатора (наприклад, Intel Tile4 або Arm AFBC) байти в пам'яті фізично перемішані. Спроба записати туди пікселі процесором напряму призведе до повного руйнування зображення, оскільки CPU не має апаратного блоку детайлінгу (англ. *detiling engine*). Для модифікованих буферів запис здійснюється виключно через графічні API (Vulkan, OpenGL, EGL) або за допомогою апаратного блітера ядра.
