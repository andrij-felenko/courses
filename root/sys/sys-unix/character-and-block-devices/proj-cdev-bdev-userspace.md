# ⚙️ Практична взаємодія з символьними та блочними пристроями з простору користувача

Взаємодія прикладних програм у просторі користувача з символьними та блочними пристроями здійснюється через єдиний уніфікований інтерфейс системних викликів VFS: `open()`, `read()`, `write()`, `lseek()`, `close()` та `ioctl()`. Попри однакові назви функцій, внутрішня механіка виконання системного виклику кардинально відрізняється залежно від класу пристрою.

Розробники системного та прикладного програмного забезпечення мусять чітко враховувати ці відмінності під час розробки високопродуктивного та надійного коду:

- **Символьний пристрій (cdev):** Працює як послідовний потік байтів без проміжного сторінкового кешування. Системний виклик `read()` повертає стільки байтів, скільки готовий надати драйвер на даний момент. Операція `lseek()` зазвичай не підтримується і повертає помилку `-ESPIPE`. Вимоги до вирівнювання адреси буфера пам'яті відсутні.
- **Блочний пристрій (bdev):** Обробляє дані порціями блоків. Стандартні виклики `read()` та `write()` проходять через Сторінковий кеш ядра (Page Cache). Проте для високопродуктивних систем (СУБД, гіпервізори віртуалізації) використовується режим прямого введення-виведення Direct I/O за допомогою прапорця `O_DIRECT`.

Режим Direct I/O виключає сторінковий кеш, що вимагає від програми суворого дотримання трьох правил апаратного вирівнювання: буфер у пам'яті, зсув у файлі та розмір порції даних мусять бути кратними логічному розміру сектора диска.

Нижче наведено два повноцінні практичні проекти з детальним розбором коду мовами C та C++.

## 1. Читання випадкових байтів із символьного пристрою `/dev/urandom`

Символьні пристрої надають простий і передбачуваний потік даних. У даному прикладі програма відкриває псевдогенератор випадкових чисел `/dev/urandom`, зчитує порцію байтів та виводить їх у формі шістнадцяткового дампу.

### Технічні особливості роботи з cdev у прикладі

1. **Відсутність вирівнювання:** Буфер пам'яті `buffer[64]` виділяється на стеку або у динамічній пам'яті за довільною адресою. Символьний драйвер ядра приймає будь-яку віртуальну адресу простору користувача.
2. **Немає кінця файлу:** Пристрій `/dev/urandom` генерує нескінченний потік байтів, тож `read()` ніколи не поверне 0. Для невеликих запитів він віддає рівно стільки байтів, скільки попросили; коротке читання можливе, якщо виклик перервав сигнал.
3. **Обробка помилок:** Програма перевіряє значення повернення `read()`. Якщо отримано `-1`, код аналізує змінну `errno` для виявлення причин збою (наприклад, `EINTR` при перериванні сигналом).

Для гарантії ресурсного очищення у C++ використовується концепція RAII (Resource Acquisition Is Initialization), де деструктор класу `CharacterDeviceReader` автоматично викликає `close()` навіть у випадку виникнення винятку `std::system_error`.

:::tabs
== C
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>

#define BUFFER_SIZE 64

int main(void) {
    // 1. Відкриття символьного пристрою у режимі "тільки для читання"
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття /dev/urandom: %s (код %d)\n", 
                strerror(errno), errno);
        return EXIT_FAILURE;
    }

    unsigned char buffer[BUFFER_SIZE];
    
    // 2. Читання послідовного потоку байтів безпосередньо з cdev
    ssize_t bytes_read = read(fd, buffer, sizeof(buffer));
    
    if (bytes_read < 0) {
        fprintf(stderr, "Помилка читання з cdev: %s (код %d)\n", 
                strerror(errno), errno);
        close(fd);
        return EXIT_FAILURE;
    }

    // 3. Форматований вивід отриманих байтів у консоль
    printf("Успішно прочитано %zd байтів із символьного пристрою /dev/urandom:\n", bytes_read);
    for (ssize_t i = 0; i < bytes_read; ++i) {
        printf("%02x ", buffer[i]);
        if ((i + 1) % 16 == 0) {
            printf("\n");
        }
    }
    printf("\n");

    // 4. Закриття файлового дескриптора
    close(fd);
    return EXIT_SUCCESS;
}
```
== C++ (C++20)
```cpp
#include <iostream>
#include <vector>
#include <iomanip>
#include <span>
#include <system_error>
#include <cstdlib>
#include <cstdint>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>

// Обгортка для безпечного управління файловим дескриптором за допомогою RAII
class CharacterDeviceReader {
    int fd_{-1};

public:
    explicit CharacterDeviceReader(const char* path) {
        fd_ = ::open(path, O_RDONLY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Не вдалося відкрити символьний пристрій");
        }
    }

    ~CharacterDeviceReader() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    // Заборона копіювання для запобігання подвійному закриттю дескриптора
    CharacterDeviceReader(const CharacterDeviceReader&) = delete;
    CharacterDeviceReader& operator=(const CharacterDeviceReader&) = delete;

    // Переміщення ресурсу
    CharacterDeviceReader(CharacterDeviceReader&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    std::vector<uint8_t> read_bytes(size_t count) {
        std::vector<uint8_t> buffer(count);
        ssize_t bytes_read = ::read(fd_, buffer.data(), buffer.size());
        
        if (bytes_read < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Помилка зчитування з символьного пристрою");
        }
        
        buffer.resize(static_cast<size_t>(bytes_read));
        return buffer;
    }
};

int main() {
    try {
        CharacterDeviceReader dev("/dev/urandom");
        auto random_data = dev.read_bytes(64);

        std::cout << "Успішно прочитано " << random_data.size() 
                  << " байтів (C++ RAII):\n";
        
        // Сучасне ітерування по суцільному масиву байтів
        std::span<const uint8_t> data_span{random_data};
        for (size_t i = 0; i < data_span.size(); ++i) {
            std::cout << std::hex << std::setw(2) << std::setfill('0') 
                      << static_cast<int>(data_span[i]) << " ";
            if ((i + 1) % 16 == 0) {
                std::cout << "\n";
            }
        }
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка виконання: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## 2. Пряме вирівняне читання з блочного пристрою (Direct I/O з `O_DIRECT`)

Другий проект демонструє низькорівневу роботу з блочним пристроєм у режимі **Direct I/O**. Цей режим вмикається прапорцем `O_DIRECT` при системному виклику `open()`. Він змушує ядро передавати дані між диском і пам'яттю програми за допомогою DMA без залучення Сторінкового кешу.

### Анатомія системних викликів `ioctl` для блочних пристроїв

Перш ніж читати блочний пристрій, програма мусить дізнатися його апаратні геометричні параметри. Для цього використовуються системні виклики `ioctl()` з прапорцями підсистеми блочного введення-виведення:

1. **`ioctl(fd, BLKGETSIZE64, &size_bytes)`:** Повертає повний розмір блочного пристрою в байтах як 64-бітне беззнакове ціле (`uint64_t`).
2. **`ioctl(fd, BLKSSZGET, &sector_size)`:** Повертає розмір логічного сектора пристрою в байтах (ціле `int`, зазвичай 512 або 4096).

### Вимога вирівнювання пам'яті через `posix_memalign`

При звичайному мовному виділенні пам'яті (`malloc()` у C або `new` у C++) адреса вказівника вирівнюється за межею 8 або 16 байтів. Проте DMA-контролер блочного пристрою в режимі `O_DIRECT` вимагає, щоб адреса буфера була суворо кратною розміру логічного сектора (наприклад, 512 або 4096 байтів).

Для виділення такої пам'яті у POSIX-стандарті призначена функція:

```c
int posix_memalign(void **memptr, size_t alignment, size_t size);
```

Якщо передати у `read()` вказівник звичайного `malloc()` при відкритому `O_DIRECT`, ядро Linux поверне помилку `-EINVAL`. Для автоматичного звільнення такої пам'яті у C++20 використовується розумний вказівник `std::unique_ptr<void, AlignedDeleter>` із власною функцією звільнення `free()`.

:::tabs
== C
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/fs.h>
#include <errno.h>
#include <string.h>
#include <stdint.h>
#include <inttypes.h>

int main(int argc, char *argv[]) {
    const char *dev_path = (argc > 1) ? argv[1] : "/dev/loop0";

    // 1. Відкриття блочного пристрою у режимі O_DIRECT (обхід сторінкового кешу)
    int fd = open(dev_path, O_RDONLY | O_DIRECT);
    if (fd < 0) {
        fprintf(stderr, "Не вдалося відкрити блочний пристрій %s: %s\n", 
                dev_path, strerror(errno));
        return EXIT_FAILURE;
    }

    uint64_t disk_size_bytes = 0;
    int sector_size = 0;

    // 2. Запит параметрів блочного пристрою через ioctl
    if (ioctl(fd, BLKGETSIZE64, &disk_size_bytes) < 0) {
        perror("Помилка ioctl(BLKGETSIZE64)");
        close(fd);
        return EXIT_FAILURE;
    }

    if (ioctl(fd, BLKSSZGET, &sector_size) < 0) {
        perror("Помилка ioctl(BLKSSZGET)");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Пристрій: %s\n", dev_path);
    printf("Розмір диска: %" PRIu64 " байтів\n", disk_size_bytes);
    printf("Розмір логічного сектора: %d байтів\n", sector_size);

    // 3. Виділення вирівняної пам'яті для O_DIRECT через posix_memalign
    void *aligned_buf = NULL;
    size_t read_size = (size_t)sector_size * 2; // Читаємо 2 сектори
    
    if (posix_memalign(&aligned_buf, sector_size, read_size) != 0) {
        fprintf(stderr, "Помилка виділення вирівняної пам'яті за межею %d B\n", sector_size);
        close(fd);
        return EXIT_FAILURE;
    }

    // 4. Позиціонування на сектор 0 (кратне sector_size)
    if (lseek(fd, 0, SEEK_SET) < 0) {
        perror("Помилка позиціонування lseek");
        free(aligned_buf);
        close(fd);
        return EXIT_FAILURE;
    }

    // 5. Виконання прямого читання без залучення сторінкового кешу
    ssize_t bytes_read = read(fd, aligned_buf, read_size);
    if (bytes_read < 0) {
        fprintf(stderr, "Помилка O_DIRECT читання bdev: %s (код %d)\n", 
                strerror(errno), errno);
        free(aligned_buf);
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Успішно прочитано %zd байтів через O_DIRECT без кешування!\n", bytes_read);

    // 6. Очищення ресурсів
    free(aligned_buf);
    close(fd);
    return EXIT_SUCCESS;
}
```
== C++ (C++20)
```cpp
#define _GNU_SOURCE
#include <iostream>
#include <memory>
#include <span>
#include <system_error>
#include <cstdlib>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/fs.h>

// Кастомний видаляч для std::unique_ptr, який викликає free() для вирівняної пам'яті
struct AlignedDeleter {
    void operator()(void* ptr) const noexcept {
        ::free(ptr);
    }
};

class BlockDeviceDirectReader {
    int fd_{-1};
    uint64_t total_size_{0};
    int sector_size_{0};

public:
    explicit BlockDeviceDirectReader(const char* dev_path) {
        fd_ = ::open(dev_path, O_RDONLY | O_DIRECT);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Не вдалося відкрити bdev у режимі O_DIRECT");
        }

        if (::ioctl(fd_, BLKGETSIZE64, &total_size_) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), 
                                   "Помилка опитування ioctl(BLKGETSIZE64)");
        }

        if (::ioctl(fd_, BLKSSZGET, &sector_size_) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), 
                                   "Помилка опитування ioctl(BLKSSZGET)");
        }
    }

    ~BlockDeviceDirectReader() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    [[nodiscard]] uint64_t size() const noexcept { return total_size_; }
    [[nodiscard]] int sector_size() const noexcept { return sector_size_; }

    void read_aligned_sectors(uint64_t start_sector, size_t sector_count) {
        size_t bytes_to_read = static_cast<size_t>(sector_size_) * sector_count;
        void* raw_ptr = nullptr;

        // Безпечне виділення пам'яті з гарантованим вирівнюванням
        if (::posix_memalign(&raw_ptr, sector_size_, bytes_to_read) != 0) {
            throw std::bad_alloc();
        }

        // Автоматичне управління життєвим циклом буфера через RAII
        std::unique_ptr<void, AlignedDeleter> aligned_buffer(raw_ptr);

        off_t offset = static_cast<off_t>(start_sector * sector_size_);
        if (::lseek(fd_, offset, SEEK_SET) < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Помилка позиціонування lseek");
        }

        ssize_t bytes_read = ::read(fd_, aligned_buffer.get(), bytes_to_read);
        if (bytes_read < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Помилка прямого читання Direct I/O");
        }

        std::cout << "C++ RAII Direct I/O: успішно прочитано " << bytes_read 
                  << " байтів починаючи з сектора " << start_sector << "\n";
    }
};

int main(int argc, char* argv[]) {
    const char* target_dev = (argc > 1) ? argv[1] : "/dev/loop0";
    try {
        BlockDeviceDirectReader bdev(target_dev);
        std::cout << "Пристрій: " << target_dev << "\n";
        std::cout << "Розмір: " << bdev.size() << " байтів, Сектор: " 
                  << bdev.sector_size() << " байтів\n";

        // Прочитати 2 вирівняні сектори з початку накопичувача
        bdev.read_aligned_sectors(0, 2);
    } catch (const std::exception& ex) {
        std::cerr << "Критичний виняток Bdev: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## 3. Зведення відмінностей у користувацькому коді

Підсумовуючи практичний досвід розробки системних додатків для Linux:

1. **Обробка EOF:** При читанні з cdev виклики `read()` можуть повертати будь-яку кількість байтів від 1 до `count`. При читанні з bdev через `O_DIRECT` виклики повертають значення, що суворо кратне логічному сектору.
2. **Багатопотокова безпека:** Декілька процесів або потоків можуть паралельно викликати `pread()` та `pwrite()` на одному блочному пристрої з різними вирівняними зсувами без взаємного пошкодження буферів. Для символьних пристроїв паралельне читання без зовнішніх системних замків зазвичай призводить до змішування байтових потоків.
3. **Діагностика збоїв:** Якщо код з блочними пристроями повертає помилку `-EINVAL`, майже завжди причиною є невирівняна адреса буфера, невирівняний зсув у пристрої або невирівняний розмір порції читання.
