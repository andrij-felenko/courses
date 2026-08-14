# ⚙️ Створення власних цільових юнітів та програмна ізоляція станів через D-Bus

Цей практичний проект демонструє розробку власного функціонального цільового юніта `kiosk.target` для розгортання вхідних терміналів та детально розбирає реалізацію системного контролера мовами C та C++, який здійснює програмну ізоляцію станів через D-Bus API системного менеджера.

---

## Концепція практичного проекту: Термінал інформаційного кіоску

Під час створення спеціалізованих вбудованих систем (наприклад, банкоматів, терміналів самообслуговування, медичних моніторів або рекламних дисплеїв) виникає потреба сформувати ізольоване операційне середовище. У такому середовищі стандартні консольні служби авторизації, фонові утиліти оновлення та графічні робочі столи мають бути примусово зупинені, а замість них повинен функціонувати лише вузький набір авторизованих додатків (браузер у режимі Kiosk Mode та Daemon моніторингу).

Для вирішення цієї задачі ми створимо власний цільовий юніт `kiosk.target`, налаштуємо його залежності через структуру каталогів `.wants/`, а також розробимо системний бінарний контролер на мовах C та C++, що виконує безпечне переключення станів через системну шину D-Bus.

---

## Проект 1: Декларативний опис та розгортання kiosk.target

Першим етапом проекту є створення та конфігурація юніт-файла нового цільового таргета у системному каталозі адміністрування.

### Крок 1. Створення конфігураційного файлу kiosk.target

Створимо файл конфігурації у каталозі `/etc/systemd/system/kiosk.target`:

```ini
[Unit]
Description=Kiosk Standalone Operational Target
Documentation=man:systemd.special(7)
Requires=multi-user.target
After=multi-user.target
Conflicts=rescue.target emergency.target
AllowIsolate=yes

[Install]
WantedBy=multi-user.target
```

#### Детальний аналіз налаштувань kiosk.target:
- **`Description=`**: Задає прозору назву юніта для системного журналу `journalctl`.
- **`Requires=multi-user.target` та `After=multi-user.target`**: Гарантують, що таргет кіоску запускається виключно поверх повністю сформованого багатокористувацького середовища (з піднятою мережею, запущені базові демони та розпізнані пристрої).
- **`Conflicts=rescue.target emergency.target`**: Визначають несумісність із режимами відновлення. Активація `kiosk.target` примусово зупиняє аварійні консолі.
- **`AllowIsolate=yes`**: Ключова директива, яка дозволяє транзакційному рушію PID 1 виконувати операцію `systemctl isolate kiosk.target`.

### Крок 2. Налаштування залежностей через каталог .wants/

Замість прямого редагування файлу `kiosk.target` скористаємося рекомендованим декларативним підходом і сформуємо склад таргета за допомогою символьних посилань у відповідному каталозі `.wants/`:

```bash
# 1. Створення каталогу декларативних залежностей таргета
sudo mkdir -p /etc/systemd/system/kiosk.target.wants

# 2. Створення юнітів служб додатків кіоску
sudo tee /etc/systemd/system/kiosk-browser.service > /dev/null << 'EOF'
[Unit]
Description=Kiosk Browser Application
After=graphical.target

[Service]
Type=simple
ExecStart=/usr/bin/chromium --kiosk --incognito https://localhost/kiosk
Restart=always
RestartSec=3s
User=kioskuser

[Install]
WantedBy=kiosk.target
EOF

sudo tee /etc/systemd/system/kiosk-watchdog.service > /dev/null << 'EOF'
[Unit]
Description=Kiosk Hardware Watchdog Daemon

[Service]
Type=simple
ExecStart=/usr/local/bin/kiosk-watchdog-daemon
Restart=always
User=root

[Install]
WantedBy=kiosk.target
EOF

# 3. Прив'язка служб до таргета через символьні посилання
sudo ln -sf /etc/systemd/system/kiosk-browser.service \
  /etc/systemd/system/kiosk.target.wants/kiosk-browser.service

sudo ln -sf /etc/systemd/system/kiosk-watchdog.service \
  /etc/systemd/system/kiosk.target.wants/kiosk-watchdog.service

# 4. Перезавантаження конфігурації PID 1 для зчитування нових таргетів
sudo systemctl daemon-reload
```

---

## Проект 2: Програмне керування ізоляцією станів через sd-bus API

У багатьох практичних сценаріях переключення операційного стану системи має виконуватися не вручну з консолі адміністратора, а повністю автоматично під дією системних подій — наприклад, при спрацюванні апаратного таймера, отриманні мережевої команди або при натисканні сервісної кнопки на панелі управління.

Для реалізації програмної ізоляції з додатків на мовах C та C++ використовується бібліотека `libsystemd` та її C-API міжпроцесного зв'язку `sd-bus`.

### Архітектура D-Bus виклику StartUnit

Програма зв'язується з системним менеджером PID 1 через системну шину D-Bus за наступними координатами:
- **Destination Name**: `org.freedesktop.systemd1`
- **Object Path**: `/org/freedesktop/systemd1`
- **Interface**: `org.freedesktop.systemd1.Manager`
- **Method Name**: `StartUnit`
- **Сигнатура аргументів**: `"ss"` (два рядки: назва юніта та режим запуску).

Передача другого аргументу у вигляді рядка `"isolate"` вказує транзакційному рушію PID 1 на необхідність виконання ізоляції станів.

### Механізм обробки помилок та управління пам'яттю D-Bus

Під час виконання IPC викликів через `sd-bus` критично важливо правильно обробляти повернені коди помилок та вчасно звільняти виділені ресурси:

1. **Ініціалізація підключення (`sd_bus_open_system`)**:
   Функція відкриває UNIX-сокет до системної шини (зазвичай `/run/systemd/system/bus`). Якщо демон D-Bus або systemd недоступний, функція повертає від'ємний код помилки (`-ECONNREFUSED` або `-ENOENT`).

2. **Обробка D-Bus помилок (`sd_bus_error`)**:
   Передана структура `sd_bus_error` заповнюється системним менеджером у разі невдачі (наприклад, якщо таргет не знайдено або у нього `AllowIsolate=no`). Після виклику обов'язково викликається `sd_bus_error_free()`.

3. **Управління лічильником посилань (`sd_bus_unref` та `sd_bus_message_unref`)**:
   Об'єкти шини та повідомлень у бібліотеці `libsystemd` використовують підрахунок посилань (Reference Counting). У C-версії очищення виконується вручну у блоці `finish`, а в C++-версії — автоматично у деструкторах смарт-вказівників `std::unique_ptr`.

### Реалізація контролера ізоляції (C та C++)

Нижче наведено два ідіоматичних варіанти реалізації контролера: у класичному стилі C із явним управлінням ресурсами та обробкою помилок `goto`, а також у сучасному стилі C++20 із застосуванням концепції RAII, розумних вказівників `std::unique_ptr` із власними делітерами та обробкою винятків `std::system_error`.

:::tabs
```c
/* controller.c — Програмна ізоляція станів через sd-bus (C) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <systemd/sd-bus.h>

/**
 * Виконує програмну ізоляцію вказаного target-юніта через D-Bus API.
 * @param target_name Назва target-юніта (наприклад, "kiosk.target")
 * @return EXIT_SUCCESS при успіху або EXIT_FAILURE при помилці
 */
int isolate_target(const char *target_name) {
    sd_bus *bus = NULL;
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    const char *job_path = NULL;
    int r;

    /* 1. Підключення до системної шини D-Bus (/run/systemd/system/bus) */
    r = sd_bus_open_system(&bus);
    if (r < 0) {
        fprintf(stderr, "Помилка: не вдалося підключитися до системної шини D-Bus: %s\n", strerror(-r));
        goto finish;
    }

    printf("Надсилання D-Bus запиту StartUnit(\"%s\", \"isolate\")...\n", target_name);

    /* 2. Відправка RPC виклику StartUnit до об'єкта PID 1 */
    r = sd_bus_call_method(
        bus,
        "org.freedesktop.systemd1",           /* Назва системного сервісу D-Bus */
        "/org/freedesktop/systemd1",          /* Шлях до головного об'єкта Manager */
        "org.freedesktop.systemd1.Manager",   /* Назва D-Bus інтерфейсу */
        "StartUnit",                          /* Метод для виклику */
        &error,                               /* Структура для повернення деталізації помилки */
        &m,                                   /* Відповідне повідомлення D-Bus */
        "ss",                                 /* Сигнатура вхідних типів: string, string */
        target_name,                          /* Аргумент 1: Назва цільового таргета */
        "isolate"                             /* Аргумент 2: Режим ізоляції */
    );

    if (r < 0) {
        fprintf(stderr, "Збій виклику StartUnit: %s\n", error.message ? error.message : strerror(-r));
        goto finish;
    }

    /* 3. Зчитування результату відповіді (ObjectPath створеної транзакції) */
    r = sd_bus_message_read(m, "o", &job_path);
    if (r < 0) {
        fprintf(stderr, "Помилка розбору відповіді D-Bus: %s\n", strerror(-r));
        goto finish;
    }

    printf("Успішно створено транзакційну роботу ізоляції: %s\n", job_path);

finish:
    /* Очищення ресурсів D-Bus */
    sd_bus_error_free(&error);
    sd_bus_message_unref(m);
    sd_bus_unref(bus);
    return r < 0 ? EXIT_FAILURE : EXIT_SUCCESS;
}

int main(int argc, char *argv[]) {
    const char *target = (argc > 1) ? argv[1] : "kiosk.target";
    return isolate_target(target);
}
```
```cpp
// controller.cpp — Програмна ізоляція станів через sd-bus RAII (C++)
#include <iostream>
#include <memory>
#include <string_view>
#include <system_error>
#include <systemd/sd-bus.h>

namespace systemd {

// Кастомний делітер для RAII обгортки шини sd_bus
struct BusDeleter {
    void operator()(sd_bus* b) const noexcept {
        if (b) {
            sd_bus_unref(b);
        }
    }
};
using BusPtr = std::unique_ptr<sd_bus, BusDeleter>;

// Кастомний делітер для RAII обгортки D-Bus повідомлення
struct MessageDeleter {
    void operator()(sd_bus_message* m) const noexcept {
        if (m) {
            sd_bus_message_unref(m);
        }
    }
};
using MessagePtr = std::unique_ptr<sd_bus_message, MessageDeleter>;

class TargetController {
public:
    /**
     * Виконує програмну ізоляцію вказаного target-юніта.
     * @param target_name Назва target-юніта
     * @throws std::system_error або std::runtime_error при помилках D-Bus
     */
    static void isolate(std::string_view target_name) {
        sd_bus* raw_bus = nullptr;
        int r = sd_bus_open_system(&raw_bus);
        if (r < 0) {
            throw std::system_error(-r, std::generic_category(), "Не вдалося відкрити системну шину D-Bus");
        }
        BusPtr bus(raw_bus);

        std::cout << "Надсилання запиту на ізоляцію для: " << target_name << "...\n";

        sd_bus_error error = SD_BUS_ERROR_NULL;
        sd_bus_message* raw_reply = nullptr;

        r = sd_bus_call_method(
            bus.get(),
            "org.freedesktop.systemd1",
            "/org/freedesktop/systemd1",
            "org.freedesktop.systemd1.Manager",
            "StartUnit",
            &error,
            &raw_reply,
            "ss",
            target_name.data(),
            "isolate"
        );

        MessagePtr reply(raw_reply);

        if (r < 0) {
            std::string err_msg = error.message ? error.message : "Невідома помилка D-Bus";
            sd_bus_error_free(&error);
            throw std::runtime_error("Збій ізоляції станів: " + err_msg);
        }

        const char* job_path = nullptr;
        r = sd_bus_message_read(reply.get(), "o", &job_path);
        if (r < 0) {
            throw std::system_error(-r, std::generic_category(), "Не вдалося зчитати ObjectPath роботи");
        }

        std::cout << "Транзакційну роботу ізоляції успішно створено: " << job_path << '\n';
    }
};

} // namespace systemd

int main(int argc, char* argv[]) {
    try {
        std::string_view target = (argc > 1) ? argv[1] : "kiosk.target";
        systemd::TargetController::isolate(target);
        return EXIT_SUCCESS;
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка виконання: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
}
```
:::

---

## Детальний розбір механізму виконання та компіляція

### Крок 1. Встановити системні залежності розробки
Для компіляції додатків, які взаємодіють із D-Bus API systemd, у системі мають бути встановлені заголовочні файли `libsystemd-dev` та інструмент `pkg-config`:

```bash
# Встановлення бібліотек розробки у Debian/Ubuntu
sudo apt-get update && sudo apt-get install -y build-essential libsystemd-dev pkg-config
```

### Крок 2. Компіляція бінарних контролерів
Компіляція виконується з лінкуванням бібліотеки `libsystemd`:

```bash
# Компіляція C-версії контролера
gcc -O2 -Wall controller.c -o isolate-c $(pkg-config --cflags --libs libsystemd)

# Компіляція C++20 версії контролера
g++ -O2 -Wall -std=c++20 controller.cpp -o isolate-cpp $(pkg-config --cflags --libs libsystemd)
```

### Крок 3. Практичне тестування ізоляції та перевірка логів

Виконаємо тестування переключення станів у реальній системі:

```bash
# 1. Запуск ізоляції та перехід у створений kiosk.target
sudo ./isolate-cpp kiosk.target

# 2. Перевірка списку активних таргетів у системі
systemctl list-units --type=target --state=active

# 3. Перевірка стану створених служб кіоску
systemctl status kiosk-browser.service kiosk-watchdog.service

# 4. Перевірка системного журналу транзакцій PID 1
sudo journalctl -u kiosk.target -n 20

# 5. Повернення системи у стандартний багатокористувацький режим
sudo ./isolate-c multi-user.target
```

У результаті виконання програми `isolate-cpp` системний менеджер PID 1 створює новий об'єкт роботи `Job`, зупиняє всі служби, які не входять до складу `kiosk.target` (і не мають захисного прапорця `IgnoreOnIsolate=yes`), та запускає служби інфокіоску, забезпечуючи точну та безпечну ізоляцію станів.
