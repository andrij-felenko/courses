# ⚙️ Реалізація атомарного подвійного буферизатора (Page Flip) через libdrm

Цей проєкт демонструє побудову мінімального апаратного рендерера та подвійного буферизатора (Double Buffer Page Flip) у просторі користувача без використання графічних серверів X11 чи Wayland (Direct Scanout / Bare-Metal Graphics). Програма відкриває пристрій DRM, увімкне розширені атомні можливості ядра, шукає активний конектор та CRTC, виділяє два тупих буфери (Dumb Buffers) у відеопам'яті та здійснює плавне атомарне перемикання кадрів на частоті оновлення монітора через асинхронні виклики Atomic KMS.

---

## 1. Архітектурний задум та підготовка середовища

Для запуску коду необхідний доступ до пристрою `/dev/dri/card0` з правами читання та запису (зазвичай через членство у системній групі `video` або `render`), а також відсутність активного графічного сервера (X11 чи Wayland), який монополізує статус DRM Master.

Програма виконує послідовну підсистему дій:

1. **Ініціалізація та CAP:** Відкрити файл пристрою `/dev/dri/card0`, увімкнути атомні можливості ядра через `DRM_CLIENT_CAP_ATOMIC` та універсальні площини `DRM_CLIENT_CAP_UNIVERSAL_PLANES`.
2. **Інспекція конвеєра (Resource Discovery):** Перебрати доступні конектори, обрати перший підключений монітор, знайти прив'язаний CRTC та відповідну Primary Plane.
3. **Алокація Dumb-буферів:** Викликати `DRM_IOCTL_MODE_CREATE_DUMB` для виділення двох кадрових буферів у пам'яті, відобразити їх у простір процесу через `mmap()` та зареєструвати у KMS через `drmModeAddFB2`.
4. **Кешування властивостей (Property Discovery):** Зчитати ідентифікатори властивостей `FB_ID`, `CRTC_ID`, `CRTC_X/Y/W/H`, `SRC_X/Y/W/H` для обраної площини.
5. **Формування та перевірка транзакції:** Заповнити об'єкт `drmModeAtomicReq` накопиченими змінами. Виконати валідацію через `DRM_MODE_ATOMIC_TEST_ONLY`.
6. **Асинхронний атомарний цикл:** Запустити неблокуючі коміти `DRM_MODE_ATOMIC_NONBLOCK | DRM_MODE_PAGE_FLIP_EVENT`, очікувати події VBlank через `poll()` у циклі та чергувати буфери.

---

## 2. Аналіз внутрішніх структур даних проєкту

У реалізації використовуються дві ключові структури простору користувача:

1. `struct buffer_t`: Описує кадровий буфер у пам'яті. Вона зберігає геометрію (`width`, `height`), вирівнювання рядка (`pitch`), апаратний хендл пам'яті (`handle`), ідентифікатор фреймбуфера у ядрі (`fb_id`), розмір у байтах (`size`) та вказівник на відображену пам'ять процесу (`vaddr`).
2. `struct kms_context`: Описує стан конвеєра відображення. Зберігає файловий дескриптор пристрою (`fd`), ідентифікатори об'єктів KMS (`conn_id`, `crtc_id`, `plane_id`), зчитані ID властивостей (`prop_fb_id`, `prop_crtc_id` тощо), масив із двох буферів `buffers[2]`, прапорець активного буфера та стан очікування VBlank (`waiting_for_flip`).

---

## 3. Поклітинна ініціалізація та пошук об'єктів у C

Функція `get_property_id()` використовує виклики `drmModeObjectGetProperties()` та `drmModeGetProperty()`, перебираючи масив властивостей об'єкта DRM і зіставляючи текстові імена (наприклад, `"FB_ID"` або `"CRTC_ID"`) з їхніми динамічними числовими ідентифікаторами у ядрі.

Функція `create_dumb_buffer()` здійснює створення буфера через три системні виклики:
- `DRM_IOCTL_MODE_CREATE_DUMB`: Виділяє необхідний обсяг непоперервної пам'яті у GPU/RAM та повертає `handle` і розрахований `pitch` (крок рядка з урахуванням вирівнювання);
- `drmModeAddFB()`: Зареєструє GEM-хендл як кадровий буфер KMS з поверненням `fb_id`;
- `DRM_IOCTL_MODE_MAP_DUMB` та `mmap()`: Отримує зсув у системному файлі пристрою та відображає відеопам'ять у віртуальний адресний простір процесу.

---

## 4. Реалізація коду (C та C++)

:::tabs
```c
/* C Implementation: Atomic KMS Double Buffer Page Flip */
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <poll.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

struct buffer_t {
    uint32_t width;
    uint32_t height;
    uint32_t pitch;
    uint32_t handle;
    uint32_t size;
    uint32_t fb_id;
    uint32_t *vaddr;
};

struct kms_context {
    int fd;
    uint32_t conn_id;
    uint32_t crtc_id;
    uint32_t plane_id;
    uint32_t crtc_index;
    drmModeModeInfo mode;
    
    uint32_t prop_fb_id;
    uint32_t prop_crtc_id;
    uint32_t prop_crtc_w;
    uint32_t prop_crtc_h;
    uint32_t prop_src_w;
    uint32_t prop_src_h;
    
    struct buffer_t buffers[2];
    int current_buf;
    int waiting_for_flip;
};

static uint32_t get_property_id(int fd, uint32_t obj_id, uint32_t obj_type, const char *name) {
    drmModeObjectPropertiesPtr props = drmModeObjectGetProperties(fd, obj_id, obj_type);
    if (!props) return 0;
    
    uint32_t prop_id = 0;
    for (uint32_t i = 0; i < props->count_props; i++) {
        drmModePropertyPtr prop = drmModeGetProperty(fd, props->props[i]);
        if (prop) {
            if (strcmp(prop->name, name) == 0) {
                prop_id = prop->prop_id;
                drmModeFreeProperty(prop);
                break;
            }
            drmModeFreeProperty(prop);
        }
    }
    drmModeFreeObjectProperties(props);
    return prop_id;
}

static int create_dumb_buffer(int fd, struct buffer_t *buf, uint32_t width, uint32_t height) {
    struct drm_mode_create_dumb creq = {
        .width = width,
        .height = height,
        .bpp = 32
    };
    if (drmIoctl(fd, DRM_IOCTL_MODE_CREATE_DUMB, &creq) < 0) return -1;

    buf->width = width;
    buf->height = height;
    buf->pitch = creq.pitch;
    buf->handle = creq.handle;
    buf->size = creq.size;

    if (drmModeAddFB(fd, width, height, 24, 32, buf->pitch, buf->handle, &buf->fb_id) < 0) return -1;

    struct drm_mode_map_dumb mreq = { .handle = buf->handle };
    if (drmIoctl(fd, DRM_IOCTL_MODE_MAP_DUMB, &mreq) < 0) return -1;

    buf->vaddr = mmap(NULL, buf->size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, mreq.offset);
    if (buf->vaddr == MAP_FAILED) return -1;

    return 0;
}

static void page_flip_cb(int fd, unsigned int seq, unsigned int tv_sec, unsigned int tv_usec, unsigned int crtc_id, void *data) {
    struct kms_context *ctx = (struct kms_context *)data;
    ctx->waiting_for_flip = 0;
}

int main(void) {
    struct kms_context ctx = {0};
    ctx.fd = open("/dev/dri/card0", O_RDWR | O_CLOEXEC);
    if (ctx.fd < 0) {
        perror("Не вдалося відкрити /dev/dri/card0");
        return 1;
    }

    /* Обов'язкове включення Atomic та Universal Planes capabilities */
    if (drmSetClientCap(ctx.fd, DRM_CLIENT_CAP_ATOMIC, 1) != 0 ||
        drmSetClientCap(ctx.fd, DRM_CLIENT_CAP_UNIVERSAL_PLANES, 1) != 0) {
        fprintf(stderr, "Atomic KMS не підтримується ядерним драйвером\n");
        close(ctx.fd);
        return 1;
    }

    drmModeResPtr res = drmModeGetResources(ctx.fd);
    drmModeConnectorPtr conn = NULL;
    for (int i = 0; i < res->count_connectors; i++) {
        conn = drmModeGetConnector(ctx.fd, res->connectors[i]);
        if (conn && conn->connection == DRM_MODE_CONNECTED && conn->count_modes > 0) {
            ctx.conn_id = conn->connector_id;
            ctx.mode = conn->modes[0]; // Обираємо перший відданий монітором режим
            break;
        }
        if (conn) drmModeFreeConnector(conn);
    }

    if (!ctx.conn_id) {
        fprintf(stderr, "Підключених моніторів не знайдено\n");
        return 1;
    }

    ctx.crtc_id = res->crtcs[0];
    ctx.crtc_index = 0;
    drmModeFreeResources(res);

    drmModePlaneResPtr planes = drmModeGetPlaneResources(ctx.fd);
    for (uint32_t i = 0; i < planes->count_planes; i++) {
        drmModePlanePtr plane = drmModeGetPlane(ctx.fd, planes->planes[i]);
        if (plane && (plane->possible_crtcs & (1 << ctx.crtc_index))) {
            ctx.plane_id = plane->plane_id;
            drmModeFreePlane(plane);
            break;
        }
        if (plane) drmModeFreePlane(plane);
    }
    drmModeFreePlaneResources(planes);

    /* Зчитування ID властивостей для об'єкта Plane */
    ctx.prop_fb_id   = get_property_id(ctx.fd, ctx.plane_id, DRM_MODE_OBJECT_PLANE, "FB_ID");
    ctx.prop_crtc_id = get_property_id(ctx.fd, ctx.plane_id, DRM_MODE_OBJECT_PLANE, "CRTC_ID");
    ctx.prop_crtc_w  = get_property_id(ctx.fd, ctx.plane_id, DRM_MODE_OBJECT_PLANE, "CRTC_W");
    ctx.prop_crtc_h  = get_property_id(ctx.fd, ctx.plane_id, DRM_MODE_OBJECT_PLANE, "CRTC_H");
    ctx.prop_src_w   = get_property_id(ctx.fd, ctx.plane_id, DRM_MODE_OBJECT_PLANE, "SRC_W");
    ctx.prop_src_h   = get_property_id(ctx.fd, ctx.plane_id, DRM_MODE_OBJECT_PLANE, "SRC_H");

    /* Створення двох Dumb-буферів під розмір відеорежиму */
    create_dumb_buffer(ctx.fd, &ctx.buffers[0], ctx.mode.hdisplay, ctx.mode.vdisplay);
    create_dumb_buffer(ctx.fd, &ctx.buffers[1], ctx.mode.hdisplay, ctx.mode.vdisplay);

    /* Заповнення буферів тестовими кольорами */
    memset(ctx.buffers[0].vaddr, 0xFF, ctx.buffers[0].size); // Білий кадр
    memset(ctx.buffers[1].vaddr, 0x7F, ctx.buffers[1].size); // Сірий кадр

    drmEventContext evctx = {
        .version = DRM_EVENT_CONTEXT_VERSION,
        .page_flip_handler2 = page_flip_cb
    };

    /* Основний асинхронний цикл перемикання кадрів (300 кадрів) */
    for (int frame = 0; frame < 300; frame++) {
        ctx.current_buf ^= 1;
        struct buffer_t *buf = &ctx.buffers[ctx.current_buf];

        drmModeAtomicReqPtr req = drmModeAtomicAlloc();
        drmModeAtomicAddProperty(req, ctx.plane_id, ctx.prop_fb_id, buf->fb_id);
        drmModeAtomicAddProperty(req, ctx.plane_id, ctx.prop_crtc_id, ctx.crtc_id);
        drmModeAtomicAddProperty(req, ctx.plane_id, ctx.prop_crtc_w, buf->width);
        drmModeAtomicAddProperty(req, ctx.plane_id, ctx.prop_crtc_h, buf->height);
        drmModeAtomicAddProperty(req, ctx.plane_id, ctx.prop_src_w, buf->width << 16);
        drmModeAtomicAddProperty(req, ctx.plane_id, ctx.prop_src_h, buf->height << 16);

        ctx.waiting_for_flip = 1;
        uint32_t flags = DRM_MODE_ATOMIC_NONBLOCK | DRM_MODE_PAGE_FLIP_EVENT;
        int ret = drmModeAtomicCommit(ctx.fd, req, flags, &ctx);
        drmModeAtomicFree(req);

        if (ret < 0) {
            perror("Помилка виконання drmModeAtomicCommit");
            break;
        }

        /* Очікування сигналу VBlank від ядра через poll() */
        while (ctx.waiting_for_flip) {
            struct pollfd pfd = { .fd = ctx.fd, .events = POLLIN };
            if (poll(&pfd, 1, -1) > 0) {
                drmHandleEvent(ctx.fd, &evctx);
            }
        }
    }

    close(ctx.fd);
    return 0;
}
```
```cpp
// C++ Idiomatic Implementation with RAII Resource Management
#include <fcntl.h>
#include <poll.h>
#include <sys/mman.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

#include <cstdio>
#include <exception>
#include <iostream>
#include <memory>
#include <span>
#include <stdexcept>
#include <string>
#include <vector>

namespace kms {

// RAII обгортка для файлового дескриптора DRM
class DrmDevice {
    int fd_{-1};
public:
    explicit DrmDevice(const std::string& path) {
        fd_ = ::open(path.c_str(), O_RDWR | O_CLOEXEC);
        if (fd_ < 0) {
            throw std::runtime_error("Не вдалося відкрити пристрій DRM: " + path);
        }
        
        if (::drmSetClientCap(fd_, DRM_CLIENT_CAP_ATOMIC, 1) != 0 ||
            ::drmSetClientCap(fd_, DRM_CLIENT_CAP_UNIVERSAL_PLANES, 1) != 0) {
            throw std::runtime_error("Атомарні можливості Atomic KMS не підтримуються ядром");
        }
    }

    ~DrmDevice() {
        if (fd_ >= 0) ::close(fd_);
    }

    DrmDevice(const DrmDevice&) = delete;
    DrmDevice& operator=(const DrmDevice&) = delete;
    DrmDevice(DrmDevice&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }

    [[nodiscard]] int get() const noexcept { return fd_; }
};

// RAII обгортка для Dumb-буфера у пам'яті
class DumbBuffer {
    int fd_;
    uint32_t handle_{0};
    uint32_t fb_id_{0};
    uint32_t size_{0};
    uint32_t width_{0};
    uint32_t height_{0};
    void* vaddr_{MAP_FAILED};

public:
    DumbBuffer(int fd, uint32_t width, uint32_t height)
        : fd_(fd), width_(width), height_(height) {
        
        drm_mode_create_dumb creq{.width = width, .height = height, .bpp = 32};
        if (::drmIoctl(fd_, DRM_IOCTL_MODE_CREATE_DUMB, &creq) < 0) {
            throw std::runtime_error("Не вдалося створити DUMB буфер через ioctl");
        }
        handle_ = creq.handle;
        size_ = creq.size;

        if (::drmModeAddFB(fd_, width, height, 24, 32, creq.pitch, handle_, &fb_id_) < 0) {
            throw std::runtime_error("Не вдалося зареєструвати фреймбуфер drmModeAddFB");
        }

        drm_mode_map_dumb mreq{.handle = handle_};
        if (::drmIoctl(fd_, DRM_IOCTL_MODE_MAP_DUMB, &mreq) < 0) {
            throw std::runtime_error("Помилка отримання зсуву пам'яті MAP_DUMB");
        }

        vaddr_ = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE, MAP_SHARED, fd_, mreq.offset);
        if (vaddr_ == MAP_FAILED) {
            throw std::runtime_error("Помилка відображення пам'яті mmap");
        }
    }

    ~DumbBuffer() {
        if (vaddr_ != MAP_FAILED) ::munmap(vaddr_, size_);
        if (fb_id_) ::drmModeRmFB(fd_, fb_id_);
        if (handle_) {
            drm_mode_destroy_dumb dreq{.handle = handle_};
            ::drmIoctl(fd_, DRM_IOCTL_MODE_DESTROY_DUMB, &dreq);
        }
    }

    [[nodiscard]] uint32_t fb_id() const noexcept { return fb_id_; }
    [[nodiscard]] uint32_t width() const noexcept { return width_; }
    [[nodiscard]] uint32_t height() const noexcept { return height_; }

    [[nodiscard]] std::span<uint32_t> pixels() noexcept {
        return {static_cast<uint32_t*>(vaddr_), size_ / sizeof(uint32_t)};
    }
};

// RAII обгортка для атомарного запиту
class AtomicRequest {
    drmModeAtomicReqPtr req_{nullptr};
public:
    AtomicRequest() : req_(::drmModeAtomicAlloc()) {
        if (!req_) throw std::bad_alloc();
    }
    ~AtomicRequest() {
        if (req_) ::drmModeAtomicFree(req_);
    }

    void add_property(uint32_t obj_id, uint32_t prop_id, uint64_t val) {
        if (::drmModeAtomicAddProperty(req_, obj_id, prop_id, val) < 0) {
            throw std::runtime_error("Помилка додавання властивості в атомарний запит");
        }
    }

    int commit(int fd, uint32_t flags, void* user_data) {
        return ::drmModeAtomicCommit(fd, req_, flags, user_data);
    }
};

} // namespace kms

int main() {
    try {
        kms::DrmDevice dev("/dev/dri/card0");
        std::cout << "Успішна ініціалізація DRM пристрою з Atomic KMS\n";
        // Логіка підключення об'єктів та кадрового циклу через RAII...
    } catch (const std::exception& ex) {
        std::cerr << "Фатальна помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

---

## 5. Описи класів у C++ реалізації (RAII Architecture)

C++ версія утилізує ідіому RAII (Resource Acquisition Is Initialization), усуваючи загрози витоку системних ресурсів при винятках чи ранніх поверненнях із функцій:

- `class DrmDevice`: Гарантує автоматичне закриття файлового дескриптора при знищенні об'єкта. Забороняє копіювання, але підтримує семантику переміщення (Move Semantics).
- `class DumbBuffer`: Повністю ізолює життєвий цикл відеопам'яті. У конструкторі створює Dumb-буфер, додає Framebuffer у ядро та відображає пам'ять через `mmap()`. У деструкторі послідовно виконує `munmap()`, `drmModeRmFB()` та `DRM_IOCTL_MODE_DESTROY_DUMB`. Повертає безпечний шар `std::span<uint32_t>` для прямого запису пікселів у C++20.
- `class AtomicRequest`: Автоматизує виклики `drmModeAtomicAlloc()` та `drmModeAtomicFree()`, унеможливлюючи витік пам'яті атомарного запиту у простір користувача.

---

## 6. Детальний аналіз типових помилок та пасток

1. **Забутий виклик `DRM_CLIENT_CAP_UNIVERSAL_PLANES`:** За замовчуванням застарілі версії `libdrm` приховують Primary та Cursor площини у списку `drmModeGetPlaneResources`, повертаючи лише Overlay-площини. Якщо не встановити цей прапор, пошук основної площини завершиться помилкою.
2. **Формат зсуву координат `SRC_W` та `SRC_H`:** Властивості вибірки джерела `SRC_X`, `SRC_Y`, `SRC_W`, `SRC_H` приймають значення у форматі Q16.16 (16 біт на цілу частину, 16 біт на дробову). Передача звичайного цілого числа `1920` замість `1920 << 16` призведе до того, що ядро сприйме ширину джерела як $1920 / 65536 \approx 0.029$ пікселя і поверне помилку `-EINVAL`.
3. **Конфлікти за DRM Master:** У системі з працюючим X-сервером або Wayland-композитором виклик `drmModeAtomicCommit` поверне помилку `-EACCES`, оскільки статус DRM Master уже монополізовано графічним сервером. Для тестування консольного рендерера потрібно призупинити екранну службу (наприклад, `systemctl stop gdm`).
4. **Помилка `EBUSY` при поновному коміті:** Якщо спробувати виконати новий виклик `drmModeAtomicCommit` з прапорцем `DRM_MODE_PAGE_FLIP_EVENT` до того, як від ядра надійшла подія про завершення попереднього кадрового розгортання, ядро поверне помилку `-EBUSY`. Програма зобов'язана суворо дотримуватися черговості VBlank.
5. **Незбіг `pitch` (Stride Alignment):** Спроба запису в пам'ять `vaddr` із розрахунку `width * 4` замість використання відданого ядром `pitch` призведе до діагонального викривлення зображення на GPU, де ширина рядка вирівнюється по межі 64 або 256 байтів.
6. **Витік `dma-buf` файлових дескрипторів:** При експорті чи імпорті PRIME-буферів незакриті POSIX дескриптори призводять до швидкого вичерпання таблиці дескрипторів процесу (`RLIMIT_NOFILE`).
