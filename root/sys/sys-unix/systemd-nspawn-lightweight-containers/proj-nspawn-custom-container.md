# ⚙️ Практичне створення та програмне управління контейнером systemd-nspawn

Дане практичне керівництво демонструє повний процес розгортання та програмного управління мінімальним контейнером systemd-nspawn у середовищі Linux. У статті детально розглядається розгортання файлового дерева `rootfs` дистрибутива, декларативне конфігурування віртуальної мережі через `systemd-networkd`, автоматизація запуску контейнера у якості системної служби хоста та побудова програмного інструментарію мовами C та C++ для взаємодії з демоном `systemd-machined` через системну шину D-Bus.

---

### 1. Підготовка файлового дерева rootfs та розгортання контейнера

Для побудови чистого системного середовища контейнера необхідно розгорнути мінімальне дерево файлової системи дистрибутива Linux. У цьому прикладі використовується інструмент `debootstrap` для розгортання базового оточення Debian Linux у директорії `/var/lib/machines/web-node1`. Інструмент виконує послідовне завантаження, перевірку підписів пакунків за допомогою ключів GPG (`/usr/share/keyrings/debian-archive-keyring.gpg`), розпакування та конфігурування основних пакунків ядра, системних бібліотек (`glibc`), базових утиліт користувацького простору та системного менеджера ініціалізації `systemd`.

Під час першої фази `debootstrap` витягує двійкові пакунки `.deb` із дзеркала дистрибутива та розпаковує їх у вказану директорію. На другій фазі інструмент викликає `chroot` для виконання конфігураційних скриптів `postinst` усередині розпакованого середовища, створюючи бази даних пакунків `dpkg`, системні облікові записи користувачів та файли конфігурації у директорії `/etc`.

Використання директорії `/var/lib/machines` є стандартною практикою екосистеми systemd: утиліти `machinectl` та `systemd-nspawn` за замовчуванням сканують цю директорію під час пошуку зареєстрованих контейнерів хоста. Монтування або створення директорій за цією адресою дозволяє службі `systemd-machined` автоматично виявляти нові файлові структури, підключати Btrfs subvolumes або OverlayFS шари та відображати їх у списках доступних системних машин.

```bash
# 1. Створення цільової директорії для файлової системи контейнера
sudo mkdir -p /var/lib/machines/web-node1

# 2. Розгортання мінімального системного дерева Debian Bookworm
sudo debootstrap --variant=minbase bookworm /var/lib/machines/web-node1 http://deb.debian.org/debian/

# 3. Встановлення пароля суперкористувача root усередині контейнера
sudo systemd-nspawn -D /var/lib/machines/web-node1 passwd
```

Після виконання цих команд директорія `/var/lib/machines/web-node1` містить автономну та повну файлову структуру ОС зі своїми директоріями `/etc`, `/usr`, `/var` та `/bin`. Усі шляхи файлової системи є ізольованими, але для повноцінного завантаження необхідно налаштувати мережеву взаємодію.

---

### 2. Декларативне конфігурування мережі та файли .nspawn

Для забезпечення мережевої ізоляції та автоматичного налаштування трансляції портів створюється конфігураційний файл `/etc/systemd/nspawn/web-node1.nspawn`. Він описує активацію повноцінного режиму завантаження ОС (`Boot=yes`), виділення унікального діапазону користувачів у User namespace (`PrivateUsers=pick`) та створення віртуальної мережевої пари `veth`.

```ini
[Exec]
Boot=yes
PrivateUsers=pick

[Network]
Private=yes
VirtualEthernet=yes
Port=tcp:8080:80
```

Коли увімкнено директиву `VirtualEthernet=yes`, `systemd-nspawn` надсилає повідомлення `RTM_NEWLINK` до підсистеми `rtnetlink` ядра Linux. Ядро створює пару зв'язаних віртуальних мережевих інтерфейсів: один інтерфейс залишається у Network namespace хоста під іменем `ve-web-node1`, а другий переміщується у Network namespace контейнера під іменем `host0`.

Для автоматичного призначення IP-адрес та надання доступу до зовнішньої мережі хоста використовується демон `systemd-networkd`. На хості створюється конфігураційний файл `/etc/systemd/network/80-nspawn-veth.network`, який автоматично перехоплює всі віртуальні мережеві інтерфейси хоста з префіксом `ve-`, виділяє їм статичну адресу та запускає внутрішній DHCP-сервер:

```ini
[Match]
Name=ve-*

[Network]
Address=10.0.0.1/24
DHCPServer=yes
IPMasquerade=ipv4
```

Директива `IPMasquerade=ipv4` наказує `systemd-networkd` автоматично додати правила трансляції мережевих адрес (NAT/Masquerade) у таблиці `nftables` або `iptables` хоста, а також увімкнути переадресацію пакетів у ядрі (`sysctl net.ipv4.ip_forward=1`). Завдяки оцій конфігурації під час запуску контейнера на хості автоматично виникає мережевий інтерфейс `ve-web-node1`, а усередині контейнера з'являється інтерфейс `host0`, який отримує IP-адресу через DHCP від хоста та має доступ до зовнішньої мережі Інтернет.

---

### 3. Автоматизація запуску контейнера через шаблонований службовий юніт

Система systemd надає вбудований шаблонований службовий юніт `systemd-nspawn@.service`. Це дозволяє керувати контейнером як звичайною системною службою хоста через `systemctl`. 

Розглянемо ключові директиви шаблонованого юніта `systemd-nspawn@.service`:
- `ExecStart=/usr/bin/systemd-nspawn --quiet --keep-unit --boot --link-journal=try-guest --settings=override --machine=%i`: Команда запуску витягує ім'я контейнера зі змінної `%i`, підключає файли налаштувань `.nspawn` та автоматично перенаправляє логи контейнера до хостового демона `systemd-journald`.
- `Delegate=yes`: Дозволяє контейнеру самостійно керувати власними дочірніми cgroups усередині виділеного scope.
- `KillMode=mixed`: При зупиненні служби systemd спочатку надсилає сигнал `SIGRTMIN+3` (сигнал акуратного завершення systemd) до PID 1 контейнера, а після вичерпання таймауту примусово завершує всі залишок процесів за допомогою `SIGKILL`.

Управління контейнером через системні служби здійснюється наступними командами:

```bash
# Активація та запуск системного юніта контейнера
sudo systemctl enable --now systemd-nspawn@web-node1.service

# Перевірка статусу зареєстрованого контейнера через утиліту machinectl
machinectl status web-node1

# Огляд журналів контейнера у реальному часі
journalctl -M web-node1 -f
```

Коли демон `systemd` запускає юніт `systemd-nspawn@web-node1.service`, він викликає `systemd-nspawn` із прочитанням налаштувань із файлу `/etc/systemd/nspawn/web-node1.nspawn` та автоматично реєструє новий контейнер у службі `systemd-machined`.

---

### 4. Програмний моніторинг та управління контейнером через D-Bus API

Для програмного управління контейнерами розробники можуть використовувати бібліотеку `libsystemd` (компонент `sd-bus`). Системний демон `systemd-machined` експортує шинний інтерфейс `org.freedesktop.machine1`, через який можна запитувати статус контейнерів, мапувати директорії або завершувати роботи процесів.

Принцип роботи D-Bus виклику полягає у маршалінгу (серіалізації) аргументів у двійковий формат D-Bus, надсиланні повідомлення через доменний сокет `/run/dbus/system_bus_socket` та очікуванні відповіді від демона `systemd-machined`.

Наведений нижче приклад описує створення програми, яка підключається до системної шини D-Bus, викликає метод `GetMachine` у служби `systemd-machined` для перевірки стану контейнера `web-node1` та отримує його внутрішній об'єктний шлях D-Bus.

:::tabs
```c
/* Inspector.c — Отримання даних контейнера nspawn через libsystemd sd-bus */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <systemd/sd-bus.h>

int main(int argc, char *argv[]) {
    const char *machine_name = (argc > 1) ? argv[1] : "web-node1";
    sd_bus *bus = NULL;
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    char *path = NULL;
    int r;

    /* 1. Підключення до системної шини D-Bus хоста */
    r = sd_bus_open_system(&bus);
    if (r < 0) {
        fprintf(stderr, "Помилка підключення до системної шини D-Bus: %s\n", strerror(-r));
        return EXIT_FAILURE;
    }

    /* 2. Виклик методу GetMachine(s) у служби org.freedesktop.machine1 */
    r = sd_bus_call_method(
        bus,
        "org.freedesktop.machine1",           /* Назва D-Bus сервісу */
        "/org/freedesktop/machine1",          /* Шлях до менеджера */
        "org.freedesktop.machine1.Manager",   /* Інтерфейс */
        "GetMachine",                         /* Назва методу */
        &error,                               /* Структура помилки */
        &m,                                   /* Повідомлення відповіді */
        "s",                                  /* Сигнатура вхідних даних */
        machine_name                          /* Назва контейнера */
    );

    if (r < 0) {
        fprintf(stderr, "Не вдалося знайти контейнер '%s': %s\n", machine_name, error.message);
        sd_bus_error_free(&error);
        sd_bus_unref(bus);
        return EXIT_FAILURE;
    }

    /* 3. Читання об'єктного шляху з отриманого повідомлення */
    r = sd_bus_message_read(m, "o", &path);
    if (r < 0) {
        fprintf(stderr, "Помилка розбору відповіді D-Bus: %s\n", strerror(-r));
        sd_bus_message_unref(m);
        sd_bus_unref(bus);
        return EXIT_FAILURE;
    }

    printf("Контейнер '%s' успішно зареєстровано у службі systemd-machined!\n", machine_name);
    printf("Об'єктний шлях D-Bus: %s\n", path);

    /* 4. Звільнення ресурсів */
    sd_bus_message_unref(m);
    sd_bus_unref(bus);
    return EXIT_SUCCESS;
}
```
```cpp
// Inspector.cpp — Ідіоматична реалізація мовою C++20 із використанням RAII та std::expected
#include <iostream>
#include <memory>
#include <string_view>
#include <system_error>
#include <expected>
#include <systemd/sd-bus.h>

namespace nspawn {

struct SDBusDeleter {
    void operator()(sd_bus* bus) const noexcept {
        if (bus) sd_bus_unref(bus);
    }
};

struct SDMessageDeleter {
    void operator()(sd_bus_message* msg) const noexcept {
        if (msg) sd_bus_message_unref(msg);
    }
};

using BusPtr = std::unique_ptr<sd_bus, SDBusDeleter>;
using MessagePtr = std::unique_ptr<sd_bus_message, SDMessageDeleter>;

class MachineInspector {
public:
    static std::expected<MachineInspector, std::error_code> create() {
        sd_bus* raw_bus = nullptr;
        int r = sd_bus_open_system(&raw_bus);
        if (r < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(-r)));
        }
        return MachineInspector(BusPtr(raw_bus));
    }

    std::expected<std::string, std::error_code> get_machine_path(std::string_view machine_name) const {
        sd_bus_error error = SD_BUS_ERROR_NULL;
        sd_bus_message* raw_msg = nullptr;

        int r = sd_bus_call_method(
            bus_.get(),
            "org.freedesktop.machine1",
            "/org/freedesktop/machine1",
            "org.freedesktop.machine1.Manager",
            "GetMachine",
            &error,
            &raw_msg,
            "s",
            machine_name.data()
        );

        sd_bus_error_free(&error);
        if (r < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(-r)));
        }

        MessagePtr msg(raw_msg);
        const char* path_str = nullptr;
        r = sd_bus_message_read(msg.get(), "o", &path_str);
        if (r < 0 || !path_str) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(-r)));
        }

        return std::string(path_str);
    }

private:
    explicit MachineInspector(BusPtr bus) : bus_(std::move(bus)) {}
    BusPtr bus_;
};

} // namespace nspawn

int main(int argc, char* argv[]) {
    const std::string_view target_machine = (argc > 1) ? argv[1] : "web-node1";

    auto inspector_res = nspawn::MachineInspector::create();
    if (!inspector_res) {
        std::cerr << "Помилка ініціалізації D-Bus: " << inspector_res.error().message() << '\n';
        return 1;
    }

    auto path_res = inspector_res->get_machine_path(target_machine);
    if (!path_res) {
        std::cerr << "Контейнер '" << target_machine << "' не знайдено або він зупинений.\n";
        return 1;
    }

    std::cout << "Успішно знайдено контейнер '" << target_machine << "'\n";
    std::cout << "Об'єктний шлях D-Bus: " << *path_res << '\n';
    return 0;
}
```
:::
