# ⚙️ Програмне керування cgroups через DBus та sd-bus

Цей проектний приклад демонструє, як програмно створювати тимчасові юніти systemd (Transient Scopes та Services), динамічно призначати їм ліміти ресурсів cgroups v2 та перевіряти стан створених контрольних груп у віртуальній файловій системі Linux.

## Задача та архітектура рішення

Уявімо, що ми розробляємо високопродуктивний обробник фонових завдань, локальний контейнерний ранер або демон оркестрації обчислень. Кожне нове завдання, яке запускається в системі, має виконуватися у власному ізольованому середовищі зі суворо обмеженими ресурсами:
- **Оперативна пам'ять**: не більше **512 МБ** (`MemoryMax = 536870912` байтів). Перевищення цієї межі має примусово завершувати процес через механізм OOM-killer;
- **Квота CPU**: не більше **100% одного ядра** (`CPUQuotaPerSecUSec = 100000` мікросекунд на секунду);
- **Захист від мульти-потокового розростання**: не більше **64 задач** (`TasksMax = 64`), що запобігає форк-бомбам (`fork bombs`).

Прямий запис у віртуальну файлову систему `/sys/fs/cgroup/` суворо заборонений, оскільки в сучасних дистрибутивах Linux діє правило єдиного письменника (`Single Writer Rule`). Якщо наша програма створить теку в `/sys/fs/cgroup/` вручну, `systemd` сприйме її як несанкціоноване сміття під час регулярного збирання незв'язаних груп і примусово видалить її.

Тому єдино правильним рішенням є звернення до системного менеджера `systemd` (PID 1) через IPC-інтерфейс системної шини DBus із використанням стандартної C-бібліотеки `libsystemd` (компонент `sd-bus`).

---

## Детальний розбір механізму упакування DBus-повідомлень

Для створення тимчасової області (`Scope`) програма формує DBus-повідомлення до методу `StartTransientUnit` об'єкта `/org/freedesktop/systemd1`.

Найскладнішою частиною цього виклику є формування масиву властивостей **`a(sv)`** — масиву структур, кожна з яких складається з двох елементів:
1. Рядка з назвою параметрам (`"PIDs"`, `"MemoryMax"`, `"TasksMax"`);
2. Варіанта (`variant`), усередині якого запаковано маркер типу DBus та безпосереднє значення.

У низькорівневому C-API `sd-bus` це вимагає чіткої послідовності відкриття та закриття вкладених контейнерів:
- `sd_bus_message_open_container(m, 'a', "(sv)")` — відкриває головний масив властивостей;
- `sd_bus_message_open_container(m, 'r', "sv")` — відкриває окремий запис структури (сигнал `'r'` вказує на `struct`);
- `sd_bus_message_append(m, "s", "MemoryMax")` — записує назву властивості;
- `sd_bus_message_open_container(m, 'v', "t")` — відкриває значення-варіант із типом `uint64_t` (сигнал `'t'`);
- `sd_bus_message_append(m, "t", value)` — записує 64-бітне значення байтів;
- `sd_bus_message_close_container(m)` — закриває варіант `'v'`;
- `sd_bus_message_close_container(m)` — закриває структуру `'r'`;
- `sd_bus_message_close_container(m)` — закриває масив `'a'`.

Порушення цієї послідовності або незбіг типів призведе до того, що `sd-bus` поверне помилку `-EINVAL` під час формування повідомлення.

При упакуванні масиву PID використовується функція `sd_bus_message_append_array`. Вона записує 32-бітні цілі числа у бінарному форматі з вирівнюванням на 4 байти. Це забезпечує максимальну швидкість серіалізації без створення проміжних рядкових копій у пам'яті.

---

## Вихідний код реалізації

Нижче наведено повну реалізацію створення тимчасової області (`custom-app-worker.scope`) для поточного процесу двома мовами: C та ідіоматичною C++.

:::tabs
```c
#include <systemd/sd-bus.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdint.h>
#include <string.h>

int main(void) {
    sd_bus *bus = NULL;
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    int r;

    // 1. Відкриття підключення до системної шини DBus
    r = sd_bus_open_system(&bus);
    if (r < 0) {
        fprintf(stderr, "Помилка підключення до системної шини DBus: %s\n", strerror(-r));
        goto finish;
    }

    // 2. Ініціалізація виклику методу StartTransientUnit
    r = sd_bus_message_new_method_call(
        bus, &m,
        "org.freedesktop.systemd1",
        "/org/freedesktop/systemd1",
        "org.freedesktop.systemd1.Manager",
        "StartTransientUnit"
    );
    if (r < 0) {
        fprintf(stderr, "Помилка створення об'єкта повідомлення: %s\n", strerror(-r));
        goto finish;
    }

    // Аргумент 1: Назва створимого юніта (Scope)
    // Аргумент 2: Режим обробки конфліктів ("fail" повертає помилку, якщо юніт існує)
    r = sd_bus_message_append(m, "ss", "custom-app-worker.scope", "fail");
    if (r < 0) goto finish;

    // Аргумент 3: Відкриваємо масив властивостей a(sv)
    r = sd_bus_message_open_container(m, 'a', "(sv)");
    if (r < 0) goto finish;

    // Властивість 1: PIDs — масив uint32 з PID поточного процесу
    r = sd_bus_message_open_container(m, 'r', "sv");
    if (r < 0) goto finish;
    r = sd_bus_message_append(m, "s", "PIDs");
    if (r < 0) goto finish;
    r = sd_bus_message_open_container(m, 'v', "au");
    if (r < 0) goto finish;
    uint32_t current_pid = (uint32_t)getpid();
    r = sd_bus_message_append_array(m, 'u', &current_pid, sizeof(current_pid));
    if (r < 0) goto finish;
    sd_bus_message_close_container(m); // закриваємо 'v'
    sd_bus_message_close_container(m); // закриваємо 'r'

    // Властивість 2: MemoryMax = 512MB (536870912 байтів)
    r = sd_bus_message_open_container(m, 'r', "sv");
    if (r < 0) goto finish;
    r = sd_bus_message_append(m, "s", "MemoryMax");
    if (r < 0) goto finish;
    r = sd_bus_message_open_container(m, 'v', "t");
    if (r < 0) goto finish;
    uint64_t mem_limit = 512ULL * 1024ULL * 1024ULL;
    r = sd_bus_message_append(m, "t", mem_limit);
    if (r < 0) goto finish;
    sd_bus_message_close_container(m); // закриваємо 'v'
    sd_bus_message_close_container(m); // закриваємо 'r'

    // Властивість 3: TasksMax = 64
    r = sd_bus_message_open_container(m, 'r', "sv");
    if (r < 0) goto finish;
    r = sd_bus_message_append(m, "s", "TasksMax");
    if (r < 0) goto finish;
    r = sd_bus_message_open_container(m, 'v', "t");
    if (r < 0) goto finish;
    r = sd_bus_message_append(m, "t", (uint64_t)64);
    if (r < 0) goto finish;
    sd_bus_message_close_container(m); // закриваємо 'v'
    sd_bus_message_close_container(m); // закриваємо 'r'

    sd_bus_message_close_container(m); // закриваємо масив 'a(sv)'

    // Аргумент 4: Порожній масив aux units a(sa(sv))
    r = sd_bus_message_append(m, "a(sa(sv))", 0);
    if (r < 0) goto finish;

    // 3. Синхронна відправка виклику через шину DBus
    r = sd_bus_call(bus, m, 0, &error, NULL);
    if (r < 0) {
        fprintf(stderr, "Помилка виконання DBus виклику: %s\n", error.message);
        goto finish;
    }

    printf("Успішно створено Scope 'custom-app-worker.scope' для PID %d\n", getpid());

finish:
    sd_bus_error_free(&error);
    sd_bus_message_unref(m);
    sd_bus_unref(bus);
    return r < 0 ? EXIT_FAILURE : EXIT_SUCCESS;
}
```
```cpp
#include <systemd/sd-bus.h>
#include <iostream>
#include <memory>
#include <system_error>
#include <string_view>
#include <vector>
#include <unistd.h>
#include <cstdint>

// Ідіоматичні RAII-обгортки для управління ресурсами C-бібліотеки sd-bus
struct SdBusDeleter {
    void operator()(sd_bus* b) const noexcept {
        if (b) sd_bus_unref(b);
    }
};

struct SdBusMessageDeleter {
    void operator()(sd_bus_message* m) const noexcept {
        if (m) sd_bus_message_unref(m);
    }
};

using BusPtr = std::unique_ptr<sd_bus, SdBusDeleter>;
using MessagePtr = std::unique_ptr<sd_bus_message, SdBusMessageDeleter>;

class SystemdScopeManager {
public:
    // Безпечне створення Scope з налаштуваннями ресурсоізоляції
    static void create_scope_for_current_process(std::string_view scope_name, 
                                                uint64_t memory_max_bytes, 
                                                uint64_t tasks_max) {
        sd_bus* raw_bus = nullptr;
        if (int r = sd_bus_open_system(&raw_bus); r < 0) {
            throw std::system_error(-r, std::generic_category(), "Не вдалося відкрити системну шину DBus");
        }
        BusPtr bus(raw_bus);

        sd_bus_message* raw_msg = nullptr;
        if (int r = sd_bus_message_new_method_call(
                bus.get(), &raw_msg,
                "org.freedesktop.systemd1",
                "/org/freedesktop/systemd1",
                "org.freedesktop.systemd1.Manager",
                "StartTransientUnit"); r < 0) {
            throw std::system_error(-r, std::generic_category(), "Не вдалося створити об'єкт повідомлення DBus");
        }
        MessagePtr msg(raw_msg);

        // Передаємо назву юніта та режим конфліктів
        sd_bus_message_append(msg.get(), "ss", scope_name.data(), "fail");

        // Відкриваємо масив властивостей a(sv)
        sd_bus_message_open_container(msg.get(), 'a', "(sv)");

        // 1. PIDs
        append_pid_property(msg.get(), static_cast<uint32_t>(getpid()));

        // 2. MemoryMax
        append_uint64_property(msg.get(), "MemoryMax", memory_max_bytes);

        // 3. TasksMax
        append_uint64_property(msg.get(), "TasksMax", tasks_max);

        sd_bus_message_close_container(msg.get()); // a(sv)

        // Порожній масив додаткових допоміжних юнітів
        sd_bus_message_append(msg.get(), "a(sa(sv))", 0);

        sd_bus_error error = SD_BUS_ERROR_NULL;
        if (int r = sd_bus_call(bus.get(), msg.get(), 0, &error, nullptr); r < 0) {
            std::string err_text = error.message ? error.message : "Невідома помилка DBus";
            sd_bus_error_free(&error);
            throw std::runtime_error("Виклик StartTransientUnit відхилено: " + err_text);
        }

        std::cout << "Успішно створено Scope '" << scope_name 
                  << "' для PID " << getpid() << std::endl;
    }

private:
    static void append_pid_property(sd_bus_message* msg, uint32_t pid) {
        sd_bus_message_open_container(msg, 'r', "sv");
        sd_bus_message_append(msg, "s", "PIDs");
        sd_bus_message_open_container(msg, 'v', "au");
        sd_bus_message_append_array(msg, 'u', &pid, sizeof(pid));
        sd_bus_message_close_container(msg);
        sd_bus_message_close_container(msg);
    }

    static void append_uint64_property(sd_bus_message* msg, const char* name, uint64_t value) {
        sd_bus_message_open_container(msg, 'r', "sv");
        sd_bus_message_append(msg, "s", name);
        sd_bus_message_open_container(msg, 'v', "t");
        sd_bus_message_append(msg, "t", value);
        sd_bus_message_close_container(msg);
        sd_bus_message_close_container(msg);
    }
};

int main() {
    try {
        uint64_t memory_512mb = 512ULL * 1024ULL * 1024ULL;
        SystemdScopeManager::create_scope_for_current_process("custom-app-worker.scope", memory_512mb, 64);
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << std::endl;
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

---

## Порівняльний аналіз C та C++ реалізацій

Порівнюючи дві наведені реалізації, можна помітити суттєві архітектурні відмінності у підходах до проектирования системного коду під Linux:

### 1. Управління життєвим циклом ресурсів (Resource Management)

У C-реалізації управління ресурсами (`sd_bus`, `sd_bus_message`, `sd_bus_error`) виконується вручну за допомогою шаблону очищення `goto finish`. Якщо програміст забуде викликати `sd_bus_message_unref(m)` в одній із гілок обробки помилок, у системі виникне витік пам'яті та відкритих файлових дескрипторів DBus-сокета.

У C++ реалізації використання шаблону **RAII (Resource Acquisition Is Initialization)** через розумні вказівники `std::unique_ptr` зі спеціалізованими делітерами `SdBusDeleter` та `SdBusMessageDeleter` гарантує, що деструктори будуть автоматично викликані при виході з функції за будь-яких умов, навіть якщо було згенеровано виняток.

### 2. Безпека типів та рядкові параметри

У C++ версії замість сирих вказівників `const char*` використовується тип `std::string_view`, що запобігає зайвому копіюванню рядків і забезпечує чітку перевірку довжини рядка на етапі компіляції. Допоміжні функції `append_pid_property` та `append_uint64_property` інкапсулюють рутинне пакування масивів DBus, роблячи головний метод `create_scope_for_current_process` чистим і зрозумілим.

---

## Інтеграція з Polkit та обробка помилок доступу

Коли бінарний файл виконується від імені звичайного (непривілейованого) користувача, виклик `sd_bus_open_system` успішно підключається до системної шини, але виклик `StartTransientUnit` може бути відхилено демоном `Polkit` з помилкою `SD_BUS_ERROR_ACCESS_DENIED`.

Для розв'язання цієї проблеми розробники мають два шляхи:
1. Використовувати шину користувача через виклик `sd_bus_open_user(&bus)`. У цьому випадку Transient Scope створюється всередині cgroup користувача (`/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/`) без вимоги прав root;
2. Налаштувати правило Polkit у файлі `/etc/polkit-1/rules.d/50-custom-worker.rules`, яке дозволяє конкретній групі користувачів викликати `StartTransientUnit` для юнітів з відповідним префіксом.

Обробка помилок повернення `sd_bus_error` дозволяє програмі точно визначити причину відмови:
- Якщо повернуто `org.freedesktop.systemd1.UnitExists`, програма може перемикнутися на виклик `SetUnitProperties` для оновлення вже наявного Scope;
- Якщо повернуто `org.freedesktop.systemd1.NoSuchUnit`, вказаний батьківський зріз ще не існує у файловій системі.

---

## Налагодження та трасування DBus викликів

Для аналізу низькорівневих сокетних повідомлень під час запуску програми розробники можуть використовувати інструменти трасування:

```bash
# Моніторинг системної шини DBus у реальному часі
dbus-monitor --system "destination='org.freedesktop.systemd1'"

# Трасування системних викликів сокета Unix утилітою strace
strace -e trace=sendmsg,recvmsg ./worker_cpp
```

Монітор DBus показує точні бінарні пакети, які надсилає `sd-bus`, та відповіді від `systemd`, що суттєво спрощує пошук помилок упакування структур `a(sv)`.

---

## Компіляція та запуск прикладу

Для компіляції вихідного коду необхідна наявність заголовочних файлів бібліотеки `libsystemd`. У дистрибутивах Debian/Ubuntu вона встановлюється пакетом `libsystemd-dev`, у Fedora/RHEL — пакетом `systemd-devel`.

```bash
# Перевірка наявності бібліотеки через pkg-config
pkg-config --cflags --libs libsystemd

# Компіляція версії мовою C
gcc -O2 -Wall main.c -o worker_c $(pkg-config --cflags --libs libsystemd)

# Компіляція версії мовою C++ (стандарт C++20)
g++ -O2 -Wall -std=c++20 main.cpp -o worker_cpp $(pkg-config --cflags --libs libsystemd)
```

---

## Еквівалентний запуск у консолі (CLI)

За допомогою службової утиліти `systemd-run` аналогічна операція створення тимчасового Scope виконується однією консольною командою:

```bash
systemd-run --scope --unit=custom-app-worker \
  -p MemoryMax=512M \
  -p TasksMax=64 \
  /bin/bash
```

Утиліта `systemd-run` під капотом здійснює точнісінько такий самий виклик `StartTransientUnit` через DBus, упаковуючи передані через прапор `-p` параметри у масив `a(sv)`.

---

## Покрокова перевірка та верифікація в cgroups v2

Після запуску бінарного файлу (або консольної команди `systemd-run`) ви знайдете підтвердження того, що процес успішно поміщено в ізольовану cgroup:

### 1. Перевірка приналежності PID через procfs

Зчитаємо файл `/proc/self/cgroup` зсередини запущенного процесу:

```bash
cat /proc/self/cgroup
```

Приклад виводу в cgroups v2:
```
0::/user.slice/user-1000.slice/user@1000.service/custom-app-worker.scope
```

### 2. Перевірка застосованих обмежень у VFS

Перевіримо атрибути, створені systemd у віртуальній файловій системі `/sys/fs/cgroup/`:

```bash
# Перевірка жорсткого ліміту пам'яті (512 МБ = 536870912 байтів)
cat /sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/custom-app-worker.scope/memory.max
# Вивід: 536870912

# Перевірка обмеження кількості задач (64)
cat /sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/custom-app-worker.scope/pids.max
# Вивід: 64

# Перевірка списку процесів у групі
cat /sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/custom-app-worker.scope/cgroup.procs
# Вивід містить PID запущенного процесу
```

### 3. Моніторинг утилітою `systemd-cgls`

Виконання команди `systemd-cgls` у консолі продемонструє нове відгалуження в загальному дереві процесів системи:

```
└─user.slice
  └─user-1000.slice
    └─user@1000.service
      └─custom-app-worker.scope
        └─4512 ./worker_cpp
```

Це доводить, що наш додаток створив ізольовану контрольну групу у повній відповідності з архітектурними вимогами systemd та cgroups v2.
