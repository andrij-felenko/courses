# ⚙️ Практичний Zero-Copy відеоконвеєр на V4L2 та DMA-BUF

Розробка високоефективних мультимедійних застосунків у середовищі Linux вимагає мінімізації або повного виключення операцій копіювання пам'яті (`memcpy`) за участю центрального процесора (ЦП). При обробці високошвидкісних відеопотоків із роздільною здатністю 1080p або 4K (наприклад, 4K UHD при 60 кадрах на секунду потребує передачі понад 700 Мегабайтів неспрямованих даних за секунду) копіювання одного кадру призводить до миттєвого вичерпання пропускної здатності системної шини пам'яті RAM, зростання затримок та невиправданого розігріву ЦП.

Цей практичний проєкт описує повну реалізацію низькорівневого відеоконвеєра із нульовим копіюванням (Zero-Copy). Програма послідовно виконує такі етапи:
1. Відкриває файл медіа-контролера `/dev/media0` та запитує загальну інформацію про апаратний граф.
2. Конфігурує формат шини (Media Bus Format) на джерельному майданчику (Source Pad) субпристрою `/dev/v4l2-subdev0` (наприклад, сенсора камери або приймача CSI-2).
3. Відкриває вузол відеозахоплення `/dev/video0` і налаштовує формат пікселів V4L2 у системній пам'яті.
4. Ініціалізує кільцеву чергу буферів Videobuf2 за допомогою ioctl `VIDIOC_REQBUFS` у режимі `V4L2_MEMORY_MMAP`.
5. Відображає буфери в адресний простір процесу (`mmap`) і здійснює їх експорт у вигляді анонімних файлових дескрипторів DMA-BUF за допомогою ioctl `VIDIOC_EXPBUF`.
6. Поміщає буфери у чергу ядра (`VIDIOC_QBUF`), запускає апаратний стримінг (`VIDIOC_STREAMON`), очікує готовність через `poll()` або `epoll()` та вилучає заповнені кадри (`VIDIOC_DQBUF`).
7. Забезпечує синхронізацію кешу ЦП через `DMABUF_IOCTL_SYNC` та коректне звільнення ресурсів при виникненні помилок.

---

## 1. Архітектурні особливості та механізм Zero-Copy

При побудові даного конвеєра використовується поєднання двох фреймворків ядра Linux: **Videobuf2 (vb2)** для виділення неперервної або Scatter-Gather пам'яті під відеокадри та **DMA-BUF** для її подальшої передачі іншим апаратним пристроям (GPU, дисплейному контролеру DRM/KMS чи апаратному кодеку).

```
 +-------------------+        +--------------------+        +-------------------+
 | V4L2 Video Capture|        |      DMA-BUF       |        |  DRM/KMS Display  |
 |   (/dev/video0)   |        | File Descriptor FD |        |   (/dev/dri/card0)|
 +---------+---------+        +---------+----------+        +---------+---------+
           |                            |                             |
           | 1. VIDIOC_EXPBUF           |                             |
           +--------------------------->|                             |
           |                            | 2. Import FD                |
           |                            +---------------------------->|
           v                                                          v
 +------------------------------------------------------------------------------+
 |                  Фізична системна пам'ять RAM (CMA / Page Array)             |
 |              (Пряма передача DMA без жодного memcpy ЦП)                      |
 +------------------------------------------------------------------------------+
```

### 1.1. Механізм експорту буферів через `VIDIOC_EXPBUF` (V4L2 як Exporter)

Коли застосунок ініціалізує буфери у V4L2 через виклик `VIDIOC_REQBUFS` із прапорцем `V4L2_MEMORY_MMAP`, ядро виділяє сторінки пам'яті (через CMA — Contiguous Memory Allocator або Scatter-Gather dma-allocator). Для того, щоб передати її іншим драйверам без копіювання, застосунок викликає ioctl `VIDIOC_EXPBUF`.

Під час виконання `VIDIOC_EXPBUF` ядро виконує такі кроки:
- Отримує внутрішній об'єкт `struct vb2_buffer` за вказаним індексом.
- Викликає внутрішньоядерний метод аллокатора `.get_dmabuf()`, який загортає масив фізичних сторінок `struct page*` у структуру `struct dma_buf`.
- Створює анонімний файловий дескриптор в описувачі файлів поточного процесу і асоціює його з цим об'єктом `dma_buf`.
- Повертає значення дескриптора у полі `expbuf.fd`.

Отриманий файловий дескриптор володіє системним лічильником посилань (`refcount`). Пам'ять залишається виділеною доти, доки відкритий файловий дескриптор `dma_buf` не буде закритий усім споживачами через системний виклик `close()`.

---

### 1.2. Механізм імпорту буферів через `V4L2_MEMORY_DMABUF` (V4L2 як Importer)

У зворотному сценарії пам'ять може виділятися зовнішнім підсистемним драйвером (наприклад DRM/KMS dumb buffer або GPU gbm_bo). У цьому випадку V4L2 виступає імпортером:

1. Застосунок відкриває `/dev/dri/card0`, виділяє буфер кадру у DRM/KMS і отримує дескриптор `drm_fd`.
2. Застосунок ініціалізує V4L2 викликом `VIDIOC_REQBUFS`, вказуючи режим `req.memory = V4L2_MEMORY_DMABUF`.
3. При виклику `VIDIOC_QBUF` у структурі `struct v4l2_buffer` передається файловий дескриптор зовнішнього буфера у полі `buf.m.fd = drm_fd`.
4. Драйвер V4L2 у ядрі викликає `dma_buf_get(drm_fd)`, будує таблицю `struct sg_table` і програмує регістри DMA відеозахоплення на фізичні адреси сторінок DRM-буфера.

---

### 1.3. Інтеграція з EGL / OpenGL ES (`EGL_EXT_image_dma_buf_import`)

Для подачі захопленого V4L2-кадру безпосередньо у графічний конвеєр GPU (наприклад для накладання тривимірної графіки чи обробки через шейдери) використовується розширення EGL `EGL_EXT_image_dma_buf_import`:

1. Застосунок передає `dmabuf_fd` у функцію `eglCreateImageKHR()` з апаратно описаними атрибутами `EGL_DMA_BUF_PLANE0_FD_EXT`, `EGL_WIDTH`, `EGL_HEIGHT`, `EGL_LINUX_DRM_FOURCC_EXT`.
2. Графічний драйвер створює `EGLImageKHR`, який зв'язує фізичні сторінки ОЗП із текстурним об'єктом OpenGL ES через `glEGLImageTargetTexture2DOES()`.
3. Рендеринг виконується з нульовим копіюванням: текстурний блок GPU читає байти прямо з фізичних сторінок, куди DMA-контролер V4L2 щойно записав кадр.

---

### 1.4. Прямий вивід на дисплей через DRM/KMS (`drmModeAddFB2WithModifiers`)

Для відображення захопленого кадру на екрані без участі GPU дескриптор DMA-BUF імпортується безпосередньо у дисплейний контролер DRM/KMS:

:::tabs
```c
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <drm_fourcc.h>

uint32_t fb_id = 0;
uint32_t handles[4] = { (uint32_t)dmabuf_fd, 0, 0, 0 };
uint32_t pitches[4] = { 1920 * 2, 0, 0, 0 };
uint32_t offsets[4] = { 0, 0, 0, 0 };

if (drmModeAddFB2(drm_fd, 1920, 1080, DRM_FORMAT_UYVY,
                  handles, pitches, offsets, &fb_id, 0) == 0) {
    /* Атомарне перемикання площини дисплея (Atomic Commit) */
    drmModePageFlip(drm_fd, crtc_id, fb_id, DRM_MODE_PAGE_FLIP_EVENT, NULL);
}
```
```cpp
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <drm_fourcc.h>
#include <system_error>
#include <array>

uint32_t fb_id = 0;
std::array<uint32_t, 4> handles{ static_cast<uint32_t>(dmabuf_fd), 0, 0, 0 };
std::array<uint32_t, 4> pitches{ 1920 * 2, 0, 0, 0 };
std::array<uint32_t, 4> offsets{ 0, 0, 0, 0 };

if (::drmModeAddFB2(drm_fd, 1920, 1080, DRM_FORMAT_UYVY,
                    handles.data(), pitches.data(), offsets.data(), &fb_id, 0) < 0) {
    throw std::system_error(errno, std::generic_category(), "drmModeAddFB2 failed");
}
::drmModePageFlip(drm_fd, crtc_id, fb_id, DRM_MODE_PAGE_FLIP_EVENT, nullptr);
```
:::

---

### 1.5. Міжпроцесна передача DMA-BUF дескрипторів (IPC via SCM_RIGHTS)

У багатьох промислових архітектурах підсистема захоплення відеопрацює у вигляді ізольованого фонового сервісу (Daemon), а рендеринг виконується в окремому процесі графічного інтерфейсу (GUI application). Оскільки файлові дескриптори локальні для кожного процесу, передача `dmabuf_fd` між процесами реалізується через доменні сокети UNIX (`AF_UNIX`) з використанням допоміжних повідомлень `SCM_RIGHTS`:

- Сервіс захоплення відкриває UNIX сокет і викликає `sendmsg()` із структурою `struct cmsghdr`, вказуючи `cmsg_level = SOL_SOCKET` та `cmsg_type = SCM_RIGHTS`.
- Процес GUI приймає повідомлення через `recvmsg()`. Ядро дублює дескриптор у таблицю файлів процесу-отримувача, збільшуючи `refcount` структури `dma_buf`.
- Фізична пам'ять залишається спільною в ОЗП, і процес GUI рендерить кадр без копіювання байтів між процесами.

---

### 1.6. Виділення неперервної пам'яті через dma-heap (`/dev/dma_heap/`)

Сучасні версії ядра Linux (починаючи з 5.6) надають універсальний підсистемний драйвер `dma-heap`, який замінив застарілий Android ION framework:

1. Застосунок відкриває пристрій кучі `/dev/dma_heap/system` або `/dev/dma_heap/reserved-cma`.
2. Виконує ioctl `DMA_HEAP_IOCTL_ALLOC`, задаючи розмір буфера у байтах.
3. Отримує чистий `dma_buf_fd` безпосередньо від аллокатора ядра.
4. Отриманий `dma_buf_fd` передається одночасно у V4L2 (`V4L2_MEMORY_DMABUF`), GPU (EGLImage) та кодек H.264/HEVC. Це забезпечує повний централізований менеджмент пам'яті в користувацькому просторі.

---

## 2. Синхронізація доступу, Cache Coherency та `dma_fence`

У Zero-Copy конвеєрах передача буферів між апаратними блоками (наприклад від камери до GPU) виконується без участі ЦП. Для уникнення гонитви даних (data race) ядро Linux використовує примітив синхронізації **`dma_fence`**.

### 2.1. Апаратні огорожі (`dma_fence`) та Explicit Sync (`sync_file`)

Кожен експортований `dma_buf` містить список об'єктів `dma_fence`. Коли V4L2 ставить кадр у чергу DMA, ядро додає write fence до буфера. Графічний процесор або дисплейний контролер перевіряє стан `dma_fence` і затримує старт апаратного зчитування кадру до моменту, поки V4L2 контролер не згенерує переривання про завершення кадру та не переведе fence у стан "signaled".

Для явного регулювання апаратних огорож у просторі користувача (Explicit Synchronization) використовується ioctl `DMABUF_IOCTL_EXPORT_SYNC_FILE`. Застосунок може витягнути файловий дескриптор `sync_file_fd` з об'єкта `dma_buf` і передати його в атомарний DRM/KMS виклик через властивість `IN_FENCE_FD`. Це дозволяє дисплейному контролеру чекати апаратне завершення кадру V4L2 без участі ЦП і без використання неблокуючих опитувань.

---

### 2.2. Синхронізація кеш-пам'яті ЦП (`DMABUF_IOCTL_SYNC`)

Якщо центральному процесору необхідно прочитати або модифікувати байти кадру безпосередньо через вказівник `mmap`, виникає проблема узгодженості кешу (Cache Coherency). Сучасні процесори (особливо ARMv7 та ARMv64 з некогерентними DMA-шинами) можуть зберігати брудні кеш-лінії у L1/L2 data cache. При спробі ЦП зчитати адреси пам'яті без попереднього інвалідування кешу, процесор поверне застарілі дані з кеш-рядків замість нових пікселів, записаних контролером захоплення у системну ОЗП.

Для безпечного доступу ЦП зобов'язаний обгортати операції читання/запису викликом ioctl `DMABUF_IOCTL_SYNC` із заголовочного файла `<linux/dma-buf.h>`:

:::tabs
```c
#include <linux/dma-buf.h>
#include <sys/ioctl.h>

struct dma_buf_sync sync;
memset(&sync, 0, sizeof(sync));

/* 1. Початок доступу ЦП на читання (Invalidate Cache Lines) */
sync.flags = DMA_BUF_SYNC_START | DMA_BUF_SYNC_READ;
if (ioctl(dmabuf_fd, DMABUF_IOCTL_SYNC, &sync) < 0) {
    perror("DMABUF_IOCTL_SYNC START failed");
}

/* Безпосереднє читання байтів з start */
unsigned char first_byte = ((unsigned char*)buffer_start)[0];

/* 2. Завершення доступу ЦП */
sync.flags = DMA_BUF_SYNC_END | DMA_BUF_SYNC_READ;
ioctl(dmabuf_fd, DMABUF_IOCTL_SYNC, &sync);
```
```cpp
#include <linux/dma-buf.h>
#include <sys/ioctl.h>
#include <system_error>

dma_buf_sync sync{};
sync.flags = DMA_BUF_SYNC_START | DMA_BUF_SYNC_READ;

if (::ioctl(dmabuf_fd, DMABUF_IOCTL_SYNC, &sync) < 0) {
    throw std::system_error(errno, std::generic_category(), "DMABUF_IOCTL_SYNC START failed");
}

// Читання кадрів ЦП у C++
uint8_t first_byte = static_cast<const uint8_t*>(buffer_start)[0];

sync.flags = DMA_BUF_SYNC_END | DMA_BUF_SYNC_READ;
::ioctl(dmabuf_fd, DMABUF_IOCTL_SYNC, &sync);
```
:::

Ігнорування `DMABUF_IOCTL_SYNC` призводить до вичитання застарілих даних із кешу ЦП або перезапису свіжих даних, збережених DMA-контролером.

---

### 2.3. Багатопотокова архітектура Producer-Consumer

У високонавантажених відеосистемах захоплення та обробка виконуються у різних потоках виконання:

- **Capture Thread (Producer):** Виконує неблокуюче очікування `epoll()` на `video_fd`. При отриманні події готовності викликає `VIDIOC_DQBUF`, вичитує індекс та передає дескриптор `dmabuf_fd` у міжпотокову чергу.
- **Render Thread (Consumer):** Отримує `dmabuf_fd` з черги, виконує рендеринг у DRM/KMS або EGL, після чого повертає індекс буфера назад у Capture Thread для виклику `VIDIOC_QBUF`.

Мінімальна кількість буферів для уникнення взаємного блокування потоків (Deadlock) розраховується за формулою:
```
N_buffers >= N_capture_queue + N_render_pipeline + 1
```
Для плавного рендерингу при 60 FPS рекомендується використовувати `N_buffers = 4` або `5`.

---

## 3. Переваги RAII та обробка помилок

При реалізації відеостеків на C++ важливо гарантувати атомарне звільнення ресурсів при виникненні винятків. У системному програмуванні для V4L2 існує три типи ресурсів, які вимагають строго визначеного порядку закриття:
1. **Файлові дескриптори пристроїв (`/dev/media0`, `/dev/v4l2-subdev0`, `/dev/video0`):** Забезпечуються класом `ScopedFd`, який у деструкторі викликає `close()`.
2. **Відображення пам'яті `mmap`:** Забезпечується класом `MmappedBuffer`, який у деструкторі викликає `munmap()`.
3. **Експортовані DMA-BUF дескриптори (`dbuf_fd`):** Зберігаються всередині об'єкта `MmappedBuffer` як вкладений `ScopedFd`.

Порядок руйнування об'єктів у C++ виконується у зворотному порядку їх створення: спочатку скасовується відображення пам'яті та закриваються DMA-BUF дескриптори, і лише потім закриваються дескриптори відеопристроїв. Це гарантує відсутність витоків пам'яті та запобігає виникненню блокувань у драйвері ядра.

---

## 4. Повна реалізація відеоконвеєра

Нижче наведено паралельні реалізації повноцінного Zero-Copy відеоконвеєра на C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <poll.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/media.h>
#include <linux/v4l2-subdev.h>
#include <linux/videodev2.h>
#include <linux/dma-buf.h>

#define BUFFER_COUNT 4

struct buffer {
    void *start;
    size_t length;
    int dbuf_fd;
};

int main(void) {
    int media_fd = -1;
    int subdev_fd = -1;
    int video_fd = -1;
    struct buffer buffers[BUFFER_COUNT];
    memset(buffers, 0, sizeof(buffers));

    /* 1. Відкриття Media Controller та аналіз графа */
    media_fd = open("/dev/media0", O_RDWR);
    if (media_fd < 0) {
        perror("Не вдалося відкрити /dev/media0");
        return EXIT_FAILURE;
    }

    struct media_device_info dev_info;
    memset(&dev_info, 0, sizeof(dev_info));
    if (ioctl(media_fd, MEDIA_IOC_DEVICE_INFO, &dev_info) < 0) {
        perror("MEDIA_IOC_DEVICE_INFO помилка");
        goto cleanup;
    }
    printf("[C] Медіа-пристрій: %s (%s), шина: %s\n", 
           dev_info.driver, dev_info.model, dev_info.bus_info);

    /* 2. Відкриття та налаштування Subdevice Pad Format */
    subdev_fd = open("/dev/v4l2-subdev0", O_RDWR);
    if (subdev_fd < 0) {
        perror("Не вдалося відкрити /dev/v4l2-subdev0");
        goto cleanup;
    }

    struct v4l2_subdev_format fmt;
    memset(&fmt, 0, sizeof(fmt));
    fmt.pad = 0; /* Source pad */
    fmt.which = V4L2_SUBDEV_FORMAT_ACTIVE;
    fmt.format.width = 1920;
    fmt.format.height = 1080;
    fmt.format.code = MEDIA_BUS_FMT_UYVY8_2X8;
    fmt.format.field = V4L2_FIELD_NONE;

    if (ioctl(subdev_fd, VIDIOC_SUBDEV_S_FMT, &fmt) < 0) {
        perror("VIDIOC_SUBDEV_S_FMT помилка");
        goto cleanup;
    }
    printf("[C] Subdev Pad format встановлено: %dx%d (code 0x%x)\n",
           fmt.format.width, fmt.format.height, fmt.format.code);

    /* 3. Відкриття відеовузла захоплення /dev/video0 */
    video_fd = open("/dev/video0", O_RDWR | O_NONBLOCK);
    if (video_fd < 0) {
        perror("Не вдалося відкрити /dev/video0");
        goto cleanup;
    }

    struct v4l2_format vfmt;
    memset(&vfmt, 0, sizeof(vfmt));
    vfmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    vfmt.fmt.pix.width = 1920;
    vfmt.fmt.pix.height = 1080;
    vfmt.fmt.pix.pixelformat = V4L2_PIX_FMT_UYVY;
    vfmt.fmt.pix.field = V4L2_FIELD_NONE;

    if (ioctl(video_fd, VIDIOC_S_FMT, &vfmt) < 0) {
        perror("VIDIOC_S_FMT помилка");
        goto cleanup;
    }

    /* 4. Запит буферів у ядра (REQBUFS) */
    struct v4l2_requestbuffers req;
    memset(&req, 0, sizeof(req));
    req.count = BUFFER_COUNT;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;

    if (ioctl(video_fd, VIDIOC_REQBUFS, &req) < 0) {
        perror("VIDIOC_REQBUFS помилка");
        goto cleanup;
    }

    /* 5. Відображення буферів (mmap) та експорт у DMA-BUF (VIDIOC_EXPBUF) */
    for (size_t i = 0; i < req.count; ++i) {
        struct v4l2_buffer buf;
        memset(&buf, 0, sizeof(buf));
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;

        if (ioctl(video_fd, VIDIOC_QUERYBUF, &buf) < 0) {
            perror("VIDIOC_QUERYBUF помилка");
            goto cleanup;
        }

        buffers[i].length = buf.length;
        buffers[i].start = mmap(NULL, buf.length,
                                PROT_READ | PROT_WRITE,
                                MAP_SHARED, video_fd, buf.m.offset);
        if (buffers[i].start == MAP_FAILED) {
            perror("mmap помилка");
            goto cleanup;
        }

        struct v4l2_exportbuffer expbuf;
        memset(&expbuf, 0, sizeof(expbuf));
        expbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        expbuf.index = i;
        expbuf.flags = O_CLOEXEC | O_RDWR;

        if (ioctl(video_fd, VIDIOC_EXPBUF, &expbuf) < 0) {
            perror("VIDIOC_EXPBUF помилка");
            goto cleanup;
        }
        buffers[i].dbuf_fd = expbuf.fd;
        printf("[C] Буфер %zu експортовано як dma-buf fd: %d\n", i, expbuf.fd);
    }

    /* 6. Постановка буферів у чергу та запуск відеопотоку */
    for (size_t i = 0; i < req.count; ++i) {
        struct v4l2_buffer buf;
        memset(&buf, 0, sizeof(buf));
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;
        if (ioctl(video_fd, VIDIOC_QBUF, &buf) < 0) {
            perror("VIDIOC_QBUF помилка");
            goto cleanup;
        }
    }

    enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (ioctl(video_fd, VIDIOC_STREAMON, &type) < 0) {
        perror("VIDIOC_STREAMON помилка");
        goto cleanup;
    }

    /* 7. Очікування та вилучення одного кадру (poll + DQBUF) */
    struct pollfd pfd;
    pfd.fd = video_fd;
    pfd.events = POLLIN;

    int poll_res = poll(&pfd, 1, 2000);
    if (poll_res > 0 && (pfd.revents & POLLIN)) {
        struct v4l2_buffer dqbuf;
        memset(&dqbuf, 0, sizeof(dqbuf));
        dqbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        dqbuf.memory = V4L2_MEMORY_MMAP;

        if (ioctl(video_fd, VIDIOC_DQBUF, &dqbuf) < 0) {
            perror("VIDIOC_DQBUF помилка");
            goto cleanup;
        }
        printf("[C] Захоплено кадр №%u, розмір: %u байт\n", dqbuf.sequence, dqbuf.bytesused);

        /* Синхронізація кешу ЦП перед читанням перших байтів */
        struct dma_buf_sync dsync;
        memset(&dsync, 0, sizeof(dsync));
        dsync.flags = DMA_BUF_SYNC_START | DMA_BUF_SYNC_READ;
        ioctl(buffers[dqbuf.index].dbuf_fd, DMABUF_IOCTL_SYNC, &dsync);

        printf("[C] Перші байти кадру: %02x %02x %02x %02x\n",
               ((unsigned char*)buffers[dqbuf.index].start)[0],
               ((unsigned char*)buffers[dqbuf.index].start)[1],
               ((unsigned char*)buffers[dqbuf.index].start)[2],
               ((unsigned char*)buffers[dqbuf.index].start)[3]);

        dsync.flags = DMA_BUF_SYNC_END | DMA_BUF_SYNC_READ;
        ioctl(buffers[dqbuf.index].dbuf_fd, DMABUF_IOCTL_SYNC, &dsync);
    }

    /* Зупинка потоку */
    ioctl(video_fd, VIDIOC_STREAMOFF, &type);

cleanup:
    for (size_t i = 0; i < BUFFER_COUNT; ++i) {
        if (buffers[i].dbuf_fd >= 0) close(buffers[i].dbuf_fd);
        if (buffers[i].start && buffers[i].start != MAP_FAILED) {
            munmap(buffers[i].start, buffers[i].length);
        }
    }
    if (video_fd >= 0) close(video_fd);
    if (subdev_fd >= 0) close(subdev_fd);
    if (media_fd >= 0) close(media_fd);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/media.h>
#include <linux/v4l2-subdev.h>
#include <linux/videodev2.h>
#include <linux/dma-buf.h>

// RAII обгортка для файлового дескриптора пристрою
class ScopedFd {
    int fd_{-1};
public:
    explicit ScopedFd(int fd = -1) : fd_(fd) {}
    ~ScopedFd() { reset(); }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;

    ScopedFd(ScopedFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

// RAII обгортка для відображеного в пам'ять V4L2 буфера
class MmappedBuffer {
    void* start_{MAP_FAILED};
    size_t length_{0};
    ScopedFd dbuf_fd_;

public:
    MmappedBuffer() = default;
    MmappedBuffer(void* start, size_t length, ScopedFd dbuf_fd)
        : start_(start), length_(length), dbuf_fd_(std::move(dbuf_fd)) {}

    ~MmappedBuffer() {
        if (start_ != MAP_FAILED && start_ != nullptr) {
            ::munmap(start_, length_);
        }
    }

    MmappedBuffer(const MmappedBuffer&) = delete;
    MmappedBuffer& operator=(const MmappedBuffer&) = delete;

    MmappedBuffer(MmappedBuffer&&) noexcept = default;
    MmappedBuffer& operator=(MmappedBuffer&&) noexcept = default;

    [[nodiscard]] void* data() const noexcept { return start_; }
    [[nodiscard]] size_t size() const noexcept { return length_; }
    [[nodiscard]] int dmabuf_fd() const noexcept { return dbuf_fd_.get(); }
};

class V4L2ZeroCopyPipeline {
    ScopedFd media_fd_;
    ScopedFd subdev_fd_;
    ScopedFd video_fd_;
    std::vector<MmappedBuffer> buffers_;

    static void check_ioctl(int res, const std::string& msg) {
        if (res < 0) {
            throw std::system_error(errno, std::generic_category(), msg);
        }
    }

public:
    void open_devices(const std::string& media_dev,
                      const std::string& subdev_dev,
                      const std::string& video_dev) {
        media_fd_.reset(::open(media_dev.c_str(), O_RDWR));
        check_ioctl(media_fd_.valid() ? 0 : -1, "Відкриття " + media_dev);

        subdev_fd_.reset(::open(subdev_dev.c_str(), O_RDWR));
        check_ioctl(subdev_fd_.valid() ? 0 : -1, "Відкриття " + subdev_dev);

        video_fd_.reset(::open(video_dev.c_str(), O_RDWR | O_NONBLOCK));
        check_ioctl(video_fd_.valid() ? 0 : -1, "Відкриття " + video_dev);
    }

    void configure_subdev_format(uint32_t pad, uint32_t width, uint32_t height, uint32_t mbus_code) {
        struct v4l2_subdev_format fmt{};
        fmt.pad = pad;
        fmt.which = V4L2_SUBDEV_FORMAT_ACTIVE;
        fmt.format.width = width;
        fmt.format.height = height;
        fmt.format.code = mbus_code;
        fmt.format.field = V4L2_FIELD_NONE;

        check_ioctl(::ioctl(subdev_fd_.get(), VIDIOC_SUBDEV_S_FMT, &fmt), "VIDIOC_SUBDEV_S_FMT");
        std::cout << "[V4L2 C++] Subdev pad format: " << fmt.format.width << "x" << fmt.format.height << "\n";
    }

    void setup_buffers_and_export(size_t buffer_count) {
        struct v4l2_format vfmt{};
        vfmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        vfmt.fmt.pix.width = 1920;
        vfmt.fmt.pix.height = 1080;
        vfmt.fmt.pix.pixelformat = V4L2_PIX_FMT_UYVY;
        vfmt.fmt.pix.field = V4L2_FIELD_NONE;

        check_ioctl(::ioctl(video_fd_.get(), VIDIOC_S_FMT, &vfmt), "VIDIOC_S_FMT");

        struct v4l2_requestbuffers req{};
        req.count = static_cast<uint32_t>(buffer_count);
        req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        req.memory = V4L2_MEMORY_MMAP;

        check_ioctl(::ioctl(video_fd_.get(), VIDIOC_REQBUFS, &req), "VIDIOC_REQBUFS");
        buffers_.reserve(req.count);

        for (uint32_t i = 0; i < req.count; ++i) {
            struct v4l2_buffer buf{};
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            buf.memory = V4L2_MEMORY_MMAP;
            buf.index = i;

            check_ioctl(::ioctl(video_fd_.get(), VIDIOC_QUERYBUF, &buf), "VIDIOC_QUERYBUF");

            void* ptr = ::mmap(nullptr, buf.length, PROT_READ | PROT_WRITE, MAP_SHARED, video_fd_.get(), buf.m.offset);
            if (ptr == MAP_FAILED) {
                throw std::system_error(errno, std::generic_category(), "mmap бувера");
            }

            struct v4l2_exportbuffer expbuf{};
            expbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            expbuf.index = i;
            expbuf.flags = O_CLOEXEC | O_RDWR;

            check_ioctl(::ioctl(video_fd_.get(), VIDIOC_EXPBUF, &expbuf), "VIDIOC_EXPBUF");

            buffers_.emplace_back(ptr, buf.length, ScopedFd(expbuf.fd));
            std::cout << "[V4L2 C++] Буфер " << i << " mmapped (" << buf.length
                      << " байт), DMABUF FD: " << expbuf.fd << "\n";
        }
    }

    void capture_frame() {
        for (uint32_t i = 0; i < buffers_.size(); ++i) {
            struct v4l2_buffer buf{};
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            buf.memory = V4L2_MEMORY_MMAP;
            buf.index = i;
            check_ioctl(::ioctl(video_fd_.get(), VIDIOC_QBUF, &buf), "VIDIOC_QBUF");
        }

        enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        check_ioctl(::ioctl(video_fd_.get(), VIDIOC_STREAMON, &type), "VIDIOC_STREAMON");

        pollfd pfd{};
        pfd.fd = video_fd_.get();
        pfd.events = POLLIN;

        int poll_res = ::poll(&pfd, 1, 2000);
        if (poll_res > 0 && (pfd.revents & POLLIN)) {
            struct v4l2_buffer dqbuf{};
            dqbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            dqbuf.memory = V4L2_MEMORY_MMAP;
            check_ioctl(::ioctl(video_fd_.get(), VIDIOC_DQBUF, &dqbuf), "VIDIOC_DQBUF");

            std::cout << "[V4L2 C++] Захоплено кадр " << dqbuf.sequence
                      << " розміром " << dqbuf.bytesused << " байт\n";

            dma_buf_sync dsync{};
            dsync.flags = DMA_BUF_SYNC_START | DMA_BUF_SYNC_READ;
            check_ioctl(::ioctl(buffers_[dqbuf.index].dmabuf_fd(), DMABUF_IOCTL_SYNC, &dsync), "DMABUF_SYNC START");

            std::cout << "[V4L2 C++] CPU Sync OK\n";

            dsync.flags = DMA_BUF_SYNC_END | DMA_BUF_SYNC_READ;
            check_ioctl(::ioctl(buffers_[dqbuf.index].dmabuf_fd(), DMABUF_IOCTL_SYNC, &dsync), "DMABUF_SYNC END");
        } else {
            std::cerr << "[V4L2 C++] Таймаут очікування кадру\n";
        }

        check_ioctl(::ioctl(video_fd_.get(), VIDIOC_STREAMOFF, &type), "VIDIOC_STREAMOFF");
    }
};

int main() {
    try {
        V4L2ZeroCopyPipeline pipeline;
        pipeline.open_devices("/dev/media0", "/dev/v4l2-subdev0", "/dev/video0");
        pipeline.configure_subdev_format(0, 1920, 1080, MEDIA_BUS_FMT_UYVY8_2X8);
        pipeline.setup_buffers_and_export(4);
        pipeline.capture_frame();
    } catch (const std::exception& ex) {
        std::cerr << "Помилка конвеєра: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

---

## 5. Аналіз крайових випадків та переривань (Edge Cases & Failure Recovery)

При реалізації даної послідовності викликів у реальних виробничих проєктах необхідно враховувати декілька критичних аспектів роботи ядра Linux:

### 5.1. Узгодження розширення та кроків пам'яті (Bytes Per Line)

При налаштуванні `VIDIOC_S_FMT` ядро може повернути значення `bytesperline`, яке перевищує чисте значення `width * bytes_per_pixel`. Це відбувається через вимоги апаратного вирівнювання ліній в ОЗП (наприклад, вирівнювання по межі 64, 128 або 256 байтів для DMA-контролерів таких SoC, як Allwinner чи Rockchip). 

Ігнорування поля `bytesperline` та розрахунок зсуву рядків як `y * width * bpp` призводить до "діагонального зсуву" та кольорового спотворення кадру при спробі відображення. Правильний зсув рядка `y` розраховується строго як:
```
offset = y * bytesperline
```

---

### 5.2. Порядок закриття ресурсів та витоки dma-buf

Скасування відображення пам'яті (`munmap`) та закриття файлових дескрипторів DMA-BUF (`dbuf_fd`) має здійснюватися **до** закриття основного файлового дескриптора пристрою `/dev/video0` та перед викликом `VIDIOC_REQBUFS` з `count = 0`. В іншому випадку ядро поверне помилку `EBUSY` при спробі звільнити буфери, оскільки лічильник посилань на об'єкт `dma_buf` залишатиметься ненульовим.

---

### 5.3. Переповнення кольорових черг (Buffer Underrun & Frame Dropping)

Якщо споживач відеокадрів (наприклад кодек H.264 чи алгоритм нейромережі) не встигає викликати `VIDIOC_DQBUF` з такою ж частотою, з якою сенсор генерує кадри, всі буфери у кільцевій черзі швидко переходять у стан `V4L2_BUF_FLAG_DONE`. При надходженні наступного кадру драйвер ядра не має вільних буферів і змушений повністю відкинути новий кадр (Frame Drop).

Для виявлення дропів кадрів застосунок зобов'язаний відстежувати монотонний ідентифікатор `dqbuf.sequence`. Якщо між двома викликами `DQBUF` різниця `seq_new - seq_old > 1`, це свідчить про пропущені кадри через затримки обробки в просторі користувача.

---

### 5.4. Динамічне переналагодження графа (Dynamic Reconfiguration)

При зміні режимів роботи камери (наприклад при перемиканні роздільної здатності кадру в режимі реального часу) сенсор посилає подія `V4L2_EVENT_SOURCE_CHANGE`. Конвеєр повинен виконати таку послідовність дій:
1. Викликати `VIDIOC_STREAMOFF` для зупинки поточного DMA.
2. Закрити всі експортовані `dbuf_fd` дескриптори та виконати `munmap()`.
3. Викликати `VIDIOC_REQBUFS` з `count = 0` для очищення черги ядра.
4. Встановити нові формати через `VIDIOC_SUBDEV_S_FMT` та `VIDIOC_S_FMT`.
5. Повторно виділити та експортувати буфери і перезапустити потік через `VIDIOC_STREAMON`.

---

### 5.5. Низькорівневе простеження сторінок пам'яті та IOMMU

У сучасних вбудованих системах (наприклад ARM64 SoC із контролерами IOMMU) апаратний блок відеозахоплення бачить не фізичну ОЗП, а віртуальний адресний простір bus addresses, створений через IOMMU. При виконанні імпорту DMA-BUF драйвер ядра будує Scatter-Gather таблицю (`struct sg_table`) та заповнює IOMMU page tables.

Для стабільної роботи конвеєра при високих роздільних здатностях (4K@60) важливо мінімізувати фрагментацію IOMMU TLB кешу. Використання алокатора CMA (Contiguous Memory Allocator) виділяє єдиний неперервний блок фізичних сторінок, що зменшує кількість записів в IOMMU до 1 сторінки великого розміру (Huge Page), знижуючи затримки DMA-транзакцій.

---

### 5.6. Обробка гарячого відключення пристрою (Hot-Unplug Handling)

При фізичному від'єднанні пристрою (наприклад, витягуванні USB-камери чи апаратному збої MIPI-шини) системний виклик `ioctl(video_fd, VIDIOC_DQBUF, ...)` або `poll()` миттєво повертає помилку `-1` із значенням `errno = ENODEV` ("No such device").

Промисловий відеоконвеєр повинен обробляти цей випадок наступним чином:
1. Видалити `video_fd` з інстансу `epoll`.
2. Скасувати всі `mmap()` відображення для виділених буферів та закрити `dbuf_fd`.
3. Закрити `video_fd`, `subdev_fd` та `media_fd`.
4. Перевести програму у стан очікування відновлення символьних файлів пристроїв у системі через `udev` або inotify моніторинг `/dev/v4l2/`.

---

### 5.7. Багатопланарний експорт буферів у Multi-Planar API (`V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE`)

При використанні розділених планарних форматів (наприклад NV12, де площина Y зберігається окремо від суміщеної площини UV) виклик `VIDIOC_EXPBUF` виконується для кожної площини окремо:

```c
struct v4l2_exportbuffer expbuf;
int plane_fds[2];

for (int p = 0; p < 2; ++p) {
    memset(&expbuf, 0, sizeof(expbuf));
    expbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
    expbuf.index = buffer_index;
    expbuf.plane = p; /* 0 for Y, 1 for UV */
    expbuf.flags = O_CLOEXEC | O_RDWR;
    
    if (ioctl(video_fd, VIDIOC_EXPBUF, &expbuf) == 0) {
        plane_fds[p] = expbuf.fd;
    }
}
```

Отриманий масив `plane_fds` передається у EGLImage через атрибути `EGL_DMA_BUF_PLANE0_FD_EXT` та `EGL_DMA_BUF_PLANE1_FD_EXT`, що забезпечує апаратний декодинг і рендеринг планарних кадрів без злиття площин у пам'яті RAM.

---

### 5.8. Апаратні часові мітки та синхронізація PTP / IEEE 1588

Для промислових та автомобільних систем (LiDAR + камери в автономному водінні) критично мати точну часову прив'язку моменту зйомки кадру до системного годинника реального часу `CLOCK_REALTIME` або мережевого протоколу PTP (Precision Time Protocol):

- При виклику `VIDIOC_DQBUF` ядро заповнює структуру `struct timeval timestamp` у структурі `struct v4l2_buffer`.
- Прапорець `V4L2_BUF_FLAG_TIMESTAMP_MONOTONIC` гарантує, що значення часу взято від системного таймера `CLOCK_MONOTONIC` і не піддається стрибкам часу NTP.
- Прапорець `V4L2_BUF_FLAG_TIMESTAMP_SRC_SOE` зазначає, що таймстамп згенеровано апаратно у момент початку випромінювання сенсора (Start of Exposure), що усуває затримки передачі даних по шині MIPI CSI-2.

---

## 6. Порівняльний розбір режимів виділення та обміну буферами

| Параметр | `V4L2_MEMORY_MMAP` (Export) | `V4L2_MEMORY_DMABUF` (Import) | `V4L2_MEMORY_USERPTR` (Legacy) |
|---|---|---|---|
| **Аллокатор пам'яті** | Драйвер ядра V4L2 (CMA / vb2) | Зовнішній драйвер (DRM/KMS/GBM/dma-heap) | Користувацький простір (`posix_memalign`) |
| **Експорт у Zero-Copy** | Підтримується (`VIDIOC_EXPBUF`) | Вже є Zero-Copy за визначенням | Не підтримується |
| **Оверхед на pinning сторінок** | Відсутній (сторінки виділені заздалегідь) | Відсутній (структура `dma_buf` вже закріплена) | Високий (виклик `get_user_pages()` при кожному QBUF) |
| **Сумісність з GPU / DRM** | Ідеальна (через `dma_buf_fd`) | Ідеальна (прямий запис у framebuffers) | Обмежена (вимагає додаткових мапінгів) |
| **Рекомендоване застосування** | Високопродуктивне камери та ISP | Прямий вивід на дисплей чи кодек | Застаріле ПЗ без підтримки DMA-BUF |

---

## 7. Простеження та діагностика відеоконвеєра

Для налагодження Zero-Copy відеоконвеєра у Linux використовуються такі системні інструменти:

1. **Консольні утиліти `v4l-utils`:**
   - Перевірка топології: `media-ctl -p -d /dev/media0`
   - Перевірка формату на майданчику: `media-ctl -d /dev/media0 --get-v4l2 '"imx219 1-0010":0'`
   - Захоплення тестових кадрів з перевіркою mmap: `v4l2-ctl -d /dev/video0 --stream-mmap --stream-count=10`

2. **Ядерне простеження tracepoints (`ftrace`):**
   Для аналізу часу обробки переривань та станів `vb2_buffer` ввімкніть відповідні події ftrace:
   ```bash
   echo 1 > /sys/kernel/debug/tracing/events/vb2/enable
   cat /sys/kernel/debug/tracing/trace_pipe
   ```
   Це дозволяє побачити точний час входу буфера у DMA та момент виклику callback-функцій `.buf_queue` і `.buf_finish` у драйвері ядра.
