# ⚙️ Реалізація zero-copy пайплайну через dma-buf heaps (V4L2 та DRM)

Високоефективний мультимедійний zero-copy конвеєр у ядрі Linux будується на прямому обміні файловими дескрипторами буферів пам'яті між пристроями. Алгоритм виділяє неперервну фізичну пам'ять через пристрій `/dev/dma_heap/linux,cma` і передає отриманий файловий дескриптор між драйвером камери (V4L2), графічним контролером виведення (DRM/KMS) та мережевим адаптером без створення жодної додаткової копії у процесорі.

## Постановка задачі та апаратні обмеження

При розробці відеосистем реального часу на ARM SoC (наприклад, системи допомоги водієві ADAS, робототехнічні камери чи системи медичної візуалізації) виникає потреба обробки відеопотоків роздільною здатністю Full HD (1920×1080) або 4K (3840×2160) зі частотою 60 кадрів на секунду.

Для кадру 1920×1080 у форматі `DRM_FORMAT_XRGB8888` (32 біти або 4 байти на піксель) обсяг одного буфера становить:

```
1920 × 1080 × 4 байти = 8 294 400 байт (приблизно 7.91 МБ)
```

При 60 кадрах на секунду загальний потік даних перевищує 497 МБ/с. Якщо програма простору користувача зчитує кадр від драйвера камери через виклик `read()`, а потім записує його в дисплейний драйвер через `write()`, дані двічі копіюються через оперативну пам'ять за допомогою процесора. Це призводить до навантаження на шину RAM у розмірі понад 1 ГБ/с, що викликає пропуски кадрів (frame drops), деградацію затримок (latency) та перегрів SoC.

Метою цієї роботи є створення повністю "безкопійного" (zero-copy) конвеєра, у якому процесор виступає лише оркестратором: він створює буфер через dma-buf heaps і передає його дескриптор підсистемам ядра. Запис даних здійснює безпосередньо контролер DMA камери, а читання — DMA-контролер графічного дисплея.

## Послідовний алгоритм обробки кадрів

Повний цикл роботи zero-copy конвеєра реалізується у п'ять послідовних етапів:

```
+-------------------------------------------------------------------------+
| EТАП 1: Виділення неперервної пам'яті у dma-buf heap                    |
| open("/dev/dma_heap/linux,cma") -> ioctl(DMA_HEAP_IOC_ALLOC) -> dmabuf_fd|
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
| EТАП 2: Конфігурація та передача буфера у V4L2 (Камера)                 |
| VIDIOC_REQBUFS (V4L2_MEMORY_DMABUF) -> VIDIOC_QBUF(m.fd = dmabuf_fd)   |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
| EТАП 3: Запуск потоку та захоплення кадру                               |
| VIDIOC_STREAMON -> VIDIOC_DQBUF (чекаємо завершення DMA запису камери)  |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
| EТАП 4: Імпорт dma-buf у DRM/KMS (Графічний дисплей)                   |
| ioctl(DRM_IOCTL_PRIME_FD_TO_HANDLE) -> drmModeAddFB2() -> GEM handle    |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
| EТАП 5: Отображення на екрані та рециркуляція                           |
| drmModePageFlip() / Atomic Commit -> VIDIOC_QBUF (повернення в чергу)   |
+-------------------------------------------------------------------------+
```

### Деталізація кроків алгоритму

1. **Виділення фізичного буфера:** Програма відкриває символьний пристрій `/dev/dma_heap/linux,cma`. За допомогою системного виклику `ioctl(DMA_HEAP_IOC_ALLOC)` запитується буфер розміром `8294400` байтів. Ядро резервує неперервний блок у регіоні CMA та повертає файловий дескриптор `dmabuf_fd`.
2. **Налаштування буферизації V4L2:** Відкривається відеопристрій камери `/dev/video0`. Програма виконує `ioctl(VIDIOC_REQBUFS)` із прапорцем `V4L2_MEMORY_DMABUF`, повідомляючи ядро, що пам'ять надаватиметься ззовні. Викликається `ioctl(VIDIOC_QBUF)`, куди передається структура `v4l2_buffer` з полем `buf.m.fd = dmabuf_fd`.
3. **Захоплення кадру:** Запускається відеопотік через `ioctl(VIDIOC_STREAMON)`. Контролер DMA камери записує сигнал із сенсора безпосередньо у фізичні адреси CMA. Після завершення запису камери ядро генерує переривання, і програма отримує сповіщення через `ioctl(VIDIOC_DQBUF)`.
4. **Прив'язка буфера до DRM/KMS:** Відкривається графічний пристрій `/dev/dri/card0`. Файловий дескриптор `dmabuf_fd` імпортується у графічний менеджер GEM за допомогою `ioctl(DRM_IOCTL_PRIME_FD_TO_HANDLE)`. Отриманий хендл `prime.handle` використовується для реєстрації фреймбуфера `fb_id` через `drmModeAddFB2()`.
5. **Виведення на дисплей:** Створений `fb_id` передається у підсистему DRM KMS через системні виклики Atomic API (`drmModeAtomicCommit`) або `drmModeSetCrtc`. Контролер дисплея зчитує кадри безпосередньо з тих самих фізичних адрес RAM. Після відображення кадру буфер повертається у чергу камери за допомогою повторного `VIDIOC_QBUF`.

## Робочий приклад програмної реалізації

Нижче наведено повну вихідну реалізацію zero-copy конвеєра мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/dma-heap.h>
#include <linux/videodev2.h>
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <drm_fourcc.h>
#include <errno.h>

/* Функція виділення неперервного DMA буфера з CMA купи */
int allocate_cma_buffer(size_t size) {
    int heap_fd = open("/dev/dma_heap/linux,cma", O_RDONLY | O_CLOEXEC);
    if (heap_fd < 0) {
        perror("Не вдалося відкрити CMA heap /dev/dma_heap/linux,cma");
        return -1;
    }

    struct dma_heap_allocation_data alloc_data = {
        .len = size,
        .fd = 0,
        .fd_flags = O_RDWR | O_CLOEXEC,
        .heap_flags = 0
    };

    if (ioctl(heap_fd, DMA_HEAP_IOC_ALLOC, &alloc_data) < 0) {
        perror("Збій ioctl DMA_HEAP_IOC_ALLOC для CMA");
        close(heap_fd);
        return -1;
    }

    close(heap_fd);
    return alloc_data.fd;
}

/* Передача буфера dma-buf у чергу V4L2 камери */
int queue_v4l2_dmabuf(int v4l2_fd, int dmabuf_fd, uint32_t index) {
    struct v4l2_buffer buf;
    memset(&buf, 0, sizeof(buf));
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_DMABUF;
    buf.index = index;
    buf.m.fd = dmabuf_fd;

    if (ioctl(v4l2_fd, VIDIOC_QBUF, &buf) < 0) {
        perror("Збій ioctl VIDIOC_QBUF V4L2_MEMORY_DMABUF");
        return -1;
    }
    return 0;
}

/* Імпорт dma-buf у DRM підсистему та створення фреймбуфера */
uint32_t create_drm_fb_from_dmabuf(int drm_fd, int dmabuf_fd, uint32_t width, uint32_t height, uint32_t pitch) {
    struct drm_prime_handle prime;
    memset(&prime, 0, sizeof(prime));
    prime.fd = dmabuf_fd;

    if (ioctl(drm_fd, DRM_IOCTL_PRIME_FD_TO_HANDLE, &prime) < 0) {
        perror("Збій DRM_IOCTL_PRIME_FD_TO_HANDLE");
        return 0;
    }

    uint32_t fb_id = 0;
    uint32_t handles[4] = { prime.handle, 0, 0, 0 };
    uint32_t pitches[4] = { pitch, 0, 0, 0 };
    uint32_t offsets[4] = { 0, 0, 0, 0 };

    if (drmModeAddFB2(drm_fd, width, height, DRM_FORMAT_XRGB8888,
                      handles, pitches, offsets, &fb_id, 0) < 0) {
        perror("Збій drmModeAddFB2");
        return 0;
    }

    return fb_id;
}

int main(void) {
    uint32_t width = 1920;
    uint32_t height = 1080;
    uint32_t pitch = width * 4;
    size_t buffer_size = (size_t)pitch * height;

    printf("=== Старт zero-copy конвеєра dma-buf heaps ===\n");

    int dmabuf_fd = allocate_cma_buffer(buffer_size);
    if (dmabuf_fd < 0) {
        fprintf(stderr, "Помилка: не вдалося виділити неперервний DMA буфер\n");
        return EXIT_FAILURE;
    }

    printf("Успішно отримано dma-buf fd: %d (розмір: %zu байтів)\n", dmabuf_fd, buffer_size);

    /* Імітація завершення роботи zero-copy конвеєра */
    close(dmabuf_fd);
    printf("Конвеєр завершив роботу без копіювання пам'яті.\n");
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <memory>
#include <expected>
#include <system_error>
#include <array>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/dma-heap.h>
#include <linux/videodev2.h>
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <drm_fourcc.h>

class DmaBuffer {
    int fd_ = -1;
    std::size_t size_ = 0;

public:
    DmaBuffer() noexcept = default;
    DmaBuffer(int fd, std::size_t size) noexcept : fd_(fd), size_(size) {}
    ~DmaBuffer() { reset(); }

    DmaBuffer(const DmaBuffer&) = delete;
    DmaBuffer& operator=(const DmaBuffer&) = delete;

    DmaBuffer(DmaBuffer&& other) noexcept : fd_(other.release()), size_(other.size_) {
        other.size_ = 0;
    }

    DmaBuffer& operator=(DmaBuffer&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.release();
            size_ = other.size_;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

    void reset() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = -1;
        }
        size_ = 0;
    }
};

std::expected<DmaBuffer, std::error_code> allocate_cma_buffer(std::size_t size) {
    int heap_fd = ::open("/dev/dma_heap/linux,cma", O_RDONLY | O_CLOEXEC);
    if (heap_fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    dma_heap_allocation_data alloc_data{};
    alloc_data.len = size;
    alloc_data.fd_flags = O_RDWR | O_CLOEXEC;
    alloc_data.heap_flags = 0;

    if (::ioctl(heap_fd, DMA_HEAP_IOC_ALLOC, &alloc_data) < 0) {
        int err = errno;
        ::close(heap_fd);
        return std::unexpected(std::error_code(err, std::generic_category()));
    }

    ::close(heap_fd);
    return DmaBuffer(static_cast<int>(alloc_data.fd), size);
}

std::expected<void, std::error_code> queue_v4l2_dmabuf(int v4l2_fd, const DmaBuffer& buf, uint32_t index) {
    v4l2_buffer vbuf{};
    vbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    vbuf.memory = V4L2_MEMORY_DMABUF;
    vbuf.index = index;
    vbuf.m.fd = buf.get();

    if (::ioctl(v4l2_fd, VIDIOC_QBUF, &vbuf) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

std::expected<uint32_t, std::error_code> create_drm_fb_from_dmabuf(int drm_fd, const DmaBuffer& buf, uint32_t width, uint32_t height, uint32_t pitch) {
    drm_prime_handle prime{};
    prime.fd = buf.get();

    if (::ioctl(drm_fd, DRM_IOCTL_PRIME_FD_TO_HANDLE, &prime) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    uint32_t fb_id = 0;
    std::array<uint32_t, 4> handles = { prime.handle, 0, 0, 0 };
    std::array<uint32_t, 4> pitches = { pitch, 0, 0, 0 };
    std::array<uint32_t, 4> offsets = { 0, 0, 0, 0 };

    if (::drmModeAddFB2(drm_fd, width, height, DRM_FORMAT_XRGB8888,
                        handles.data(), pitches.data(), offsets.data(), &fb_id, 0) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return fb_id;
}

int main() {
    constexpr uint32_t width = 1920;
    constexpr uint32_t height = 1080;
    constexpr uint32_t pitch = width * 4;
    constexpr std::size_t buffer_size = static_cast<std::size_t>(pitch) * height;

    std::cout << "=== Старт zero-copy конвеєра dma-buf heaps (C++23) ===\n";

    auto result = allocate_cma_buffer(buffer_size);
    if (!result) {
        std::cerr << "Помилка виділення DMA пам'яті: " << result.error().message() << '\n';
        return 1;
    }

    DmaBuffer buffer = std::move(*result);
    std::cout << "Успішно отримано dma-buf fd: " << buffer.get() 
              << " (" << buffer.size() << " байтів)\n";

    return 0;
}
```
:::

## Пастки, апаратні обмеження та крайові випадки

При реалізації zero-copy конвеєрів у розробників виникає низка специфічних проблем, пов'язаних з апаратними обмеженнями SoC.

### 1. Апаратне вирівнювання рядків (Pitch / Stride Alignment)

Різні апаратні блоки мають власні вимоги до вирівнювання ширини рядка кадру (stride/pitch). Наприклад, контролер дисплея може вимагати, щоб крок рядка був кратним 64 байтам, а графічний процесор GPU — кратним 256 байтам або межі 64 КБ.

Якщо ширину кадру `1920` пікселів помножити на 3 байти (формат RGB888):

```
1920 × 3 = 5760 байт (кратне 64, але не кратне 256)
```

Якщо розмір рядка не відповідає вимогам апаратного вирівнювання, зображення на екрані буде нахилене по діагоналі ("зсув рядків"). Для вирішення цієї проблеми розробник зобов'язаний округлювати `pitch` вгору до найближчого апаратно вирівняного значення і обчислювати розмір буфера з урахуванням доповнення (padding bytes).

### 2. Специфікація вирівнювання сторінок у CMA

Фреймворк dma-buf heaps автоматично округлює розмір виділення `len` до найближчої системної сторінки `PAGE_SIZE` (4096 байт). Однак деякі застарілі периферійні пристрої вимагають, щоб початкова фізична адреса буфера була вирівняна по межі 64 КБ або 1 МБ (alignment mask). У dma-buf heaps вирівнювання адреси залежить від реалізації конкретної купи ядра. У разі використання CMA це вирішується на рівні конфігурації ядра Linux.

### 3. Керування життєвим циклом файлових дескрипторів

Кожен файловий дескриптор `dma-buf` є об'єктом із підрахунком посилань (reference count). Виклик `ioctl(DRM_IOCTL_PRIME_FD_TO_HANDLE)` збільшує внутрішній лічильник посилань на об'єкт пам'яті у ядрі. Якщо програма простору користувача виконує `close(dmabuf_fd)`, фізична пам'ять не звільняється миттєво, якщо драйвери V4L2 або DRM все ще утримують свої внутрішні посилання `struct dma_buf`. Пам'ять повернеться у пул CMA лише тоді, калі остання підсистема закриє свій хендл.

### 4. Діагностика витоків пам'яті конвеєра

Витоки `dma-buf` файлових дескрипторів швидко призводять до вичерпання пулу CMA і падіння всієї мультимедійної системи. Для перевірки стану конвеєра слід контролювати кількість відкритих файлових дескрипторів процесу:

```bash
$ ls -l /proc/<PID>/fd/
```

А також аналізувати системний зріз підсистеми:

```bash
$ cat /sys/kernel/debug/dma_buf/bufinfo
```
