# ⚙️ Детектор рестарт-петлі та інспектор відмов юнітів systemd

Коли системна служба потрапляє в нескінченну рестарт-петлю (*CrashLoop*), супервізор systemd щосекунди породжує нові процеси, фіксує їхні аварії та заповнює системний журнал тисячами дубльованих повідомлень. Спроба розібратися в такій ситуації стандартними засобами ускладнюється тим, що вивід `systemctl status` постійно мерехтить між станами `activating`, `auto-restart` та фінальним `failed (Result: start-limit-hit)`.

У цій практичній роботі створено інженерну діагностичну утиліту `systemd-service-probe`, яка підключається напряму до системної шини D-Bus (`org.freedesktop.systemd1`), програмно вичитує низькорівневі властивості юніта в пам'яті PID 1, виявляє циклічні перезапуски та генерує точний людинозрозумілий звіт про першопричину аварії.

---

## 1. Архітектура протоколу D-Bus та механізм sd-bus

Системний менеджер systemd не зберігає свій внутрішній стан у тимчасових файлах чи реляційних базах даних. Єдиним джерелом правди про кожен зареєстрований юніт є дерево об'єктів усередині адресного простору процесу PID 1. Будь-яка консольна утиліта (`systemctl`, `journalctl`, `systemd-analyze`) взаємодіє з менеджером виключно через протокол міжпроцесної взаємодії D-Bus.

Замість важкої та застарілої бібліотеки `libdbus-1`, сучасна екосистема Linux використовує `sd-bus` — високопродуктивну реалізацію клієнта D-Bus, інтегровану в бібліотеку `libsystemd`. Основними перевагами `sd-bus` є:
* **Нульове зайве копіювання:** пряма робота з пам'яттю повідомлень та мінімальне навантаження на динамічну купу (*heap*).
* **Пряме з'єднання з ядром:** можливість взаємодії як через стандартний брокер `/run/dbus/system_bus_socket`, так і через приватний UNIX-сокет PID 1 `/run/systemd/private` у випадку збою загальносистемного демона `dbus-daemon`.
* **Типобезпечні макроси маршалінгу:** сувора перевірка сигнатур типів D-Bus (`s` для рядків, `u` для 32-бітних беззнакових цілих, `t` для 64-бітних часових міток `uint64_t`, `i` для 32-бітних знакових цілих).

Для аналізу конкретної служби утиліта виконує такий діагностичний алгоритм:
1. Ініціалізує контекст шини через системний виклик `sd_bus_open_system()`.
2. Виконує обов'язкове екранування імені юніта. Оскільки специфікація D-Bus забороняє символи крапки, дефіса та знака `@` в ідентифікаторах шляхів, виклик `sd_bus_path_encode("/org/freedesktop/systemd1/unit", unit_name, &path)` транслює рядок `nginx-custom.service` у канонічний шлях `/org/freedesktop/systemd1/unit/nginx_2dcustom_2eservice`.
3. Вичитує властивості інтерфейсу `org.freedesktop.systemd1.Unit`:
   * `ActiveState` — глобальний стан юніта (`active`, `activating`, `deactivating`, `failed`, `inactive`);
   * `SubState` — детальний стан життєвого циклу служби (`running`, `auto-restart`, `start-pre`, `dead`, `failed`);
   * `Result` — фінальний вердикт менеджера (`success`, `exit-code`, `signal`, `timeout`, `start-limit-hit`, `oom-kill`).
4. Вичитує властивості інтерфейсу `org.freedesktop.systemd1.Service`:
   * `NRestarts` — лічильник виконаних автоматичних перезапусків у поточному вікні;
   * `RestartUSec` — налаштована затримка між спробами запуску в мікросекундах;
   * `ExecMainPID` — числовий ідентифікатор останнього головного процесу;
   * `ExecMainCode` — тип виходу процесу за системними константами POSIX (`CLD_EXITED`, `CLD_KILLED`, `CLD_DUMPED`);
   * `ExecMainStatus` — числовий статус повернення `exit()` або номер сигналу ядра.

---

## 2. Реалізація діагностичної програми

Нижче наведено дві паралельні реалізації утиліти мовами C та C++. Обидві програми виконують повне опитування D-Bus, аналізують бітові комбінації статусів та виводять структурований вердикт.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <systemd/sd-bus.h>
#include <signal.h>
#include <stdbool.h>

typedef struct {
    char active_state[64];
    char sub_state[64];
    char result[64];
    uint32_t n_restarts;
    uint64_t restart_usec;
    uint32_t main_pid;
    int32_t main_code;
    int32_t main_status;
} unit_diagnostics_t;

static int query_unit_properties(sd_bus *bus, const char *unit_name, unit_diagnostics_t *diag) {
    char *path = NULL;
    int r = sd_bus_path_encode("/org/freedesktop/systemd1/unit", unit_name, &path);
    if (r < 0) {
        fprintf(stderr, "Помилка кодування об'єктного шляху D-Bus: %s\n", strerror(-r));
        return r;
    }

    char *active = NULL, *sub = NULL, *res = NULL;

    r = sd_bus_get_property_string(bus, "org.freedesktop.systemd1", path,
                                   "org.freedesktop.systemd1.Unit", "ActiveState",
                                   NULL, &active);
    if (r >= 0 && active) {
        strncpy(diag->active_state, active, sizeof(diag->active_state) - 1);
        free(active);
    }

    r = sd_bus_get_property_string(bus, "org.freedesktop.systemd1", path,
                                   "org.freedesktop.systemd1.Unit", "SubState",
                                   NULL, &sub);
    if (r >= 0 && sub) {
        strncpy(diag->sub_state, sub, sizeof(diag->sub_state) - 1);
        free(sub);
    }

    r = sd_bus_get_property_string(bus, "org.freedesktop.systemd1", path,
                                   "org.freedesktop.systemd1.Unit", "Result",
                                   NULL, &res);
    if (r >= 0 && res) {
        strncpy(diag->result, res, sizeof(diag->result) - 1);
        free(res);
    }

    sd_bus_get_property_trivial(bus, "org.freedesktop.systemd1", path,
                                "org.freedesktop.systemd1.Service", "NRestarts",
                                NULL, 'u', &diag->n_restarts);

    sd_bus_get_property_trivial(bus, "org.freedesktop.systemd1", path,
                                "org.freedesktop.systemd1.Service", "RestartUSec",
                                NULL, 't', &diag->restart_usec);

    sd_bus_get_property_trivial(bus, "org.freedesktop.systemd1", path,
                                "org.freedesktop.systemd1.Service", "ExecMainPID",
                                NULL, 'u', &diag->main_pid);

    sd_bus_get_property_trivial(bus, "org.freedesktop.systemd1", path,
                                "org.freedesktop.systemd1.Service", "ExecMainCode",
                                NULL, 'i', &diag->main_code);

    sd_bus_get_property_trivial(bus, "org.freedesktop.systemd1", path,
                                "org.freedesktop.systemd1.Service", "ExecMainStatus",
                                NULL, 'i', &diag->main_status);

    free(path);
    return 0;
}

static void print_verdict(const char *unit_name, const unit_diagnostics_t *diag) {
    printf("=================================================================\n");
    printf("ДІАГНОСТИЧНИЙ ПАСПОРТ ЮНІТА: %s\n", unit_name);
    printf("=================================================================\n");
    printf("Стан (Active/Sub):    %s / %s\n", diag->active_state, diag->sub_state);
    printf("Результат менеджера:  %s\n", diag->result);
    printf("Кількість перезапусків: %u (інтервал: %.1f c)\n",
           diag->n_restarts, (double)diag->restart_usec / 1000000.0);
    printf("Останній PID:          %u (код: %d, статус: %d)\n",
           diag->main_pid, diag->main_code, diag->main_status);
    printf("-----------------------------------------------------------------\n");

    printf("АНАЛІЗ ТА РЕКОМЕНДАЦІЇ:\n");

    if (strcmp(diag->result, "start-limit-hit") == 0) {
        printf("⚠️  КРИТИЧНО: Служба потрапила в CrashLoop і заблокована менеджером!\n");
        printf("    Перевищено ліміт StartLimitBurst у межах StartLimitIntervalSec.\n");
        printf("    Щоб відновити спроби запуску після виправлення причини, виконайте:\n");
        printf("    --> systemctl reset-failed %s\n", unit_name);
    } else if (strcmp(diag->sub_state, "auto-restart") == 0) {
        printf("⚠️  УВАГА: Служба перебуває в активній рестарт-петлі (стан очікування).\n");
        printf("    Зафіксовано вже %u невдалих перезапусків.\n", diag->n_restarts);
        printf("    Зупиніть службу для запобігання спаму в логах:\n");
        printf("    --> systemctl stop %s\n", unit_name);
    }

    if (diag->main_code == CLD_EXITED) {
        if (diag->main_status == 203) {
            printf("❌ ПОМИЛКА 203/EXEC: Ядро не змогло виконати бінарник.\n");
            printf("   1. Перевірте існування файлу ExecStart= та права chmod +x.\n");
            printf("   2. Якщо це скрипт — перевірте шлях до інтерпретатора у першому рядку (шебанг).\n");
            printf("   3. Перевірте наявність динамічного лінкера (ldd <binary>).\n");
        } else if (diag->main_status == 217) {
            printf("❌ ПОМИЛКА 217/USER: Неможливо перемкнутися на користувача в User=.\n");
            printf("   Користувач відсутній у /etc/passwd або мережевий NSS (SSSD/LDAP) ще не готовий.\n");
        } else if (diag->main_status == 226) {
            printf("❌ ПОМИЛКА 226/NAMESPACE: Збій налаштування пісочниці монтування.\n");
            printf("   Перевірте сумісність директив ProtectSystem=, PrivateTmp= з файловою системою.\n");
        } else if (diag->main_status != 0) {
            printf("❌ ПРИКЛАДНИЙ ЗБІЙ (код %d): Застосунок вийшов із власною помилкою.\n", diag->main_status);
            printf("   Перегляньте точний лог падіння:\n");
            printf("   --> journalctl -u %s -b -e --no-pager\n", unit_name);
        }
    } else if (diag->main_code == CLD_KILLED) {
        if (diag->main_status == SIGKILL) {
            printf("❌ ЗНИЩЕНО СИГНАЛОМ SIGKILL (9):\n");
            printf("   1. Спрацював ядерний cgroup OOM-killer через перевищення MemoryMax=.\n");
            printf("   2. Вичерпано таймаут запуску TimeoutStartSec= (Type=notify не надіслав READY=1).\n");
            printf("   Перевірте dmesg: dmesg -T | grep -i oom\n");
        } else if (diag->main_status == SIGABRT) {
            printf("❌ ЗНИЩЕНО СИГНАЛОМ SIGABRT (6): Програма викликала abort() або впав assert.\n");
        } else if (diag->main_status == SIGSEGV) {
            printf("❌ ЗНИЩЕНО СИГНАЛОМ SIGSEGV (11): Порушення адресації пам'яті (Segfault).\n");
        }
    }

    printf("=================================================================\n");
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <назва_юніта.service>\n", argv[0]);
        return 1;
    }

    const char *unit_name = argv[1];
    sd_bus *bus = NULL;

    int r = sd_bus_open_system(&bus);
    if (r < 0) {
        fprintf(stderr, "Не вдалося підключитися до системної шини D-Bus: %s\n", strerror(-r));
        return 1;
    }

    unit_diagnostics_t diag;
    memset(&diag, 0, sizeof(diag));

    r = query_unit_properties(bus, unit_name, &diag);
    if (r == 0) {
        print_verdict(unit_name, &diag);
    }

    sd_bus_unref(bus);
    return (r < 0) ? 1 : 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <systemd/sd-bus.h>
#include <csignal>
#include <format>
#include <expected>

namespace systemd_probe {

struct UnitDiagnostics {
    std::string active_state;
    std::string sub_state;
    std::string result;
    uint32_t n_restarts{0};
    uint64_t restart_usec{0};
    uint32_t main_pid{0};
    int32_t main_code{0};
    int32_t main_status{0};
};

struct BusDeleter {
    void operator()(sd_bus* b) const noexcept {
        if (b) ::sd_bus_unref(b);
    }
};

struct PathDeleter {
    void operator()(char* p) const noexcept {
        if (p) ::free(p);
    }
};

using ScopedBus = std::unique_ptr<sd_bus, BusDeleter>;
using ScopedPath = std::unique_ptr<char, PathDeleter>;

class Inspector {
public:
    static std::expected<Inspector, std::string> create() {
        sd_bus* raw_bus = nullptr;
        int r = ::sd_bus_open_system(&raw_bus);
        if (r < 0) {
            return std::unexpected(std::string("Не вдалося відкрити D-Bus: ") + ::strerror(-r));
        }
        return Inspector(ScopedBus(raw_bus));
    }

    std::expected<UnitDiagnostics, std::string> probe(std::string_view unit_name) const {
        char* raw_path = nullptr;
        int r = ::sd_bus_path_encode("/org/freedesktop/systemd1/unit", unit_name.data(), &raw_path);
        if (r < 0) {
            return std::unexpected(std::string("Помилка кодування шляху: ") + ::strerror(-r));
        }
        ScopedPath path(raw_path);

        UnitDiagnostics diag;

        diag.active_state = getStringProperty(path.get(), "org.freedesktop.systemd1.Unit", "ActiveState");
        diag.sub_state = getStringProperty(path.get(), "org.freedesktop.systemd1.Unit", "SubState");
        diag.result = getStringProperty(path.get(), "org.freedesktop.systemd1.Unit", "Result");

        ::sd_bus_get_property_trivial(bus_.get(), "org.freedesktop.systemd1", path.get(),
                                      "org.freedesktop.systemd1.Service", "NRestarts",
                                      nullptr, 'u', &diag.n_restarts);

        ::sd_bus_get_property_trivial(bus_.get(), "org.freedesktop.systemd1", path.get(),
                                      "org.freedesktop.systemd1.Service", "RestartUSec",
                                      nullptr, 't', &diag.restart_usec);

        ::sd_bus_get_property_trivial(bus_.get(), "org.freedesktop.systemd1", path.get(),
                                      "org.freedesktop.systemd1.Service", "ExecMainPID",
                                      nullptr, 'u', &diag.main_pid);

        ::sd_bus_get_property_trivial(bus_.get(), "org.freedesktop.systemd1", path.get(),
                                      "org.freedesktop.systemd1.Service", "ExecMainCode",
                                      nullptr, 'i', &diag.main_code);

        ::sd_bus_get_property_trivial(bus_.get(), "org.freedesktop.systemd1", path.get(),
                                      "org.freedesktop.systemd1.Service", "ExecMainStatus",
                                      nullptr, 'i', &diag.main_status);

        return diag;
    }

private:
    explicit Inspector(ScopedBus bus) : bus_(std::move(bus)) {}

    std::string getStringProperty(const char* path, const char* iface, const char* prop) const {
        char* val = nullptr;
        int r = ::sd_bus_get_property_string(bus_.get(), "org.freedesktop.systemd1", path,
                                             iface, prop, nullptr, &val);
        if (r >= 0 && val) {
            std::string res(val);
            ::free(val);
            return res;
        }
        return {};
    }

    ScopedBus bus_;
};

void printReport(std::string_view unit_name, const UnitDiagnostics& diag) {
    std::cout << "=================================================================\n";
    std::cout << "ДІАГНОСТИЧНИЙ ПАСПОРТ ЮНІТА: " << unit_name << "\n";
    std::cout << "=================================================================\n";
    std::cout << "Стан (Active/Sub):    " << diag.active_state << " / " << diag.sub_state << "\n";
    std::cout << "Результат менеджера:  " << diag.result << "\n";
    std::cout << "Кількість перезапусків: " << diag.n_restarts
              << " (інтервал: " << (static_cast<double>(diag.restart_usec) / 1'000'000.0) << " c)\n";
    std::cout << "Останній PID:          " << diag.main_pid
              << " (код: " << diag.main_code << ", статус: " << diag.main_status << ")\n";
    std::cout << "-----------------------------------------------------------------\n";

    std::cout << "АНАЛІЗ ТА РЕКОМЕНДАЦІЇ:\n";

    if (diag.result == "start-limit-hit") {
        std::cout << "⚠️  КРИТИЧНО: Служба потрапила в CrashLoop і заблокована менеджером!\n"
                  << "    Перевищено ліміт StartLimitBurst у межах StartLimitIntervalSec.\n"
                  << "    Щоб відновити спроби запуску після виправлення причини, виконайте:\n"
                  << "    --> systemctl reset-failed " << unit_name << "\n";
    } else if (diag.sub_state == "auto-restart") {
        std::cout << "⚠️  УВАГА: Служба перебуває в активній рестарт-петлі (стан очікування).\n"
                  << "    Зафіксовано вже " << diag.n_restarts << " невдалих перезапусків.\n"
                  << "    Зупиніть службу для запобігання спаму в логах:\n"
                  << "    --> systemctl stop " << unit_name << "\n";
    }

    if (diag.main_code == CLD_EXITED) {
        if (diag.main_status == 203) {
            std::cout << "❌ ПОМИЛКА 203/EXEC: Ядро не змогло виконати бінарник.\n"
                      << "   1. Перевірте існування файлу ExecStart= та права chmod +x.\n"
                      << "   2. Якщо це скрипт — перевірте шлях до інтерпретатора у шебангу (#!).\n"
                      << "   3. Перевірте наявність динамічного лінкера (ldd <binary>).\n";
        } else if (diag.main_status == 217) {
            std::cout << "❌ ПОМИЛКА 217/USER: Неможливо перемкнутися на користувача в User=.\n"
                      << "   Користувач відсутній у /etc/passwd або мережевий NSS (SSSD/LDAP) ще не готовий.\n";
        } else if (diag.main_status == 226) {
            std::cout << "❌ ПОМИЛКА 226/NAMESPACE: Збій налаштування пісочниці монтування.\n"
                      << "   Перевірте сумісність директив ProtectSystem=, PrivateTmp= з файловою системою.\n";
        } else if (diag.main_status != 0) {
            std::cout << "❌ ПРИКЛАДНИЙ ЗБІЙ (код " << diag.main_status << "): Застосунок вийшов із власною помилкою.\n"
                      << "   Перегляньте точний лог падіння:\n"
                      << "   --> journalctl -u " << unit_name << " -b -e --no-pager\n";
        }
    } else if (diag.main_code == CLD_KILLED) {
        if (diag.main_status == SIGKILL) {
            std::cout << "❌ ЗНИЩЕНО СИГНАЛОМ SIGKILL (9):\n"
                      << "   1. Спрацював ядерний cgroup OOM-killer через перевищення MemoryMax=.\n"
                      << "   2. Вичерпано таймаут запуску TimeoutStartSec= (Type=notify не надіслав READY=1).\n"
                      << "   Перевірте dmesg: dmesg -T | grep -i oom\n";
        } else if (diag.main_status == SIGABRT) {
            std::cout << "❌ ЗНИЩЕНО СИГНАЛОМ SIGABRT (6): Програма викликала abort() або впав assert.\n";
        } else if (diag.main_status == SIGSEGV) {
            std::cout << "❌ ЗНИЩЕНО СИГНАЛОМ SIGSEGV (11): Порушення адресації пам'яті (Segfault).\n";
        }
    }

    std::cout << "=================================================================\n";
}

} // namespace systemd_probe

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <назва_юніта.service>\n";
        return 1;
    }

    auto inspector = systemd_probe::Inspector::create();
    if (!inspector) {
        std::cerr << "Помилка ініціалізації: " << inspector.error() << "\n";
        return 1;
    }

    auto diag = inspector->probe(argv[1]);
    if (!diag) {
        std::cerr << "Помилка опитування юніта: " << diag.error() << "\n";
        return 1;
    }

    systemd_probe::printReport(argv[1], *diag);
    return 0;
}
```
:::

---

## 3. Збірка та покроковий розбір коду

Для компіляції програми потрібна наявність заголовних файлів бібліотеки `libsystemd` (пакет `libsystemd-dev` в Ubuntu/Debian або `systemd-devel` в RHEL/Fedora).

```bash
# Збірка версії на мові C:
gcc -O2 -Wall -Wextra -o systemd-probe-c probe.c -lsystemd

# Збірка версії на мові C++:
g++ -O2 -std=c++23 -Wall -Wextra -o systemd-probe-cpp probe.cpp -lsystemd
```

### Ключові відмінності архітектури C та C++
1. **Керування пам'яттю та дескрипторами (RAII):** У варіанті C розробник зобов'язаний вручну контролювати парність викликів `sd_bus_open_system()` та `sd_bus_unref()`, а також звільняти рядки, виділені функціями `sd_bus_path_encode()` та `sd_bus_get_property_string()`, через виклик `free()`. У версії C++ створено спеціальні структури-видалячі `BusDeleter` та `PathDeleter`, загорнуті в розумні покажчики `std::unique_ptr`. Це унеможливлює витік пам'яті або відкритих дескрипторів сокетів при виникненні винятків чи достроковому виході з функцій.
2. **Обробка системних помилок:** Замість передачі сирих числових статусів помилок POSIX (`-errno`), C++23 використовує монадний тип `std::expected<Inspector, std::string>`. Це чітко розділяє успішний результат і текстовий опис помилки, не вимагаючи глобальних змінних.
3. **Робота з рядками:** Використання `std::string_view` усуває зайві алокації при передачі імені юніта з аргументів командного рядка в методи інспектора.

---

## 4. Практичний сценарій діагностики аварійної служби

Розглянемо вивід утиліти при діагностиці аварійної служби, яка перевищила ліміт рестартів через відсутній бінарник:

```
$ ./systemd-probe-cpp nginx-custom.service
=================================================================
ДІАГНОСТИЧНИЙ ПАСПОРТ ЮНІТА: nginx-custom.service
=================================================================
Стан (Active/Sub):    failed / failed
Результат менеджера:  start-limit-hit
Кількість перезапусків: 5 (інтервал: 0.1 c)
Останній PID:          45129 (код: 1, статус: 203)
-----------------------------------------------------------------
АНАЛІЗ ТА РЕКОМЕНДАЦІЇ:
⚠️  КРИТИЧНО: Служба потрапила в CrashLoop і заблокована менеджером!
    Перевищено ліміт StartLimitBurst у межах StartLimitIntervalSec.
    Щоб відновити спроби запуску після виправлення причини, виконайте:
    --> systemctl reset-failed nginx-custom.service
❌ ПОМИЛКА 203/EXEC: Ядро не змогло виконати бінарник.
   1. Перевірте існування файлу ExecStart= та права chmod +x.
   2. Якщо це скрипт — перевірте шлях до інтерпретатора у шебангу (#!).
   3. Перевірте наявність динамічного лінкера (ldd <binary>).
=================================================================
```

---

## 5. Інспекція стану через утиліту busctl

Якщо скомпільованої бінарної утиліти немає під рукою, системний інженер може виконати еквівалентне дослідження за допомогою штатної утиліти `busctl`, яка входить до базового складу systemd:

```bash
# Перегляд усіх зареєстрованих властивостей юніта:
busctl introspect org.freedesktop.systemd1 \
  /org/freedesktop/systemd1/unit/nginx_2dcustom_2eservice \
  org.freedesktop.systemd1.Unit

# Точкове зчитування конкретного поля Result:
busctl get-property org.freedesktop.systemd1 \
  /org/freedesktop/systemd1/unit/nginx_2dcustom_2eservice \
  org.freedesktop.systemd1.Unit Result

# Зчитування лічильника перезапусків з інтерфейсу Service:
busctl get-property org.freedesktop.systemd1 \
  /org/freedesktop/systemd1/unit/nginx_2dcustom_2eservice \
  org.freedesktop.systemd1.Service NRestarts
```

---

## 6. Підводні камені та крайові випадки у клієнтах D-Bus

Під час розробки автоматизованих агентів моніторингу та діагностики системних служб слід враховувати кілька неочевидних особливостей підсистеми D-Bus:

1. **Екранування імен об'єктів (`sd_bus_path_encode`):** Юніти з дефісами, крапками чи символами `@` (шаблонізовані юніти, як-от `user@1000.service`) не можуть передаватися в D-Bus як сирі рядки. Специфікація вимагає шістнадцяткового кодування байтів (`-` перетворюється на `_2d`, `.` — на `_2e`, `@` — на `_40`). Використання функції `sd_bus_path_encode()` гарантує правильне формування об'єктного шляху.
2. **Права доступу та PolicyKit:** Непривілейований процес може вільно читати будь-які властивості юнітів через відкриту системну шину D-Bus, проте виклик активних керуючих методів (таких як `StartUnit`, `StopUnit` або `ResetFailedUnit`) вимагає підтвердження прав через підсистему `polkit`. Якщо процес не має прав root, виклик завершується помилкою `AccessDenied`.
3. **Замасковані юніти (*Masked Units*):** Якщо службу замасковано адміністратором (`systemctl mask`), її стан `ActiveState` дорівнює `inactive`, а спроба виклику методу запуску через D-Bus повертає спеціалізовану помилку `org.freedesktop.systemd1.UnitMasked`.
4. **Транзитивні стани (Race Conditions):** При опитуванні служби, що перебуває в середині фази `activating (start-pre)`, значення `ExecMainPID` може дорівнювати 0, оскільки дочірній процес основного бінарника ще не був породжений ядром. Надійний діагностичний інструмент зобов'язаний перевіряти комбінацію `ActiveState` та `SubState` перед зверненням до полів `ExecMain*`.
