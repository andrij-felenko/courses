# ⚙️ Програмне керування NVMe Target через configfs мовами C та C++

Утиліта `nvmetcli` є зручним високорівневим інструментом, написаним мовою Python. Вона чудово підходить для системного адміністрування та ручного налаштування сховищ через інтерфейс командного рядка. Однак у масштабних програмно-визначених сховищах (Software-Defined Storage, SDS), керуючих демонах (Control Plane) та високозавантажених контейнерних оркестраторах (наприклад, Kubernetes CSI-драйверах) виклики зовнішніх Python-скриптів є неприпустимими. Створення окремого процесу (`fork()`/`exec()`), виклик інтерпретатора Python та розбір JSON-файлів на кожну операцію підключення диска створюють величезні накладні витрати на CPU, затримують мову створення томів і вносять додаткові точки відмови.

У таких високопродуктивних системах налаштування підсистеми `nvmet` здійснюється програмно — безпосередньо з коду системного демона мовами C або C++ за допомогою системних викликів ядра для роботи з файловою системою `configfs`.

## 1. Сценарій конфігурації та логіка зв'язків у configfs

Файлова система `configfs` зазвичай монтується у точку `/sys/kernel/config/`. На відміну від `sysfs`, яка лише відображає наявний стан ядерних об'єктів і є статичною, `configfs` дозволяє користувацькому простору створювати нові дискові сутності ядра шляхом створення звичайних директорій (`mkdir`).

Процес програмного налаштування NVMe Target складається з двох послідовних фаз: створення дерева об'єктів (Provisioning Phase) та їх належного системного розмонтування (Teardown Phase).

```
/sys/kernel/config/nvmet/
├── subsystems/
│   └── nqn.2026-08.org.example:target-storage/  <── [mkdir]
│       ├── attr_allow_any_host                  <── [write: "1"]
│       └── namespaces/
│           └── 1/                               <── [mkdir]
│               ├── device_path                  <── [write: "/dev/ram0"]
│               └── enable                       <── [write: "1"]
└── ports/
    └── 1/                                       <── [mkdir]
        ├── addr_trtype                          <── [write: "tcp"]
        ├── addr_traddr                          <── [write: "192.168.1.50"]
        ├── addr_trsvcid                         <── [write: "4420"]
        ├── addr_adrfam                          <── [write: "ipv4"]
        └── subsystems/
            └── nqn.2026-08.org.example:target-storage <── [symlink]
```

### Послідовність кроків ініціалізації (Provisioning)

1. **Створення підсистеми NVMe:** Створення директорії `subsystems/<NQN>`. Ядро генерує внутрішню структуру `struct nvmet_subsys`. Ім'я директорії повинно відповідати специфікації NQN (NVMe Qualified Name).
2. **Встановлення політики авторизації:** Запис значення `"1\n"` у файл-атрибут `attr_allow_any_host`. Це дозволяє підключатися будь-якому ініціатору без перевірки списку дозволених Host NQN у списку `allowed_hosts`.
3. **Створення простору імен (Namespace):** Створення директорії `namespaces/1`, запис шляху до блокового пристрою (наприклад, `/dev/ram0` або `/dev/vg_data/lv_vol1`) у файл `device_path` та активація простору імен шляхом запису `"1\n"` у файл `enable`. Під час запису значення `"1"` ядро відкриває блоковий пристрій і вичитує його фізичний розмір та розмір сектора.
4. **Створення та налаштування мережевого порту:** Створення директорії `ports/1` та запис параметрів мережевого слухача у відповідні файли-атрибути:
   - `addr_trtype`: тип мережевого транспорту (`tcp`, `rdma`, `fc`, `loop`);
   - `addr_traddr`: IP-адреса локального мережевого інтерфейсу (`192.168.1.50`);
   - `addr_trsvcid`: номер TCP-порту або сервісу (`4420`);
   - `addr_adrfam`: сімейство мережевих адрес (`ipv4` або `ipv6`).
5. **Атомарна активація (Symlink):** Створення символічного посилання `ports/1/subsystems/<NQN>`, яке вказує на директорію підсистеми. Саме створення цього посилання спонукає ядро викликати функцію транспорту `add_port()`, відкрити мережевий сокет слухача і розпочати обробку прибуваючих з'єднань від віддалених ініціаторів.

## 2. Програмна реалізація мовами C та C++

Нижче наведено повні приклади реалізації. Вкладка C демонструє роботу з низькорівневими системними викликами POSIX (`open`, `write`, `close`, `mkdir`, `symlink`), строгим контролем файлових дескрипторів та очищенням ресурсів через шаблон `goto cleanup_*`. Вкладка C++ показує сучасний ідіоматичний підхід (стандарт C++20) з використанням кросплатформеного модуля `std::filesystem`, RAII-обгортки `configfs_directory_guard` для атомарного видалення об'єктів у разі виникнення винятків та пересилання параметрів через `std::string_view`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>

/* Допоміжна функція запису рядка у файл-атрибут configfs */
static int write_attr(const char *path, const char *val) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття атрибута %s: %s\n", path, strerror(errno));
        return -1;
    }
    ssize_t len = strlen(val);
    if (write(fd, val, len) != len) {
        fprintf(stderr, "Помилка запису у %s: %s\n", path, strerror(errno));
        close(fd);
        return -1;
    }
    close(fd);
    return 0;
}

int main(void) {
    const char *subsys_dir = "/sys/kernel/config/nvmet/subsystems/nqn.2026-08.org.example:target-storage";
    const char *ns_dir     = "/sys/kernel/config/nvmet/subsystems/nqn.2026-08.org.example:target-storage/namespaces/1";
    const char *port_dir   = "/sys/kernel/config/nvmet/ports/1";
    const char *link_dir   = "/sys/kernel/config/nvmet/ports/1/subsystems/nqn.2026-08.org.example:target-storage";

    printf("Розпочинаємо конфігурацію NVMe Target через C API...\n");

    /* 1. Створення підсистеми */
    if (mkdir(subsys_dir, 0755) < 0 && errno != EEXIST) {
        perror("mkdir subsys failed");
        return 1;
    }
    if (write_attr("/sys/kernel/config/nvmet/subsystems/nqn.2026-08.org.example:target-storage/attr_allow_any_host", "1\n") < 0)
        goto cleanup_subsys;

    /* 2. Налаштування простору імен */
    if (mkdir(ns_dir, 0755) < 0 && errno != EEXIST) {
        perror("mkdir namespace failed");
        goto cleanup_subsys;
    }
    if (write_attr("/sys/kernel/config/nvmet/subsystems/nqn.2026-08.org.example:target-storage/namespaces/1/device_path", "/dev/ram0\n") < 0)
        goto cleanup_ns;
    if (write_attr("/sys/kernel/config/nvmet/subsystems/nqn.2026-08.org.example:target-storage/namespaces/1/enable", "1\n") < 0)
        goto cleanup_ns;

    /* 3. Створення та конфігурація порту */
    if (mkdir(port_dir, 0755) < 0 && errno != EEXIST) {
        perror("mkdir port failed");
        goto cleanup_ns;
    }
    if (write_attr("/sys/kernel/config/nvmet/ports/1/addr_trtype", "tcp\n") < 0) goto cleanup_port;
    if (write_attr("/sys/kernel/config/nvmet/ports/1/addr_traddr", "192.168.1.50\n") < 0) goto cleanup_port;
    if (write_attr("/sys/kernel/config/nvmet/ports/1/addr_trsvcid", "4420\n") < 0) goto cleanup_port;
    if (write_attr("/sys/kernel/config/nvmet/ports/1/addr_adrfam", "ipv4\n") < 0) goto cleanup_port;

    /* 4. Прив'язка підсистеми до порту через symlink (Активація) */
    if (symlink(subsys_dir, link_dir) < 0 && errno != EEXIST) {
        perror("symlink failed");
        goto cleanup_port;
    }

    printf("NVMe Target успішно зконфігуровано та запущено через C API!\n");
    return 0;

/* Політика відкату при виникненні помилок */
cleanup_port:
    rmdir(port_dir);
cleanup_ns:
    write_attr("/sys/kernel/config/nvmet/subsystems/nqn.2026-08.org.example:target-storage/namespaces/1/enable", "0\n");
    rmdir(ns_dir);
cleanup_subsys:
    rmdir(subsys_dir);
    return 1;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string_view>
#include <system_error>
#include <utility>

namespace fs = std::filesystem;

// RAII-обгортка для автоматичного відкату конфігурації у разі винятків
class configfs_directory_guard {
public:
    explicit configfs_directory_guard(fs::path path) : path_(std::move(path)) {
        std::error_code ec;
        fs::create_directories(path_, ec);
        if (ec) {
            throw std::system_error(ec, "Не вдалося створити директорію configfs: " + path_.string());
        }
        created_ = true;
    }

    ~configfs_directory_guard() {
        if (created_) {
            std::error_code ec;
            fs::remove(path_, ec);
        }
    }

    // Відключення автоматичного вилучення після успішного виконання
    void dismiss() noexcept { created_ = false; }
    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    fs::path path_;
    bool created_{false};
};

static void write_config_attribute(const fs::path& attr_path, std::string_view value) {
    std::ofstream ofs(attr_path);
    if (!ofs.is_open()) {
        throw std::runtime_error("Не вдалося відкрити атрибут: " + attr_path.string());
    }
    ofs << value << '\n';
    if (!ofs.good()) {
        throw std::runtime_error("Помилка запису в атрибут: " + attr_path.string());
    }
}

int main() {
    try {
        const fs::path configfs_root = "/sys/kernel/config/nvmet";
        const std::string subsys_nqn = "nqn.2026-08.org.example:target-storage";

        std::cout << "Розпочинаємо конфігурацію NVMe Target через C++ RAII API...\n";

        // 1. Створення підсистеми з RAII захистом від збоїв
        configfs_directory_guard subsys_guard(configfs_root / "subsystems" / subsys_nqn);
        write_config_attribute(subsys_guard.path() / "attr_allow_any_host", "1");

        // 2. Створення та активація простору імен
        configfs_directory_guard ns_guard(subsys_guard.path() / "namespaces" / "1");
        write_config_attribute(ns_guard.path() / "device_path", "/dev/ram0");
        write_config_attribute(ns_guard.path() / "enable", "1");

        // 3. Створення мережевого порту
        configfs_directory_guard port_guard(configfs_root / "ports" / "1");
        write_config_attribute(port_guard.path() / "addr_trtype", "tcp");
        write_config_attribute(port_guard.path() / "addr_traddr", "192.168.1.50");
        write_config_attribute(port_guard.path() / "addr_trsvcid", "4420");
        write_config_attribute(port_guard.path() / "addr_adrfam", "ipv4");

        // 4. Створення символічного посилання прив'язки (Активація)
        const fs::path link_path = port_guard.path() / "subsystems" / subsys_nqn;
        std::error_code ec;
        fs::create_directory_symlink(subsys_guard.path(), link_path, ec);
        if (ec) {
            throw std::system_error(ec, "Не вдалося створити symlink прив'язки порту");
        }

        // У разі успіху скасовуємо автоматичне вилучення об'єктів у деструкторах
        port_guard.dismiss();
        ns_guard.dismiss();
        subsys_guard.dismiss();

        std::cout << "NVMe Target успішно зконфігуровано та запущено мовою C++ (RAII)!\n";
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка конфігурації: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

## 3. Правила вилучення ресурсів (Teardown Phase)

При демонтажі конфігурації, зупинці демона або вилученні дискового тому у сервісах оркестрації вимагається **суворий зворотний порядок виконання системних операцій**. Порушення послідовності викликів спричиняє негайну відмову системних викликів ядра:

1. **Вилучення символічного посилання (`unlink`):** Спочатку видаляється `symlink` у директорії `ports/1/subsystems/<NQN>`. Це спонукає ядро закрити TCP-сокет або зупинити RDMA-слухача. Спроба видалити директорію підсистеми `subsystems/<NQN>`, коли на неї ще вказує активний порт, поверне помилку `EBUSY` (Device or resource busy).
2. **Деактивація простору імен (`enable = 0`):** Перед вилученням директорії `namespaces/1` необхідно записати `"0\n"` у файл `enable`. Спроба виконати системний виклик `rmdir` на активному namespace відхиляється ядром з кодом `EBUSY`.
3. **Вилучення директорій (`rmdir`):** Після успішної деактивації послідовно видаляються директорії `namespaces/1`, `subsystems/<NQN>` та `ports/1`.

## 4. Підводні камені, коди помилок ядра та виробничі сценарії

Під час розробки програмних контролерів для роботи у високодоступних середовищах слід враховувати наступні специфічні коди помилок системних викликів:

- **`EADDRINUSE` при створенні `symlink`:** Виникає під час запису символічного посилання, якщо вказаний TCP-порт (наприклад, 4420) вже зайнятий іншим процесом або іншою підсистемою `nvmet`.
- **`EADDRNOTAVAIL` при створенні `symlink`:** Виникає, якщо IP-адреса, вказана у `addr_traddr`, відсутня на мережевих інтерфейсах поточного мережевого простору імен (Network Namespace).
- **`EINVAL` при запису атрибутів:** Ядро виконує строгу валідацію значень у момент виклику `write()`. Передача літер у полі порту `addr_trsvcid` або неіснуючого шляху в `device_path` викликає помилку `EINVAL` (Invalid argument).
- **Багатопотокова синхронізація в оркестраторах:** При паралельному виділенні томів із кількох потоків керуючого демона необхідно забезпечити атомарну генерацію унікальних номерів портів (`ports/1`, `ports/2`) або використовувати міжпроцесні блокування (`flock`), щоб запобігти гонитві процесів (Race Condition) за однакові директорії `configfs`.
- **Знеструмлення та аварійне завершення:** Якщо процес керуючого демона завершується аномально (`SIGKILL`), вже створена у `configfs` конфігурація залишається дієздатною всередині ядра. При перезапуску демон повинен коректно обробляти помилку `EEXIST` під час створення директорій і перевіряти стан наявних посилань.
