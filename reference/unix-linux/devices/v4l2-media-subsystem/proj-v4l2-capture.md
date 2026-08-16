# ⚙️ Практичний проект захоплення відеокадрів та конфігурації Media Controller

Практичний приклад показує повний розробницький цикл роботи з сучасним медіа-конвеєром ядра Linux у просторі користувача. Проект охоплює всі стадії ініціалізації: від динамічної конфігурації топології медіа-графа через символьний вузол `/dev/media0` та налаштування форматів медіа-шини на субпристрої `/dev/v4l-subdev0` до виділення пам'яті під кільцеву чергу буферів, очікування переривань кадру та експорту буферів у підсистему `dma-buf`.

Приклад реалізовано паралельно у двох мовних варіантах — стандартною мовою C та сучасною мовою C++20 у вигляді порівняльних вкладок. Реалізація мовою C++20 спирається на концепцію RAII (Resource Acquisition Is Initialization), усуває ризики витоку дескрипторів та відображень пам'яті (`mmap`), а також замінює небезпечні вказівники та блоки ручного вивільнення ресурсів `goto` на прозорі RAII-обгортки та контейнери `std::span`.

:::tabs
```c
/* v4l2_mc_capture.c — Захоплення відео через Media Controller та V4L2 (C implementation) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdint.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <poll.h>
#include <linux/videodev2.h>
#include <linux/media.h>
#include <linux/v4l2-subdev.h>

#define REQ_BUF_COUNT 4

struct buffer_entry {
    void  *start;
    size_t length;
};

/* Активація зв'язку у графі Media Controller */
static int enable_media_link(int media_fd, uint32_t src_ent, uint16_t src_pad, uint32_t sink_ent, uint16_t sink_pad) {
    struct media_link_desc link;
    memset(&link, 0, sizeof(link));

    link.source.entity = src_ent;
    link.source.index  = src_pad;
    link.sink.entity   = sink_ent;
    link.sink.index    = sink_pad;
    link.flags         = MEDIA_LNK_FL_ENABLED;

    if (ioctl(media_fd, MEDIA_IOC_SETUP_LINK, &link) < 0) {
        perror("MEDIA_IOC_SETUP_LINK failed");
        return -1;
    }
    return 0;
}

/* Налаштування формату на субпристрої (сенсор/CSI) */
static int set_subdev_format(const char *subdev_path, uint32_t pad, uint32_t width, uint32_t height, uint32_t code) {
    int sd_fd = open(subdev_path, O_RDWR);
    if (sd_fd < 0) {
        perror("Failed to open subdev");
        return -1;
    }

    struct v4l2_subdev_format fmt;
    memset(&fmt, 0, sizeof(fmt));
    fmt.pad = pad;
    fmt.which = V4L2_SUBDEV_FORMAT_ACTIVE;
    fmt.format.width = width;
    fmt.format.height = height;
    fmt.format.code = code; /* наприклад, MEDIA_BUS_FMT_YUYV8_1X16 */
    fmt.format.field = V4L2_FIELD_NONE;

    if (ioctl(sd_fd, VIDIOC_SUBDEV_S_FMT, &fmt) < 0) {
        perror("VIDIOC_SUBDEV_S_FMT failed");
        close(sd_fd);
        return -1;
    }

    close(sd_fd);
    return 0;
}

int main(void) {
    int media_fd = -1, video_fd = -1;
    struct buffer_entry buffers[REQ_BUF_COUNT] = {0};
    enum v4l2_buf_type type;

    /* 1. Відкриваємо Media Controller та активуємо зв'язок у графі */
    media_fd = open("/dev/media0", O_RDWR);
    if (media_fd >= 0) {
        printf("[MC] Configuring media topology link...\n");
        enable_media_link(media_fd, 1, 0, 2, 0); /* Entity 1 Pad 0 -> Entity 2 Pad 0 */
        close(media_fd);
    }

    /* 2. Конфігуруємо проміжний субпристрій */
    printf("[Subdev] Setting format on /dev/v4l-subdev0...\n");
    set_subdev_format("/dev/v4l-subdev0", 0, 1920, 1080, 0x200f /* MEDIA_BUS_FMT_YUYV8_1X16 */);

    /* 3. Відкриваємо вузол відеопотоку /dev/video0 */
    video_fd = open("/dev/video0", O_RDWR | O_NONBLOCK);
    if (video_fd < 0) {
        perror("Failed to open /dev/video0");
        return EXIT_FAILURE;
    }

    /* 4. Встановлюємо формат захоплення на відеовузлі */
    struct v4l2_format fmt;
    memset(&fmt, 0, sizeof(fmt));
    fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    fmt.fmt.pix.width       = 1920;
    fmt.fmt.pix.height      = 1080;
    fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
    fmt.fmt.pix.field       = V4L2_FIELD_NONE;

    if (ioctl(video_fd, VIDIOC_S_FMT, &fmt) < 0) {
        perror("VIDIOC_S_FMT failed");
        goto err_close;
    }

    /* 5. Просимо ядро виділити буфери (MMAP) */
    struct v4l2_requestbuffers req;
    memset(&req, 0, sizeof(req));
    req.count  = REQ_BUF_COUNT;
    req.type   = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;

    if (ioctl(video_fd, VIDIOC_REQBUFS, &req) < 0) {
        perror("VIDIOC_REQBUFS failed");
        goto err_close;
    }

    /* 6. Відображаємо буфери в адресний простір процесу та ставимо в чергу */
    for (size_t i = 0; i < req.count; ++i) {
        struct v4l2_buffer buf;
        memset(&buf, 0, sizeof(buf));
        buf.type   = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index  = i;

        if (ioctl(video_fd, VIDIOC_QUERYBUF, &buf) < 0) {
            perror("VIDIOC_QUERYBUF failed");
            goto err_close;
        }

        buffers[i].length = buf.length;
        buffers[i].start = mmap(NULL, buf.length, PROT_READ | PROT_WRITE, MAP_SHARED, video_fd, buf.m.offset);
        if (buffers[i].start == MAP_FAILED) {
            perror("mmap failed");
            goto err_close;
        }

        if (ioctl(video_fd, VIDIOC_QBUF, &buf) < 0) {
            perror("VIDIOC_QBUF failed");
            goto err_close;
        }
    }

    /* 7. Запускаємо відеоплин */
    type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (ioctl(video_fd, VIDIOC_STREAMON, &type) < 0) {
        perror("VIDIOC_STREAMON failed");
        goto err_close;
    }

    printf("[V4L2] Streaming started. Waiting for frames...\n");

    /* 8. Очікуємо готовності кадру через poll() */
    struct pollfd pfd = { .fd = video_fd, .events = POLLIN };
    if (poll(&pfd, 1, 2000) > 0) {
        struct v4l2_buffer buf;
        memset(&buf, 0, sizeof(buf));
        buf.type   = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;

        if (ioctl(video_fd, VIDIOC_DQBUF, &buf) == 0) {
            printf("[V4L2] Captured frame index %u, bytes used: %u\n", buf.index, buf.bytesused);
            /* Обробка кадру у buffers[buf.index].start ... */
            ioctl(video_fd, VIDIOC_QBUF, &buf); /* повертаємо буфер у чергу */
        }
    }

    /* 9. Зупинка потоку та вивільнення ресурсів */
    ioctl(video_fd, VIDIOC_STREAMOFF, &type);

err_close:
    for (size_t i = 0; i < REQ_BUF_COUNT; ++i) {
        if (buffers[i].start && buffers[i].start != MAP_FAILED) {
            munmap(buffers[i].start, buffers[i].length);
        }
    }
    if (video_fd >= 0) close(video_fd);
    return 0;
}
```
```cpp
// v4l2_mc_capture.cpp — Захоплення відео через Media Controller та V4L2 (C++20 RAII implementation)
#include <iostream>
#include <vector>
#include <string_view>
#include <memory>
#include <system_error>
#include <span>
#include <cstdlib>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <poll.h>
#include <linux/videodev2.h>
#include <linux/media.h>
#include <linux/v4l2-subdev.h>

// RAII обгортка для файлового дескриптора POSIX
class FileDescriptor {
    int fd_ = -1;
public:
    explicit FileDescriptor(int fd = -1) : fd_(fd) {}
    ~FileDescriptor() { if (fd_ >= 0) ::close(fd_); }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
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

// RAII обгортка відображення пам'яті mmap
class MmappedBuffer {
    void* ptr_ = MAP_FAILED;
    size_t size_ = 0;
public:
    MmappedBuffer(int fd, size_t length, off_t offset) : size_(length) {
        ptr_ = ::mmap(nullptr, length, PROT_READ | PROT_WRITE, MAP_SHARED, fd, offset);
        if (ptr_ == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "mmap failed");
        }
    }

    ~MmappedBuffer() {
        if (ptr_ != MAP_FAILED) {
            ::munmap(ptr_, size_);
        }
    }

    MmappedBuffer(const MmappedBuffer&) = delete;
    MmappedBuffer& operator=(const MmappedBuffer&) = delete;

    MmappedBuffer(MmappedBuffer&& other) noexcept : ptr_(other.ptr_), size_(other.size_) {
        other.ptr_ = MAP_FAILED;
        other.size_ = 0;
    }

    MmappedBuffer& operator=(MmappedBuffer&& other) noexcept {
        if (this != &other) {
            if (ptr_ != MAP_FAILED) ::munmap(ptr_, size_);
            ptr_ = other.ptr_;
            size_ = other.size_;
            other.ptr_ = MAP_FAILED;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] std::span<uint8_t> as_span(size_t used_bytes) const noexcept {
        return { static_cast<uint8_t*>(ptr_), used_bytes };
    }
};

class MediaPipeline {
public:
    static void setup_link(const char* media_path, uint32_t src_ent, uint16_t src_pad, uint32_t sink_ent, uint16_t sink_pad) {
        FileDescriptor fd(::open(media_path, O_RDWR));
        if (!fd.valid()) return; // Граф може бути вже налаштований у системі

        struct media_link_desc link{};
        link.source.entity = src_ent;
        link.source.index  = src_pad;
        link.sink.entity   = sink_ent;
        link.sink.index    = sink_pad;
        link.flags         = MEDIA_LNK_FL_ENABLED;

        if (::ioctl(fd.get(), MEDIA_IOC_SETUP_LINK, &link) < 0) {
            throw std::system_error(errno, std::generic_category(), "MEDIA_IOC_SETUP_LINK failed");
        }
    }

    static void set_subdev_format(const char* subdev_path, uint32_t pad, uint32_t width, uint32_t height, uint32_t code) {
        FileDescriptor fd(::open(subdev_path, O_RDWR));
        if (!fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Failed to open subdev node");
        }

        struct v4l2_subdev_format fmt{};
        fmt.pad = pad;
        fmt.which = V4L2_SUBDEV_FORMAT_ACTIVE;
        fmt.format.width = width;
        fmt.format.height = height;
        fmt.format.code = code;
        fmt.format.field = V4L2_FIELD_NONE;

        if (::ioctl(fd.get(), VIDIOC_SUBDEV_S_FMT, &fmt) < 0) {
            throw std::system_error(errno, std::generic_category(), "VIDIOC_SUBDEV_S_FMT failed");
        }
    }
};

int main() {
    try {
        std::cout << "[MC] Setting up topology links...\n";
        MediaPipeline::setup_link("/dev/media0", 1, 0, 2, 0);

        std::cout << "[Subdev] Configuring camera subdevice format...\n";
        MediaPipeline::set_subdev_format("/dev/v4l-subdev0", 0, 1920, 1080, 0x200f);

        FileDescriptor video_fd(::open("/dev/video0", O_RDWR | O_NONBLOCK));
        if (!video_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Failed to open /dev/video0");
        }

        struct v4l2_format fmt{};
        fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        fmt.fmt.pix.width       = 1920;
        fmt.fmt.pix.height      = 1080;
        fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
        fmt.fmt.pix.field       = V4L2_FIELD_NONE;

        if (::ioctl(video_fd.get(), VIDIOC_S_FMT, &fmt) < 0) {
            throw std::system_error(errno, std::generic_category(), "VIDIOC_S_FMT failed");
        }

        constexpr uint32_t buf_count = 4;
        struct v4l2_requestbuffers req{};
        req.count  = buf_count;
        req.type   = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        req.memory = V4L2_MEMORY_MMAP;

        if (::ioctl(video_fd.get(), VIDIOC_REQBUFS, &req) < 0) {
            throw std::system_error(errno, std::generic_category(), "VIDIOC_REQBUFS failed");
        }

        std::vector<MmappedBuffer> buffers;
        buffers.reserve(req.count);

        for (uint32_t i = 0; i < req.count; ++i) {
            struct v4l2_buffer buf{};
            buf.type   = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            buf.memory = V4L2_MEMORY_MMAP;
            buf.index  = i;

            if (::ioctl(video_fd.get(), VIDIOC_QUERYBUF, &buf) < 0) {
                throw std::system_error(errno, std::generic_category(), "VIDIOC_QUERYBUF failed");
            }

            buffers.emplace_back(video_fd.get(), buf.length, buf.m.offset);

            if (::ioctl(video_fd.get(), VIDIOC_QBUF, &buf) < 0) {
                throw std::system_error(errno, std::generic_category(), "VIDIOC_QBUF failed");
            }
        }

        enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        if (::ioctl(video_fd.get(), VIDIOC_STREAMON, &type) < 0) {
            throw std::system_error(errno, std::generic_category(), "VIDIOC_STREAMON failed");
        }

        std::cout << "[V4L2] Streaming active. Polling for frame...\n";

        struct pollfd pfd{ .fd = video_fd.get(), .events = POLLIN, .revents = 0 };
        if (::poll(&pfd, 1, 2000) > 0) {
            struct v4l2_buffer buf{};
            buf.type   = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            buf.memory = V4L2_MEMORY_MMAP;

            if (::ioctl(video_fd.get(), VIDIOC_DQBUF, &buf) == 0) {
                auto frame_bytes = buffers[buf.index].as_span(buf.bytesused);
                std::cout << "[V4L2] Frame acquired! Memory address: " 
                          << static_cast<void*>(frame_bytes.data()) 
                          << ", Size: " << frame_bytes.size() << " bytes.\n";

                ::ioctl(video_fd.get(), VIDIOC_QBUF, &buf);
            }
        }

        ::ioctl(video_fd.get(), VIDIOC_STREAMOFF, &type);
    } catch (const std::exception& e) {
        std::cerr << "[Error] " << e.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

## Покроковий розбір стадій виконання проекту

Робота з медіа-конвеєром ядра вимагає дотримання суворої послідовності кроків, недотримання якої призводить до помилок ядра під час валідації графа.

### Крок 1. Активація зв'язку у графі Media Controller

Функція `enable_media_link()` відкриває контролер `/dev/media0` та формує структуру `struct media_link_desc`. Поле `source.entity` вказує на ідентифікатор сутності сенсора камери, `sink.entity` — на ідентифікатор приймача MIPI CSI-2, а `source.index` і `sink.index` — на номери відповідних майданчиків. Прапор `MEDIA_LNK_FL_ENABLED` сповіщає ядро, що потік даних між цими двома блоками активовано. Якщо цей крок пропустити, подальший запуск відеопотоку поверне помилку `EPIPE` (Broken pipe).

### Крок 2. Налаштування формату на субпристрої

Функція `set_subdev_format()` відкриває вузол субпристрою `/dev/v4l-subdev0` та викликає `VIDIOC_SUBDEV_S_FMT`. Зверніть увагу, що поле `which` встановлено у `V4L2_SUBDEV_FORMAT_ACTIVE`. Це означає, що переданий колірний код шини `MEDIA_BUS_FMT_YUYV8_1X16` записується безпосередньо в апаратні регістри контролера.

### Крок 3. Налаштування формату на потоковому відеовузлі

Основна програма відкриває пристрій `/dev/video0` із прапором `O_NONBLOCK`. Прапор незаблокованого вводу/виводу є критично важливим: він запобігає «зависанню» потоку виконання на виклику `VIDIOC_DQBUF`, якщо апаратура камери ще не згенерувала новий кадр. Далі через `VIDIOC_S_FMT` фіксується вихідна роздільна здатність (1920×1080) та колірний FourCC-код (`V4L2_PIX_FMT_YUYV`).

### Крок 4. Запит буферів у підсистеми Videobuf2

Виклик `VIDIOC_REQBUFS` із типом пам'яті `V4L2_MEMORY_MMAP` змушує драйвер ядра виділити кільцеву чергу з 4 буферів (`REQ_BUF_COUNT`) — звичайними сторінками ядра або, якщо апаратурі потрібна суцільна фізична пам'ять, у зоні CMA. У циклі для кожного буфера виконується виклик `VIDIOC_QUERYBUF`: він повертає у `m.offset` умовний зсув, який `mmap()` на цьому ж дескрипторі впізнає як позначку конкретного буфера й відображає його в адресний простір нашого процесу.

### Крок 5. Постановка буферів у чергу та запуск DMA

Перед початком трансляції всі підготовлені буфери віддаються ядру викликами `VIDIOC_QBUF`. Після наповнення черги виклик `VIDIOC_STREAMON` вмикає контролер DMA та запускає генерацію пікселів на сенсорі.

### Крок 6. Асинхронне очікування кадру та вилучення

Оскільки пристрій відкрито у режимі `O_NONBLOCK`, додаток викликає системний `poll()` із таймаутом 2000 мс. Повернення з `poll()` із прапором `POLLIN` гарантує, що апаратне переривання кадру вже відбулося і при виклику `VIDIOC_DQBUF` ядро негайно поверне індекс заповненого буфера `buf.index` та кількість реально записаних байтів `buf.bytesused`.

---

## Експорт буферів Zero-Copy через dma-buf

Для передачі захопленого відеокадру безпосередньо у GPU для рендерингу (через EGL / Vulkan) або у дисплейний контролер DRM/KMS без викликів `memcpy` простір користувача використовує виклик `VIDIOC_EXPBUF`:

:::tabs
```c
struct v4l2_exportbuffer expbuf;
memset(&expbuf, 0, sizeof(expbuf));
expbuf.type  = V4L2_BUF_TYPE_VIDEO_CAPTURE;
expbuf.index = buf.index;
expbuf.flags = O_CLOEXEC | O_RDWR;

if (ioctl(video_fd, VIDIOC_EXPBUF, &expbuf) == 0) {
    int dmabuf_fd = expbuf.fd;
    /* Файловий дескриптор dmabuf_fd передається у gbm_bo_import() або eglCreateImageKHR() */
}
```
```cpp
struct v4l2_exportbuffer expbuf{};
expbuf.type  = V4L2_BUF_TYPE_VIDEO_CAPTURE;
expbuf.index = buf.index;
expbuf.flags = O_CLOEXEC | O_RDWR;

if (::ioctl(video_fd.get(), VIDIOC_EXPBUF, &expbuf) == 0) {
    FileDescriptor dmabuf_fd(expbuf.fd);
    // Файловий дескриптор dmabuf_fd передається у gbm_bo_import() або eglCreateImageKHR()
}
```
:::

Виклик `VIDIOC_EXPBUF` створює у ядрі файловий дескриптор підсистеми `dma-buf`, який експортує сторінки пам'яті буфера Videobuf2. Це дає змогу іншим драйверам (DRM/KMS чи NPU-прискорювачу) імпортувати ці ж фізичні сторінки пам'яті через IOMMU, уникаючи зайвого копіювання процесором.

---

## Моніторинг та налагодження через sysfs і tracepoints

Для діагностики проблем із продуктивністю або втратою кадрів у системі розробник може використовувати ядерні трасувальні точки (tracepoints):

- `/sys/kernel/debug/tracing/events/v4l2/v4l2_dqbuf/enable`: Вмикає трасування викликів вилучення буферів. У файл `trace` записуються часові мітки `timestamp`, індекси буферів та прапорці помилок.
- `/sys/class/video4linux/video0/dev`: Містить старший та молодший номери пристрою (`dev_t`) для ідентифікації пристрою VFS.
- `v4l2-ctl --log-status`: Запитує у драйвера вивід поточного стану апаратних регістрів та лічильників переривань у системний журнал `dmesg`.

---

## Типові пастки системного розробника та їх подолання

- **Помилка `EPIPE` (Broken Pipe) при `VIDIOC_STREAMON`**: Виникає під час валідації графа у ядрі (`media_pipeline_start()`). Найчастіші причини: розбіжність роздільної здатності між вихідним майданчиком субпристрою та відеовузлом, вимкнений зв'язок між сутностями, або неузгоджені коди медіа-шини.
- **Помилка `EBUSY` при `VIDIOC_S_FMT`**: Спроба змінити формат відеовузла, коли буфери вже виділені викликом `VIDIOC_REQBUFS` або коли потік вже запущено. Зміна формату вимагає попередньої зупинки `VIDIOC_STREAMOFF` та звільнення буферів `VIDIOC_REQBUFS` із `count = 0`.
- **Витік відображень пам'яті `mmap` у мові C**: Якщо вихід із програми здійснюється за помилкою через `goto err_close`, скасування відображень `munmap()` має відбутися для кожного виділеного буфера. У реалізації C++20 деструктор `MmappedBuffer` гарантує виклики `munmap()` навіть при виникненні винятків `std::system_error`.
- **Гонка ресурсів при повторному виклику `VIDIOC_QBUF`**: Після обробки кадрів у просторі користувача буфер обов'язково повинен бути повернений ядру викликом `VIDIOC_QBUF`. Якщо додаток не повертає буфери вчасно, кільцева черга Videobuf2 вичерпується і драйвер починає скидати кадри (Frame drops).
