# ⚙️ Практика M2M: апаратне масштабування та конвертація формату

Апаратні модулі двовимірної обробки зображень (2D Scaler, Color Space Converter, Rotator) є невіддільною частиною сучасних однокристальних систем на базі архітектур ARM, RISC-V та x86 (сімейства NXP i.MX, Allwinner, Rockchip, TI Sitara, Intel Atom). У ядрі Linux такі блоки реєструються як символьні вузли V4L2 M2M (наприклад, `/dev/video10`).

Головне завдання такого прискорювача — виконання потокової зміни роздільності (Downscaling / Upscaling) та перетворення формату пікселів (наприклад, щільного формату камери `YUYV` 1920×1080 у напівпланарний `NV12` 640×480) у режимі реального часу з мінімальною затримкою та нульовим навантаженням на центральний процесор.

## Архітектурний контракт програми з M2M-вузлом

Робота програми користувацького простору з пристроєм M2M підпорядковується чіткому протоколу взаємодії з двома чергами `videobuf2`:

1. **Відкриття вузла та валідація:** Пристрій відкривається викликом `open("/dev/video10", O_RDWR | O_NONBLOCK)`. Обов'язково перевіряється наявність прапорця `V4L2_CAP_VIDEO_M2M` або `V4L2_CAP_VIDEO_M2M_MPLANE` у структурі `v4l2_capability`.
2. **Конфігурація геометрії черги OUTPUT:** Черга `OUTPUT` приймає вхідні кадри. Викликом `VIDIOC_S_FMT` задаються ширина, висота та формат пікселів джерела (1920×1080 YUYV). Драйвер обчислює крок рядка (`bytesperline`) та загальний розмір буфера (`sizeimage`) з урахуванням апаратних обмежень вирівнювання пам'яті.
3. **Конфігурація геометрії черги CAPTURE:** Черга `CAPTURE` видає оброблені кадри. Викликом `VIDIOC_S_FMT` задаються бажані цільові параметри (640×480 NV12).
4. **Виділення пулу буферів:** Для кожної черги викликається `VIDIOC_REQBUFS` з типом пам'яті `V4L2_MEMORY_MMAP`. Драйвер виділяє фізично суцільні області пам'яті під кадри.
5. **Відображення в адресний простір (mmap):** Для кожного виділеного буфера надсилається запит `VIDIOC_QUERYBUF` для отримання зсуву пам'яті (`buf.m.offset`), після чого викликається системний виклик `mmap()`.
6. **Подача вхідних даних:** Вхідний буфер заповнюється пікселями, встановлюється поле `bytesused`, і буфер ставиться в чергу `OUTPUT` за допомогою `VIDIOC_QBUF`.
7. **Подача порожнього приймача:** Порожній буфер ставиться в чергу `CAPTURE` за допомогою `VIDIOC_QBUF`.
8. **Активація конвеєра:** Надсилаються команди `VIDIOC_STREAMON` для обох черг. Планувальник ядра `v4l2-mem2mem` бачить наявність буферів у обох чергах, бере м'ютекс апаратури та запускає апаратний блок обробки.
9. **Очікування та вилучення результату:** Програма очікує завершення апаратної операції через системний виклик `poll()` (подія `POLLIN`). Коли дескриптор стає читним, викликається `VIDIOC_DQBUF` для черги `CAPTURE` для отримання готового результату та `VIDIOC_DQBUF` для черги `OUTPUT` для вивільнення вхідного буфера.
10. **Зупинка та звільнення ресурсів:** Потоки зупиняються викликами `VIDIOC_STREAMOFF`, пам'ять звільняється через `munmap()`, а дескриптор закривається.

## Розрахунок геометрії та вирівнювання рядків

Під час налаштування форматів пікселів важливо враховувати, що апаратні контролери DMA вимагають вирівнювання рядків пам'яті по межах 16, 32 або 64 байтів.

Для вхідного кадру YUYV (2 байти на піксель) при ширині 1920 точок розмір рядка становить:
```
довжина рядка (stride) = 1920 · 2 = 3840 байтів (кратне 64)
загальний обсяг кадру   = 3840 · 1080 = 4 147 200 байтів ≈ 4.15 МБ
```

Для вихідного кадру NV12 (1.5 байта на піксель) при роздільності 640×480:
```
площина яскравості Y   = 640 · 480 = 307 200 байтів
площина кольоровості UV = 640 · 240 = 153 600 байтів
загальний обсяг кадру   = 307 200 + 153 600 = 460 800 байтів ≈ 450 КБ
```

Драйвер ядра самостійно коригує поля `bytesperline` та `sizeimage` у відповіді на `VIDIOC_S_FMT`. Програма завжди повинна використовувати значення, повернуті ядром, а не розраховані вручну константи.

## Організація кільцевого пулу буферів (Pipelining)

У демонстраційному прикладі для простоти виділено по одному буферу на кожну чергу (синхронна робота «кадр за кадром»). Проте в реальних високонавантажених відеопотоках (30–60 кадрів на секунду) така схема створює простої кремнію: поки процесор заповнює вхідний буфер або зчитує вихідний кадр, прискорювач очікує.

Професійна архітектура вимагає кільцевого пулу щонайменше з 3–4 буферів на кожній черзі:
* **Буфер N:** обробляється апаратним блоком DMA в поточний момент.
* **Буфер N+1:** уже стоїть у черзі ядра, готовий до миттєвого підхоплення планувальником M2M.
* **Буфер N-1:** вилучений користувацьким процесом (`DQBUF`) і передається на рендеринг або кодування.

Завдяки паралелізму обробка кадрів стає безперервною, а затримка конвеєра знижується до апаратного мінімуму. Якщо під час виклику `VIDIOC_DQBUF` у неблокуючому режимі в черзі немає готового кадру, ядро повертає код помилки `EAGAIN` (або `EWOULDBLOCK`), що вказує на необхідність повторного очікування через `poll()`.

Коректна обробка сигналів завершення програми (`SIGINT`, `SIGTERM`) вимагає негайного виклику `VIDIOC_STREAMOFF` на обох чергах: це сигналізує ядру про необхідність переривання активного апаратного завдання через зворотний виклик `job_abort` та повертає всі буфери в стан вилучення без блокування процесу.

## Повна реалізація конвеєра на C та C++

Нижче наведено робочий приклад програми масштабування синтетичного кадру за допомогою M2M-пристрою двома мовами програмування. У вкладці C++ реалізовано патерн RAII: дескриптор файлу, виділені буфери `mmap` та стан потоків керуються автоматично деструкторами класу.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <poll.h>
#include <linux/videodev2.h>

#define SRC_W 1920
#define SRC_H 1080
#define DST_W 640
#define DST_H 480

struct buffer_info {
    void *start;
    size_t length;
};

static int xioctl(int fd, unsigned long request, void *arg) {
    int r;
    do {
        r = ioctl(fd, request, arg);
    } while (r == -1 && errno == EINTR);
    return r;
}

int main(int argc, char **argv) {
    const char *dev_name = (argc > 1) ? argv[1] : "/dev/video10";
    int fd = open(dev_name, O_RDWR | O_NONBLOCK);
    if (fd < 0) {
        perror("Не вдалося відкрити пристрій V4L2 M2M");
        return EXIT_FAILURE;
    }

    struct v4l2_capability cap;
    memset(&cap, 0, sizeof(cap));
    if (xioctl(fd, VIDIOC_QUERYCAP, &cap) < 0) {
        perror("VIDIOC_QUERYCAP помилка");
        close(fd);
        return EXIT_FAILURE;
    }

    if (!(cap.capabilities & (V4L2_CAP_VIDEO_M2M | V4L2_CAP_STREAMING))) {
        fprintf(stderr, "Пристрій не підтримує інтерфейс V4L2 M2M потоків\n");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 1. Налаштування формату черги OUTPUT (Вхідні дані) */
    struct v4l2_format fmt_out;
    memset(&fmt_out, 0, sizeof(fmt_out));
    fmt_out.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;
    fmt_out.fmt.pix.width = SRC_W;
    fmt_out.fmt.pix.height = SRC_H;
    fmt_out.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
    fmt_out.fmt.pix.field = V4L2_FIELD_NONE;
    if (xioctl(fd, VIDIOC_S_FMT, &fmt_out) < 0) {
        perror("Помилка встановлення формату OUTPUT");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 2. Налаштування формату черги CAPTURE (Вихідні дані) */
    struct v4l2_format fmt_cap;
    memset(&fmt_cap, 0, sizeof(fmt_cap));
    fmt_cap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    fmt_cap.fmt.pix.width = DST_W;
    fmt_cap.fmt.pix.height = DST_H;
    fmt_cap.fmt.pix.pixelformat = V4L2_PIX_FMT_NV12;
    fmt_cap.fmt.pix.field = V4L2_FIELD_NONE;
    if (xioctl(fd, VIDIOC_S_FMT, &fmt_cap) < 0) {
        perror("Помилка встановлення формату CAPTURE");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 3. Виділення буферів для черги OUTPUT */
    struct v4l2_requestbuffers req_out;
    memset(&req_out, 0, sizeof(req_out));
    req_out.count = 1;
    req_out.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;
    req_out.memory = V4L2_MEMORY_MMAP;
    if (xioctl(fd, VIDIOC_REQBUFS, &req_out) < 0) {
        perror("Помилка REQBUFS OUTPUT");
        close(fd);
        return EXIT_FAILURE;
    }

    struct v4l2_buffer buf_out;
    memset(&buf_out, 0, sizeof(buf_out));
    buf_out.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;
    buf_out.memory = V4L2_MEMORY_MMAP;
    buf_out.index = 0;
    if (xioctl(fd, VIDIOC_QUERYBUF, &buf_out) < 0) {
        perror("Помилка QUERYBUF OUTPUT");
        close(fd);
        return EXIT_FAILURE;
    }

    struct buffer_info src_buf;
    src_buf.length = buf_out.length;
    src_buf.start = mmap(NULL, buf_out.length, PROT_READ | PROT_WRITE, MAP_SHARED, fd, buf_out.m.offset);
    if (src_buf.start == MAP_FAILED) {
        perror("Помилка mmap OUTPUT");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 4. Виділення буферів для черги CAPTURE */
    struct v4l2_requestbuffers req_cap;
    memset(&req_cap, 0, sizeof(req_cap));
    req_cap.count = 1;
    req_cap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req_cap.memory = V4L2_MEMORY_MMAP;
    if (xioctl(fd, VIDIOC_REQBUFS, &req_cap) < 0) {
        perror("Помилка REQBUFS CAPTURE");
        munmap(src_buf.start, src_buf.length);
        close(fd);
        return EXIT_FAILURE;
    }

    struct v4l2_buffer buf_cap;
    memset(&buf_cap, 0, sizeof(buf_cap));
    buf_cap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf_cap.memory = V4L2_MEMORY_MMAP;
    buf_cap.index = 0;
    if (xioctl(fd, VIDIOC_QUERYBUF, &buf_cap) < 0) {
        perror("Помилка QUERYBUF CAPTURE");
        munmap(src_buf.start, src_buf.length);
        close(fd);
        return EXIT_FAILURE;
    }

    struct buffer_info dst_buf;
    dst_buf.length = buf_cap.length;
    dst_buf.start = mmap(NULL, buf_cap.length, PROT_READ | PROT_WRITE, MAP_SHARED, fd, buf_cap.m.offset);
    if (dst_buf.start == MAP_FAILED) {
        perror("Помилка mmap CAPTURE");
        munmap(src_buf.start, src_buf.length);
        close(fd);
        return EXIT_FAILURE;
    }

    /* 5. Заповнення вхідного буфера тестовим шаблоном (сірий колір) */
    memset(src_buf.start, 0x80, src_buf.length);
    buf_out.bytesused = src_buf.length;
    if (xioctl(fd, VIDIOC_QBUF, &buf_out) < 0) {
        perror("Помилка QBUF OUTPUT");
        goto cleanup;
    }

    /* 6. Постановка порожнього буфера в CAPTURE */
    if (xioctl(fd, VIDIOC_QBUF, &buf_cap) < 0) {
        perror("Помилка QBUF CAPTURE");
        goto cleanup;
    }

    /* 7. Запуск потоків */
    enum v4l2_buf_type type_out = V4L2_BUF_TYPE_VIDEO_OUTPUT;
    enum v4l2_buf_type type_cap = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (xioctl(fd, VIDIOC_STREAMON, &type_out) < 0 || xioctl(fd, VIDIOC_STREAMON, &type_cap) < 0) {
        perror("Помилка STREAMON");
        goto cleanup;
    }

    /* 8. Очікування виконання через poll() */
    struct pollfd pfd;
    pfd.fd = fd;
    pfd.events = POLLIN;
    int ret = poll(&pfd, 1, 2000); /* тайм-аут 2000 мс */
    if (ret <= 0) {
        fprintf(stderr, "Тайм-аут або збій апаратного прискорювача\n");
        goto cleanup;
    }

    /* 9. Вилучення готових буферів */
    if (xioctl(fd, VIDIOC_DQBUF, &buf_cap) < 0) {
        perror("Помилка DQBUF CAPTURE");
        goto cleanup;
    }
    printf("Кадр успішно оброблено! Отримано %u байтів у форматі NV12 640x480\n", buf_cap.bytesused);

    if (xioctl(fd, VIDIOC_DQBUF, &buf_out) < 0) {
        perror("Помилка DQBUF OUTPUT");
    }

cleanup:
    xioctl(fd, VIDIOC_STREAMOFF, &type_out);
    xioctl(fd, VIDIOC_STREAMOFF, &type_cap);
    munmap(src_buf.start, src_buf.length);
    munmap(dst_buf.start, dst_buf.length);
    close(fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <system_error>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <poll.h>
#include <linux/videodev2.h>

class M2MScalerDevice {
public:
    explicit M2MScalerDevice(const std::string &dev_path) {
        fd_ = ::open(dev_path.c_str(), O_RDWR | O_NONBLOCK);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити пристрій M2M");
        }
    }

    ~M2MScalerDevice() {
        stop_streaming();
        unmap_buffers();
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    // Заборона копіювання для збереження коректності володіння дескриптором
    M2MScalerDevice(const M2MScalerDevice &) = delete;
    M2MScalerDevice &operator=(const M2MScalerDevice &) = delete;

    void configure_formats(uint32_t src_w, uint32_t src_h, uint32_t dst_w, uint32_t dst_h) {
        v4l2_format fmt_out{};
        fmt_out.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;
        fmt_out.fmt.pix.width = src_w;
        fmt_out.fmt.pix.height = src_h;
        fmt_out.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
        fmt_out.fmt.pix.field = V4L2_FIELD_NONE;
        send_ioctl(VIDIOC_S_FMT, &fmt_out, "Помилка встановлення формату OUTPUT");

        v4l2_format fmt_cap{};
        fmt_cap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        fmt_cap.fmt.pix.width = dst_w;
        fmt_cap.fmt.pix.height = dst_h;
        fmt_cap.fmt.pix.pixelformat = V4L2_PIX_FMT_NV12;
        fmt_cap.fmt.pix.field = V4L2_FIELD_NONE;
        send_ioctl(VIDIOC_S_FMT, &fmt_cap, "Помилка встановлення формату CAPTURE");
    }

    void allocate_and_mmap() {
        // Виділення та відображення вхідного буфера OUTPUT
        v4l2_requestbuffers req_out{};
        req_out.count = 1;
        req_out.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;
        req_out.memory = V4L2_MEMORY_MMAP;
        send_ioctl(VIDIOC_REQBUFS, &req_out, "Помилка REQBUFS OUTPUT");

        v4l2_buffer buf_out{};
        buf_out.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;
        buf_out.memory = V4L2_MEMORY_MMAP;
        buf_out.index = 0;
        send_ioctl(VIDIOC_QUERYBUF, &buf_out, "Помилка QUERYBUF OUTPUT");

        out_len_ = buf_out.length;
        out_ptr_ = ::mmap(nullptr, out_len_, PROT_READ | PROT_WRITE, MAP_SHARED, fd_, buf_out.m.offset);
        if (out_ptr_ == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "Помилка mmap OUTPUT");
        }

        // Виділення та відображення вихідного буфера CAPTURE
        v4l2_requestbuffers req_cap{};
        req_cap.count = 1;
        req_cap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        req_cap.memory = V4L2_MEMORY_MMAP;
        send_ioctl(VIDIOC_REQBUFS, &req_cap, "Помилка REQBUFS CAPTURE");

        v4l2_buffer buf_cap{};
        buf_cap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf_cap.memory = V4L2_MEMORY_MMAP;
        buf_cap.index = 0;
        send_ioctl(VIDIOC_QUERYBUF, &buf_cap, "Помилка QUERYBUF CAPTURE");

        cap_len_ = buf_cap.length;
        cap_ptr_ = ::mmap(nullptr, cap_len_, PROT_READ | PROT_WRITE, MAP_SHARED, fd_, buf_cap.m.offset);
        if (cap_ptr_ == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "Помилка mmap CAPTURE");
        }
    }

    void process_single_frame() {
        // Заповнення вхідного буфера тестовими даними
        std::memset(out_ptr_, 0x7F, out_len_);

        v4l2_buffer buf_out{};
        buf_out.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;
        buf_out.memory = V4L2_MEMORY_MMAP;
        buf_out.index = 0;
        buf_out.bytesused = out_len_;
        send_ioctl(VIDIOC_QBUF, &buf_out, "Помилка QBUF OUTPUT");

        v4l2_buffer buf_cap{};
        buf_cap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf_cap.memory = V4L2_MEMORY_MMAP;
        buf_cap.index = 0;
        send_ioctl(VIDIOC_QBUF, &buf_cap, "Помилка QBUF CAPTURE");

        v4l2_buf_type type_out = V4L2_BUF_TYPE_VIDEO_OUTPUT;
        v4l2_buf_type type_cap = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        send_ioctl(VIDIOC_STREAMON, &type_out, "Помилка STREAMON OUTPUT");
        send_ioctl(VIDIOC_STREAMON, &type_cap, "Помилка STREAMON CAPTURE");
        streaming_ = true;

        pollfd pfd{fd_, POLLIN, 0};
        int ret = ::poll(&pfd, 1, 2000);
        if (ret <= 0) {
            throw std::runtime_error("Апаратний блок не відповів за відведений тайм-аут");
        }

        send_ioctl(VIDIOC_DQBUF, &buf_cap, "Помилка DQBUF CAPTURE");
        std::cout << "C++: Кадр масштабовано! Отримано " << buf_cap.bytesused << " байтів NV12.\n";

        send_ioctl(VIDIOC_DQBUF, &buf_out, "Помилка DQBUF OUTPUT");
    }

private:
    void send_ioctl(unsigned long request, void *arg, const char *err_msg) {
        int r;
        do {
            r = ::ioctl(fd_, request, arg);
        } while (r == -1 && errno == EINTR);

        if (r < 0) {
            throw std::system_error(errno, std::generic_category(), err_msg);
        }
    }

    void stop_streaming() noexcept {
        if (streaming_ && fd_ >= 0) {
            v4l2_buf_type type_out = V4L2_BUF_TYPE_VIDEO_OUTPUT;
            v4l2_buf_type type_cap = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            ::ioctl(fd_, VIDIOC_STREAMOFF, &type_out);
            ::ioctl(fd_, VIDIOC_STREAMOFF, &type_cap);
            streaming_ = false;
        }
    }

    void unmap_buffers() noexcept {
        if (out_ptr_ && out_ptr_ != MAP_FAILED) {
            ::munmap(out_ptr_, out_len_);
            out_ptr_ = nullptr;
        }
        if (cap_ptr_ && cap_ptr_ != MAP_FAILED) {
            ::munmap(cap_ptr_, cap_len_);
            cap_ptr_ = nullptr;
        }
    }

    int fd_{-1};
    void *out_ptr_{nullptr};
    size_t out_len_{0};
    void *cap_ptr_{nullptr};
    size_t cap_len_{0};
    bool streaming_{false};
};

int main(int argc, char **argv) {
    try {
        const std::string dev = (argc > 1) ? argv[1] : "/dev/video10";
        M2MScalerDevice scaler(dev);
        scaler.configure_formats(1920, 1080, 640, 480);
        scaler.allocate_and_mmap();
        scaler.process_single_frame();
    } catch (const std::exception &ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

> 🔧 **Навіщо це.** Якщо масштабувати зображення 1080p у 480p програмно на центральному процесорі через компіляторні цикли або бібліотеки на кшталт OpenCV, один потік процесора ARM Cortex-A53 витрачає близько 18–25 мілісекунд на кадр, що споживає до 80% ядерного часу при частоті 30 к/с. Апаратний блок 2D-масштабування через драйвер M2M виконує ту саму операцію за 1.2–2.0 мілісекунди без участі процесора, залишаючи обчислювальні потужності для високорівневих алгоритмів розпізнавання образів або бізнес-логіки.
