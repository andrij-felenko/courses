# ⚙️ Розробка утиліти керування DTBO через ConfigFS

Динамічне підключення дочірніх плат (capes, Raspberry Pi HATs, розширювальні модулі) у просторі користувача вимагає від системних сервісів та демонів керування периферією прямої взаємодії з інтерфейсом ConfigFS ядра Linux. Розробка повнофункціонального програмного менеджера оверлеїв Дерева Пристроїв (DTBO Loader) забезпечує програмне завантаження, перевірку цілісності та безпечне демонтування оверлеїв через віртуальну файлову систему `/sys/kernel/config/device-tree/overlays` без залучення сторонніх shell-скриптів чи зовнішніх утиліт.

## 1. Архітектура менеджера оверлеїв та його роль у вбудованих Linux-системах

У багатьох сучасних вбудованих Linux-комп'ютерах (Embedded Linux) та гетерогенних обчислювальних системах конфігурація апаратного забезпечення перестала бути статичною. Модульні розширювальні плати (Raspberry Pi HATs, BeagleBone Capes), програмовані логічні матриці (FPGA/SoC, такі як Xilinx Zynq або Altera Cyclone V) та зовнішні периферійні модулі можуть підключатися під час роботи системи або ініціалізуватися залежно від поточної конфігурації обладнання. Можливість динамічного конфігурування шин без зупинки системи стає критичною для промислових контролерів, телекомунікаційних комутаторів та робототехнічних комплексів.

Класичний підхід із запусків shell-скриптів (`cat overlay.dtbo > /sys/kernel/config/...`) має суттєві недоліки:
1. **Відсутність валідації:** Скрипт не перевіряє цілісність бінарного файлу `.dtbo` перед відправкою у ядро. Якщо файл пошкоджений або має неправильний формат, ядро повертає помилку `-EINVAL`, проте процес не має системних засобів для точної діагностики причини.
2. **Управління ресурсами та витоки:** Якщо процес завантажив оверлей, але аварійно завершився або отримав сигнал `SIGTERM`, утиліти shell не здатні автоматично вичистити створені вузли та підключені пристрої з Дерева Пристроїв.
3. **Обробка гонки потоків (Race Conditions):** При одночасному зверненні кількох процесів до підсистеми ConfigFS відсутня синхронізація перевірки існування каталогу та виклику `mkdir()`.

Створення спеціалізованого менеджера оверлеїв мовами C та C++ дозволяє вирішити ці проблеми за рахунок чіткого дотримання семантики системних викликів, атомарного керування пам'яттю, валідації FDT-заголовка та реалізації концепції RAII (Resource Acquisition Is Initialization) для автовидалення оверлею під час завершення життєвого циклу об'єкта.

## 2. Анатомія системних викликів та файлового I/O при роботі з ConfigFS

Взаємодія програми простору користувача з підсистемою оверлеїв розбита на кілька послідовних фаз, кожна з яких опирається на конкретні системні виклики ядра Linux:

### 2.1. Перевірка та моніторинг ConfigFS (`stat`, `mount`)
Перед проведенням маніпуляцій менеджер повинен переконатися, що віртуальна файлова система ConfigFS змонтована за стандартним шляхом `/sys/kernel/config`. Для цього використовується системний виклик `stat()`. Якщо каталог відсутній або файлова система не змонтована, програма звертається до виклику `mount("none", "/sys/kernel/config", "configfs", 0, NULL)`. Якщо ядро не зібрано з підтримкою `CONFIG_CONFIGFS_FS` або `CONFIG_OF_CONFIGFS`, системний виклик поверне помилку `ENODEV`.

### 2.2. Валідація бінарного блоку FDT (`open`, `fstat`, `read`)
Файл оверлею `.dtbo` описується специфікацією Flattened Device Tree. Перші 40 байт файлу займає структура `struct fdt_header`. Менеджер зчитує заголовок і перевіряє поле `magic`. У специфікації FDT магічне число визначено як `0xd00dfeed`. Оскільки всі числові поля у заголовку FDT зберігаються у форматі Big-Endian (мережевий порядок байтів), на архітектурах Little-Endian (ARM, x86_64, RISC-V) програма повинна виконувати конвертацію через макроси `be32_to_cpu()` або функцію `std::byteswap()`.

Крім магічного числа, перевіряється поле `totalsize` — воно не повинно перевищувати фактичний розмір файла, отриманий через `fstat()`. Попередня валідація гарантує, що у ядро не буде передано довільне сміття або фрагментований блок пам'яті.

### 2.3. Створення токена оверлею (`mkdir`)
Виклик `mkdir("/sys/kernel/config/device-tree/overlays/my_overlay", 0755)` ініціює створення внутрішнього об'єкта у підсистемі ConfigFS. Ядро виділяє нову структуру `struct cfs_overlay_item` та створює у створеному каталозі віртуальні атрибути `dtbo`, `status` та `path`.

### 2.4. Передача даних та атомарність запису (`open`, `write`)
Передача бінарного блоку здійснюється шляхом відкриття атрибута `dtbo` у режимі запису (`O_WRONLY`) та виклику `write()`. Важлива вимога ядра полягає у тому, що увесь вміст `.dtbo` файлу має бути переданий за один системний виклик `write()`. Реалізації атрибута приймають блоб цілим шматком, тому запис малими порціями (наприклад, по 512 байт у циклі) у загальному випадку не працює: ядро дістає неповний FDT і відхиляє його з `-EINVAL`.

### 2.5. Верифікація результату (`read`)
Після завершення `write()` ядро виконує розгортання дерева, розв'язання phandle та виклики `probe()` драйверів. Для перевірки успішності операції менеджер відкриває атрибут `status` і зчитує рядок. Якщо накладання пройшло успішно, ядро повертає `"applied\n"`. Якщо виникла помилка у драйвері або цільовий вузол не знайдено, у файл записується код помилки.

### 2.6. Демонтування та очищення (`rmdir`)
Для видалення оверлею менеджер викликає `rmdir("/sys/kernel/config/device-tree/overlays/my_overlay")`. Ядро зупиняє пристрої, перехоплює виклики `remove()` драйверів, звільняє пам'ять структур `device_node` та відкочує транзакційні зміни `struct of_changeset`. У разі успішного виконання системного виклику каталожна структура у файловій системі ConfigFS негайно зникає, а пов'язані з нею системні ресурси повертаються до загального пулу ядра.

## 3. Реалізація менеджера оверлеїв мовами C та C++

Нижче наведено ідіоматичні реалізації менеджера оверлеїв. Приклад мовою C використовує системні виклики POSIX, явний контроль помилок та виділення пам'яті. Приклад мовою C++ використовує стандарт C++23 (`std::byteswap`), бібліотеку `std::filesystem`, RAII для автоматичного керування життєвим циклом ресурсу та обробку помилок без винятків через `std::error_code`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/mount.h>

#define CONFIGFS_PATH "/sys/kernel/config"
#define OVERLAYS_PATH "/sys/kernel/config/device-tree/overlays"
#define FDT_MAGIC 0xd00dfeedU

/* Структура заголовка Flattened Device Tree (Big-Endian) */
struct fdt_header {
    uint32_t magic;
    uint32_t totalsize;
    uint32_t off_dt_struct;
    uint32_t off_dt_strings;
    uint32_t off_mem_rsvmap;
    uint32_t version;
    uint32_t last_comp_version;
    uint32_t boot_cpuid_phys;
    uint32_t size_dt_strings;
    uint32_t size_dt_struct;
};

static uint32_t fdt32_to_cpu(uint32_t val) {
#if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
    return __builtin_bswap32(val);
#else
    return val;
#endif
}

/* Перевірка наявності та монтування ConfigFS */
static int ensure_configfs_mounted(void) {
    struct stat st;
    if (stat(OVERLAYS_PATH, &st) == 0 && S_ISDIR(st.st_mode)) {
        return 0;
    }

    if (stat(CONFIGFS_PATH, &st) != 0) {
        fprintf(stderr, "[ERR] Точка монтування %s відсутня\n", CONFIGFS_PATH);
        return -ENOENT;
    }

    if (mount("none", CONFIGFS_PATH, "configfs", 0, NULL) != 0) {
        if (errno != EBUSY) {
            perror("[ERR] Помилка монтування ConfigFS");
            return -errno;
        }
    }

    if (stat(OVERLAYS_PATH, &st) != 0 || !S_ISDIR(st.st_mode)) {
        fprintf(stderr, "[ERR] Ядро не підтримує підсистему DTBO ConfigFS (%s)\n", OVERLAYS_PATH);
        return -ENOPROTOOPT;
    }

    return 0;
}

/* Перевірка заголовка бінарного файлу DTBO */
static bool validate_dtbo_header(const uint8_t *buf, size_t size) {
    if (size < sizeof(struct fdt_header)) {
        fprintf(stderr, "[ERR] Файл занадто малий для заголовка FDT\n");
        return false;
    }

    const struct fdt_header *hdr = (const struct fdt_header *)buf;
    uint32_t magic = fdt32_to_cpu(hdr->magic);
    uint32_t totalsize = fdt32_to_cpu(hdr->totalsize);

    if (magic != FDT_MAGIC) {
        fprintf(stderr, "[ERR] Некоректний magic FDT: 0x%08x (очікувалося 0x%08x)\n", magic, FDT_MAGIC);
        return false;
    }

    if (totalsize > size) {
        fprintf(stderr, "[ERR] Заявлений розмір FDT (%u) перевищує розмір файлу (%zu)\n", totalsize, size);
        return false;
    }

    return true;
}

/* Завантаження та накладання оверлею */
int dtbo_apply(const char *overlay_name, const char *dtbo_filepath) {
    char target_dir[512];
    char dtbo_attr[512];
    char status_attr[512];
    uint8_t *buffer = NULL;
    int res = -1;
    int fd = -1;
    ssize_t nread, nwritten;
    struct stat st;

    if (ensure_configfs_mounted() != 0) {
        return -1;
    }

    fd = open(dtbo_filepath, O_RDONLY);
    if (fd < 0) {
        perror("[ERR] Помилка відкриття DTBO файлу");
        return -1;
    }

    if (fstat(fd, &st) != 0) {
        perror("[ERR] Помилка fstat");
        goto out_close_fd;
    }

    size_t file_size = (size_t)st.st_size;
    buffer = (uint8_t *)malloc(file_size);
    if (!buffer) {
        fprintf(stderr, "[ERR] Нестача пам'яті для читання DTBO\n");
        goto out_close_fd;
    }

    nread = read(fd, buffer, file_size);
    if (nread != (ssize_t)file_size) {
        fprintf(stderr, "[ERR] Неповне читання DTBO файлу\n");
        goto out_free_buf;
    }
    close(fd);
    fd = -1;

    if (!validate_dtbo_header(buffer, file_size)) {
        goto out_free_buf;
    }

    snprintf(target_dir, sizeof(target_dir), "%s/%s", OVERLAYS_PATH, overlay_name);
    if (mkdir(target_dir, 0755) != 0) {
        if (errno == EEXIST) {
            /* Каталог створив хтось інший — не чіпаємо чужий оверлей:
               інакше на будь-якій помилці нижче ми зробили б rmdir для нього. */
            fprintf(stderr, "[ERR] Оверлей %s вже існує\n", overlay_name);
        } else {
            perror("[ERR] Помилка створення каталогу оверлею в ConfigFS");
        }
        goto out_free_buf;
    }

    snprintf(dtbo_attr, sizeof(dtbo_attr), "%s/dtbo", target_dir);
    fd = open(dtbo_attr, O_WRONLY);
    if (fd < 0) {
        perror("[ERR] Помилка відкриття атрибута dtbo");
        rmdir(target_dir);
        goto out_free_buf;
    }

    nwritten = write(fd, buffer, file_size);
    close(fd);
    fd = -1;

    if (nwritten != (ssize_t)file_size) {
        fprintf(stderr, "[ERR] Помилка запису бінарного блоку в ConfigFS\n");
        rmdir(target_dir);
        goto out_free_buf;
    }

    /* Перевірка статусу накладання у ядрі */
    snprintf(status_attr, sizeof(status_attr), "%s/status", target_dir);
    fd = open(status_attr, O_RDONLY);
    if (fd >= 0) {
        char status_buf[64] = {0};
        nread = read(fd, status_buf, sizeof(status_buf) - 1);
        close(fd);
        fd = -1;
        if (nread > 0) {
            status_buf[strcspn(status_buf, "\r\n")] = 0;
            if (strcmp(status_buf, "applied") != 0) {
                fprintf(stderr, "[ERR] Ядро відхилило оверлей: %s\n", status_buf);
                rmdir(target_dir);
                goto out_free_buf;
            }
        }
    }

    printf("[OK] Оверлей '%s' успішно застосовано в ядрі\n", overlay_name);
    res = 0;

out_free_buf:
    free(buffer);
out_close_fd:
    if (fd >= 0) {
        close(fd);
    }
    return res;
}

/* Демонтування оверлею */
int dtbo_remove(const char *overlay_name) {
    char target_dir[512];
    snprintf(target_dir, sizeof(target_dir), "%s/%s", OVERLAYS_PATH, overlay_name);

    if (rmdir(target_dir) != 0) {
        perror("[ERR] Помилка видалення оверлею з ConfigFS");
        return -1;
    }

    printf("[OK] Оверлей '%s' успішно демонтовано\n", overlay_name);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Використання: %s <apply|remove> <ім'я_оверлею> [файл.dtbo]\n", argv[0]);
        return 1;
    }

    if (strcmp(argv[1], "apply") == 0) {
        if (argc < 4) {
            fprintf(stderr, "Потрібно вказати шлях до файлу .dtbo\n");
            return 1;
        }
        return dtbo_apply(argv[2], argv[3]) == 0 ? 0 : 1;
    } else if (strcmp(argv[1], "remove") == 0) {
        return dtbo_remove(argv[2]) == 0 ? 0 : 1;
    }

    fprintf(stderr, "Невідома команда: %s\n", argv[1]);
    return 1;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <filesystem>
#include <system_error>
#include <bit>
#include <cstdint>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/mount.h>

namespace fs = std::filesystem;

/* RAII-обгортка сирого дескриптора: блоб має піти в ядро одним write(),
   а std::ofstream такої гарантії не дає. */
class FileDescriptor {
public:
    explicit FileDescriptor(int fd = -1) noexcept : fd_(fd) {}
    ~FileDescriptor() { reset(); }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    explicit operator bool() const noexcept { return fd_ >= 0; }
    [[nodiscard]] int get() const noexcept { return fd_; }
    void reset() noexcept { if (fd_ >= 0) { ::close(fd_); fd_ = -1; } }

private:
    int fd_;
};

class DtboOverlayManager {
public:
    static constexpr std::string_view configfs_path = "/sys/kernel/config";
    static constexpr std::string_view overlays_path = "/sys/kernel/config/device-tree/overlays";
    static constexpr uint32_t fdt_magic = 0xd00dfeedU;

    struct FdtHeader {
        uint32_t magic;
        uint32_t totalsize;
        uint32_t off_dt_struct;
        uint32_t off_dt_strings;
        uint32_t off_mem_rsvmap;
        uint32_t version;
        uint32_t last_comp_version;
        uint32_t boot_cpuid_phys;
        uint32_t size_dt_strings;
        uint32_t size_dt_struct;
    };

    explicit DtboOverlayManager(std::string overlay_name)
        : name_(std::move(overlay_name)),
          target_path_(fs::path(overlays_path) / name_) {}

    ~DtboOverlayManager() {
        if (applied_) {
            std::error_code ec;
            remove_overlay(ec);
        }
    }

    DtboOverlayManager(const DtboOverlayManager&) = delete;
    DtboOverlayManager& operator=(const DtboOverlayManager&) = delete;

    DtboOverlayManager(DtboOverlayManager&& other) noexcept
        : name_(std::move(other.name_)),
          target_path_(std::move(other.target_path_)),
          applied_(other.applied_) {
        other.applied_ = false;
    }

    DtboOverlayManager& operator=(DtboOverlayManager&& other) noexcept {
        if (this != &other) {
            if (applied_) {
                std::error_code ec;
                remove_overlay(ec);
            }
            name_ = std::move(other.name_);
            target_path_ = std::move(other.target_path_);
            applied_ = other.applied_;
            other.applied_ = false;
        }
        return *this;
    }

    bool apply_overlay(const fs::path& dtbo_filepath, std::error_code& ec) {
        if (!ensure_configfs(ec)) {
            return false;
        }

        auto buffer = read_file(dtbo_filepath, ec);
        if (ec) {
            return false;
        }

        if (!validate_header(buffer, ec)) {
            return false;
        }

        if (!fs::exists(target_path_)) {
            if (!fs::create_directory(target_path_, ec)) {
                return false;
            }
        }

        fs::path dtbo_attr = target_path_ / "dtbo";
        FileDescriptor fd(::open(dtbo_attr.c_str(), O_WRONLY));
        if (!fd) {
            ec = std::error_code(errno, std::generic_category());
            std::error_code rm;
            fs::remove(target_path_, rm);
            return false;
        }

        const ssize_t written = ::write(fd.get(), buffer.data(), buffer.size());
        fd.reset();
        if (written < 0 || static_cast<size_t>(written) != buffer.size()) {
            ec = std::error_code(errno, std::generic_category());
            std::error_code rm;
            fs::remove(target_path_, rm);
            return false;
        }

        if (!check_status(ec)) {
            fs::remove(target_path_, ec);
            return false;
        }

        applied_ = true;
        return true;
    }

    bool remove_overlay(std::error_code& ec) {
        if (!applied_ && !fs::exists(target_path_)) {
            return true;
        }

        if (fs::remove(target_path_, ec)) {
            applied_ = false;
            return true;
        }
        return false;
    }

    [[nodiscard]] bool is_applied() const noexcept { return applied_; }
    [[nodiscard]] const std::string& name() const noexcept { return name_; }

private:
    std::string name_;
    fs::path target_path_;
    bool applied_{false};

    static bool ensure_configfs(std::error_code& ec) {
        if (fs::exists(overlays_path)) {
            return true;
        }

        if (!fs::exists(configfs_path)) {
            ec = std::make_error_code(std::errc::no_such_file_or_directory);
            return false;
        }

        if (::mount("none", configfs_path.data(), "configfs", 0, nullptr) != 0) {
            if (errno != EBUSY) {
                ec = std::error_code(errno, std::generic_category());
                return false;
            }
        }

        if (!fs::exists(overlays_path)) {
            ec = std::make_error_code(std::errc::protocol_not_supported);
            return false;
        }
        return true;
    }

    static std::vector<uint8_t> read_file(const fs::path& path, std::error_code& ec) {
        std::ifstream ifs(path, std::ios::binary | std::ios::ate);
        if (!ifs) {
            ec = std::make_error_code(std::errc::no_such_file_or_directory);
            return {};
        }

        auto size = ifs.tellg();
        ifs.seekg(0, std::ios::beg);

        std::vector<uint8_t> buffer(size);
        if (!ifs.read(reinterpret_cast<char*>(buffer.data()), size)) {
            ec = std::make_error_code(std::errc::io_error);
            return {};
        }

        return buffer;
    }

    static bool validate_header(const std::vector<uint8_t>& buffer, std::error_code& ec) {
        if (buffer.size() < sizeof(FdtHeader)) {
            ec = std::make_error_code(std::errc::executable_format_error);
            return false;
        }

        const auto* hdr = reinterpret_cast<const FdtHeader*>(buffer.data());
        const auto from_be = [](uint32_t v) -> uint32_t {
            if constexpr (std::endian::native == std::endian::little) {
                return std::byteswap(v);
            } else {
                return v;
            }
        };
        uint32_t magic = from_be(hdr->magic);
        uint32_t totalsize = from_be(hdr->totalsize);

        if (magic != fdt_magic || totalsize > buffer.size()) {
            ec = std::make_error_code(std::errc::illegal_byte_sequence);
            return false;
        }

        return true;
    }

    bool check_status(std::error_code& ec) const {
        fs::path status_attr = target_path_ / "status";
        std::ifstream ifs(status_attr);
        if (!ifs) {
            ec = std::make_error_code(std::errc::no_such_file_or_directory);
            return false;
        }

        std::string status;
        std::getline(ifs, status);
        if (!status.empty() && status.back() == '\r') {
            status.pop_back();
        }

        if (status != "applied") {
            ec = std::make_error_code(std::errc::state_not_recoverable);
            return false;
        }

        return true;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cout << "Використання: " << argv[0] << " <apply|remove> <ім'я_оверлею> [файл.dtbo]\n";
        return 1;
    }

    std::string_view cmd = argv[1];
    std::string name = argv[2];
    std::error_code ec;

    if (cmd == "apply") {
        if (argc < 4) {
            std::cerr << "Потрібно вказати шлях до файлу .dtbo\n";
            return 1;
        }

        DtboOverlayManager mgr(name);
        if (!mgr.apply_overlay(argv[3], ec)) {
            std::cerr << "[ERR] Не вдалося застосувати оверлей: " << ec.message() << "\n";
            return 1;
        }

        std::cout << "[OK] Оверлей '" << name << "' застосовано. Натисніть Enter для видалення...\n";
        std::cin.get();
        return 0;
    } else if (cmd == "remove") {
        DtboOverlayManager mgr(name);
        if (!mgr.remove_overlay(ec)) {
            std::cerr << "[ERR] Не вдалося видалити оверлей: " << ec.message() << "\n";
            return 1;
        }
        std::cout << "[OK] Оверлей '" << name << "' видалено.\n";
        return 0;
    }

    std::cerr << "Невідома команда: " << cmd << "\n";
    return 1;
}
```
:::

## 4. Порівняльний аналіз реалізацій C та C++

Обидві реалізації виконують однакову послідовність файлових операцій над підсистемою ConfigFS, проте демонструють суттєві відмінності в архітектурі управління ресурсами, безпеці типів та обробці помилок.

### 4.1. Управління пам'яттю та ресурсами
- **Версія мовою C:** Використовує ручне виділення пам'яті через `malloc()` та `free()`. Для очищення ресурсів у випадку виникнення помилок на будь-якому кроці використовується паттерн із мітками `goto out_free_buf` та `goto out_close_fd`. Це гарантує відсутність витоків пам'яті або відкритих файлових дескрипторів при передчасному виході з функції, проте вимагає від розробника ретельного стеження за кожною гілкою виконання.
- **Версія мовою C++:** Реалізує концепцію RAII. Динамічний буфер під вміст DTBO зберігається у контексті `std::vector<uint8_t>`, який автоматично вивільняє пам'ять під час виходу з області видимості. Потік читання `std::ifstream` закривається автоматично у деструкторі, а сирий дескриптор для запису блобу (він потрібен, щоб уся передача була одним `write()`) тримає обгортка `FileDescriptor`, яка викликає `close()` у своєму деструкторі.

### 4.2. Автоматичне видалення оверлею та життєвий цикл
- **Версія мовою C:** Вимагає явного виклику функції `dtbo_remove()`. Якщо програма припиняє роботу аварійно або отримує сигнал `SIGKILL`, каталог оверлею у `/sys/kernel/config/device-tree/overlays` залишається змонтованим, і пристрої залишаються в ядрі до вручного виклику `rmdir`.
- **Версія мовою C++:** Клас `DtboOverlayManager` містить прапор стану `applied_`. Деструктор класу перевіряє цей прапор і у разі його істинності автоматично викликає `remove_overlay()`. Це забезпечує локальну безпеку ресурсу: щойно об'єкт менеджеру виходить з області видимості (наприклад, при виході з функції або завершенні блоку `try/catch`), оверлей автоматично демонтується з ядра.

### 4.3. Семантика переміщення (Move Semantics)
- У версії C++ конструктори та оператори копіювання заблоковані (`= delete`), щоб уникнути ситуації, коли два об'єкти вказують на один і той самий оверлей у ConfigFS та намагаються демонтувати його двічі.
- Реалізовано конструктор та оператор переміщення (`noexcept move constructor/assignment`), які передають володіння прапором `applied_` та шляхом `target_path_` новому об'єкту, скидаючи стан попереднього об'єкта в `false`.

## 5. Процес компіляції оверлею та інтеграція з збіркою ядра

Для того, щоб менеджер оверлеїв міг успішно завантажити пристрій у ядро, джерельний код оверлею `.dts` повинен бути правильно відкомпільований у бінарний формат `.dtbo`.

### 5.1. Попередня обробка та прапори dtc
Синтаксис `.dts` підтримує макроси препроцесора C (`#include <dt-bindings/gpio/gpio.h>`). Компіляція оверлею складається з двох етапів:

1. **Запуск препроцесора C (`gcc -E`):**
   ```bash
   gcc -E -P -x assembler-with-cpp -I include/ my_overlay.dts -o my_overlay.tmp.dts
   ```
2. **Компіляція у бінарний блоб з прапором символів (`dtc -@`):**
   ```bash
   dtc -@ -I dts -O dtb -o my_overlay.dtbo my_overlay.tmp.dts
   ```

Прапор `-@` є критично важливим: без нього компілятор `dtc` не створить мета-вузол `__fixups__`, і під час спроби завантаження через `dtbo_apply()` ядро поверне помилку `status: failed to resolve fixups`.

### 5.2. Розширений аналіз багатьох фрагментів (Multi-fragment Overlays)
Складні платформи розширення (наприклад, плата з дисплеєм, сенсорним контролером I2C, аудіо-кодеком та підсвіткою PWM) вимагають створення кількох незалежних фрагментів усередині одного файлу `.dtbo`:

```dts
/dts-v1/;
/plugin/;

/ {
    fragment@0 {
        target = <&i2c1>;
        __overlay__ {
            touchscreen@38 {
                compatible = "focaltech,ft6236";
                reg = <0x38>;
            };
        };
    };

    fragment@1 {
        target = <&spi0>;
        __overlay__ {
            display@0 {
                compatible = "ilitek,ili9341";
                reg = <0>;
                spi-max-frequency = <32000000>;
            };
        };
    };
};
```

Менеджер оверлеїв обробляє такий бінарний файл суцільним блоком: функція `of_overlay_fdt_apply()` розгортає кожен фрагмент послідовно. Якщо хоча б один із фрагментів містить некоректний цільовий вузол (наприклад, `spi0` вимкнений у системі), ядро атомарно скасовує накладання усіх фрагментів оверлею, запобігаючи частковому завантаженню периферії.

### 5.3. Перевірка цілісності бінарного блоку через бібліотеку libfdt
Перед передачею бінарних даних у файлову систему ConfigFS системні демони можуть використовувати офіційну бібліотеку `libfdt` для глибшого аналізу структури DTBO у просторі користувача. Функція `fdt_check_header(buffer)` перевіряє магічне число `0xd00dfeed`, версію формату та узгодженість `totalsize` зі зміщеннями блоків — контрольної суми формат FDT не має взагалі, тож глибша перевірка вмісту лишається на утиліті. Використання `fdt_path_offset(buffer, "/__fixups__")` дозволяє утиліті заздалегідь переконатися, що оверлей містить необхідні метадані для зв'язування з базовим Деревом Пристроїв, усуваючи потребу відправляти некоректний блоб у ядро.

Утиліти керування також можуть перевіряти версію специфікації Дерева Пристроїв через поле `version` заголовка FDT (зазвичай версія 17). Якщо файл був компільований застарілою версією `dtc`, яка не підтримує розширення для оверлеїв, функція валідації заздалегідь інформує адміністратора про необхідність оновлення інструментів збірки.

## 6. Інтеграція з системними демонами та фонова експлуатація

У промислових системних рішеннях менеджер оверлеїв функціонує не як одноразова CLI-утиліта, а як внутрішній модуль фонового сервісу (daemon) у зв'язці з `systemd` та подіями `udev`.

### 6.1. Подія гарячого підключення пристрою (udev event)
Коли користувач підключає нову плату розширення (наприклад, I2C сенсорний модуль з роз'ємом hot-plug), підсистема `udev` виявляє появу пристрою на шині I2C та зчитує вміст його EEPROM. Правило `udev` генерує uevent з назвою сумісного оверлею:

```ini
ACTION=="add", SUBSYSTEM=="i2c", ATTR{name}=="hat-eeprom", RUN+="/usr/bin/dtbo-loader apply hat-sensor /lib/firmware/hat-sensor.dtbo"
```

Демон `dtbo-loader` отримує цю подію, зчитує файл з `/lib/firmware` та виконує `dtbo_apply()`. Завдяки цьому новий пристрій автоматично реєструється у ядрі, а відповідний драйвер завантажується без перезавантаження операційної системи.

### 6.2. Інтеграція з systemd unit-файлами
Якщо накладання оверлею вимагається на час роботи конкретного системного сервісу (наприклад, драйвера керування кроковими двигунами 3D-принтера чи графічного стека на SPI-дисплеї), керування оверлеєм зв'язується із життєвим циклом `systemd.service`:

```ini
[Unit]
Description=Dynamic Device Tree Overlay Manager for SPI Display
Before=display-manager.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/dtbo-loader apply spi_display /lib/firmware/spi-display.dtbo
ExecStop=/usr/bin/dtbo-loader remove spi_display

[Install]
WantedBy=multi-user.target
```

Використання директиви `RemainAfterExit=yes` у поєднанні з командами `ExecStart` та `ExecStop` гарантує, що оверлей буде накладено перед стартом залежних графічних сервісів та безпечно вилучено під час зупинки системи.

## 7. Крайові випадки, помилки та методи налагодження

Під час експлуатації утиліти керування DTBO у реальних Linux-системах розробник може зіткнутися з низкою системних помилок.

### 7.1. Помилки прав доступу (`EPERM`, `EACCES`)
Каталоги ConfigFS належать `root` і закриті звичайними правами доступу, тому для непривілейованого процесу `mkdir()` у групі оверлеїв або запис у файл `dtbo` завершиться помилкою `EACCES`; обійти перевірку прав дає лише `CAP_DAC_OVERRIDE`, а монтування самої `configfs` додатково вимагає `CAP_SYS_ADMIN`. Рекомендується перевіряти ефективний UID процесу (`geteuid() == 0`) перед викликом `dtbo_apply()` і видавати зрозумілу діагностику замість сирого коду помилки.

### 7.2. Відсутність цільового вузла у Дереві Пристроїв (`-ENODEV`)
Якщо оверлей посилається на мітку `target = <&i2c1>`, проте у базовому дереві `of_root` вузол `i2c1` відсутній або відключений (`status = "disabled"`), ядро відхилить накладання. У файлі `status` з'явиться рядок з описом помилки, а виклик `write()` поверне `-ENODEV` або `-EINVAL`. Для налагодження слід перевірити наявність вузла у каталозі `/proc/device-tree`.

### 7.3. Заблоковані пристрої при видаленні (`EBUSY`)
Якщо програма виконує `rmdir()` для демонтування оверлею, проте якийсь із створених пристроїв перебуває у використанні (наприклад, відкритий файл пристрою `/dev/spidev0.0` або утримується лінія переривань), системний виклик `rmdir()` поверне помилку `EBUSY`. Утиліта повинна спочатку завершити роботу з периферією у просторі користувача і лише після цього відключати оверлей.

### 7.4. Простеження через dmesg та ftrace
У разі виникнення складнодіагностованих помилок (наприклад, коли запис у атрибут `dtbo` завершується з невідомим кодом помилки), розробник може скористатися журналом ядра `dmesg`. Включення динамічного налагодження для модуля `drivers/of/overlay.c` командою `echo "file overlay.c +p" > /sys/kernel/debug/dynamic_debug/control` змушує ядро виводити покрокові повідомлення про процес розв'язання phandle, створення токенів та сповіщення нотифікаторів шин.

Додатково можна скористатися точками трасування ftrace:
```bash
echo 1 > /sys/kernel/debug/tracing/events/of/enable
cat /sys/kernel/debug/tracing/trace_pipe
```
Це дозволяє у реальному часі спостерігати за фазами `of_overlay_fdt_apply()` та виявляти точний фрагмент DTBO, який викликав помилку розв'язання посилань. Інструментарій ftrace разом із системним журналом `dmesg` дає системному програмісту повне бачення поведінки підсистеми Дерева Пристроїв на рівнях ядра та простору користувача.

Побудований утилітарний модуль демонструє повний цикл керування динамічною конфігурацією апаратури та слугує надійним шаблоном для проектування сучасних вбудованих Linux-систем.
