# ⚙️ Розробка власного генератора systemd на C та C++

Ця практична вставка детально демонструє процес створення, налаштування та тестування власного двійкового генератора для системного менеджера systemd. Створений генератор при запуску зчитує конфігураційний файл `/etc/custom-app.conf`, здійснює його парсинг, динамічно ґенерує юніт-файл служби `custom-app.service` у наданому каталозі `$1` (`normal_dir`) та створює символьне посилання у підкаталозі `multi-user.target.wants/` для забезпечення автоматичного запуску служби під час завантаження системи.

## Покрокова архітектура та алгоритм генератора

Для гарантії стабільної роботи системного менеджера генератор повинен суворо дотримуватися послідовності кроків та правил безпеки виконання:

1. **Перевірка аргументів контракту systemd**: Програма аналізує лічильник аргументів `argc`. Якщо аргументів менше чотирьох (`argv[0]` — назва бінарника, `argv[1]` — `normal_dir`, `argv[2]` — `early_dir`, `argv[3]` — `late_dir`), генератор виводить повідомлення про помилку у `stderr` та завершується з ненульовим кодом `EXIT_FAILURE`.
2. **Перевірка існування конфігураційного файлу**: Генератор перевіряє наявність файлу `/etc/custom-app.conf`. Якщо конфігурація відсутня на диску, це є цілком штатною ситуацією (наприклад, сервіс не налаштовано на даному вузлі). Генератор зобов'язаний негайно повернути код успіху `0` (`EXIT_SUCCESS`), щоб не зупиняти процес ініціалізації PID 1.
3. **Парсинг вхідних даних**: Програма зчитує текстовий файл рядок за рядком, виключає коментарі (рядки, що починаються з `#`) та порожні рядки, після чого витягує значення ключів `EXEC=` (шлях до виконуваного файлу) та `PORT=` (номер мережевого порту).
4. **Створення юніт-файла у каталозі виводу**: У каталозі `argv[1]` створюється новий файл `custom-app.service`. У файл записується INI-структура з описом служби, її залежностями (`After=network.target`), параметрами запуску (`ExecStart=`) та правилами перезапуску при збоях (`Restart=on-failure`).
5. **Формування символьного посилання залежностей**: Для автоматичного включення сервісу у граф завантаження генератор створює каталог `multi-user.target.wants` всередині `argv[1]`, після чого створює відносне символьне посилання на `../custom-app.service`.

## Крайові випадки та безпека файлових операцій

При розробці генераторів системного рівня важливо враховувати крайові випадки та потенційні збої файлової системи:

- **Гонка файлових шляхів (Race conditions)**: Символьні посилання у каталогах виводу можуть залишатися від попередніх викликів (наприклад, якщо каталоги не були очищені вручну при локальному тестуванні). Перед створенням символьного посилання викликом `symlink()` або `fs::create_relative_symlink()` розробник зобов'язаний видалити існуюче посилання (`unlink()` або `fs::remove()`), щоб уникнути помилки `EEXIST`.
- **Захист від блокування I/O**: Якщо файл конфігурації знаходиться на заблокованому змонтованому томі, відкриття файлу через `fopen()` або `std::ifstream` може затримати виконання. Генератор повинен використовувати швидкі локальні перевірки наявності через `access()` чи `fs::exists()`.
- **Коректне форматування INI-файлів**: Синтаксис systemd вимагає наявності символу нового рядка наприкінці кожного юніт-файла. Відсутність нового рядка у `ExecStart=` може призвести до помилки парсингу в PID 1.
- **Обробка некоректних портів та символів**: Якщо файл конфігурації містить некоректний номер порту (наприклад, текстовий рядок замість числа), генератор повинен або застосовувати безпечні значення за замовчуванням (`8080`), або фіксувати помилку у логу.

## Двомовна реалізація: C та C++

Нижче наведено два незалежні, ідіоматичні варіанти реалізації цього генератора. Варіант мовою C використовує низькорівневі виклики POSIX API (`mkdir`, `symlink`, `fopen`), тоді як варіант мовою C++ спирається на стандартну бібліотеку файлової системи `std::filesystem`, концепцію RAII для управління ресурсами файлів та типізовані рядкові подання `std::string_view`.

:::tabs
```c
/* custom-generator.c - Системний генератор systemd мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <errno.h>

#define CONFIG_PATH "/etc/custom-app.conf"
#define DEFAULT_EXEC "/usr/local/bin/custom-app"
#define DEFAULT_PORT "8080"

static void parse_config(const char *path, char *exec_path, size_t exec_sz, char *port, size_t port_sz) {
    FILE *f = fopen(path, "r");
    if (!f) return;

    char line[256];
    while (fgets(line, sizeof(line), f)) {
        /* Видалення символу нового рядка */
        line[strcspn(line, "\r\n")] = 0;
        if (line[0] == '#' || line[0] == '\0') continue;

        if (strncmp(line, "EXEC=", 5) == 0) {
            snprintf(exec_path, exec_sz, "%s", line + 5);
        } else if (strncmp(line, "PORT=", 5) == 0) {
            snprintf(port, port_sz, "%s", line + 5);
        }
    }
    fclose(f);
}

int main(int argc, char *argv[]) {
    /* Перевірка аргументів контракту systemd */
    if (argc < 4) {
        fprintf(stderr, "Помилка: генератор вимагає 3 аргументи (normal, early, late dirs)\n");
        return EXIT_FAILURE;
    }

    const char *normal_dir = argv[1];

    /* Перевірка наявності конфігурації */
    if (access(CONFIG_PATH, F_OK) != 0) {
        /* Якщо конфіг відсутній - це нормально, просто виходимо */
        return EXIT_SUCCESS;
    }

    char exec_path[256] = DEFAULT_EXEC;
    char port[16] = DEFAULT_PORT;
    parse_config(CONFIG_PATH, exec_path, sizeof(exec_path), port, sizeof(port));

    /* Створення шляху до юніта: <normal_dir>/custom-app.service */
    char service_path[512];
    snprintf(service_path, sizeof(service_path), "%s/custom-app.service", normal_dir);

    FILE *sf = fopen(service_path, "w");
    if (!sf) {
        fprintf(stderr, "Не вдалося створити unit-файл %s: %s\n", service_path, strerror(errno));
        return EXIT_FAILURE;
    }

    fprintf(sf,
        "[Unit]\n"
        "Description=Динамічна служба Custom App (порт %s)\n"
        "After=network.target\n\n"
        "[Service]\n"
        "Type=simple\n"
        "ExecStart=%s --port %s\n"
        "Restart=on-failure\n\n"
        "[Install]\n"
        "WantedBy=multi-user.target\n",
        port, exec_path, port);
    fclose(sf);

    /* Створення каталогу <normal_dir>/multi-user.target.wants/ */
    char wants_dir[512];
    snprintf(wants_dir, sizeof(wants_dir), "%s/multi-user.target.wants", normal_dir);
    if (mkdir(wants_dir, 0755) < 0 && errno != EEXIST) {
        fprintf(stderr, "Не вдалося створити каталог %s: %s\n", wants_dir, strerror(errno));
        return EXIT_FAILURE;
    }

    /* Створення відносного символьного посилання */
    char symlink_path[512];
    snprintf(symlink_path, sizeof(symlink_path), "%s/custom-app.service", wants_dir);

    /* Видаляємо старе посилання, якщо існувало */
    unlink(symlink_path);
    if (symlink("../custom-app.service", symlink_path) < 0) {
        fprintf(stderr, "Не вдалося створити symlink %s: %s\n", symlink_path, strerror(errno));
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
```cpp
// custom-generator.cpp - Ідіоматичний системний генератор systemd мовою C++
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <system_error>

namespace fs = std::filesystem;

constexpr std::string_view kConfigPath = "/etc/custom-app.conf";
constexpr std::string_view kDefaultExec = "/usr/local/bin/custom-app";
constexpr std::string_view kDefaultPort = "8080";

struct Config {
    std::string exec_path{kDefaultExec};
    std::string port{kDefaultPort};
};

static Config parse_config(const fs::path& config_path) {
    Config cfg;
    std::ifstream file(config_path);
    if (!file.is_open()) return cfg;

    std::string line;
    while (std::getline(file, line)) {
        if (line.empty() || line.starts_with('#')) continue;

        if (line.starts_with("EXEC=")) {
            cfg.exec_path = line.substr(5);
        } else if (line.starts_with("PORT=")) {
            cfg.port = line.substr(5);
        }
    }
    return cfg;
}

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Помилка: генератор вимагає 3 аргументи (normal, early, late dirs)\n";
        return EXIT_FAILURE;
    }

    const fs::path normal_dir = argv[1];
    const fs::path config_path = kConfigPath;

    std::error_code ec;
    if (!fs::exists(config_path, ec)) {
        return EXIT_SUCCESS;
    }

    const auto config = parse_config(config_path);
    const fs::path service_path = normal_dir / "custom-app.service";

    {
        std::ofstream sf(service_path);
        if (!sf.is_open()) {
            std::cerr << "Не вдалося створити unit-файл " << service_path << "\n";
            return EXIT_FAILURE;
        }

        sf << "[Unit]\n"
           << "Description=Динамічна служба Custom App (порт " << config.port << ")\n"
           << "After=network.target\n\n"
           << "[Service]\n"
           << "Type=simple\n"
           << "ExecStart=" << config.exec_path << " --port " << config.port << "\n"
           << "Restart=on-failure\n\n"
           << "[Install]\n"
           << "WantedBy=multi-user.target\n";
    }

    const fs::path wants_dir = normal_dir / "multi-user.target.wants";
    fs::create_directories(wants_dir, ec);
    if (ec) {
        std::cerr << "Не вдалося створити каталог " << wants_dir << ": " << ec.message() << "\n";
        return EXIT_FAILURE;
    }

    const fs::path symlink_path = wants_dir / "custom-app.service";
    fs::remove(symlink_path, ec);

    fs::create_relative_symlink(service_path, symlink_path, ec);
    if (ec) {
        std::cerr << "Не вдалося створити symlink " << symlink_path << ": " << ec.message() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## Ключові відмінності реалізацій мовами C та C++

При порівнянні двох наведених варіантів чітко видно відмінності у підходах системного програмування:

- **Керування ресурсами файлів**: У C++ варіанті вихідний потік `std::ofstream` знаходиться у власному блоці видимості `{}`. Завдяки концепції RAII (Resource Acquisition Is Initialization) файл автоматично закривається та флашиться на диск при виході з блоку. У C варіанті розробник мусить явно викликати `fclose(sf)`.
- **Робота з файловою системою**: У C++ використовується `std::filesystem::create_directories`, яка автоматично створює всі проміжні каталоги та повертає код помилки `std::error_code` без використання винятків. У C варіанті виклик `mkdir` вимагає ручної перевірки `errno != EEXIST`.
- **Створення символьних посилань**: Функція `fs::create_relative_symlink` у C++ самостійно обчислює відносний шлях між файлом та цільовим каталогом, усуваючи потребу хардкодити відносні префікси на кшталт `../custom-app.service`.

## Покрокова інсталяція, тестування та відлагодження

Для розгортання та перевірки створеного генератора у реальній системі Linux виконайте наступні команди під обліковим записом розробника або адміністратора.

### Крок 1: Компіляція та інсталяція двійкового файлу

Скомпілюйте один із варіантів генератора та скопіюйте його у системний каталог генераторів:

```bash
# Компіляція C++ версії:
g++ -O2 -std=c++20 -Wall custom-generator.cpp -o custom-generator

# Встановлення виконуваного файлу у системний каталог:
sudo cp custom-generator /lib/systemd/system-generators/
sudo chmod 0755 /lib/systemd/system-generators/custom-generator
```

### Крок 2: Автономне тестування без перезавантаження PID 1

Перш ніж підключати генератор до реального системного менеджера, його можна випробувати ручним викликом у тимчасових каталогах користувача. Це гарантує, що помилки у коді не зашкодять завантаженню системи:

```bash
# Створення тестових каталогів:
mkdir -p /tmp/gen-test/normal /tmp/gen-test/early /tmp/gen-test/late

# Запуск генератора з трьома тестовими аргументами:
/lib/systemd/system-generators/custom-generator \
  /tmp/gen-test/normal /tmp/gen-test/early /tmp/gen-test/late

# Перевірка наявності та вмісту згенерованих файлів:
ls -la /tmp/gen-test/normal/
cat /tmp/gen-test/normal/custom-app.service
ls -la /tmp/gen-test/normal/multi-user.target.wants/
```

### Крок 3: Інтеграційне тестування у системному менеджері

Створіть тестовий файл конфігурації у `/etc/custom-app.conf` та заставте systemd перезавантажити конфігурацію:

```bash
# Створення конфігураційного файлу:
echo -e "EXEC=/usr/bin/python3\nPORT=9090" | sudo tee /etc/custom-app.conf

# Виконання перезавантаження конфігураційного графа PID 1:
sudo systemctl daemon-reload

# Перевірка згенерованого файлу в оперативній пам'яті:
ls -la /run/systemd/generator/custom-app.service
cat /run/systemd/generator/custom-app.service

# Перевірка статусу юніта через systemctl:
systemctl status custom-app.service
```

Якщо все налаштовано вірно, `systemctl status` покаже службу `custom-app.service` як розпізнаний юніт у стані `loaded`, а джерелом юніта буде вказано шлях `/run/systemd/generator/custom-app.service`.
