# ⚙️ Управління юнітами systemd через D-Bus та бібліотеку sd-bus

Під час розробки високонавантажених серверних платформ або управляючих демонів виникає потреба динамічно запускати, зупиняти та моніторити фонові обробники без використання системних командних оболонок. Виклик `systemctl` через `fork()` та `execve()` створює надмірне навантаження на процесор, вимагає парсингу текстового виводу та робить обробку помилок ненадійною. Пряма взаємодія з PID 1 через D-Bus розв'язує ці проблеми, надаючи суворий бінарний протокол IPC із точним поверненням статусів та кодів помилок.

Нижче розбирається побудова шаблонного юніт-файла `app@.service` з використанням специфікаторів, оверридів та обмежень ресурсів, а також реалізація утиліти мовами C та C++ для програмного управління через системну шину D-Bus за допомогою бібліотеки `libsystemd` (`sd-bus`).

---

## 1. Архітектурне завдання та конструкція шаблонного юніта

Для забезпечення масштабованості фонових обробників створимо шаблонний юніт `/etc/systemd/system/app@.service`. Він описує загальну структуру служби, але використовує специфікатори `%i` (ім'я конкретного інстансу) та `%u` (користувач, від якого виконується процес). Окрім параметрів запуску, юніт декларує суворі межі ізоляції підсистеми `cgroups v2` та пісочниці файлової системи:

```ini
[Unit]
Description=Примірник фонової служби обробки даних для інстансу %i
After=network.target
Wants=network.target
Documentation=man:systemd.service(5)

[Service]
Type=exec
User=nobody
Group=nogroup
ExecStart=/usr/local/bin/app-worker --instance=%i --owner=%u
Restart=on-failure
RestartSec=3s

# Межі ресурсів підсистеми cgroups та пісочниця
ProtectSystem=full
ProtectHome=yes
PrivateTmp=yes
MemoryMax=256M

[Install]
WantedBy=multi-user.target
```

У цій конфігурації директива `Type=exec` гарантує, що PID 1 вважатиме службу успішно запущеною лише після того, як системний виклик `execve()` замінить образ процесу бінарним файлом `/usr/local/bin/app-worker`. Якщо бінарний файл відсутній або не має прав виконання, `ExecStart=` негайно завершиться з кодом помилки `203/EXEC`, і PID 1 переведе юніт у стан `ActiveState=failed`.

Прапорці ізоляції `ProtectSystem=full` та `PrivateTmp=yes` створюють для процесу окремий простір імен файлової системи (mount namespace). Системні каталоги `/usr`, `/etc` та `/boot` монтуються у режимі лише для читання (`read-only`), а каталог `/tmp` замінюється приватним тимчасовим каталогом у `/tmp/systemd-private-...-app@.../tmp`, що повністю виключає можливість атаки через тимчасові файли інших служб.

---

## 2. Створення оверриду без редагування шаблону

Якщо для конкретного примірника `app@worker1.service` потрібно виділити більше пам'яті та змінити командний рядок запуску, створюється дроп-ін файл у каталозі `/etc/systemd/system/app@worker1.service.d/10-custom.conf`:

```ini
[Service]
# Порожнє значення ключа скидає попередньо завантажений список команд
ExecStart=
ExecStart=/usr/local/bin/app-worker --instance=%i --owner=%u --high-performance

# Перевизначення межі пам'яті cgroup та додавання змінних оточення
MemoryMax=512M
Environment="WORKER_ENV=production" "LOG_LEVEL=debug"
ExecStartPre=/usr/bin/logger -t app-worker "Запуск інстансу %i з розширеною пам'яттю"
```

Коли PID 1 виконує `daemon-reload`, він спочатку парсит шаблон `app@.service`, а потім застосовує оверрид `10-custom.conf`. Рядок `ExecStart=` скидає попереднє значення `/usr/local/bin/app-worker...`, запобігаючи помилці спроби виконання кількох команд поспіль для служби типу `Type=exec`. Під час старту процесу ядро Linux записує межу `512M` у контрольний файл `memory.max` підсистеми `cgroups v2` за шляхом `/sys/fs/cgroup/system.slice/system-app.slice/app@worker1.service/memory.max`.

---

## 3. Програмне управління службою через C-бібліотеку `sd-bus`

Замість виконання `fork()` та `execve()` утиліти `systemctl` через системну оболонку, системне програмне забезпечення спілкується з PID 1 безпосередньо через C-бібліотеку `libsystemd`. Бібліотека надає модуль `sd-bus`, який реалізує протокол D-Bus з високою продуктивністю та нульовим копіюванням пам'яті.

### Механіка функцій `sd-bus`

1. **`sd_bus_open_system(sd_bus **ret)`** — підключає процес до сокета системної шини D-Bus (`/run/systemd/system/bus`). Виконує SASL-авотентифікацію через сокетні креденціали `SO_PEERCRED`.
2. **`sd_bus_call_method()`** — пакує назву методу, D-Bus сигнатуру вхідних аргументів (наприклад, `"ss"` для двох рядків) та надсилає синхронний запит до PID 1.
3. **`sd_bus_message_read()`** — розпаковує вихідні аргументи D-Bus відповіді за типом сигнатури (наприклад, `"o"` для об'єктного шляху D-Bus).
4. **`sd_bus_error_free()`** — звільняє текстову інформацію про помилки D-Bus у разі збою.

Нижче наведено повну реалізацію утиліти управління мовами C та C++.

:::tabs
```c
/* systemd_ctl.c — Програмне управління юнітами C-бібліотекою sd-bus */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <systemd/sd-bus.h>

#define SYSTEMD_BUS_NAME "org.freedesktop.systemd1"
#define SYSTEMD_PATH     "/org/freedesktop/systemd1"
#define SYSTEMD_MANAGER  "org.freedesktop.systemd1.Manager"

static int query_unit_state(sd_bus *bus, const char *unit_name) {
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    char *unit_path = NULL;
    char *active_state = NULL;
    int r;

    /* 1. Отримати об'єктний шлях юніта через D-Bus метод GetUnit */
    r = sd_bus_call_method(bus,
                           SYSTEMD_BUS_NAME,
                           SYSTEMD_PATH,
                           SYSTEMD_MANAGER,
                           "GetUnit",
                           &error,
                           &m,
                           "s",
                           unit_name);
    if (r < 0) {
        fprintf(stderr, "Помилка виклику GetUnit: %s\n", error.message ? error.message : "невідомо");
        sd_bus_error_free(&error);
        return r;
    }

    r = sd_bus_message_read(m, "o", &unit_path);
    if (r < 0) {
        fprintf(stderr, "Помилка зчитування шляху об'єкта: %s\n", strerror(-r));
        sd_bus_message_unref(m);
        return r;
    }
    printf("Об'єктний шлях юніта %s: %s\n", unit_name, unit_path);

    /* 2. Прочитати властивість ActiveState з юніта */
    r = sd_bus_get_property_string(bus,
                                   SYSTEMD_BUS_NAME,
                                   unit_path,
                                   "org.freedesktop.systemd1.Unit",
                                   "ActiveState",
                                   &error,
                                   &active_state);
    if (r < 0) {
        fprintf(stderr, "Помилка читання ActiveState: %s\n", error.message ? error.message : "невідомо");
        sd_bus_error_free(&error);
        sd_bus_message_unref(m);
        return r;
    }

    printf("Поточний стан (ActiveState) юніта %s: %s\n", unit_name, active_state);

    free(active_state);
    sd_bus_message_unref(m);
    return 0;
}

static int start_unit(sd_bus *bus, const char *unit_name) {
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    char *job_path = NULL;
    int r;

    /* Викликати StartUnit із режимом транзакції "replace" */
    r = sd_bus_call_method(bus,
                           SYSTEMD_BUS_NAME,
                           SYSTEMD_PATH,
                           SYSTEMD_MANAGER,
                           "StartUnit",
                           &error,
                           &m,
                           "ss",
                           unit_name,
                           "replace");
    if (r < 0) {
        fprintf(stderr, "Не вдалося запустити юніт %s: %s\n", unit_name, error.message ? error.message : "невідомо");
        sd_bus_error_free(&error);
        return r;
    }

    r = sd_bus_message_read(m, "o", &job_path);
    if (r >= 0) {
        printf("Запит на запуск відправлено. Шлях транзакції Job: %s\n", job_path);
    }

    sd_bus_message_unref(m);
    return 0;
}

int main(int argc, char *argv[]) {
    sd_bus *bus = NULL;
    const char *unit_name = (argc > 1) ? argv[1] : "app@worker1.service";
    int r;

    /* Підключитися до системної шини D-Bus */
    r = sd_bus_open_system(&bus);
    if (r < 0) {
        fprintf(stderr, "Не вдалося підключитися до системної шини: %s\n", strerror(-r));
        return EXIT_FAILURE;
    }

    printf("Підключено до D-Bus systemd.\n");

    if (query_unit_state(bus, unit_name) >= 0) {
        printf("Надсилання команди StartUnit для %s...\n", unit_name);
        start_unit(bus, unit_name);
    }

    sd_bus_unref(bus);
    return EXIT_SUCCESS;
}
```
```cpp
// systemd_ctl.cpp — Програмне управління юнітами C++17 RAII обгорткою над sd-bus
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <system_error>
#include <systemd/sd-bus.h>

namespace sysd {

// RAII функтор для автоматичного вивантаження шини D-Bus
struct bus_deleter {
    void operator()(sd_bus* b) const noexcept {
        if (b) sd_bus_unref(b);
    }
};

// RAII функтор для вивантаження повідомлень D-Bus
struct message_deleter {
    void operator()(sd_bus_message* m) const noexcept {
        if (m) sd_bus_message_unref(m);
    }
};

using bus_ptr = std::unique_ptr<sd_bus, bus_deleter>;
using message_ptr = std::unique_ptr<sd_bus_message, message_deleter>;

class manager {
public:
    static manager connect_system() {
        sd_bus* b = nullptr;
        int r = sd_bus_open_system(&b);
        if (r < 0) {
            throw std::system_error(-r, std::generic_category(), "Не вдалося відкрити системну шину D-Bus");
        }
        return manager(bus_ptr(b));
    }

    std::string get_unit_path(std::string_view unit_name) const {
        sd_bus_error error = SD_BUS_ERROR_NULL;
        sd_bus_message* reply_raw = nullptr;

        int r = sd_bus_call_method(bus_.get(),
                                   "org.freedesktop.systemd1",
                                   "/org/freedesktop/systemd1",
                                   "org.freedesktop.systemd1.Manager",
                                   "GetUnit",
                                   &error,
                                   &reply_raw,
                                   "s",
                                   std::string(unit_name).c_str());
        
        message_ptr reply(reply_raw);
        if (r < 0) {
            std::string msg = error.message ? error.message : "Помилка D-Bus виклику";
            sd_bus_error_free(&error);
            throw std::runtime_error(msg);
        }

        char* path = nullptr;
        r = sd_bus_message_read(reply.get(), "o", &path);
        if (r < 0 || !path) {
            throw std::runtime_error("Не вдалося розпарсити об'єктний шлях юніта з відповіді");
        }

        return std::string(path);
    }

    std::string get_active_state(std::string_view unit_path) const {
        sd_bus_error error = SD_BUS_ERROR_NULL;
        char* state_str = nullptr;

        int r = sd_bus_get_property_string(bus_.get(),
                                           "org.freedesktop.systemd1",
                                           std::string(unit_path).c_str(),
                                           "org.freedesktop.systemd1.Unit",
                                           "ActiveState",
                                           &error,
                                           &state_str);
        if (r < 0) {
            std::string msg = error.message ? error.message : "Помилка читання ActiveState";
            sd_bus_error_free(&error);
            throw std::runtime_error(msg);
        }

        std::string result(state_str);
        free(state_str);
        return result;
    }

    std::string start_unit(std::string_view unit_name, std::string_view mode = "replace") const {
        sd_bus_error error = SD_BUS_ERROR_NULL;
        sd_bus_message* reply_raw = nullptr;

        int r = sd_bus_call_method(bus_.get(),
                                   "org.freedesktop.systemd1",
                                   "/org/freedesktop/systemd1",
                                   "org.freedesktop.systemd1.Manager",
                                   "StartUnit",
                                   &error,
                                   &reply_raw,
                                   "ss",
                                   std::string(unit_name).c_str(),
                                   std::string(mode).c_str());

        message_ptr reply(reply_raw);
        if (r < 0) {
            std::string msg = error.message ? error.message : "Не вдалося запустити юніт";
            sd_bus_error_free(&error);
            throw std::runtime_error(msg);
        }

        char* job_path = nullptr;
        r = sd_bus_message_read(reply.get(), "o", &job_path);
        return job_path ? std::string(job_path) : std::string();
    }

private:
    explicit manager(bus_ptr b) : bus_(std::move(b)) {}
    bus_ptr bus_;
};

} // namespace sysd

int main(int argc, char* argv[]) {
    try {
        const std::string unit_name = (argc > 1) ? argv[1] : "app@worker1.service";
        auto sysd_mgr = sysd::manager::connect_system();
        std::cout << "Успішне підключення до D-Bus systemd (C++ RAII).\n";

        std::string path = sysd_mgr.get_unit_path(unit_name);
        std::cout << "Об'єктний шлях: " << path << '\n';

        std::string state = sysd_mgr.get_active_state(path);
        std::cout << "Поточний ActiveState: " << state << '\n';

        std::cout << "Запуск юніта " << unit_name << "...\n";
        std::string job = sysd_mgr.start_unit(unit_name);
        std::cout << "Створено транзакційну роботу Job: " << job << '\n';
    }
    catch (const std::exception& ex) {
        std::cerr << "Критична помилка виконання: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 4. Особливості C++ реалізації та управління ресурсами (RAII)

У реалізації C++ класи підключення та повідомлень загорнуті у розумні вказівники `std::unique_ptr` із власними деструкторами `bus_deleter` та `message_deleter`. Це гарантує відсутність витоків пам'яті та дескрипторів сокетів навіть у разі виникнення винятків під час виклику D-Bus методів.

Переваги C++ RAII обгортки перед прямим C API:
- **Автоматичне управління ресурсами.** У разі викидання винятку `std::runtime_error` під час розпарсингу відповіді D-Bus, деструктори `bus_ptr` та `message_ptr` автоматично деінсталюють підключення та викличуть `sd_bus_unref()`.
- **Безпечна передача рядків.** Застосування `std::string_view` у викликах методів виключає непотрібне копіювання рядків на стеку, а вихідні значення повертаються у вигляді бепечних об'єктів `std::string`.
- **Строга трансформованість помилок.** Помилки `sd_bus_error` конвертуються у винятки `std::system_error` з відповідними кодами системних категорій.

---

## 5. Компіляція, виконання та верифікація

Для успішного збирання обох проектів у системі мають бути встановлені заголовочні файли та бібліотека `libsystemd` (пакет `libsystemd-dev` у дистрибутивах Debian/Ubuntu або `systemd-devel` у Fedora/RHEL/CentOS).

Компіляція виконується наступними командами:

```bash
# Компіляція C-реалізації з лінкуванням бібліотеки -lsystemd
gcc -Wall -Wextra systemd_ctl.c -lsystemd -o systemd_ctl_c

# Компіляція C++17-реалізації
g++ -std=c++17 -Wall -Wextra systemd_ctl.cpp -lsystemd -o systemd_ctl_cpp
```

### Запуск та верифікація ресурсів у cgroups

Оскільки взаємодія з системною шиною вимагає привілейованого доступу до системного менеджера, утиліти запускаються з правами користувача `root` або через `sudo`:

```bash
# Завантажити нові юніти у пам'ять PID 1
sudo systemctl daemon-reload

# Виконати програмний запуск юніта через C++ утиліту
sudo ./systemd_ctl_cpp app@worker1.service
```

Після виконання утиліти перевірка стану через `systemctl status app@worker1.service` підтверджує, що служба була завантажена з урахуванням оверридів, а її процеси розміщені у відповідному вузлі контрольної групи cgroups:

```
● app@worker1.service - Примірник фонової служби обробки даних для інстансу worker1
     Loaded: loaded (/etc/systemd/system/app@.service; disabled; vendor preset: enabled)
    Drop-In: /etc/systemd/system/app@worker1.service.d
             └─10-custom.conf
     Active: active (running) since Fri 2026-08-14 10:00:00 EEST; 5s ago
   Main PID: 8412 (app-worker)
      Tasks: 1 (limit: 4915)
     Memory: 4.2M (max: 512.0M)
        CPU: 12ms
     CGroup: /system.slice/system-app.slice/app@worker1.service
             └─8412 /usr/local/bin/app-worker --instance=worker1 --owner=nobody --high-performance
```

### Моніторинг трафіку D-Bus через `busctl`

Для діагностики викликів D-Bus під час роботи програмного коду використовують інструмент `busctl`:

```bash
# Відстеження повідомлень у реальному часі на шині systemd
sudo busctl monitor org.freedesktop.systemd1
```

Результат виводу підтверджує успішне поєднання шаблону `%i`, застосування оверриду `10-custom.conf` (`MemoryMax: 512.0M`), та коректний програмний запуск через D-Bus без виклику зовнішніх інтерпретаторів Shell.
