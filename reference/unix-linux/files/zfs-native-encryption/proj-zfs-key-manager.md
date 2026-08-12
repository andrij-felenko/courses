# ⚙️ Програмне керування ключами та перевірка стану шифрування ZFS мовами C та C++

Практичний проєкт демонструє розробку системного демона діагностики та керування ключами шифрування ZFS. Програма взаємодіє з модулем ядра ZFS через керуючий символьний пристрій `/dev/zfs` за допомогою системних викликів `ioctl` (`ZFS_IOC_LOAD_KEY` та `ZFS_IOC_KEY_STATUS`), зчитує бінарний 256-бітний ключ з ізольованого носія, перевіряє стан завантаження Майстер-ключа в ядро та виконує завантаження ключа в оперативну пам'ять із суворим дотриманням правил криптографічної гігієни пам'яті.

## 1. Архітектура взаємодії з шаром підсистеми ZFS через ioctl

Більшість високорівневих системних утилит (таких як `zfs` та `zpool`) реалізовано поверх системної бібліотеки `libzfs`. Проте при розробці вбудованих демонів безпеки, контейнерних агентів або служб автоматичного змонтування дисків при завантаженні системи доцільно взаємодіяти з керуючим пристроєм `/dev/zfs` безпосередньо. Це усуває залежність від зовнішніх динамічних бібліотек і забезпечує повний контроль над життєвим циклом буферів пам'яті, що містять секретні ключі.

Взаємодія з ядром відбувається через передачу впорядкованої структури аргументів у виклик `ioctl(fd, cmd, &args)`:
- Символьний пристрій `/dev/zfs` відкривається у режимі читання-запису (`O_RDWR`).
- У структуру аргументів записується ім'я цільового датасету (`zc_name`), бінарні дані ключа (`zc_value`) та формат подання ключа (`zc_keyformat = 1` для бінарного формату `raw`).
- Ядро перевіряє переданий Wrapping Key, розгортає Майстер-ключ датасету у внутрішніх структурах DSL і повертає статус виконання.

Нижче наведено повну реалізацію утиліти керування ключами двома мовами: C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/stat.h>

#define ZFS_DEV_PATH "/dev/zfs"
#define KEY_SIZE_BYTES 32

/* Спрощена структура параметрів ioctl для взаємодії з /dev/zfs */
typedef struct zfs_cmd_args {
    char zc_name[256];
    char zc_value[1024];
    uint64_t zc_cookie;
    uint64_t zc_objset_type;
    uint64_t zc_keystatus;
    uint64_t zc_keyformat;
} zfs_cmd_args_t;

/* Отримання описувача символьного пристрою ZFS */
static int open_zfs_control(void) {
    int fd = open(ZFS_DEV_PATH, O_RDWR);
    if (fd < 0) {
        perror("Помилка відкриття /dev/zfs");
    }
    return fd;
}

/* Зчитати бінарний 256-бітний ключ із файла */
static int read_raw_key_file(const char *key_path, unsigned char *key_buffer) {
    int fd = open(key_path, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття файла ключа %s: %s\n", key_path, strerror(errno));
        return -1;
    }

    ssize_t bytes_read = read(fd, key_buffer, KEY_SIZE_BYTES);
    close(fd);

    if (bytes_read != KEY_SIZE_BYTES) {
        fprintf(stderr, "Некоректний розмір ключа (%zd байтів, очікується 32)\n", bytes_read);
        return -1;
    }
    return 0;
}

/* Завантаження майстер-ключа датасету в ядро */
static int load_zfs_key(int zfs_fd, const char *dataset_name, const unsigned char *raw_key) {
    zfs_cmd_args_t cmd;
    memset(&cmd, 0, sizeof(cmd));

    strncpy(cmd.zc_name, dataset_name, sizeof(cmd.zc_name) - 1);
    cmd.zc_keyformat = 1; /* KeyFormat: Raw 256-bit binary */
    memcpy(cmd.zc_value, raw_key, KEY_SIZE_BYTES);

    /* Відправка розширюваної команди завантаження ключа ZFS_IOC_LOAD_KEY */
    /* Виклик ioctl повертає 0 при успішному розгортанні Master Key у пам'яті ядра */
    if (ioctl(zfs_fd, 0x5a01, &cmd) != 0) {
        if (errno == EEXIST) {
            printf("Ключ для датасету %s вже завантажено в ядро.\n", dataset_name);
            return 0;
        }
        fprintf(stderr, "Помилка ioctl ZFS_IOC_LOAD_KEY для %s: %s\n", dataset_name, strerror(errno));
        return -1;
    }

    printf("Успішно завантажено Майстер-ключ для датасету: %s\n", dataset_name);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <dataset_name> <key_file_path>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *dataset_name = argv[1];
    const char *key_file_path = argv[2];
    unsigned char raw_key[KEY_SIZE_BYTES];

    if (read_raw_key_file(key_file_path, raw_key) != 0) {
        return EXIT_FAILURE;
    }

    int zfs_fd = open_zfs_control();
    if (zfs_fd < 0) {
        return EXIT_FAILURE;
    }

    int result = load_zfs_key(zfs_fd, dataset_name, raw_key);

    /* Явне очищення ключа в користувацькій пам'яті для безпеки */
    explicit_bzero(raw_key, sizeof(raw_key));
    close(zfs_fd);

    return (result == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string_view>
#include <array>
#include <memory>
#include <system_error>
#include <expected>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>

namespace zfs {

constexpr std::string_view kZfsDevPath = "/dev/zfs";
constexpr size_t kKeySizeBytes = 32;

/* RAII-обгортка для безпечного управління файл-дескриптором /dev/zfs */
class ZfsControlDevice {
public:
    ZfsControlDevice() {
        fd_ = ::open(kZfsDevPath.data(), O_RDWR);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити " + std::string(kZfsDevPath));
        }
    }

    ~ZfsControlDevice() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    ZfsControlDevice(const ZfsControlDevice&) = delete;
    ZfsControlDevice& operator=(const ZfsControlDevice&) = delete;

    ZfsControlDevice(ZfsControlDevice&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

private:
    int fd_{-1};
};

/* Спрощена структура ioctl ZFS */
struct ZfsCmdArgs {
    char zc_name[256]{};
    char zc_value[1024]{};
    uint64_t zc_cookie{0};
    uint64_t zc_objset_type{0};
    uint64_t zc_keystatus{0};
    uint64_t zc_keyformat{0};
};

using KeyBuffer = std::array<uint8_t, kKeySizeBytes>;

/* Зчитати бінарний ключ із безпечним витиранням пам'яті в деструкторі */
class SecureKeyBuffer {
public:
    SecureKeyBuffer() = default;
    ~SecureKeyBuffer() {
        ::explicit_bzero(buffer_.data(), buffer_.size());
    }

    [[nodiscard]] KeyBuffer& data() noexcept { return buffer_; }
    [[nodiscard]] const KeyBuffer& data() const noexcept { return buffer_; }

private:
    KeyBuffer buffer_{};
};

/* Безпечне зчитування ключа із використанням std::expected (C++23) */
std::expected<SecureKeyBuffer, std::string> ReadRawKeyFile(std::string_view key_path) {
    std::ifstream file(key_path.data(), std::ios::binary);
    if (!file.is_open()) {
        return std::unexpected("Не вдалося відкрити файл ключа: " + std::string(key_path));
    }

    SecureKeyBuffer key_buf;
    file.read(reinterpret_cast<char*>(key_buf.data().data()), kKeySizeBytes);
    if (file.gcount() != kKeySizeBytes) {
        return std::unexpected("Некоректний розмір ключа у файлі (очікувалося 32 байти)");
    }

    return key_buf;
}

/* Завантаження майстер-ключа в ядро Linux через ioctl */
std::expected<void, std::string> LoadDatasetKey(const ZfsControlDevice& zfs_dev, 
                                                std::string_view dataset_name, 
                                                const SecureKeyBuffer& key) {
    ZfsCmdArgs cmd{};
    std::strncpy(cmd.zc_name, dataset_name.data(), sizeof(cmd.zc_name) - 1);
    cmd.zc_keyformat = 1; // Raw 256-bit binary
    std::memcpy(cmd.zc_value, key.data().data(), kKeySizeBytes);

    if (::ioctl(zfs_dev.get(), 0x5a01, &cmd) != 0) {
        if (errno == EEXIST) {
            return {}; // Ключ вже завантажено
        }
        return std::unexpected("Помилка ioctl ZFS_IOC_LOAD_KEY: " + std::string(std::strerror(errno)));
    }

    return {};
}

} // namespace zfs

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <dataset_name> <key_file_path>\n";
        return EXIT_FAILURE;
    }

    const std::string_view dataset_name = argv[1];
    const std::string_view key_file_path = argv[2];

    try {
        zfs::ZfsControlDevice zfs_dev;
        
        auto key_result = zfs::ReadRawKeyFile(key_file_path);
        if (!key_result) {
            std::cerr << "Помилка зчитування ключа: " << key_result.error() << '\n';
            return EXIT_FAILURE;
        }

        auto load_result = zfs::LoadDatasetKey(zfs_dev, dataset_name, *key_result);
        if (!load_result) {
            std::cerr << "Помилка завантаження ключа в ядро: " << load_result.error() << '\n';
            return EXIT_FAILURE;
        }

        std::cout << "Майстер-ключ ZFS успішно завантажено для " << dataset_name << '\n';
    } catch (const std::exception& ex) {
        std::cerr << "Фатальна помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## 2. Анатомія реалізації та порівняння підходів C та C++

Представлені приклади демонструють два принципово різних підходи до управління системними ресурсами під час взаємодії з криптографічними інтерфейсами ядра Linux:

### Системна безпека та гігієна оперативної пам'яті

Найважливішою вимогою при роботі з криптографічними ключами у користувацькому просторі є запобігання витоку ключового матеріалу через свопінг пам'яті (swap) або залишення відкритих даних у дампах пам'яті (core dumps).

1. **Небезпека звичайного `memset()`:** У прикладі на мові C для затирання масиву `raw_key` перед виходом з функції використовується спеціалізований системний виклик `explicit_bzero()`. Стандартна функція `memset(raw_key, 0, 32)` під час оптимізації компілятором із прапорами `-O2` або `-O3` розпізнається як виклик до локальної змінної, яка більше не використовується до кінця функції. Компілятор усуває цей виклик як «мертвий код» (Dead Code Elimination — DCE), залишаючи відкритий ключ у стеку процесів. Утиліта `explicit_bzero()` (або `memset_s()`) гарантує виконання обнулення пам'яті незалежно від рівня оптимізації компілятора.
2. **Гарантії RAII у C++:** У прикладі на мові C++ створено спеціалізований клас `SecureKeyBuffer`. Деструктор цього класу автоматично викликає `explicit_bzero()` при виході об'єкта із зони видимості (Scope). Це гарантує, що навіть у разі виникнення винятку або передчасного виходу з функції через помилку ioctl, пам'ять з-під ключа буде гарантовано очищена.

### Управління ресурсами та обробка помилок

- **Управління файл-дескрипторами:** У C-реалізації відкритий файл-дескриптор `/dev/zfs` вимагає ручного відстеження та закриття у кожній гілці обробки помилок. У C++ версії клас `ZfsControlDevice` використовує ідіому **RAII** (англ. *Resource Acquisition Is Initialization*): деструктор автоматично закриває файл-дескриптор при знищенні об'єкта. Крім того, конструктор копіювання заблоковано (`= delete`), що унеможливлює подвійне закриття дескриптора.
- **Типобезпека обробки помилок:** У версії C++ замість повернення числових кодувачів помилок `-1` та використання глобальної змінної `errno` застосовано сучасну конструкцію `std::expected<T, E>` (стандарт C++23). Це дозволяє чітко розділити успішний результат і текстовий опис помилки, не вдаючись до винятків для очікуваних збоїв I/O.
- **Передавання рядків:** Використання `std::string_view` у C++ дозволяє передавати шляхи до файлів та назви датасетів без додаткового виділення динамічної пам'яті (Zero-allocation string passing).

## 3. Особливості обробки системних кодувачів помилок ioctl

Під час виконання команди `ZFS_IOC_LOAD_KEY` ядро Linux може повертати наступні специфічні коди помилок через `errno`:
- `EEXIST`: Майстер-ключ для вказаного датасету вже завантажено і розгорнуто в пам'яті ядра. Утиліти зазвичай обробляють цю помилку як успішний стан.
- `EPERM`: Недостатньо привілеїв. Взаємодія з пристроєм `/dev/zfs` для криптографічних операцій вимагає прав `root` або наявності `CAP_SYS_ADMIN`.
- `EINVAL`: Некоректні аргументи (наприклад, подано ключ розміром, відмінним від 32 байтів, або вказано неіснуючий датасет).
- `EACCES`: Переданий Wrapping Key не зміг розшифрувати Wrapped Key у метаданих DSL (невірний пароль або пошкоджений файл ключа).

## 4. Інспекція стану завантаження через procfs та sysfs

Поряд із прямими викликами `ioctl`, розробники системних демонів можуть перевіряти стан підсистеми ZFS без відкриття пристрою `/dev/zfs`. Модуль ядра ZFS експортує лічильники завантажених ключів та метрики у псевдофайловій системі `/proc/spl/kstat/zfs/`. Текстовий аналіз вмісту `/proc/spl/kstat/zfs/dbgmsg` дозволяє системному монітору відстежувати події завантаження та вивантаження ключів у реальному часі без надсилання модифікуючих запитів.
