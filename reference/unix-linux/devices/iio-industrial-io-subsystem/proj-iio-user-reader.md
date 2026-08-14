# ⚙️ Практичний проект: зчитування даних IIO у просторі користувача

Цей практичний проект пропонує вичерпне розробницьке керівництво зі створення додатків простору користувача Linux, які взаємодіють із підсистемою Industrial I/O (IIO) напряму через стандартні системні виклики VFS без використання зовнішніх сторонніх бібліотек. У проекті детально розбирається алгоритм програмування sysfs-інтерфейсу для конфігурації кільцевого буфера ядра `kfifo`, налаштування маски селекції активних каналів, прив'язки програмного тригера та високоефективного потокового зчитування бінарних семплів із дескриптора `/dev/iio:device0` з витяганням наносекундного таймстампа ядра.

## 1. Архітектурна постановка задачі та детальний алгоритм

Метою проекту є розробка консольної утиліти збору даних, здатної зчитати серію з 100 високочастотних бінарних семплів з аналогово-цифрового перетворювача (АЦП) або 3D-акселерометра. Для досягнення максимальної швидкості та мінімізації навантаження на центральний процесор програма відмовляється від текстового опитування sysfs-файлів на користь буферизованого символьного пристрою `/dev/iio:device0`.

Алгоритм взаємодії додатку з підсистемою IIO складається з восьми послідовних кроків:

1. **Деактивація поточного буфера**: Запис значення `0` у системний файл `/sys/bus/iio/devices/iio:device0/buffer/enable`. Зміна будь-яких параметрів селекції каналів або розміру буфера заборонена ядром, коли буфер перебуває в активному стані.
2. **Селекція активних вимірювальних каналів**: Запис `1` у відповідні прапорці підкаталогу `scan_elements/`. У нашому проекті ми активуємо перший канал напруги `scan_elements/in_voltage0_en` та 64-бітне поле таймстампа `scan_elements/in_timestamp_en`.
3. **Конфігурація розміру кільцевого буфера**: Запис бажаної ємності у файл `buffer/length` (наприклад, 128 семплів). Це визначає розмір внутрішнього масиву сторінок пам'яті `kfifo`, що виділяється ядром для захисту від переповнення.
4. **Конфігурація порогу вотермарка (Watermark)**: Запис бажаної кількості накопичених семплів у файл `buffer/watermark` (наприклад, 16 семплів). Це знижує кількість розбуджень процесора, активуючи `poll()` лише при наявності пачки даних.
5. **Прив'язка тригера джерела даних**: Запис назви джерела тригера у системний файл `trigger/current_trigger` (наприклад, `sysfstrig0` для системного тригера або `hrtimer_trigger` для високоточного таймера).
6. **Активація буфера ядра**: Запис `1` у файл `buffer/enable`. З цього моменту ядро виділяє пам'ять `kfifo`, підключає обробник тригера і починає заповнення буфера бінарними кадрами.
7. **Відкриття символьного пристрою**: Виклик `open("/dev/iio:device0", O_RDONLY)` для отримання файлового дескриптора потокового зчитування.
8. **Потоковий цикл читання та обробки**: Опитування готовності даних через виклик `poll()` та блокуюче зчитування кадру фіксованої довжини викликом `read()`.
9. **Коректне звільнення ресурсів**: Закриття дескриптора файлу та запис `0` у `buffer/enable` для виключення буфера ядра і зупинки переривань.

## 2. Анатомія вирівнювання бінарного кадру в пам'яті

Найважливішим аспектом бінарного зчитування з `/dev/iio:device0` є точна відповідність структури даних у просторі користувача специфікації `scan_type`, яку драйвер ядра експортує через sysfs.

У нашому прикладі кадр складається з 16-бітного сирого значення АЦП та 64-бітного системного таймстампа. Згідно з вимогами архітектури Linux ABI, 64-бітне ціле число `int64_t` у пам'яті повинно бути вирівняне по 8-байтній межі. Оскільки 16-бітний відлік займає лише 2 байти, ядро додає 6 байтів падінгу перед таймстампом.

Отже, бінарний розмір структури кадру складає рівно 16 байтів:
- Байти 0..1: `uint16_t raw_value` (12-бітний або 16-бітний відлік АЦП);
- Байти 2..7: `uint16_t padding[3]` (6 байтів вирівнювального заповнення ядра);
- Байти 8..15: `int64_t timestamp_ns` (64-бітний системний таймстамп у наносекундах).

Якщо додаток зчитує 3D-акселерометр (канали X, Y, Z по 16 біт кожен), розмір масиву осей складає 6 байтів. Ядро додасть 2 байти падінгу, щоб таймстамп розпочинався з 8-го байта. Розрахунок паддінгу є критичним для запобігання зсуву даних при парсингу бінарного потоку.

## 3. Внутрішньоядерний шлях передачі даних (Kernel-to-Userspace Data Path)

Під час виконання потокового зчитування бінарні дані долають декілька проміжних рівнів ядра Linux:

1. **Апаратне переривання тригера**: Лінія переривання IRQ генерує сигнал. Ядро викликає функцію `iio_trigger_poll()`, яка перебуває у контексті переривання (Hard IRQ).
2. **Фіксація таймстампа**: Виклик `iio_pollfunc_store_time()` фіксує значення системного таймстампа `ktime_get_boottime_ns()`.
3. **Обробник нижньої половини (Threaded IRQ Handler)**: Ядро викликає колбек драйвера `iio_triggered_buffer_setup()`. Драйвер зчитує дані з регістрів чипа через шину I2C/SPI або DMA.
4. **Запис у кільцевий буфер**: Виклик `iio_push_to_buffers_with_timestamp()` упаковує масив вимірів разом із таймстампом і поміщає його у кільцеву чергу `kfifo`.
5. **Сигналізація простір користувача**: `kfifo` оновлює покажчики запису та перевіряє поріг `watermark`. Якщо кількість накопичених кадрів досягла вотермарка, ядро розбуджує чергу очікування `wait_queue_head_t`.
6. **Системний виклик read()**: Процес простору користувача розбуджується у виклику `poll()`, виконує системний виклик `read()`, і ядро копіює бінарний блок пам'яті через `copy_to_user()` у буфер додатка.

## 4. Розширене простеження та трасування підсистеми IIO

Для діагностики продуктивності та виявлення пропущених семплів розробники ядра використовують підсистему трасування `ftrace` та утиліти `trace-cmd`.

Підсистема IIO надає вбудовані точки трасування (tracepoints):

```bash
# Перелік точок трасування IIO у ядрі
ls /sys/kernel/tracing/events/iio/

# Активація трасування тригерів та буферів
echo 1 > /sys/kernel/tracing/events/iio/iio_trigger_poll/enable
echo 1 > /sys/kernel/tracing/events/iio/iio_push_to_buffer/enable

# Перегляд логу трасування у реальному часі
cat /sys/kernel/tracing/trace_pipe
```

Вивід tracepoint показує точні моменти спрацьовування тригера, ідентифікатор пристрою та розмір записаних байтів, що дозволяє виміряти затримку між апаратним сигналом та читанням у просторі користувача.

## 5. Реалізація проекту мовами C та C++

Нижче наведено робочий код проекту у двох варіантах реалізації: класичній мові C та ідіоматичному сучасному C++ з використанням концепції RAII, семантики `std::expected` для обробки системних помилок без винятків та системних типів `std::filesystem`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>
#include <errno.h>
#include <sys/poll.h>

#define SYSFS_PATH "/sys/bus/iio/devices/iio:device0"
#define DEV_PATH   "/dev/iio:device0"

static int write_sysfs_int(const char *path, int val) {
    char buf[32];
    int fd = open(path, O_WRONLY);
    if (fd < 0) return -errno;

    int len = snprintf(buf, sizeof(buf), "%d\n", val);
    ssize_t ret = write(fd, buf, len);
    close(fd);
    return (ret == len) ? 0 : -EIO;
}

static int write_sysfs_str(const char *path, const char *str) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) return -errno;

    size_t len = strlen(str);
    ssize_t ret = write(fd, str, len);
    close(fd);
    return (ret == (ssize_t)len) ? 0 : -EIO;
}

// Структура кадру: 16-біт відлік АЦП + 6-байтний паддінг + 64-бітний таймстамп
struct __attribute__((packed)) iio_sample_frame {
    uint16_t raw_value;
    uint16_t padding[3];
    int64_t timestamp_ns;
};

int main(void) {
    printf("Ініціалізація та налаштування кільцевого буфера IIO...\n");

    // 1. Деактивувати буфер перед конфігурацією
    write_sysfs_int(SYSFS_PATH "/buffer/enable", 0);

    // 2. Увімкнути перший канал напруги та системний таймстамп
    if (write_sysfs_int(SYSFS_PATH "/scan_elements/in_voltage0_en", 1) < 0) {
        perror("Помилка включення scan_elements/in_voltage0_en");
        return EXIT_FAILURE;
    }
    write_sysfs_int(SYSFS_PATH "/scan_elements/in_timestamp_en", 1);

    // 3. Встановити розмір кільцевого буфера kfifo
    write_sysfs_int(SYSFS_PATH "/buffer/length", 128);

    // 4. Встановити вотермарк для зменшення кількості розбуджень
    write_sysfs_int(SYSFS_PATH "/buffer/watermark", 16);

    // 5. Активувати буфер ядра
    if (write_sysfs_int(SYSFS_PATH "/buffer/enable", 1) < 0) {
        perror("Помилка активації buffer/enable");
        return EXIT_FAILURE;
    }

    // 6. Відкрити символьний пристрій для читання бінарних семплів
    int dev_fd = open(DEV_PATH, O_RDONLY);
    if (dev_fd < 0) {
        perror("Помилка відкриття файлу " DEV_PATH);
        write_sysfs_int(SYSFS_PATH "/buffer/enable", 0);
        return EXIT_FAILURE;
    }

    struct pollfd pfd = { .fd = dev_fd, .events = POLLIN };
    struct iio_sample_frame frame;

    printf("Розпочато зчитування семплів із пристрою " DEV_PATH "...\n");
    for (int i = 0; i < 10; ++i) {
        int poll_ret = poll(&pfd, 1, 5000); // 5 секунд таймаут
        if (poll_ret <= 0) {
            fprintf(stderr, "Таймаут або помилка системного виклику poll()\n");
            break;
        }

        ssize_t bytes = read(dev_fd, &frame, sizeof(frame));
        if (bytes == sizeof(frame)) {
            printf("[%d] RAW: %5u | Timestamp: %lld ns\n",
                   i, frame.raw_value, (long long)frame.timestamp_ns);
        } else {
            fprintf(stderr, "Помилка читання: прочитано %zd байт замість %zu\n",
                    bytes, sizeof(frame));
        }
    }

    // Деактивація та чистка ресурсів
    close(dev_fd);
    write_sysfs_int(SYSFS_PATH "/buffer/enable", 0);
    printf("Збір даних завершено успішно.\n");
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <filesystem>
#include <chrono>
#include <expected>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/poll.h>

namespace fs = std::filesystem;

class IIODevice {
private:
    fs::path sysfs_base_;
    fs::path dev_path_;
    int dev_fd_ = -1;

    std::expected<void, std::error_code> write_sysfs(const std::string& relative_path, const std::string& val) {
        std::ofstream ofs(sysfs_base_ / relative_path);
        if (!ofs.is_open()) {
            return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
        }
        ofs << val << std::endl;
        return ofs.good() ? std::expected<void, std::error_code>{} 
                          : std::unexpected(std::make_error_code(std::errc::io_error));
    }

public:
    struct alignas(8) SampleFrame {
        uint16_t raw_value;
        uint16_t padding[3];
        int64_t timestamp_ns;
    };

    explicit IIODevice(std::string device_name = "iio:device0")
        : sysfs_base_("/sys/bus/iio/devices" / fs::path(device_name)),
          dev_path_("/dev" / fs::path(device_name)) {}

    ~IIODevice() {
        stop_buffer();
        if (dev_fd_ >= 0) {
            ::close(dev_fd_);
        }
    }

    std::expected<void, std::error_code> configure_buffer(std::size_t buffer_length = 128, std::size_t watermark = 16) {
        stop_buffer();
        if (auto res = write_sysfs("scan_elements/in_voltage0_en", "1"); !res) return res;
        if (auto res = write_sysfs("scan_elements/in_timestamp_en", "1"); !res) return res;
        if (auto res = write_sysfs("buffer/length", std::to_string(buffer_length)); !res) return res;
        if (auto res = write_sysfs("buffer/watermark", std::to_string(watermark)); !res) return res;
        return {};
    }

    std::expected<void, std::error_code> start_buffer() {
        if (auto res = write_sysfs("buffer/enable", "1"); !res) return res;
        dev_fd_ = ::open(dev_path_.c_str(), O_RDONLY);
        if (dev_fd_ < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
        }
        return {};
    }

    void stop_buffer() noexcept {
        (void)write_sysfs("buffer/enable", "0");
    }

    std::expected<SampleFrame, std::error_code> read_sample(int timeout_ms = 1000) {
        if (dev_fd_ < 0) {
            return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));
        }

        ::pollfd pfd{ .fd = dev_fd_, .events = POLLIN, .revents = 0 };
        int ret = ::poll(&pfd, 1, timeout_ms);
        if (ret == 0) return std::unexpected(std::make_error_code(std::errc::timed_out));
        if (ret < 0)  return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));

        SampleFrame frame{};
        ssize_t n = ::read(dev_fd_, &frame, sizeof(frame));
        if (n != sizeof(frame)) {
            return std::unexpected(std::make_error_code(std::errc::io_error));
        }
        return frame;
    }
};

int main() {
    std::cout << "Ініціалізація IIODevice (C++23 RAII)..." << std::endl;
    IIODevice sensor("iio:device0");

    if (auto res = sensor.configure_buffer(128, 16); !res) {
        std::cerr << "Помилка конфігурації буфера IIO у sysfs" << std::endl;
        return 1;
    }

    if (auto res = sensor.start_buffer(); !res) {
        std::cerr << "Помилка запуску буфера IIO" << std::endl;
        return 1;
    }

    std::cout << "Успішно запущено. Зчитування семплів..." << std::endl;
    for (int i = 0; i < 10; ++i) {
        auto sample_res = sensor.read_sample(2000);
        if (sample_res) {
            const auto& sample = sample_res.value();
            auto time_pt = std::chrono::nanoseconds(sample.timestamp_ns);
            std::cout << "[" << i << "] RAW: " << sample.raw_value 
                      << " | Timestamp: " << time_pt.count() << " ns" << std::endl;
        } else {
            std::cerr << "Помилка зчитування семпла з буфера" << std::endl;
            break;
        }
    }

    return 0;
}
```
:::

## 6. Збірка та розв'язання можливих проблем при запуску

Для компіляції вихідного коду скористайтеся стандартними компіляторами ядра Linux:

```bash
# Компіляція прикладу мовою C
gcc -Wall -Wextra -O2 iio_reader.c -o iio_reader

# Компіляція прикладу мовою C++ (вимагає стандарту C++23)
g++ -std=c++23 -Wall -Wextra -O2 iio_reader.cpp -o iio_reader_cpp
```

### Налагодження збоїв при запуску:
1. **Помилка `Permission denied` при відкритті sysfs або `/dev/iio:device0`**:
   Запуск додатків, які змінюють налаштування буфера та читають прямі символьні пристрої ядра, вимагає прав суперкористувача `root` або входження користувача до групи `iio` чи `plugdev`. Створіть правило udev у `/etc/udev/rules.d/99-iio.rules`:
   ```text
   KERNEL=="iio:device*", GROUP="iio", MODE="0660"
   ```
2. **Помилка `Device or resource busy` при записі у `buffer/enable`**:
   Помилка свідчить про те, що буфер вже активовано іншим процесом, або спроба змінити конфігурацію виконується без попереднього запису `0` у `buffer/enable`.
3. **Таймаут у виклику `poll()`**:
   Якщо додаток зависає у `poll()`, перевірте, чи прив'язано активний тригер у `/sys/bus/iio/devices/iio:device0/trigger/current_trigger`. Якщо тригер не встановлено, ядро не генерує події тактування і буфер залишається порожнім.
